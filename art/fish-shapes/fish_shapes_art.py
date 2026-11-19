"""Ticket 23 candidates: top-down fish outlines for the shoals, in the style of the approved fish shadow (art/dive-visuals).

White shapes on 64x64, facing east (head to the right), that the renderer tints, scales, fades and bends:
  FishSlim.png     a slim, mackerel-like fish
  FishStocky.png   a deep-bodied, bream-like fish
  FishLarge.png    a big, broad-headed fish
  FishLong.png     a long, eel-like fish (shoals of 1-2)
The generic outline is the approved fish shadow (art/dive-visuals ShadowB), unchanged; since ticket 27 it ships as
FishShadow_Medium.png, the same pixels.

Two candidate looks: A, soft edge like the approved shadow (1.6 px blur); B, crisper (0.8 px blur).

The tail sway is a bent mesh in the game, not extra textures: the body's tail half shifts sideways by a travelling wave.
The sheet shows the same bend, done here by shifting pixel columns.

Ticket 27: depth sets how crisp a fish's edge is. Every look-A outline, the generic one included, is also drawn at the
three depth blur levels of art/depth_blur.py (crisp 0.8 px, medium 1.6 px = look A, soft 2.8 px), and the game
crossfades them by depth. The medium level is pixel for pixel the approved look A.

Usage: python -I fish_shapes_art.py <out_dir> [<texture_dir>]
Writes the candidate textures and the panels for the contact sheet into out_dir, and the depth blur levels
(Fish<Name>_<Crisp|Medium|Soft>.png) with their panels into out_dir/levels. With texture_dir it also writes the
depth blur levels there as the game's textures (the generic outline as FishShadow_<Level>.png).
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from depth_blur import blur_levels  # noqa: E402

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
TEX = Path(sys.argv[2]) if len(sys.argv) > 2 else None
HERE = Path(__file__).resolve().parent
GENERIC = HERE.parent.parent / "Textures" / "Spearfishing" / "Dive" / "FishShadow_Medium.png"
SS = 8
N = 64


def white_shape(draw_fn, blur):
    a = Image.new("L", (N * SS, N * SS), 0)
    draw_fn(ImageDraw.Draw(a), SS)
    if blur:
        a = a.filter(ImageFilter.GaussianBlur(blur * SS))
    a = a.resize((N, N), Image.LANCZOS)
    img = Image.new("RGBA", (N, N), (255, 255, 255, 0))
    img.putalpha(a)
    return img


def pts(u, ps):
    return [(x * u, y * u) for x, y in ps]


def slim(d, u):
    d.ellipse([14 * u, 26 * u, 56 * u, 38 * u], fill=255)
    d.polygon(pts(u, [(19, 32), (4, 23), (9, 32), (4, 41)]), fill=255)


def stocky(d, u):
    d.ellipse([18 * u, 19 * u, 55 * u, 45 * u], fill=255)
    d.polygon(pts(u, [(24, 32), (9, 21), (13, 32), (9, 43)]), fill=255)


def large(d, u):
    d.ellipse([14 * u, 17 * u, 60 * u, 47 * u], fill=255)
    d.polygon(pts(u, [(18, 32), (3, 17), (7, 32), (3, 47)]), fill=255)
    # Pectoral fins, so the big fish reads broad at the shoulders.
    d.polygon(pts(u, [(46, 24), (33, 11), (30, 23)]), fill=255)
    d.polygon(pts(u, [(46, 40), (33, 53), (30, 41)]), fill=255)


def long(d, u):
    d.polygon(pts(u, [(61, 32), (57, 28.5), (44, 27.5), (24, 29), (8, 30.5), (3, 32), (8, 33.5), (24, 35), (44, 36.5),
                      (57, 35.5)]), fill=255)
    d.polygon(pts(u, [(10, 32), (2, 27), (4, 32), (2, 37)]), fill=255)


SHAPES = {"Slim": slim, "Stocky": stocky, "Large": large, "Long": long}
LOOKS = {"A": 1.6, "B": 0.8}
# Drawn size in cells over the shallowest water, and how many fish a full shoal holds (the game's ranges).
SIZE = {"Generic": 0.6, "Slim": 0.55, "Stocky": 0.6, "Large": 0.85, "Long": 1.0}
SHOAL = {"Generic": 6, "Slim": 8, "Stocky": 5, "Large": 3, "Long": 2}
# Over the shallowest and the deepest water: size factor and alpha (the game's values).
SHALLOW = (1.0, 0.50)
DEEP = (0.72, 0.28)
# Tail sway: sideways shift of the tail tip as a share of the fish's length (the game's value).
SWAY = 0.09

generic = Image.open(GENERIC).convert("RGBA")
candidates = {look: {"Generic": generic, **{name: white_shape(fn, blur) for name, fn in SHAPES.items()}} for look, blur in LOOKS.items()}
for look, shapes in candidates.items():
    for name, img in shapes.items():
        if name != "Generic":
            img.save(OUT / f"Fish{name}_{look}.png")

WATER_SHALLOW = (58, 104, 100)
WATER_DEEP = (34, 70, 84)
TINT = (8, 20, 26)
CELL = 77  # px per cell, as in the capture
font = ImageFont.load_default(size=16)


def tinted(img, alpha):
    t = Image.new("RGBA", img.size, TINT + (0,))
    t.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    return t


def bend(img, phase, amp):
    """The game's sway: the tail half shifts sideways by a travelling wave, the head stays put."""
    w, h = img.size
    out = Image.new("RGBA", img.size, (255, 255, 255, 0))
    for x in range(w):
        t = 1 - x / (w - 1)  # 0 at the head, 1 at the tail
        off = amp * h * t * t * math.sin(phase + 2.4 * t)
        out.alpha_composite(img.crop((x, 0, x + 1, h)), (x, int(round(off))))
    return out


