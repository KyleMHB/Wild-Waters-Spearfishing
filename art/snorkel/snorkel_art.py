"""Snorkel candidates for Spearfishing. Procedural PIL drawing in the house rendering (art/glass-mask, art/pole-spear): a few
flat two-tone shapes, a black outward outline and black lines between materials, no fine detail.

Each candidate has an item sprite (128x128, Graphic_Single, drawSize 1, 4 px outline at the 8x master's scale) and worn views
for the EyeCover layer (128x128 head textures, _south, _east and _north, 3 px outline), placed on vanilla's 128 px head frame
(head about x 41-87, y 39-89; the glass mask's lens covers y 58-82, so the mouthpiece sits just under it). The tube rises on the
wearer's left, above the head, so the north view shows it.

Usage: python -I snorkel_art.py <out_dir>. Writes Snorkel_<X>_<name>.png and Snorkel_<X>_<name>_<dir>.png, and preview tiles
Preview_<X>_<dir>.png: the worn view over a plain stand-in head (not vanilla art) wearing the approved glass mask, at 2x."""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
HERE = Path(__file__).resolve().parent
MASK_DIR = HERE.parent.parent / "Textures" / "Things" / "Spearfishing" / "Apparel" / "GlassMask"
SS = 8
S = 128
W = S * SS
INK = (12, 10, 10, 255)
WOOD_LIGHT, WOOD_DARK = (196, 146, 92, 255), (150, 104, 62, 255)
REED_LIGHT, REED_DARK = (206, 190, 112, 255), (162, 146, 74, 255)
LEATHER_LIGHT, LEATHER_DARK = (92, 64, 46, 255), (64, 44, 32, 255)
CAP_LIGHT, CAP_DARK = (214, 72, 52, 255), (164, 46, 36, 255)
SKIN, SKIN_DARK, HAIR = (226, 184, 148, 255), (196, 152, 118, 255), (96, 66, 44, 255)
LINE = int(1.5 * SS)


def with_outline(layer, px):
    alpha = layer.getchannel("A").point(lambda v: 255 if v > 127 else 0)
    ring = alpha.filter(ImageFilter.MaxFilter(px * 2 + 1))
    base = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    base.paste(Image.new("RGBA", layer.size, INK), (0, 0), ring)
    base.alpha_composite(layer)
    return base


def finish(img, outline):
    return with_outline(img, outline * SS).resize((S, S), Image.LANCZOS)


def new():
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def stroke(d, pts, width, fill):
    """A thick polyline with round joins and caps, in 128 px units."""
    pts = [(x * SS, y * SS) for x, y in pts]
    w = width * SS
    d.line(pts, fill=fill, width=int(w), joint="curve")
    for x, y in pts:
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=fill)


def arc(cx, cy, r, a0, a1, n=10):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def tube(d, pts, width, light, dark, shine_side=-1):
    """The tube: black line, dark body, a light stripe along one side."""
    stroke(d, pts, width + 3, INK)
    stroke(d, pts, width, dark)
    off = shine_side * width * 0.18
    stroke(d, [(x + off, y + off) for x, y in pts], width * 0.45, light)


def bands(d, pts, width, at, colour):
    """Dark rings across a straight vertical stretch of tube, at the given y values."""
    x = pts[0][0]
    for y in at:
        d.rectangle([(x - width / 2 - 1) * SS, (y - 1.6) * SS, (x + width / 2 + 1) * SS, (y + 1.6) * SS], fill=INK)
        d.rectangle([(x - width / 2) * SS, (y - 1.6) * SS + LINE / 2, (x + width / 2) * SS, (y + 1.6) * SS - LINE / 2], fill=colour)


def cap(d, x, y_top, width, height):
    d.rounded_rectangle([(x - width / 2 - 1.5) * SS, (y_top - 1.5) * SS, (x + width / 2 + 1.5) * SS, (y_top + height + 1.5) * SS],
                        radius=3 * SS, fill=INK)
    d.rounded_rectangle([(x - width / 2) * SS, y_top * SS, (x + width / 2) * SS, (y_top + height) * SS], radius=2 * SS, fill=CAP_DARK)
    d.rounded_rectangle([(x - width / 2) * SS, y_top * SS, x * SS, (y_top + height) * SS], radius=2 * SS, fill=CAP_LIGHT)


def mouthpiece(d, box):
    x0, y0, x1, y1 = box
    r = (y1 - y0) * SS / 2
    d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r, fill=INK)
    d.rounded_rectangle([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, y1 * SS - LINE], radius=r - LINE, fill=LEATHER_DARK)
    d.rounded_rectangle([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, (y0 + y1) / 2 * SS], radius=r / 2, fill=LEATHER_LIGHT)


