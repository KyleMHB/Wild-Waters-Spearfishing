"""Dry snorkel candidates for Spearfishing (gear tiers, ticket 04). Procedural PIL drawing in the house rendering of the
approved wooden snorkel (art/snorkel): a few flat two-tone shapes, a black outward outline and black lines between materials.

The dry snorkel keeps the wooden snorkel's J shape and worn placement, so it sits on the head exactly where the approved one
does (the east view's tube at the back edge of the head, "A, tube moved back"). What makes it industrial is three parts:
  - a moulded plastic tube in a fixed colour (the candidates differ here);
  - a dry valve on top: a wider block than the tube, the part that reads at game size;
  - black silicone below: a flexible section where the arm meets the mouthpiece, and the mouthpiece.

Each candidate has an item sprite (128x128, Graphic_Single, drawSize 1, 4 px outline at the 8x master's scale, exported as the
wooden snorkel's: alpha bounds fitted to 100 px) and worn views for the EyeCover layer (128x128 head textures, _south, _east
and _north, 3 px outline). West mirrors east in game.

Usage: python -I dry_snorkel_art.py <out_dir> [<sheet_path>]
Writes DrySnorkel_<X>_<name>.png and DrySnorkel_<X>_<name>_<dir>.png per candidate, the approved C as the game textures
DrySnorkel.png and DrySnorkel_<dir>.png and, with <sheet_path>, the contact sheet:
the approved wooden snorkel and each candidate as the item at 1.5x and at game size, worn south, east and north with the
approved glass mask on a plain stand-in head (drawn here, not vanilla art), and floating face down (the north view sunk in
the water with the approved shoulders and waterline shapes, at the in-game sizes, offsets and tints of DiveVisuals.cs).
The sheet reads the approved textures from Textures/; nothing it composites is written back."""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
SHEET = Path(sys.argv[2]) if len(sys.argv) > 2 else None
HERE = Path(__file__).resolve().parent
TEX = HERE.parent.parent / "Textures"
APPAREL = TEX / "Things" / "Spearfishing" / "Apparel"
SS = 8
S = 128
W = S * SS
INK = (12, 10, 10, 255)
SILICONE_LIGHT, SILICONE_DARK = (78, 80, 86, 255), (44, 45, 49, 255)
SKIN, HAIR = (226, 184, 148, 255), (96, 66, 44, 255)
LINE = int(1.5 * SS)

# key: (name, tube light, tube dark, valve light, valve dark)
STYLES = {
    "A": ("yellow", (228, 192, 74, 255), (186, 148, 44, 255), SILICONE_LIGHT, SILICONE_DARK),
    "B": ("blue", (92, 152, 206, 255), (56, 106, 162, 255), SILICONE_LIGHT, SILICONE_DARK),
    "C": ("black-orange", (88, 92, 98, 255), (54, 56, 61, 255), (232, 128, 52, 255), (184, 90, 34, 255)),
}


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


def tube(d, pts, width, light, dark):
    """As the wooden snorkel's tube: black line, dark body, a light stripe along one side."""
    stroke(d, pts, width + 3, INK)
    stroke(d, pts, width, dark)
    off = -width * 0.18
    stroke(d, [(x + off, y + off) for x, y in pts], width * 0.45, light)


def flex(d, x0, x1, y, width, ribs):
    """The black silicone flexible section on the horizontal arm, from x0 to x1, with a black line at each end where it
    meets the plastic and, on the item only, a few ribs across it."""
    h = width / 2
    d.rectangle([(x0 - 0.8) * SS, (y - h - 1.5) * SS, (x1 + 0.8) * SS, (y + h + 1.5) * SS], fill=INK)
    d.rectangle([x0 * SS + LINE / 2, (y - h) * SS, x1 * SS - LINE / 2, (y + h) * SS], fill=SILICONE_DARK)
    d.rectangle([x0 * SS + LINE / 2, (y - h) * SS, x1 * SS - LINE / 2, (y - h * 0.15) * SS], fill=SILICONE_LIGHT)
    for i in range(1, ribs + 1):
        x = x0 + (x1 - x0) * i / (ribs + 1)
        d.rectangle([(x - 0.6) * SS, (y - h) * SS, (x + 0.6) * SS, (y + h) * SS], fill=INK)


def valve(d, x, y_bottom, width, height, light, dark, vents):
    """The dry valve on top of the tube: a rounded block wider than the tube, light on its left half like the tube's stripe,
    with dark vent slots across it on the item."""
    x0, x1, y0 = x - width / 2, x + width / 2, y_bottom - height
    d.rounded_rectangle([(x0 - 1.5) * SS, (y0 - 1.5) * SS, (x1 + 1.5) * SS, (y_bottom + 1.5) * SS], radius=3.5 * SS, fill=INK)
    d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y_bottom * SS], radius=2.5 * SS, fill=dark)
    d.rounded_rectangle([x0 * SS, y0 * SS, x * SS, y_bottom * SS], radius=2.5 * SS, fill=light)
    for i in range(1, vents + 1):
        y = y0 + height * i / (vents + 1)
        d.rectangle([(x0 + 2) * SS, (y - 0.8) * SS, (x1 - 2) * SS, (y + 0.8) * SS], fill=INK)


