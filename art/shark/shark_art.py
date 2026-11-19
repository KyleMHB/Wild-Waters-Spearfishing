"""Ticket 11, part 1: the shark shadow, our own top-down silhouette in the style of the fish shoal outlines.

A white shape facing east (snout to the right), like the fish, that the renderer tints, scales, fades, bends and
turns by heading. Pointed snout, long swept-back pectoral fins, small pelvic fins, a slim body tapering to a thin
tail stalk and a forked tail with one lobe longer. Drawn procedurally; no Waves or other mod's art is used.

One texture per depth blur level from art/depth_blur.py (crisp 0.8, medium 1.6, soft 2.8 texels). The shark is
256 x 256 rather than the fish's 64 so its texels per cell (about 109 at 2.35 cells) are close to the deep dive shadow's
(about 116, 64 px at 0.55 cells): the blur levels are in texels, so a smaller texture would blur the shark far more than
the diver beside it. The shape is laid out in 128-space texels and scaled to N.

Second candidate (after the first in-game look): the first shark drew at the dive shadow's bottom-of-dive scale, about
1 cell and alpha 0.30 over deep ocean, and was lost among the fish shadows (deep fish: up to 0.72 cells, alpha 0.28).
This one is SHARK_SIZE cells of canvas over deep ocean (a body of about 2.2 cells, a 2 to 3 m shark beside a pawn),
scaled from there by the diver's bottom size, with a material alpha of 0.70 over deep water rising to 0.85 at the
lunge. The body and fins are drawn at texture alpha BODY / 255 and the dorsal ridge and spine at full alpha, so the
tint shows a darker ridge down the back.

Usage:
  python -I shark_art.py <out_dir> [<texture_dir>]
      Writes SharkShadow_<Crisp|Medium|Soft>.png (128 x 128) and the contact-sheet panels into out_dir. With
      texture_dir it also writes the three textures there (part 2 only, after approval).
  python -I shark_art.py --stack <out.png> <sheet.png>...
      Stacks contact sheets top to bottom on the sheet background.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from depth_blur import BLUR_LEVELS, blur_levels  # noqa: E402

N = 256
ROOT = Path(__file__).resolve().parent.parent.parent
DIVE = ROOT / "Textures" / "Spearfishing" / "Dive"

# Drawn canvas size of the shark in cells over deep ocean (the body is 120 of the 128 texels, so about 2.2 cells); the
# size strip offers bodies of about 1.8, 2.2 and 2.5 cells. Must match SharkLength in DiveVisuals.cs.
SHARK_SIZE = 2.35
SIZE_STRIP = (1.9, 2.35, 2.65)
# The shark's material alpha over the shallowest and the deepest water; must match DiveVisuals.cs.
SHARK_SHALLOW_ALPHA, SHARK_DEEP_ALPHA = 0.85, 0.70
# Dive shadow values from Source/Visuals/DiveVisuals.cs.
DIVER_SURFACE = 1.35
DEPTHS = {  # name: (depth, diver bottom size in cells, bottom alpha, blur level)
    "Shallow": (0.0, 0.85, 0.50, "Crisp"),
    "Middle": (0.5, 0.70, 0.36, "Medium"),
    "Deep": (1.0, 0.55, 0.22, "Soft"),
}
DIVER_OFFSET = 0.3  # cells behind the heading
SWAY = 0.06  # tail tip shift as a share of length; a shark beats slower and stiffer than the fish's 0.09

WATER_SHALLOW = (58, 104, 100)
WATER_DEEP = (34, 70, 84)
WATER_MIDDLE = tuple((a + b) // 2 for a, b in zip(WATER_SHALLOW, WATER_DEEP))
WATER = {"Shallow": WATER_SHALLOW, "Middle": WATER_MIDDLE, "Deep": WATER_DEEP}
TINT = (8, 20, 26)  # the game's ShadowColor
CELL = 77  # px per cell, as in the fish sheets
LABEL = (225, 235, 235)
font = ImageFont.load_default(size=14)


def half_width(s):
    """Body half-width in 128-space texels at s, 0 at the snout and 1 at the tail stalk."""
    if s < 0.32:
        return 13 * math.sin(math.pi / 2 * s / 0.32) ** 0.95  # a pointed, not rounded, snout
    return 2.5 + 10.5 * (1 - (s - 0.32) / 0.68) ** 1.5


# Texture alpha of the body and fins; the dorsal ridge is at full alpha, so the tint draws it as a darker core along the
# back. From straight above a dorsal fin is edge-on, so this ridge is how the silhouette shows it.
BODY = 190
RIDGE = 255


def shark(d, u):
    """The shark in 128-space texels, drawn at u texture pixels per texel (scaled again for an N other than 128)."""
    u = u * N / 128
    snout, stalk = 124, 25
    steps = 200
    xs = [snout - (snout - stalk) * i / steps for i in range(steps + 1)]
    top = [(x, 64 - half_width((snout - x) / (snout - stalk))) for x in xs]
    bottom = [(x, 64 + half_width((snout - x) / (snout - stalk))) for x in reversed(xs)]
    d.polygon([(x * u, y * u) for x, y in top + bottom], fill=BODY)
    for side in (-1, 1):
        # Pectoral fins: long, sickle-shaped and swept back, the widest point of the silhouette.
        fin = [(96, 9), (88, 22), (77, 34), (68, 40), (71, 32), (79, 19), (82, 9)]
        d.polygon([(x * u, (64 + side * y) * u) for x, y in fin], fill=BODY)
        # Pelvic fins: small, near the vent.
        pelvic = [(52, 4), (45, 10), (42, 10), (44, 4)]
        d.polygon([(x * u, (64 + side * y) * u) for x, y in pelvic], fill=BODY)
    # Crescent tail: two swept lobes, the upper one longer, with a concave trailing edge.
    tail = [(28, -2.5), (20, -9), (9, -18), (2, -23), (8, -14), (13, -6), (15, 0), (13, 5), (9, 11),
            (4, 16), (11, 13), (19, 7), (28, 2.5)]
    d.polygon([(x * u, (64 + y) * u) for x, y in tail], fill=BODY)
    # Dorsal ridge: a slim wedge on the back behind the pectorals, pointed at both ends.
    ridge = [(82, 0), (74, -2.6), (64, -3.4), (56, -2.2), (46, 0), (56, 2.2), (64, 3.4), (74, 2.6)]
    d.polygon([(x * u, (64 + y) * u) for x, y in ridge], fill=RIDGE)
    # A fainter line of the same dark down the back to the tail, so the spine reads from snout to tail.
    d.polygon([(x * u, (64 + y) * u) for x, y in [(104, 0), (90, -1.6), (82, 0), (90, 1.6)]], fill=225)
    d.polygon([(x * u, (64 + y) * u) for x, y in [(46, 0), (38, -1.2), (28, 0), (38, 1.2)]], fill=225)


def tinted(img, alpha):
    t = Image.new("RGBA", img.size, TINT + (0,))
    t.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    return t


def bend(img, phase, amp):
    """The game's sway: the tail half shifts sideways by a travelling wave, the head stays put."""
    w, h = img.size
    out = Image.new("RGBA", img.size, (255, 255, 255, 0))
    for x in range(w):
        t = 1 - x / (w - 1)
        off = amp * h * t * t * math.sin(phase + 2.4 * t)
        out.alpha_composite(img.crop((x, 0, x + 1, h)), (x, int(round(off))))
    return out


