"""Basic wetsuit candidates for Spearfishing. Procedural PIL drawing in the house rendering (art/wooden-fins, art/glass-mask):
a few flat two-tone shapes, a black outward outline and black lines between materials, no fine detail.

The suit is stuffed (Leathery), so every texture is greyscale and RimWorld tints it by the leather's colour.
Each candidate has an item sprite (128x128, Graphic_Single, drawSize 1, 4 px outline at 128) and worn views for the OnSkin
layer: 128x128 body textures named <path>_<BodyType>_<dir>.png. A worn view fills the vanilla naked body's silhouette for
that body type (its alpha only, used so the suit fits the body exactly; no vanilla colour pixels are used), with a 3 px
inward outline and the candidate's own features.
Usage: python -I wetsuit_art.py <vanilla_bodies_dir> <out_dir> [body types...]. Writes Wetsuit_<X>_<name>.png and
Wetsuit_<X>_<name>_<BodyType>_<dir>.png, and the approved game textures Wetsuit.png and Wetsuit_<BodyType>_<dir>.png;
Male only unless body types are given."""
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

BODIES = Path(sys.argv[1])
OUT = Path(sys.argv[2])
TYPES = sys.argv[3:] or ["Male"]
OUT.mkdir(parents=True, exist_ok=True)
SS = 8
S = 128
W = S * SS
INK = (12, 10, 10, 255)
LIGHT, SHADE, DARK, DARK_SHADE = (232, 232, 232, 255), (184, 184, 184, 255), (120, 120, 120, 255), (96, 96, 96, 255)
LINE = int(1.5 * SS)  # material line, 1.5 px at 128
SHIFT = 5 * SS  # the shade band on the lower right of each shape, light from the upper left


def p(*xy):
    return [v * SS for v in xy]


def solid(alpha, colour):
    layer = Image.new("RGBA", alpha.size, (0, 0, 0, 0))
    layer.paste(Image.new("RGBA", alpha.size, colour), (0, 0), alpha)
    return layer


def two_tone(alpha, light, shade):
    """Shade fill with the light tone where the shape, moved down-right, still covers it: a shade band on the lower right."""
    moved = ImageChops.offset(alpha, SHIFT, SHIFT)
    lit = ImageChops.multiply(alpha, moved)
    out = solid(alpha, shade)
    out.alpha_composite(solid(lit, light))
    return out


def outward(layer, px):
    alpha = layer.getchannel("A").point(lambda v: 255 if v > 127 else 0)
    ring = alpha.filter(ImageFilter.MaxFilter(px * 2 + 1))
    base = solid(ring, INK)
    base.alpha_composite(layer)
    return base


def shrink(img):
    return img.resize((S, S), Image.LANCZOS)


def band(alpha, box):
    """The part of a shape inside a box, as an alpha mask."""
    m = Image.new("L", alpha.size, 0)
    ImageDraw.Draw(m).rectangle(box, fill=255)
    return ImageChops.multiply(alpha, m)


def lined(img, alpha, region, light, shade):
    """Paint a region of the shape in another tone, with a black material line around it."""
    region = ImageChops.multiply(alpha, region)
    grown = region.filter(ImageFilter.MaxFilter(LINE * 2 + 1))
    img.alpha_composite(solid(ImageChops.multiply(alpha, grown), INK))
    img.alpha_composite(two_tone(region, light, shade))


def seam(img, alpha, x0, y0, x1, y1):
    d = Image.new("L", alpha.size, 0)
    ImageDraw.Draw(d).line([x0, y0, x1, y1], fill=255, width=int(2.5 * SS))
    img.alpha_composite(solid(ImageChops.multiply(alpha, d), INK))


# ---- Item sprite: the suit laid flat -------------------------------------------------------------------------------------