def mouthpiece(d, box):
    x0, y0, x1, y1 = box
    r = (y1 - y0) * SS / 2
    d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r, fill=INK)
    d.rounded_rectangle([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, y1 * SS - LINE], radius=r - LINE, fill=SILICONE_DARK)
    d.rounded_rectangle([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, (y0 + y1) / 2 * SS], radius=r / 2, fill=SILICONE_LIGHT)


def j_path(x_mouth, y_mouth, x_side, y_top, r):
    """From the mouthpiece across to the side, round the bend, then straight up (the wooden snorkel's path)."""
    return [(x_mouth, y_mouth), (x_side - r, y_mouth)] + arc(x_side - r, y_mouth - r, r, 90, 0) + [(x_side, y_top)]


# ---- Item sprite ---------------------------------------------------------------------------------------------------------

def item(key, master=False):
    _, light, dark, vlight, vdark = STYLES[key]
    img, d = new()
    tube(d, j_path(34, 100, 92, 24, 16), 13, light, dark)
    flex(d, 40, 62, 100, 13, ribs=3)
    valve(d, 92, 28, 21, 18, vlight, vdark, vents=2)
    mouthpiece(d, (14, 90, 42, 110))
    return with_outline(img, 4 * SS) if master else finish(img, 4)


# ---- Worn views (same placement as the approved wooden snorkel) ------------------------------------------------------------

def worn(key):
    _, light, dark, vlight, vdark = STYLES[key]
    # South: mouthpiece under the mask, tube to the wearer's left (viewer's right) and up past the head, valve on top.
    s, d = new()
    tube(d, j_path(66, 86, 92, 30, 7), 6, light, dark)
    flex(d, 71, 82, 86, 6, ribs=0)
    valve(d, 92, 31, 10, 10, vlight, vdark, vents=0)
    mouthpiece(d, (56, 82, 72, 90))
    # East: the tube at the back edge of the head, the arm along the jaw to the mouth (as the approved "tube moved back").
    e, de = new()
    tube(de, [(92, 85), (56, 85)] + arc(56, 78, 7, 90, 180) + [(49, 30)], 6, light, dark)
    flex(de, 72, 86, 85, 6, ribs=0)
    valve(de, 49, 31, 10, 10, vlight, vdark, vents=0)
    mouthpiece(de, (86, 81, 96, 89))
    # North: the back of the head; the tube on the wearer's left, now the viewer's left, its valve standing above the head.
    n, dn = new()
    tube(dn, [(43, 80), (43, 30)], 6, light, dark)
    valve(dn, 43, 31, 10, 10, vlight, vdark, vents=0)
    return finish(s, 3), finish(e, 3), finish(n, 3)


