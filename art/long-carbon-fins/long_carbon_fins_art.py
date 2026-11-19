"""Procedural candidate designs for Spearfishing's long carbon fins (gear tiers, spacer), round 2.

Same method as the approved wooden fins (art/wooden-fins/fins_art.py) and plastic fins (candidate A of
art/plastic-fins/plastic_fins_art.py, whose helpers this script reuses): the item is drawn at 4x (512 px) as a splayed paddle
pair with smooth upper-left light, a black exterior contour and black material lines, then reduced with the fins' export recipe
at a larger fill (longest side 112 px on the 128 canvas, against 100 px for the other fins), so the pair reads longer.

Round 2 (the user's answer to round 1): the fins are black, blade and foot pocket alike, and the pocket is rubber, never
plasteel. The blade is a cool blue-black carbon with one broad soft gloss; the pocket is a neutral-warm matte black rubber, so
the two separate by gloss and a small hue shift as well as the material line. Every dark stays clearly above the outline's black.
The candidates differ in how the blade is told apart from the pocket: gloss alone, a coarse weave hint, or lighter edge rails.
Fins are item only, with no worn graphic (ticket 02's approval).

Usage: python -I long_carbon_fins_art.py <out_dir>
  Writes LongCarbonFins_<X>_<name>_master512.png, LongCarbonFins_<X>_<name>.png (item export) and contact_sheet.png, which
  shows each candidate beside the plastic fins (A, drawn in memory) and the wooden fins. No vanilla art is used.
"""
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("plastic_fins_art", HERE.parent / "plastic-fins" / "plastic_fins_art.py")
pf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pf)

S, LINE, MAT_LINE = pf.S, pf.LINE, pf.MAT_LINE

CARBON = np.array([58, 62, 72], float)          # cool blue-black carbon: darkest shaded pixel stays near 48, clear of the outline
CARBON_GLOSS = np.array([116, 124, 138], float)  # one broad soft value lift, never a white streak
CARBON_RAIL = np.array([92, 98, 110], float)     # candidate C: lighter charcoal edge band, inside the contour
RUBBER = np.array([60, 57, 54], float)           # black rubber foot pocket: neutral-warm and matte against the cool glossy blade
INSIDE = np.array([30, 30, 32], float)           # inside of the foot opening: darker than the pocket, above the outline's black

LENGTH, WH, WT = 420, 92, 132                   # plastic fins: 330, 104, 150
POCKET = 126                                    # absolute pocket length, as the plastic fins' (0.38 x 330)
FILL = 112                                      # export: longest side on the 128 canvas (other fins: 100), so they read longer

# key: (name, label, weave, rails). Every candidate: black carbon blade with a gloss band, black matte rubber pocket.
CANDIDATES = {
    "A": ("gloss", "gloss blade, matte rubber pocket", False, False),
    "B": ("weave", "gloss blade with a coarse weave hint, matte rubber pocket", True, False),
    "C": ("rails", "gloss blade with lighter edge rails, matte rubber pocket", False, True),
}


def carbon_fill(m, cx, cy, angle, weave):
    """Blue-black with smooth upper-left light and one broad gloss band running down the blade's upper-left half."""
    col = pf.shade(m, CARBON, strength=0.18)
    yy, xx = np.mgrid[0:S, 0:S].astype(float)
    a = math.radians(angle)
    lx = (xx - cx) * math.cos(a) + (yy - cy) * math.sin(a)        # across the blade
    ly = -(-(xx - cx) * math.sin(a) + (yy - cy) * math.cos(a))    # along the blade, 0 at heel, up positive
    if weave:
        # Coarse, low-contrast twill: 28 px squares at 4x (about 7 px at 128), a small alternating value step.
        p = 28.0
        u, v = (lx + ly) / p, (ly - lx) / p
        check = (np.sign(np.sin(math.pi * u) * np.sin(math.pi * v)) + 1) / 2
        col = col * (1 + 0.10 * (pf.blur(check * m, 1.5)[..., None] - 0.5))
    band = np.exp(-((lx + WH * 0.18) / (WH * 0.16)) ** 2)
    band *= np.clip((ly - POCKET) / 60, 0, 1) * np.clip((LENGTH - ly) / 90, 0, 1)
    band = pf.blur(band, 6) * m * 0.55
    return col * (1 - band[..., None]) + CARBON_GLOSS * band[..., None]