def place(bg, tex, size_cells, alpha, cx, cy, rotate_deg, phase=None):
    px = max(4, int(CELL * size_cells))
    f = tex.resize((px, px), Image.LANCZOS)
    if phase is not None:
        f = bend(f, phase, SWAY)
    f = tinted(f, alpha).rotate(rotate_deg, expand=True, resample=Image.BICUBIC)
    bg.alpha_composite(f, (int(round(cx - f.width / 2)), int(round(cy - f.height / 2))))


def depth_values(depth_name, shark_size=SHARK_SIZE):
    depth, bottom, _, level = DEPTHS[depth_name]
    alpha = SHARK_SHALLOW_ALPHA + (SHARK_DEEP_ALPHA - SHARK_SHALLOW_ALPHA) * depth
    return shark_size * bottom / DEPTHS["Deep"][1], alpha, level, bottom


def draw_diver(bg, divers, depth_name, cx, cy, heading=90.0):
    """The diver's dive shadow at the bottom of a dive, heading in degrees anticlockwise from east."""
    _, bottom, alpha, level = DEPTHS[depth_name]
    h = math.radians(heading)
    x, y = cx - DIVER_OFFSET * CELL * math.cos(h), cy + DIVER_OFFSET * CELL * math.sin(h)
    place(bg, divers[level], bottom, alpha, x, y, heading - 90)