def export(master, fill=100):
    """As the wooden snorkel, glass mask and fins: fit the master's alpha bounds into `fill` px of the 128 canvas, centred,
    one uniform Lanczos reduction from the 8x master."""
    crop = master.crop(master.getchannel("A").getbbox())
    scale = fill / max(crop.size)
    small = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    canvas.alpha_composite(small, ((S - small.width) // 2, (S - small.height) // 2))
    return canvas


# ---- Contact sheet (never shipped) -----------------------------------------------------------------------------------------

def head(direction):
    """The plain stand-in head the wooden snorkel's sheet used, on vanilla's frame: not vanilla art."""
    img, d = new()
    box = (44, 39, 92, 89) if direction == "east" else (41, 39, 87, 89)
    d.rounded_rectangle([v * SS for v in box], radius=20 * SS, fill=SKIN)
    if direction == "north":
        d.rounded_rectangle([box[0] * SS, box[1] * SS, box[2] * SS, (box[3] - 6) * SS], radius=20 * SS, fill=HAIR)
    else:
        d.rounded_rectangle([box[0] * SS, box[1] * SS, box[2] * SS, 52 * SS], radius=16 * SS, fill=HAIR)
    return finish(img, 3)


def load(path):
    return Image.open(path).convert("RGBA")


def worn_head(snorkel_view, direction):
    tile = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    tile.alpha_composite(head(direction))
    tile.alpha_composite(load(APPAREL / "GlassMask" / f"GlassMask_{direction}.png"))
    tile.alpha_composite(snorkel_view)
    return tile


# DiveVisuals.cs, look C (art/face-down/APPROVAL.md): sizes and offsets in cells south of the head's centre.
SHADOW, RING = (8, 20, 26), (214, 240, 255)
SHOULDERS = (0.95, 0.38, 0.5)
WATERLINE = (1.0, 0.10, 0.45)
SEA = (62, 98, 86)
HEAD_PX_PER_CELL = S / 1.5  # head textures draw on a 1.5-cell mesh


def tinted(img, rgb, alpha, size):
    img = img.resize((size, size), Image.LANCZOS)
    t = Image.new("RGBA", img.size, rgb + (0,))
    t.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    return t


def face_down(snorkel_north, px_per_cell=96, cells=1.7):
    """The face-down floater at px_per_cell: water, the sunk shoulders, the waterline ring, then the north view of the head
    with the glass mask and the snorkel (the game draws them in that order)."""
    size = int(px_per_cell * cells)
    tile = Image.new("RGBA", (size, size), SEA + (255,))
    cx, cy = size // 2, int(size * 0.42)
    for tex, rgb, (cell_size, offset, alpha) in ((TEX / "Spearfishing" / "Dive" / "Shoulders.png", SHADOW, SHOULDERS),
                                                 (TEX / "Spearfishing" / "Dive" / "Waterline.png", RING, WATERLINE)):
        shape = tinted(load(tex), rgb, alpha, int(cell_size * px_per_cell))
        tile.alpha_composite(shape, (cx - shape.width // 2, cy + int(offset * px_per_cell) - shape.height // 2))
    k = int(S * px_per_cell / HEAD_PX_PER_CELL)
    head_img = worn_head(snorkel_north, "north").resize((k, k), Image.LANCZOS)
    tile.alpha_composite(head_img, (cx - k // 2, cy - k // 2))
    return tile


def on_backdrop(img, size, colour=(70, 74, 66)):
    tile = Image.new("RGBA", (size, size), colour + (255,))
    tile.alpha_composite(img, ((size - img.width) // 2, (size - img.height) // 2))
    return tile


def font(px):
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(rows, path):
    """rows: [(label, item_128, (south, east, north))]. One row per snorkel, one column per view."""
    tile, gap, left, top = 196, 14, 230, 150
    cols = ["Item 1.5x", "Item game size", "Worn south", "Worn east", "Worn north", "Face down"]
    width = left + len(cols) * (tile + gap) + 20
    height = top + len(rows) * (tile + gap) + 70
    out = Image.new("RGBA", (width, height), (30, 31, 36, 255))
    d = ImageDraw.Draw(out)
    d.rectangle([28, 32, 33, 92], fill=(232, 150, 60))
    d.text((48, 28), "Dry snorkel candidates (gear tiers, ticket 04)", font=font(30), fill=(240, 240, 240))
    d.text((48, 68), "Beside the approved wooden snorkel. Worn with the approved glass mask on a plain stand-in head.",
           font=font(17), fill=(170, 172, 180))
    for i, c in enumerate(cols):
        x = left + i * (tile + gap) + tile // 2
        d.text((x, top - 22), c, font=font(17), fill=(200, 200, 205), anchor="mm")
    for r, (label, item_img, views) in enumerate(rows):
        y = top + r * (tile + gap)
        d.text((40, y + tile // 2), label, font=font(20), fill=(235, 235, 235), anchor="lm")
        tiles = [
            on_backdrop(item_img.resize((192, 192), Image.LANCZOS), tile),
            on_backdrop(item_img.resize((64, 64), Image.LANCZOS), tile),
            *[on_backdrop(worn_head(v, dname).resize((192, 192), Image.LANCZOS), tile) for v, dname in zip(views, ("south", "east", "north"))],
            on_backdrop(face_down(views[2]).resize((tile, tile), Image.LANCZOS), tile),
        ]
        for i, t in enumerate(tiles):
            out.alpha_composite(t, (left + i * (tile + gap), y))
    d.text((40, height - 44), "Game size: 1 cell at 64 px. Worn views at 1.5x. Face down: Shoulders and Waterline at their "
           "in-game size, offset and tint, at 96 px per cell.", font=font(15), fill=(150, 152, 160))
    out.convert("RGB").save(path)


if __name__ == "__main__":
    rows = [("Wooden (approved)", load(APPAREL / "Snorkel" / "Snorkel.png"),
             tuple(load(APPAREL / "Snorkel" / f"Snorkel_{d}.png") for d in ("south", "east", "north")))]
    for key, (name, *_rest) in STYLES.items():
        item_img = export(item(key, master=True))
        item_img.save(OUT / f"DrySnorkel_{key}_{name}.png")
        views = worn(key)
        for direction, im in zip(("south", "east", "north"), views):
            im.save(OUT / f"DrySnorkel_{key}_{name}_{direction}.png")
        rows.append((f"Dry {key}: {name}", item_img, views))
    # The approved candidate (C, 2026-11-17; APPROVAL.md) as the game textures, by the wooden snorkel's recipe: the item from
    # the 8x master fitted to 100 px, the worn views as drawn. West mirrors east in game.
    export(item("C", master=True)).save(OUT / "DrySnorkel.png")
    for direction, im in zip(("south", "east", "north"), worn("C")):
        im.save(OUT / f"DrySnorkel_{direction}.png")
    if SHEET:
        SHEET.parent.mkdir(parents=True, exist_ok=True)
        sheet(rows, SHEET)
        print(SHEET)
