"""Thermal wetsuit candidates for Spearfishing (gear-tiers ticket 10). Procedural PIL drawing in the house rendering of the
approved basic wetsuit (art/wetsuit) and the approved neoprene wetsuit (art/neoprene-wetsuit, candidate B): the same laid-flat
item silhouette and worn construction, flat two-tone shapes lit from the upper left, a black outward outline and black lines
between materials, no fine detail. Only the palette and the panels change from the neoprene script.

This is the spacer tier, made from synthread, plasteel and an advanced component, and a fixed material, so the colour is baked
in. The tiers are told apart by colour and panels, not by a new rendering: the neoprene suit is charcoal with a blue chest
yoke, so the thermal suit is pale synthread grey with a warm amber accent (saturation 0.68) for warmth. It is sealed, so unlike
the neoprene suit it has no back zip; the north view shows the panels only. On B's worn views the heated core is built from
each body's silhouette (core_panel) and shaded with the suit under it (lined_on_body), with a narrower back pad on north.

Each candidate has an item sprite (128x128, Graphic_Single, drawSize 1, 4 px outline at 128) and worn views for the OnSkin
layer: 128x128 body textures named <path>_<BodyType>_<dir>.png. A worn view fills the vanilla naked body's silhouette for
that body type (its alpha only, so the suit fits the body; no vanilla colour pixels are used), with a 3 px inward outline.
As for the earlier suits, the east (side) view has no centre seam, and nothing on it is one-sided, because west is east
mirrored. Markings stay above 0.8 of the body's height, because vanilla bodies stop around the thigh.

Usage: python -I thermal_wetsuit_art.py <vanilla_bodies_dir> <out_dir> [body types...]. Writes ThermalWetsuit_<X>_<name>.png
and ThermalWetsuit_<X>_<name>_<BodyType>_<dir>.png; Male only unless body types are given."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

BODIES = Path(sys.argv[1])
OUT = Path(sys.argv[2])
TYPES = sys.argv[3:] or ["Male"]
OUT.mkdir(parents=True, exist_ok=True)
SS = 8
S = 128
W = S * SS
INK = (12, 10, 10, 255)
# Pale synthread grey, well clear of the neoprene suit's charcoal; a slate panel tone; a warm amber accent (saturation 0.68).
SUIT, SUIT_SHADE = (176, 180, 184, 255), (142, 146, 152, 255)
SLATE, SLATE_SHADE = (78, 86, 96, 255), (60, 66, 75, 255)
ACCENT, ACCENT_SHADE = (200, 128, 64, 255), (162, 102, 50, 255)
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
        # Slate yoke: the neoprene suit's chest yoke carried up a tier, in slate on the pale suit.
        yoke = mask(a.size, lambda d: d.rectangle(p(0, 0, 128, 34), fill=255))
        lined(img, a, yoke, SLATE, SLATE_SHADE)
    elif kind == "B":
        # Heated core: an amber panel round the torso, chest to hips; arms and legs stay pale.
        core = mask(a.size, lambda d: d.rectangle(p(38, 34, 90, 62), fill=255))
        lined(img, a, core, ACCENT, ACCENT_SHADE)
    else:
        # Slate flanks: a slate panel down each side of the body and the outside of each leg, an amber chest band.
        side = mask(a.size, lambda d: (d.polygon(p(30, 30, 47, 30, 47, 70, 49, 116, 30, 116), fill=255),
                                       d.polygon(p(98, 30, 81, 30, 81, 70, 79, 116, 98, 116), fill=255)))
        lined(img, a, side, SLATE, SLATE_SHADE)
        band = mask(a.size, lambda d: d.rectangle(p(0, 34, 128, 41), fill=255))
        lined(img, a, band, ACCENT, ACCENT_SHADE)
    # The collar: an amber band round the neck opening on every candidate, the warm mark of this tier.
    collar = mask(a.size, lambda d: d.ellipse(p(50, 6, 78, 28), fill=255))
    lined(img, a, collar, ACCENT, ACCENT_SHADE)
    img = outward(img, 4 * SS)
    return img if master else shrink(img)


# ---- Worn views on the body silhouette -----------------------------------------------------------------------------------

def body_alpha(body, direction):
    a = Image.open(BODIES / f"Naked_{body}_{direction}.png").convert("RGBA").getchannel("A")
    return a.resize((W, W), Image.BILINEAR).point(lambda v: 255 if v > 127 else 0)


def lined_on_body(img, alpha, region, light, shade):
    """As lined(), but the panel is also shaded wherever the suit under it is, so the suit's shade band runs on across the
    panel instead of stopping at its edge, and the panel keeps its own shade lip like the neoprene suit's yoke."""
    region = ImageChops.multiply(alpha, region)
    grown = region.filter(ImageFilter.MaxFilter(LINE * 2 + 1))
    img.alpha_composite(solid(ImageChops.multiply(alpha, grown), INK))
    body_lit = ImageChops.multiply(alpha, ImageChops.offset(alpha, SHIFT, SHIFT))
    own_lit = ImageChops.multiply(region, ImageChops.offset(region, SHIFT, SHIFT))
    img.alpha_composite(solid(region, shade))
    img.alpha_composite(solid(ImageChops.multiply(own_lit, body_lit), light))