def draw_shark(bg, sharks, level, size, alpha, cx, cy, heading, phase):
    place(bg, sharks[level], size, alpha, cx, cy, heading, phase)


def grid(bg):
    d = ImageDraw.Draw(bg)
    for i in range(1, bg.width // CELL + 1):
        d.line([(i * CELL, 0), (i * CELL, bg.height)], fill=(255, 255, 255, 28))
    for i in range(1, bg.height // CELL + 1):
        d.line([(0, i * CELL), (bg.width, i * CELL)], fill=(255, 255, 255, 28))


def water(cells_w, cells_h, colour):
    bg = Image.new("RGBA", (CELL * cells_w, CELL * cells_h), colour + (255,))
    over = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    grid(over)
    bg.alpha_composite(over)
    return bg


def caption(bg, text):
    ImageDraw.Draw(bg).text((6, bg.height - 20), text, font=font, fill=LABEL)


def depth_panel(sharks, divers, depth_name):
    """Shark beside the diver at the bottom of a dive, with the outline alone in an inset."""
    size, alpha, level, _ = depth_values(depth_name)
    bg = water(4, 4, WATER[depth_name])
    inset = sharks[level].resize((96, 96), Image.LANCZOS)
    box = Image.new("RGBA", inset.size, WATER_SHALLOW + (255,))
    box.alpha_composite(tinted(inset, 0.55))
    bg.alpha_composite(box, (6, 6))
    ImageDraw.Draw(bg).rectangle([5, 5, 102, 102], outline=LABEL)
    draw_diver(bg, divers, depth_name, CELL * 1.4, CELL * 2.3)
    draw_shark(bg, sharks, level, size, alpha, CELL * 2.75, CELL * 2.55, 70, 0.8)
    caption(bg, f"shark {size:.2f}, diver {DEPTHS[depth_name][1]:.2f}, alpha {alpha:.2f}, {level.lower()}")
    return bg


def size_panel(sharks, divers, shark_size):
    size, alpha, level, _ = depth_values("Middle", shark_size)
    bg = water(4, 4, WATER_MIDDLE)
    draw_diver(bg, divers, "Middle", CELL * 1.0, CELL * 2.0)
    draw_shark(bg, sharks, level, size, alpha, CELL * 2.6, CELL * 2.0, 90, 0.8)
    caption(bg, f"{shark_size:.2f} cells over deep ocean, shown at middle depth")
    return bg


# Encounter frames over deep water, diver at the bottom of the dive facing north at the panel's centre.
# Each frame: (shark x, y in cells, heading anticlockwise from east, size factor, alpha, level, tail phase).
DEEP_SIZE, DEEP_ALPHA, _, _ = depth_values("Deep")
MID_SIZE, MID_ALPHA, _, _ = depth_values("Middle")


def circle(angle_deg, radius):
    a = math.radians(angle_deg)
    return 2 + radius * math.cos(a), 2 - radius * math.sin(a), angle_deg + 90  # anticlockwise, tangent heading


FRAMES = {
    # Passing: fades in at the edge and circles the diver once, wide, at the diver's depth.
    "Passing": [
        (*circle(-60, 1.35), 1.0, DEEP_ALPHA * 0.35, "Soft", 0.0, "0.0 s fades in"),
        (*circle(-15, 1.3), 1.0, DEEP_ALPHA * 0.8, "Soft", 1.6, "0.8 s"),
        (*circle(35, 1.25), 1.0, DEEP_ALPHA, "Soft", 3.2, "1.6 s"),
        (*circle(85, 1.2), 1.0, DEEP_ALPHA, "Soft", 4.8, "2.4 s"),
    ],
    # Striking: turns in and lunges; it comes up to the diver, so it grows, darkens and sharpens towards medium.
    "Striking": [
        (*circle(130, 1.3)[:2], -50, 1.0, DEEP_ALPHA, "Soft", 0.0, "0.0 s turns in"),
        (2 - 0.75, 2 - 0.35, -20, 1.05, (DEEP_ALPHA + MID_ALPHA) / 2, "Soft", 1.2, "0.3 s"),
        (2 - 0.15, 2 - 0.05, -10, 1.12, MID_ALPHA, "Medium", 2.4, "0.5 s bite"),
        (2 + 0.25, 2 + 0.2, -40, 1.08, MID_ALPHA, "Medium", 3.6, "0.7 s"),
    ],
    # Leaving: swings away and sinks, shrinking and fading out at the soft level.
    "Leaving": [
        (2 + 0.7, 2 + 0.55, -50, 1.0, DEEP_ALPHA, "Soft", 0.0, "0.0 s turns away"),
        (2 + 1.1, 2 + 1.05, -60, 0.92, DEEP_ALPHA * 0.7, "Soft", 1.6, "0.6 s sinks"),
        (2 + 1.45, 2 + 1.5, -65, 0.85, DEEP_ALPHA * 0.4, "Soft", 3.2, "1.2 s"),
        (2 + 1.75, 2 + 1.9, -70, 0.8, DEEP_ALPHA * 0.12, "Soft", 4.8, "1.8 s gone"),
    ],
}


def frame_panel(sharks, divers, frame):
    x, y, heading, factor, alpha, level, phase, label = frame
    bg = water(4, 4, WATER_DEEP)
    draw_diver(bg, divers, "Deep", CELL * 2, CELL * 2)
    draw_shark(bg, sharks, level, DEEP_SIZE * factor, alpha, CELL * x, CELL * y, heading, phase)
    caption(bg, f"{label}: x{factor:.2f}, alpha {alpha:.2f}, {level.lower()}")
    return bg


def stack(out, sheets):
    imgs = [Image.open(p).convert("RGB") for p in sheets]
    w = max(i.width for i in imgs)
    sheet = Image.new("RGB", (w, sum(i.height for i in imgs)), imgs[0].getpixel((2, 2)))
    y = 0
    for i in imgs:
        sheet.paste(i, (0, y))
        y += i.height
    sheet.save(out)
    print(out, sheet.size)


def main():
    if sys.argv[1] == "--stack":
        stack(sys.argv[2], sys.argv[3:])
        return
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    tex = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    sharks = blur_levels(shark, N)
    for level, img in sharks.items():
        img.save(out / f"SharkShadow_{level}.png")
        if tex:
            img.save(tex / f"SharkShadow_{level}.png")
    divers = {level: Image.open(DIVE / f"DiveShadowPawn_{level}.png").convert("RGBA") for level in BLUR_LEVELS}
    for name in DEPTHS:
        depth_panel(sharks, divers, name).save(out / f"depth-{name}.png")
    for s in SIZE_STRIP:
        size_panel(sharks, divers, s).save(out / f"size-{s:.1f}.png")
    for row, frames in FRAMES.items():
        for i, frame in enumerate(frames, 1):
            frame_panel(sharks, divers, frame).save(out / f"{row.lower()}-{i}.png")
    print(out)


if __name__ == "__main__":
    main()
