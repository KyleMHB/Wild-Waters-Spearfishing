"""Neoprene wetsuit candidates for Spearfishing (gear-tiers ticket 05). Procedural PIL drawing in the house rendering of the
approved basic wetsuit (art/wetsuit): the same laid-flat item silhouette and worn construction, flat two-tone shapes lit from
the upper left, a black outward outline and black lines between materials, no fine detail.

Unlike the basic suit this one is a fixed material (neoprene, made from chemfuel, cloth and a component), so the colour is
baked in: a charcoal suit, never black, so the outline and material lines still read, with a muted blue accent below 0.7
saturation. The tiers are told apart by colour and panels, not by a new rendering.

Each candidate has an item sprite (128x128, Graphic_Single, drawSize 1, 4 px outline at 128) and worn views for the OnSkin
layer: 128x128 body textures named <path>_<BodyType>_<dir>.png. A worn view fills the vanilla naked body's silhouette for
that body type (its alpha only, so the suit fits the body; no vanilla colour pixels are used), with a 3 px inward outline.
Following the author's rule for the basic suit, the east (side) view has no centre seam, and nothing on it is one-sided,
because west is east mirrored.

Usage: python -I neoprene_wetsuit_art.py <vanilla_bodies_dir> <out_dir> [body types...]. Writes NeopreneWetsuit_<X>_<name>.png
and NeopreneWetsuit_<X>_<name>_<BodyType>_<dir>.png; Male only unless body types are given."""
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
# Charcoal neoprene, well above the outline's black so the lines stay visible, and a muted blue accent (saturation about 0.65).
SUIT, SUIT_SHADE = (86, 90, 97, 255), (64, 67, 73, 255)
ACCENT, ACCENT_SHADE = (60, 116, 156, 255), (45, 90, 124, 255)
PAD, PAD_SHADE = (128, 132, 138, 255), (102, 105, 111, 255)
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


def mask(size, draw):
    m = Image.new("L", size, 0)
    draw(ImageDraw.Draw(m))
    return m


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


def zip_pull(img, alpha, x, y):
    """The back zip's pull: a small accent tab with a black line round it, at the top of the zip."""
    tab = mask(alpha.size, lambda d: d.rectangle([x - 3 * SS, y, x + 3 * SS, y + 7 * SS], fill=255))
    lined(img, alpha, tab, ACCENT, ACCENT_SHADE)


# ---- Item sprite: the suit laid flat, the basic suit's silhouette ---------------------------------------------------------

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
    img = two_tone(a, SUIT, SUIT_SHADE)
    if kind == "A":
        # Side panels: an accent panel down each flank of the body, running on down the outside of each leg.
        side = mask(a.size, lambda d: (d.polygon(p(30, 30, 47, 30, 47, 70, 49, 116, 30, 116), fill=255),
                                       d.polygon(p(98, 30, 81, 30, 81, 70, 79, 116, 98, 116), fill=255)))
        lined(img, a, side, ACCENT, ACCENT_SHADE)
    elif kind == "B":
        # Chest yoke: the shoulders, upper chest and upper arms in the accent, a straight line across the chest.
        yoke = mask(a.size, lambda d: d.rectangle(p(0, 0, 128, 34), fill=255))
        lined(img, a, yoke, ACCENT, ACCENT_SHADE)
    else:
        # Pads: lighter knee pads and an accent chest band.
        knees = mask(a.size, lambda d: (d.rounded_rectangle(p(42, 84, 60, 98), radius=4 * SS, fill=255),
                                        d.rounded_rectangle(p(68, 84, 86, 98), radius=4 * SS, fill=255)))
        lined(img, a, knees, PAD, PAD_SHADE)
        band = mask(a.size, lambda d: d.rectangle(p(0, 34, 128, 42), fill=255))
        lined(img, a, band, ACCENT, ACCENT_SHADE)
    # The collar: an accent band round the neck opening, as the basic suit's dark collar.
    collar = mask(a.size, lambda d: d.ellipse(p(50, 6, 78, 28), fill=255))
    lined(img, a, collar, ACCENT, ACCENT_SHADE)
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
    img = two_tone(inner, SUIT, SUIT_SHADE)
    east = direction == "east"
    if kind == "A":
        if east:
            # The flank panel seen from the side: a band down the middle, symmetric so it mirrors for west.
            side = mask(a.size, lambda d: d.rectangle([fx(0.36), fy(0.18), fx(0.64), W], fill=255))
        else:
            side = mask(a.size, lambda d: (d.rectangle([0, fy(0.2), fx(0.22), W], fill=255),
                                           d.rectangle([fx(0.78), fy(0.2), W, W], fill=255)))
        lined(img, inner, side, ACCENT, ACCENT_SHADE)
    elif kind == "B":
        yoke = mask(a.size, lambda d: d.rectangle([0, 0, W, fy(0.3)], fill=255))
        lined(img, inner, yoke, ACCENT, ACCENT_SHADE)
    else:
        band = mask(a.size, lambda d: d.rectangle([0, fy(0.3), W, fy(0.38)], fill=255))
        lined(img, inner, band, ACCENT, ACCENT_SHADE)
        if east:
            knee = mask(a.size, lambda d: d.rectangle([fx(0.5), fy(0.8), W, fy(0.92)], fill=255))
        elif direction == "south":
            knee = mask(a.size, lambda d: (d.rectangle([0, fy(0.8), fx(0.44), fy(0.92)], fill=255),
                                           d.rectangle([fx(0.56), fy(0.8), W, fy(0.92)], fill=255)))
        else:
            knee = None  # knee pads are on the front only
        if knee is not None:
            lined(img, inner, knee, PAD, PAD_SHADE)
    if direction == "north":
        # A back zip on every candidate, the industrial suit's mark: a seam down the spine with a pull at the top.
        seam(img, inner, fx(0.5), fy(0.2), fx(0.5), fy(0.72))
        zip_pull(img, inner, fx(0.5), fy(0.2))
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


NAMES = {"A": "sidepanels", "B": "yoke", "C": "pads"}
if __name__ == "__main__":
    for key, name in NAMES.items():
        export(item(key, master=True)).save(OUT / f"NeopreneWetsuit_{key}_{name}.png")
        for body in TYPES:
            for direction in ("south", "east", "north"):
                worn(key, body, direction).save(OUT / f"NeopreneWetsuit_{key}_{name}_{body}_{direction}.png")

    # Approved: B, chest yoke (APPROVAL.md). Game textures: NeopreneWetsuit.png (item, the basic suit's 100 px export) and
    # NeopreneWetsuit_<BodyType>_<dir>.png (worn views, unchanged) for every body type given.
    export(item("B", master=True)).save(OUT / "NeopreneWetsuit.png")
    for body in TYPES:
        for direction in ("south", "east", "north"):
            worn("B", body, direction).save(OUT / f"NeopreneWetsuit_{body}_{direction}.png")