def item_shape():
    m = Image.new("L", (W, W), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle(p(38, 16, 90, 70), radius=10 * SS, fill=255)  # body
    d.polygon(p(42, 18, 30, 22, 12, 60, 24, 66, 40, 40), fill=255)  # left arm
    d.polygon(p(86, 18, 98, 22, 116, 60, 104, 66, 88, 40), fill=255)  # right arm
    d.polygon(p(38, 60, 64, 60, 62, 116, 42, 116), fill=255)  # left leg
    d.polygon(p(90, 60, 64, 60, 66, 116, 86, 116), fill=255)  # right leg
    d.ellipse(p(54, 10, 74, 24), fill=0)  # neck opening
    return m


def item(kind, master=False):
    a = item_shape()
    img = two_tone(a, LIGHT, SHADE)
    if kind == "A":
        seam(img, a, 64 * SS, 22 * SS, 64 * SS, 66 * SS)
    elif kind == "B":
        lined(img, a, band(a, p(0, 54, 128, 66)), DARK, DARK_SHADE)
    else:
        side = Image.new("L", (W, W), 0)
        d = ImageDraw.Draw(side)
        d.rectangle(p(0, 0, 50, 128), fill=255)
        d.rectangle(p(78, 0, 128, 128), fill=255)
        d.rectangle(p(0, 70, 128, 128), fill=0)
        lined(img, a, side, DARK, DARK_SHADE)
    # The collar: a dark band round the neck opening.
    collar = Image.new("L", (W, W), 0)
    ImageDraw.Draw(collar).ellipse(p(50, 6, 78, 28), fill=255)
    lined(img, a, collar, DARK, DARK_SHADE)
    img = outward(img, 4 * SS)
    return img if master else shrink(img)


# ---- Worn views on the body silhouette -----------------------------------------------------------------------------------

def body_alpha(body, direction):
    a = Image.open(BODIES / f"Naked_{body}_{direction}.png").convert("RGBA").getchannel("A")
    return a.resize((W, W), Image.BILINEAR).point(lambda v: 255 if v > 127 else 0)


def worn(kind, body, direction):
    a = body_alpha(body, direction)
    x0, y0, x1, y1 = a.getbbox()
    w, h = x1 - x0, y1 - y0
    fx = lambda f: x0 + w * f
    fy = lambda f: y0 + h * f
    inner = a.filter(ImageFilter.MinFilter(3 * SS * 2 + 1))
    img = two_tone(inner, LIGHT, SHADE)
    if kind == "A":
        # One seam down the front (south) or the back (north). The side view has none: the author asked for that on approval.
        if direction != "east":
            seam(img, inner, fx(0.5), fy(0.25), fx(0.5), y1)
    elif kind == "B":
        lined(img, inner, band(inner, [0, fy(0.62), W, fy(0.76)]), DARK, DARK_SHADE)
    else:
        side = Image.new("L", (W, W), 0)
        d = ImageDraw.Draw(side)
        if direction == "east":
            d.rectangle([0, 0, fx(0.32), W], fill=255)  # the back panel
        else:
            d.rectangle([0, 0, fx(0.3), W], fill=255)
            d.rectangle([fx(0.7), 0, W, W], fill=255)
        lined(img, inner, side, DARK, DARK_SHADE)
    out = solid(a, INK)
    out.alpha_composite(img)
    return shrink(out)


def export(master, fill=100):
    """The fins' and glass mask's item recipe: fit the master's alpha bounds into `fill` px of the 128 canvas, centred, one
    uniform Lanczos reduction from the 8x master."""
    crop = master.crop(master.getchannel("A").getbbox())
    scale = fill / max(crop.size)
    small = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    canvas.alpha_composite(small, ((S - small.width) // 2, (S - small.height) // 2))
    return canvas


NAMES = {"A": "seamed", "B": "belted", "C": "panelled"}
for key, name in NAMES.items():
    item(key).save(OUT / f"Wetsuit_{key}_{name}.png")
    for body in TYPES:
        for direction in ("south", "east", "north"):
            worn(key, body, direction).save(OUT / f"Wetsuit_{key}_{name}_{body}_{direction}.png")

# Approved: A seamed, without a seam on the side view (APPROVAL.md). Game textures: Wetsuit.png (item, 100 px export) and
# Wetsuit_<BodyType>_<dir>.png (worn views, unchanged) for every body type given.
export(item("A", master=True)).save(OUT / "Wetsuit.png")
for body in TYPES:
    for direction in ("south", "east", "north"):
        worn("A", body, direction).save(OUT / f"Wetsuit_{body}_{direction}.png")