def fish_at(bg, img, size_cells, alpha, cx, cy, heading_deg, phase=0.0, amp=0.0):
    px = max(4, int(CELL * size_cells))
    f = img.resize((px, px), Image.LANCZOS)
    if amp:
        f = bend(f, phase, amp)
    f = tinted(f, alpha).rotate(heading_deg, expand=True, resample=Image.BICUBIC)
    bg.alpha_composite(f, (int(cx - f.width / 2), int(cy - f.height / 2)))


def alone(img, scale=3):
    big = img.resize((N * scale, N * scale), Image.LANCZOS)
    bg = Image.new("RGBA", big.size, WATER_SHALLOW + (255,))
    bg.alpha_composite(tinted(big, 0.55))
    return bg


# Follower offsets behind and beside the leader, in cells (leader first), as the game lays them out.
OFFSETS = [(0, 0), (-0.7, 0.45), (-0.7, -0.45), (-1.35, 0.0), (-1.35, 0.85), (-1.35, -0.85), (-2.0, 0.4), (-2.0, -0.4)]


def shoal(name, img):
    bg = Image.new("RGBA", (CELL * 4, CELL * 4), WATER_SHALLOW + (255,))
    n = SHOAL[name]
    spread = 1.3 if name in ("Large", "Long") else 1.0
    heading = 20.0
    hx, hy = CELL * 2.9, CELL * 2.0
    for i in range(n):
        ox, oz = OFFSETS[i]
        ox *= spread
        oz *= spread
        a = math.radians(heading)
        x = hx + (ox * math.cos(a) + oz * math.sin(a)) * CELL
        y = hy - (ox * math.sin(a) - oz * math.cos(a)) * CELL
        fish_at(bg, img, SIZE[name], SHALLOW[1], x, y, heading + (i * 7 % 11) - 5, phase=i * 1.3, amp=SWAY)
    return bg


