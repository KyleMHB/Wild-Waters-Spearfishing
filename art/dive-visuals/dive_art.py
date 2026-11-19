"""Ticket 12 candidates: fish shadow and spear burst, 64x64, white shapes the renderer tints. Facing east.
Usage: python -I dive_art.py <out_dir> <frame_png> <frame_png>"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
FRAMES = sys.argv[2:]
SS = 8
N = 64


def finish(img, blur=0):
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur * SS))
    return img.resize((N, N), Image.LANCZOS)


def white_shape(draw_fn, blur=0):
    a = Image.new("L", (N * SS, N * SS), 0)
    draw_fn(ImageDraw.Draw(a), N * SS)
    a = finish(a, blur)
    img = Image.new("RGBA", (N, N), (255, 255, 255, 0))
    img.putalpha(a)
    return img


def ellipse_pts(cx, cy, rx, ry, n=48, a0=0, a1=360):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


# ---- Fish shadows (east-facing). Bold, few parts: body plus tail.
def shadow_a(d, s):  # plump body, forked tail, hard edge
    u = s / 64
    d.ellipse([18 * u, 22 * u, 54 * u, 42 * u], fill=255)
    d.polygon([(22 * u, 32 * u), (8 * u, 21 * u), (12 * u, 32 * u), (8 * u, 43 * u)], fill=255)


def shadow_b(d, s):  # same plan, softened like a shadow seen through water
    shadow_a(d, s)


def shadow_c(d, s):  # slim mackerel: long body, small fan tail
    u = s / 64
    d.ellipse([16 * u, 26 * u, 56 * u, 38 * u], fill=255)
    d.polygon([(20 * u, 32 * u), (6 * u, 24 * u), (10 * u, 32 * u), (6 * u, 40 * u)], fill=255)


SHADOWS = {"A plump, hard edge": white_shape(shadow_a), "B plump, soft edge": white_shape(shadow_b, blur=1.6),
           "C slim, soft edge": white_shape(shadow_c, blur=1.2)}


# ---- Bursts (drawn white, grown and faded by the renderer).
def burst_a(d, s):  # one bold ring
    u = s / 64
    d.ellipse([8 * u, 8 * u, 56 * u, 56 * u], fill=255)
    d.ellipse([17 * u, 17 * u, 47 * u, 47 * u], fill=0)


def burst_b(d, s):  # six chunky droplets around a small centre
    u = s / 64
    c = 32 * u
    for k in range(6):
        a = math.radians(k * 60 + 30)
        x, y = c + math.cos(a) * 20 * u, c + math.sin(a) * 20 * u
        d.ellipse([x - 6 * u, y - 6 * u, x + 6 * u, y + 6 * u], fill=255)
    d.ellipse([c - 7 * u, c - 7 * u, c + 7 * u, c + 7 * u], fill=255)


def burst_c(d, s):  # four-point splash star
    u = s / 64
    c = 32 * u
    pts = []
    for k in range(8):
        a = math.radians(k * 45)
        r = (28 if k % 2 == 0 else 9) * u
        pts.append((c + math.cos(a) * r, c + math.sin(a) * r))
    d.polygon(pts, fill=255)


BURSTS = {"A ring": white_shape(burst_a, blur=0.4), "B droplets": white_shape(burst_b, blur=0.3), "C splash star": white_shape(burst_c, blur=0.3)}

for name, img in {**{"Shadow" + k[0]: v for k, v in SHADOWS.items()}, **{"Burst" + k[0]: v for k, v in BURSTS.items()}}.items():
    img.save(OUT / f"{name}.png")

# ---- Contact sheet
WATER = (52, 92, 92)
SHADOW_TINT = (8, 20, 26)
font = ImageFont.load_default(size=18)
small = ImageFont.load_default(size=14)


def tinted(img, rgb, alpha):
    t = Image.new("RGBA", img.size, rgb + (0,))
    t.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    return t


def tile(img, rgb, alpha, scale):
    big = img.resize((N * scale, N * scale), Image.LANCZOS)
    bg = Image.new("RGBA", big.size, WATER + (255,))
    bg.alpha_composite(tinted(big, rgb, alpha))
    return bg


def game_scale(img, rgb, alpha, scene=False):
    # About 77 px per cell in the capture; shadow drawn 0.75 cells, three circling a centre.
    cell = 77
    bg = Image.new("RGBA", (cell * 5, cell * 5), WATER + (255,))
    size = int(cell * 0.75)
    small_img = tinted(img.resize((size, size), Image.LANCZOS), rgb, alpha)
    cx = cy = cell * 2.5
    for i, (r, a) in enumerate([(1.1, 20), (1.5, 150), (1.9, 260)]):
        rot = small_img.rotate(-(a + 90), expand=True, resample=Image.BICUBIC)  # face along the circle, as in game
        x = cx + math.cos(math.radians(a)) * r * cell - rot.width / 2
        y = cy + math.sin(math.radians(a)) * r * cell - rot.height / 2
        bg.alpha_composite(rot, (int(x), int(y)))
    return bg


W = 1840
rows = []
sheet = Image.new("RGBA", (W, 1700), (30, 30, 34, 255))
d = ImageDraw.Draw(sheet)
d.text((20, 12), "Spearfishing ticket 12: dive visuals candidates (pending approval). Textures are white shapes; the game tints and fades them.", font=font, fill=(235, 235, 235))
y = 50
d.text((20, y), "Fish shadows (64x64, facing east, drawn 0.75 cells, dark tint at 45% opacity, under Waves' foam)", font=font, fill=(200, 220, 255))
y += 30
x = 20
for name, img in SHADOWS.items():
    d.text((x, y), name, font=small, fill=(230, 230, 230))
    sheet.alpha_composite(tile(img, SHADOW_TINT, 0.45, 3), (x, y + 20))
    sheet.alpha_composite(game_scale(img, SHADOW_TINT, 0.45), (x + 200, y + 20))
    x += 200 + 385 + 20
d.text((20, y + 430), "left: 3x zoom; right: three circling one diver at capture scale (~77 px per cell)", font=small, fill=(170, 170, 170))
y += 460
d.text((20, y), "Spear burst (64x64, pale blue-white; grows 0.5 to 1.6 cells while fading out over 0.6 s)", font=font, fill=(200, 220, 255))
y += 30
x = 20
for name, img in BURSTS.items():
    d.text((x, y), name, font=small, fill=(230, 230, 230))
    for j, (k, sc) in enumerate([(1.0, 0.6), (0.6, 1.0), (0.25, 1.4)]):
        size = int(77 * sc)
        bg = Image.new("RGBA", (120, 120), WATER + (255,))
        b = tinted(img.resize((size, size), Image.LANCZOS), (215, 240, 255), k)
        bg.alpha_composite(b, ((120 - size) // 2, (120 - size) // 2))
        sheet.alpha_composite(bg, (x + j * 125, y + 20))
    x += 3 * 125 + 160
d.text((20, y + 150), "each: start, middle, end of the burst at capture scale", font=small, fill=(170, 170, 170))
y += 190
d.text((20, y), "In game, placeholders (raw fish tinted dark; vanilla flash): diver hidden mid-dive, label stays; three shadows circle", font=font, fill=(200, 220, 255))
y += 30
x = 20
for f in FRAMES:
    im = Image.open(f).convert("RGBA")
    crop = im.crop((640, 160, 1900, 1000)).resize((630, 420), Image.LANCZOS)
    sheet.alpha_composite(crop, (x, y))
    x += 650
sheet = sheet.crop((0, 0, W, y + 440))
sheet.convert("RGB").save(OUT / "dive-visuals-contact-sheet.png")
print(OUT / "dive-visuals-contact-sheet.png")