def fin(c, cx, cy, angle, weave, rails):
    m = pf.mask_of(pf.transform(pf.blade_outline(LENGTH, WH, WT), cx, cy, angle))
    col = carbon_fill(m, cx, cy, angle, weave)
    if rails:
        # Lighter charcoal band along each long edge, inside the black contour (a value change, no keyline or outer rim).
        inner = np.clip(m - pf.dilate(1 - m, 1), 0, 1)
        core = 1 - pf.dilate(1 - m, 13)
        railm = pf.blur(np.clip(inner - core, 0, 1), 2) * m
        col = col * (1 - railm[..., None]) + pf.shade(m, CARBON_RAIL) * railm[..., None]
    c.part(m, col)

    # Black rubber foot pocket over the heel, behind a black material line: matte, so flatter light and no gloss.
    band = pf.mask_of(pf.transform([(-WT, 20), (WT, 20), (WT, -POCKET), (-WT, -POCKET)], cx, cy, angle))
    pocket = np.clip(m * band - pf.dilate(1 - m, 7), 0, 1)
    c.part(pocket, pf.shade(pocket, RUBBER, strength=0.12), line=MAT_LINE)
    oy = (20 - POCKET) / 2 + 18
    hole = pf.ellipse_mask(*pf.transform([(0, oy)], cx, cy, angle)[0], WH * 0.26, 330 * 0.07, angle) * pocket
    h = pf.blur(hole, 5)
    c.rgb = c.rgb * (1 - h[..., None]) + INSIDE * h[..., None]


def item_master(weave, rails):
    c = pf.Canvas()
    fin(c, 200, 462, -7, weave, rails)
    fin(c, 312, 462, 7, weave, rails)
    img = c.image()
    a = np.array(img)[..., 3]
    assert not (a[0].any() or a[-1].any() or a[:, 0].any() or a[:, -1].any()), "fin touches the master canvas edge"
    return img


SAND = (214, 198, 158, 255)


def contact_sheet(out_dir, items, plastic, wooden):
    W = 1320
    H = 200 + 300 * (len(items) + 1)
    title, label, small = pf.font(30), pf.font(20), pf.font(16)
    sheet = Image.new("RGBA", (W, H), (36, 38, 42, 255))
    d = ImageDraw.Draw(sheet)
    d.text((30, 18), "Long carbon fins, round 2: candidates (pick one)", font=title, fill=(240, 240, 240))
    d.text((30, 58), "Black carbon blade with one soft gloss, black matte rubber foot pocket (no plasteel). Same paddle pair and "
                     "light as the wooden and plastic fins.", font=small, fill=(200, 200, 200))
    d.text((30, 80), f"Larger export, as chosen: longest side {FILL} px on the 128 canvas (plastic and wooden fins: 100 px). "
                     "Item only (ticket 02).", font=small, fill=(255, 220, 150))
    for x, t in [(30, "Item at 1.5x (192 px)"), (260, "Plastic fins A at 1.5x"),
                 (490, "Game size, 64 px per cell: candidate, plastic fins A, wooden fins")]:
        d.text((x, 120), t, font=small, fill=(220, 220, 220))

    rows = [(f"{k}  {name}", img) for k, (name, img) in items.items()]
    y = 150
    for name, item in rows:
        d.text((30, y), name, font=label, fill=(255, 230, 160))
        top = y + 30
        for i, art in enumerate((item, plastic)):
            bg = pf.tile(SAND, 48, 4, 4)
            bg.alpha_composite(art.resize((192, 192), Image.LANCZOS))
            sheet.alpha_composite(bg, (30 + i * 230, top))
        strip = pf.tile(SAND, 64, 12, 3)
        for i, art in enumerate((item, plastic, wooden)):
            strip.alpha_composite(art.resize((64, 64), Image.LANCZOS), (64 + i * 192, 64))
        sheet.alpha_composite(strip.crop((0, 0, 576 + 128, 192)), (490, top))
        y += 300

    # Tier line at 1.5x: wooden, plastic, then each carbon candidate.
    d.text((30, y), "Tier line at 1.5x: wooden fins, plastic fins A, long carbon fins A, B, C", font=label, fill=(190, 220, 255))
    for i, art in enumerate([wooden, plastic] + [img for _, img in items.values()]):
        bg = pf.tile(SAND, 48, 4, 4)
        bg.alpha_composite(art.resize((192, 192), Image.LANCZOS))
        sheet.alpha_composite(bg, (30 + i * 210, y + 30))
    sheet.convert("RGB").save(out_dir / "contact_sheet.png")


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    items = {}
    for key, (name, label, weave, rails) in CANDIDATES.items():
        master = item_master(weave, rails)
        master.save(out_dir / f"LongCarbonFins_{key}_{name}_master512.png")
        item = pf.export(master, fill=FILL)
        item.save(out_dir / f"LongCarbonFins_{key}_{name}.png")
        items[key] = (label, item)
    kind, _, plastic_col, plastic_rail = pf.CANDIDATES["A"]
    plastic = pf.export(pf.item_master(kind, plastic_col, plastic_rail))
    wooden = Image.open(REPO / "Textures/Things/Spearfishing/Apparel/WoodenFins.png").convert("RGBA")
    contact_sheet(out_dir, items, plastic, wooden)