STYLES = {
    "A": ("plain", WOOD_LIGHT, WOOD_DARK, None, False),
    "B": ("reed", REED_LIGHT, REED_DARK, REED_DARK, False),
    "C": ("redcap", WOOD_LIGHT, WOOD_DARK, None, True),
}


def j_path(x_mouth, y_mouth, x_side, y_top, r):
    """From the mouthpiece across to the side, round the bend, then straight up."""
    return [(x_mouth, y_mouth), (x_side - r, y_mouth)] + arc(x_side - r, y_mouth - r, r, 90, 0) + [(x_side, y_top)]


def draw_snorkel(d, path, width, key, top, band_ys=()):
    _, light, dark, band, capped = STYLES[key]
    tube(d, path, width, light, dark)
    if band:
        bands(d, path[-2:], width, band_ys, band)
    if capped:
        cap(d, top[0], top[1] - width / 2 - 1, width + 3, max(9, width))


# ---- Item sprite ---------------------------------------------------------------------------------------------------------

def item(key, master=False):
    img, d = new()
    path = j_path(34, 100, 92, 14, 16)
    draw_snorkel(d, path, 13, key, (92, 14), band_ys=(30, 48, 66))
    mouthpiece(d, (14, 90, 42, 110))
    return with_outline(img, 4 * SS) if master else finish(img, 4)


# ---- Worn views ----------------------------------------------------------------------------------------------------------

def worn(key):
    # South: mouthpiece under the mask, tube to the wearer's left (viewer's right) and up past the head.
    s, d = new()
    draw_snorkel(d, j_path(66, 86, 92, 26, 7), 6, key, (92, 26), band_ys=(40, 54))
    mouthpiece(d, (56, 82, 72, 90))
    # East: facing right; the tube stands at the back edge of the head, clear of the face, and its arm runs along the jaw
    # to the mouth. Approved change to A: "A, tube moved back" (from the middle of the head).
    e, de = new()
    path = [(92, 85), (56, 85)] + arc(56, 78, 7, 90, 180) + [(49, 26)]
    draw_snorkel(de, path, 6, key, (49, 26), band_ys=(40, 54))
    mouthpiece(de, (86, 81, 96, 89))
    # North: the back of the head; the tube on the wearer's left, now the viewer's left, standing above the head.
    n, dn = new()
    draw_snorkel(dn, [(43, 80), (43, 26)], 6, key, (43, 26), band_ys=(40, 54))
    return finish(s, 3), finish(e, 3), finish(n, 3)


# ---- Previews (sheet only, never shipped) ----------------------------------------------------------------------------------

def head(direction):
    """A plain stand-in head on vanilla's frame, drawn here: not vanilla art."""
    img, d = new()
    if direction == "east":
        box = (44, 39, 92, 89)
    else:
        box = (41, 39, 87, 89)
    d.rounded_rectangle([v * SS for v in box], radius=20 * SS, fill=SKIN)
    if direction == "north":
        d.rounded_rectangle([box[0] * SS, box[1] * SS, box[2] * SS, (box[3] - 6) * SS], radius=20 * SS, fill=HAIR)
    else:
        d.rounded_rectangle([box[0] * SS, box[1] * SS, box[2] * SS, 52 * SS], radius=16 * SS, fill=HAIR)
    return finish(img, 3)


def preview(worn_img, direction):
    tile = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    tile.alpha_composite(head(direction))
    mask = MASK_DIR / f"GlassMask_{direction}.png"
    if mask.exists():
        tile.alpha_composite(Image.open(mask).convert("RGBA"))
    tile.alpha_composite(worn_img)
    return tile.resize((S * 2, S * 2), Image.NEAREST)


def export(master, fill=100):
    """As the glass mask and fins: fit the master's alpha bounds into `fill` px of the 128 canvas, centred, one uniform Lanczos
    reduction from the 8x master."""
    crop = master.crop(master.getchannel("A").getbbox())
    scale = fill / max(crop.size)
    small = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    canvas.alpha_composite(small, ((S - small.width) // 2, (S - small.height) // 2))
    return canvas


if __name__ == "__main__":
    for key, (name, *_rest) in STYLES.items():
        export(item(key, master=True)).resize((S * 2, S * 2), Image.NEAREST).save(OUT / f"Preview_{key}_item.png")
        export(item(key, master=True)).save(OUT / f"Snorkel_{key}_{name}.png")
        for direction, im in zip(("south", "east", "north"), worn(key)):
            im.save(OUT / f"Snorkel_{key}_{name}_{direction}.png")
            preview(im, direction).save(OUT / f"Preview_{key}_{direction}.png")
    # Approved: A plain wood, east tube moved back (APPROVAL.md). The item goes through the 100 px export; the worn views are
    # already at their game size. West mirrors east in game.
    export(item("A", master=True)).save(OUT / "Snorkel.png")
    for direction, im in zip(("south", "east", "north"), worn("A")):
        im.save(OUT / f"Snorkel_{direction}.png")