def sway(name, img):
    """Six frames of one tail beat, two cells wide each, in a 3 by 2 grid."""
    w = CELL * 2
    bg = Image.new("RGBA", (w * 3, w * 2), WATER_SHALLOW + (255,))
    for k in range(6):
        fish_at(bg, img, 1.6, 0.55, w * (k % 3) + w / 2, w * (k // 3) + w / 2, 0, phase=k * 2 * math.pi / 6, amp=SWAY)
    return bg


def depths(name, img):
    w = CELL * 2
    bg = Image.new("RGBA", (w * 2, w), WATER_SHALLOW + (255,))
    ImageDraw.Draw(bg).rectangle([w, 0, w * 2, w], fill=WATER_DEEP + (255,))
    for i, (scale, alpha) in enumerate((SHALLOW, DEEP)):
        fish_at(bg, img, SIZE[name] * scale, alpha, w * i + w / 2, w / 2, 30, phase=0.6, amp=SWAY)
    d = ImageDraw.Draw(bg)
    d.text((6, 4), "shallow", font=font, fill=(225, 235, 235))
    d.text((w + 6, 4), "deep", font=font, fill=(225, 235, 235))
    return bg


for look, shapes in candidates.items():
    for name, img in shapes.items():
        alone(img).save(OUT / f"{look}-{name}-1-alone.png")
        shoal(name, img).save(OUT / f"{look}-{name}-2-shoal.png")
        sway(name, img).save(OUT / f"{look}-{name}-3-sway.png")
        depths(name, img).save(OUT / f"{look}-{name}-4-depth.png")


# ---- Ticket 27: depth blur levels.
def generic(d, u):
    """The generic outline, redrawn from shadow_a in art/dive-visuals/dive_art.py, so it can take every blur level."""
    d.ellipse([18 * u, 22 * u, 54 * u, 42 * u], fill=255)
    d.polygon(pts(u, [(22, 32), (8, 21), (12, 32), (8, 43)]), fill=255)


LEVELS_OUT = OUT / "levels"
LEVELS_OUT.mkdir(exist_ok=True)
levels = {name: blur_levels(fn, N, SS) for name, fn in {"Generic": generic, **SHAPES}.items()}
for name, by_level in levels.items():
    for level, img in by_level.items():
        img.save(LEVELS_OUT / f"Fish{name}_{level}.png")
        if TEX:
            img.save(TEX / f"{'FishShadow' if name == 'Generic' else 'Fish' + name}_{level}.png")

# Shallow, middle and deep water, paired with the level the game shows there (depth 0, 0.5, 1).
WATER_MIDDLE = tuple((a + b) // 2 for a, b in zip(WATER_SHALLOW, WATER_DEEP))
DEPTH_STEPS = {"Crisp": (0.0, WATER_SHALLOW), "Medium": (0.5, WATER_MIDDLE), "Soft": (1.0, WATER_DEEP)}


def level_panel(name, img, level):
    """4 by 4 cells of water at the level's depth: the outline alone, 2x, in an inset, and a shoal at game scale."""
    depth, water = DEPTH_STEPS[level]
    scale = SHALLOW[0] + (DEEP[0] - SHALLOW[0]) * depth
    alpha = SHALLOW[1] + (DEEP[1] - SHALLOW[1]) * depth
    bg = Image.new("RGBA", (CELL * 4, CELL * 4), water + (255,))
    inset = img.resize((N * 2, N * 2), Image.LANCZOS)
    box = Image.new("RGBA", inset.size, WATER_SHALLOW + (255,))
    box.alpha_composite(tinted(inset, 0.55))
    bg.alpha_composite(box, (6, 6))
    ImageDraw.Draw(bg).rectangle([5, 5, 6 + N * 2, 6 + N * 2], outline=(225, 235, 235))
    n = SHOAL[name]
    spread = 1.3 if name in ("Large", "Long") else 1.0
    heading = 20.0
    hx, hy = CELL * 2.9, CELL * 2.2
    for i in range(n):
        ox, oz = OFFSETS[i]
        ox *= spread
        oz *= spread
        a = math.radians(heading)
        x = hx + (ox * math.cos(a) + oz * math.sin(a)) * CELL
        y = hy - (ox * math.sin(a) - oz * math.cos(a)) * CELL
        fish_at(bg, img, SIZE[name] * scale, alpha, x, y, heading + (i * 7 % 11) - 5, phase=i * 1.3, amp=SWAY)
    return bg


for name, by_level in levels.items():
    for level, img in by_level.items():
        level_panel(name, img, level).save(LEVELS_OUT / f"{name}-{level}-panel.png")
print(OUT)
