"""Glass mask candidates for Spearfishing. Procedural PIL drawing in the house rendering (art/pole-spear, art/wooden-fins):
a few flat two-tone shapes, a black outward outline and black lines between materials, no fine detail.

Each candidate has an item sprite (128x128, Graphic_Single, drawSize 1, about 100 px across like the fins, 4 px outline =
2 px at 64 px per cell) and worn views for the EyeCover layer (128x128 head textures, _south, _east and _north, 3 px outline),
placed on the eyes of vanilla's 128 px head frame (eyes near y 70; head about x 41-87, y 39-89).
Usage: python -I glass_mask_art.py <out_dir>. Writes GlassMask_<X>_<name>.png and GlassMask_<X>_<name>_<dir>.png, and the
approved C visor's game textures (APPROVAL.md): GlassMask.png (item, export at 100 px) and GlassMask_<dir>.png (worn views,
unchanged)."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
SS = 8
S = 128
W = S * SS
INK = (12, 10, 10, 255)
STEEL_LIGHT, STEEL_DARK = (196, 200, 204, 255), (138, 144, 150, 255)
GLASS, GLASS_SHADE, GLASS_SHINE = (150, 206, 214, 255), (112, 170, 184, 255), (226, 244, 246, 255)
STRAP, STRAP_DARK = (120, 84, 58, 255), (92, 62, 42, 255)
LINE = int(1.5 * SS)  # material line, 1.5 px at 128


def with_outline(layer, px):
    alpha = layer.getchannel("A").point(lambda v: 255 if v > 127 else 0)
    ring = alpha.filter(ImageFilter.MaxFilter(px * 2 + 1))
    base = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    base.paste(Image.new("RGBA", layer.size, INK), (0, 0), ring)
    base.alpha_composite(layer)
    return base


def finish(img, outline):
    return with_outline(img, outline * SS).resize((S, S), Image.LANCZOS)


def p(*xy):
    return [v * SS for v in xy]


def lens(d, box, rim, shape="ellipse"):
    """A steel rim around glass: black line, two-tone steel, black line, glass with a shade and one broad shine."""
    x0, y0, x1, y1 = box
    draw = d.ellipse if shape == "ellipse" else (lambda b, fill: d.rounded_rectangle(b, radius=min(b[2] - b[0], b[3] - b[1]) * 0.45, fill=fill))
    draw(p(x0, y0, x1, y1), fill=INK)
    draw([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, y1 * SS - LINE], fill=STEEL_DARK)
    d.chord([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, y1 * SS - LINE], 150, 330, fill=STEEL_LIGHT) if shape == "ellipse" else \
        draw([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, (y0 + y1) / 2 * SS], fill=STEEL_LIGHT)
    gx0, gy0, gx1, gy1 = x0 + rim, y0 + rim, x1 - rim, y1 - rim
    draw(p(gx0, gy0, gx1, gy1), fill=INK)
    g = [gx0 * SS + LINE, gy0 * SS + LINE, gx1 * SS - LINE, gy1 * SS - LINE]
    draw(g, fill=GLASS_SHADE)
    draw([g[0], g[1], g[2] - (g[2] - g[0]) * 0.12, g[3] - (g[3] - g[1]) * 0.18], fill=GLASS)
    # One broad shine toward the upper left.
    w, h = g[2] - g[0], g[3] - g[1]
    d.ellipse([g[0] + w * 0.16, g[1] + h * 0.14, g[0] + w * 0.42, g[1] + h * 0.36], fill=GLASS_SHINE)


def strap(d, box):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=(y1 - y0) * SS / 2, fill=INK)
    d.rounded_rectangle([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, y1 * SS - LINE], radius=(y1 - y0) * SS / 2 - LINE, fill=STRAP_DARK)
    d.rounded_rectangle([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, (y0 + y1) / 2 * SS], radius=(y1 - y0) * SS / 4, fill=STRAP)


def strap_loop(d, cx, cy, rx, ry, width):
    """The strap behind the item: a thick ellipse ring seen from the front."""
    d.ellipse(p(cx - rx, cy - ry, cx + rx, cy + ry), fill=INK)
    d.ellipse([(cx - rx) * SS + LINE, (cy - ry) * SS + LINE, (cx + rx) * SS - LINE, (cy + ry) * SS - LINE], fill=STRAP)
    d.ellipse(p(cx - rx + width, cy - ry + width, cx + rx - width, cy + ry - width), fill=INK)
    d.ellipse([(cx - rx + width) * SS + LINE, (cy - ry + width) * SS + LINE, (cx + rx - width) * SS - LINE, (cy + ry - width) * SS - LINE],
              fill=(0, 0, 0, 0))


def new():
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


# ---- Item sprites -------------------------------------------------------------------------------------------------------

def item_a():
    """Porthole: one big round lens in a thick steel ring, strap looped behind."""
    img, d = new()
    strap_loop(d, 64, 72, 50, 30, 8)
    lens(d, (26, 24, 102, 100), 11)
    return finish(img, 4)


def item_b():
    """Twin goggles: two round lenses joined by a steel bridge, strap looped behind."""
    img, d = new()
    strap_loop(d, 64, 70, 54, 28, 8)
    d.rectangle(p(56, 58, 72, 70), fill=INK)
    d.rectangle([56 * SS, 58 * SS + LINE, 72 * SS, 70 * SS - LINE], fill=STEEL_DARK)
    lens(d, (14, 38, 64, 88), 8)
    lens(d, (64, 38, 114, 88), 8)
    return finish(img, 4)


def item_c(master=False):
    """Visor: one wide rounded window in a steel frame, strap looped behind."""
    img, d = new()
    strap_loop(d, 64, 70, 54, 30, 8)
    lens(d, (14, 36, 114, 94), 9, shape="rounded")
    return with_outline(img, 4 * SS) if master else finish(img, 4)


def export(master, fill=100):
    """Approved recipe, as the fins: fit the master's alpha bounds into `fill` px of the 128 canvas, centred, one uniform
    Lanczos reduction from the 8x master."""
    crop = master.crop(master.getchannel("A").getbbox())
    scale = fill / max(crop.size)
    small = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    canvas.alpha_composite(small, ((S - small.width) // 2, (S - small.height) // 2))
    return canvas


# ---- Worn views (vanilla head frame) ------------------------------------------------------------------------------------

def worn_strap_sides(d, y):
    strap(d, (38, y - 3, 46, y + 3))
    strap(d, (82, y - 3, 90, y + 3))


def worn_north(y=68):
    img, d = new()
    strap(d, (39, y - 3, 89, y + 3))
    return finish(img, 3)


def worn_east_strap(d, y=68, front=84):
    strap(d, (42, y - 3, front, y + 3))


def worn_a():
    s, d = new()
    worn_strap_sides(d, 68)
    lens(d, (48, 55, 80, 87), 5)
    e, de = new()
    worn_east_strap(de, 68, 82)
    de.rounded_rectangle(p(80, 52, 94, 86), radius=6 * SS, fill=INK)
    de.rounded_rectangle([80 * SS + LINE, 52 * SS + LINE, 94 * SS - LINE, 86 * SS - LINE], radius=5 * SS, fill=STEEL_DARK)
    de.rounded_rectangle([88 * SS, 56 * SS, 94 * SS - LINE, 82 * SS], radius=3 * SS, fill=GLASS)
    return finish(s, 3), finish(e, 3), worn_north()


def worn_b():
    s, d = new()
    worn_strap_sides(d, 70)
    d.rectangle(p(61, 66, 67, 72), fill=STEEL_DARK)
    lens(d, (44, 60, 63, 80), 4)
    lens(d, (65, 60, 84, 80), 4)
    e, de = new()
    worn_east_strap(de, 70, 80)
    lens(de, (78, 61, 92, 79), 3)
    return finish(s, 3), finish(e, 3), worn_north(70)


def worn_c():
    s, d = new()
    worn_strap_sides(d, 70)
    lens(d, (42, 58, 86, 82), 4, shape="rounded")
    e, de = new()
    worn_east_strap(de, 70, 82)
    de.rounded_rectangle(p(80, 57, 94, 83), radius=6 * SS, fill=INK)
    de.rounded_rectangle([80 * SS + LINE, 57 * SS + LINE, 94 * SS - LINE, 83 * SS - LINE], radius=5 * SS, fill=STEEL_DARK)
    de.rounded_rectangle([88 * SS, 60 * SS, 94 * SS - LINE, 80 * SS], radius=3 * SS, fill=GLASS)
    return finish(s, 3), finish(e, 3), worn_north(70)


for key, name, item, worn in (("A", "porthole", item_a, worn_a), ("B", "goggles", item_b, worn_b), ("C", "visor", item_c, worn_c)):
    item().save(OUT / f"GlassMask_{key}_{name}.png")
    for direction, im in zip(("south", "east", "north"), worn()):
        im.save(OUT / f"GlassMask_{key}_{name}_{direction}.png")

# Approved: C visor. The item goes through the fins' 100 px export; the worn views are already at their game size.
export(item_c(master=True)).save(OUT / "GlassMask.png")
for direction, im in zip(("south", "east", "north"), worn_c()):
    im.save(OUT / f"GlassMask_{direction}.png")