# The heated core per facing, all as fractions of the body's height or of each row's width:
# - top / bottom: how far the panel's top edge sits below the suit's own top contour (the shoulders), and its hem above the
#   suit's bottom contour, column by column, so both edges echo the body's curve: a V hem on Hulk, a round one on Fat;
# - scoop: how far the top edge dips at the centre (a scooped neckline; negative arches it up);
# - inset: the side margins (left, right) as a share of each row's width, so the sides follow the taper, waist and bulge.
# The front is a deep panel; the back is a narrower, shorter heating pad, as on a heated vest; the side view runs to the
# front edge and tapers towards the narrower back pad, so it reads as wrapping round the torso.
CORE = {
    "south": dict(top=0.17, bottom=0.30, scoop=0.05, inset=(0.11, 0.11)),
    "north": dict(top=0.25, bottom=0.40, scoop=-0.03, inset=(0.24, 0.24)),
    "east": dict(top=0.17, bottom=0.30, scoop=0.02, inset=(0.15, 0.0)),
}
EAST_TAPER = 0.07  # on the east view, how much the panel's top and bottom close in towards the back (left) edge
CORE_MIN = 5 * SS  # the narrowest panel, so Thin keeps a readable strip of amber between its material lines


def core_panel(inner, direction):
    """The core's mask, built from the suit's own silhouette so it follows each body type rather than a fixed rectangle."""
    c = CORE[direction]
    body = np.array(inner) > 127
    rows = np.flatnonzero(body.any(axis=1))
    cols = np.flatnonzero(body.any(axis=0))
    h = rows[-1] - rows[0]
    cx, hw = (cols[0] + cols[-1]) / 2, (cols[-1] - cols[0]) / 2
    xs = np.arange(W)
    t = np.clip((xs - cx) / hw, -1, 1)
    has = body.any(axis=0)
    top_contour = np.where(has, body.argmax(axis=0), W)
    bottom_contour = np.where(has, W - 1 - body[::-1].argmax(axis=0), -1)
    top = top_contour + h * (c["top"] + c["scoop"] * (1 - t * t))
    bottom = bottom_contour - h * c["bottom"]
    if direction == "east":
        back = np.clip(-t, 0, 1)
        top += h * EAST_TAPER * back
        bottom -= h * EAST_TAPER * back
    ys = np.arange(W)[:, None]
    m = np.zeros_like(body)
    for y in rows:
        row = np.flatnonzero(body[y])
        left, right = row[0], row[-1]
        a = left + (right - left) * c["inset"][0]
        b = right - (right - left) * c["inset"][1]
        if b - a < CORE_MIN:
            a, b = (a + b - CORE_MIN) / 2, (a + b + CORE_MIN) / 2
        m[y, int(a):int(b)] = True
    m &= (ys >= top[None, :]) & (ys <= bottom[None, :])
    return Image.fromarray((m * 255).astype(np.uint8), "L")


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
        yoke = mask(a.size, lambda d: d.rectangle([0, 0, W, fy(0.3)], fill=255))
        lined(img, inner, yoke, SLATE, SLATE_SHADE)
    elif kind == "B":
        core = core_panel(inner, direction)
        lined_on_body(img, inner, core, ACCENT, ACCENT_SHADE)
    else:
        if east:
            # The flank panel seen from the side: a band down the middle, symmetric so it mirrors for west.
            side = mask(a.size, lambda d: d.rectangle([fx(0.36), fy(0.18), fx(0.64), W], fill=255))
        else:
            side = mask(a.size, lambda d: (d.rectangle([0, fy(0.2), fx(0.22), W], fill=255),
                                           d.rectangle([fx(0.78), fy(0.2), W, W], fill=255)))
        lined(img, inner, side, SLATE, SLATE_SHADE)
        band = mask(a.size, lambda d: d.rectangle([0, fy(0.3), W, fy(0.38)], fill=255))
        lined(img, inner, band, ACCENT, ACCENT_SHADE)
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


NAMES = {"A": "slateyoke", "B": "core", "C": "flanks"}
if __name__ == "__main__":
    for key, name in NAMES.items():
        export(item(key, master=True)).save(OUT / f"ThermalWetsuit_{key}_{name}.png")
        for body in TYPES:
            for direction in ("south", "east", "north"):
                worn(key, body, direction).save(OUT / f"ThermalWetsuit_{key}_{name}_{body}_{direction}.png")

    # Approved: B, heated core (APPROVAL.md). Game textures: ThermalWetsuit.png (item, the basic suit's 100 px export) and
    # ThermalWetsuit_<BodyType>_<dir>.png (worn views, unchanged) for every body type given.
    export(item("B", master=True)).save(OUT / "ThermalWetsuit.png")
    for body in TYPES:
        for direction in ("south", "east", "north"):
            worn("B", body, direction).save(OUT / f"ThermalWetsuit_{body}_{direction}.png")
