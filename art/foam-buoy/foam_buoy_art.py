"""Procedural candidate designs for Spearfishing's foam buoy item sprite (128x128, Graphic_Single, 128 px per cell).

The industrial tier of the approved wooden buoy (art/wooden-buoy, candidate B "cask float"). Drawn with the wooden buoy's own
helpers (contour, material lines, upper-left shading, export recipe), so contour weight and shading match it: each candidate is
drawn at 4x (512 px) as at most three broad parts and reduced with export(fill=100). Each master's longest side is close to the
wooden buoy's (436 px), so the contour lands at the same game width after export. The silhouettes differ from the cask, so the
two buoys can be told apart in a stockpile. Materials follow the recipe (chemfuel, cloth, a component): moulded foam, cloth
webbing and a steel ring.

Procedural only: no reference images, vanilla, DLC or third-party art go into the masters. Vanilla is not used on the sheet.

Usage: python -I foam_buoy_art.py <out_dir> [sheet_path]
  Writes FoamBuoyA/B/C_master512.png and FoamBuoyA/B/C.png (exports) to out_dir and, with sheet_path, the contact sheet.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "wooden-buoy"))
from buoy_art import (MAT_LINE, S, Canvas, at_game_scale, band, ellipse_mask, export, font,  # noqa: E402
                      poly_mask, ring_mask, round_shade, tile)

FOAM = np.array([204, 112, 64], float)       # muted safety orange, saturation 0.69
PALE = np.array([226, 218, 200], float)      # off-white foam / reflective band
WEBBING = np.array([84, 100, 116], float)    # slate cloth webbing, kept well clear of the black line
STEEL = np.array([188, 194, 198], float)     # the steel pole spear's steel family


def capsule_mask(x0, x1, cy, r):
    """Horizontal capsule: a rectangle with round ends from x0 to x1."""
    pts = []
    for k in range(41):
        t = -math.pi / 2 + math.pi * k / 40
        pts.append((x1 - r + r * math.cos(t), cy + r * math.sin(t)))
    for k in range(41):
        t = math.pi / 2 + math.pi * k / 40
        pts.append((x0 + r + r * math.cos(t), cy + r * math.sin(t)))
    return poly_mask(pts)


def flat(mask, color, var=0.0):
    """Webbing: flat colour with a faint weave, like the wooden buoy's cord but smoother."""
    yy, xx = np.mgrid[0:S, 0:S].astype(float)
    return color[None, None, :] * (1 - var + var * np.sin((xx - yy) / 6.0))[..., None] * mask[..., None]


def steel_ring(c, cx, cy, r_out, r_in, clip):
    ring = np.clip(ring_mask(cx, cy, r_out, r_in) * (1 - clip), 0, 1)
    c.part(ring, round_shade(ring_mask(cx, cy, r_out, 0.1), STEEL, strength=0.30, highlight=0.12), line=MAT_LINE)


def candidate_a():
    """Torpedo float: a moulded foam capsule with one webbing strap round its middle and a steel tow ring at one end."""
    c = Canvas()
    body = capsule_mask(52, 420, 280, 86)
    steel_ring(c, 446, 280, 40, 20, body)
    c.part(body, round_shade(body, FOAM, strength=0.30))
    strap = np.clip(band(236, 280, 90, 120, 22) * body, 0, 1)
    c.part(strap, flat(strap, WEBBING, 0.06), line=MAT_LINE)
    return c.image()


def candidate_b():
    """Ball float: a foam ball with a pale reflective band round its middle and a steel ring on a webbing tab on top."""
    c = Canvas()
    body = ellipse_mask(256, 296, 172, 166)
    tab = np.clip(band(256, 120, 90, 34, 18) * (1 - body), 0, 1)
    steel_ring(c, 256, 90, 38, 20, np.clip(body + tab, 0, 1))
    c.part(tab, flat(tab, WEBBING, 0.06), line=MAT_LINE)
    c.part(body, round_shade(body, FOAM, strength=0.30))
    stripe = np.clip(band(256, 296, 0, 190, 30) * body, 0, 1)
    c.part(stripe, round_shade(body, PALE, strength=0.22) * stripe[..., None], line=MAT_LINE)
    return c.image()


def candidate_c():
    """Ring buoy: a foam life ring with four pale quarter bands, the shape everyone reads as 'buoy'."""
    c = Canvas()
    ring = ring_mask(256, 270, 214, 104)
    c.part(ring, round_shade(ring, FOAM, strength=0.30))
    for ang in (45, 135):
        seg = np.clip(band(256, 270, ang, 240, 34) * ring, 0, 1)
        c.part(seg, round_shade(ring, PALE, strength=0.22) * seg[..., None], line=MAT_LINE)
    return c.image()


CANDIDATES = {"A": ("Torpedo float", candidate_a), "B": ("Ball float", candidate_b), "C": ("Ring buoy", candidate_c)}


# ---- Measurements reported on the sheet --------------------------------------------------------------------------------------

def outline_px(img):
    """Median run of near-black opaque pixels inward from the alpha edge, over every row and column, in the image's own pixels."""
    a = np.array(img.convert("RGBA"), float)
    opaque, dark = a[..., 3] > 127, a[..., :3].max(axis=2) <= 60
    runs = []
    for o, d in ((opaque, dark), (opaque.T, dark.T)):
        for row_o, row_d in zip(o, d):
            idx = np.nonzero(row_o)[0]
            if len(idx) < 8:
                continue
            for start, step in ((idx[0], 1), (idx[-1], -1)):
                n, i = 0, start
                while 0 <= i < len(row_o) and row_o[i] and row_d[i]:
                    n, i = n + 1, i + step
                runs.append(n)
    return float(np.median(runs))


def sat_p90(img):
    a = np.array(img.convert("RGBA"), float)
    rgb = a[..., :3][(a[..., 3] > 200) & (a[..., :3].max(axis=2) > 60)]
    mx = rgb.max(axis=1)
    return float(np.percentile((mx - rgb.min(axis=1)) / mx, 90))


# ---- Contact sheet -------------------------------------------------------------------------------------------------------------

SAND, SEA = (214, 198, 158, 255), (46, 92, 120, 255)


def strip(items, cell_px, bg, per=2):
    """Each item at `cell_px` per cell on alternating tiles, one item every `per` cells."""
    img = tile(bg, cell_px, len(items) * per + 1, 1)
    for i, (_, tex) in enumerate(items):
        g = at_game_scale(tex, cell_px, 128)
        img.alpha_composite(g, (i * per * cell_px + cell_px + (cell_px - g.width) // 2, (cell_px - g.height) // 2))
    return img


def contact_sheet(out_dir, sheet_path):
    repo = HERE.parents[1]
    wooden = Image.open(repo / "Textures/Things/Spearfishing/Apparel/WoodenBuoy.png").convert("RGBA")
    fins = Image.open(repo / "Textures/Things/Spearfishing/Apparel/WoodenFins.png").convert("RGBA")
    cands = [(k, Image.open(out_dir / f"FoamBuoy{k}.png").convert("RGBA")) for k in CANDIDATES]
    items = cands + [("wooden buoy*", wooden)]

    W = 1700
    title, label, small = font(30), font(20), font(16)
    sheet = Image.new("RGBA", (W, 1400), (36, 38, 42, 255))
    d = ImageDraw.Draw(sheet)
    d.text((30, 20), "Foam buoy: candidates (pick one)", font=title, fill=(240, 240, 240))
    d.text((30, 60), "Industrial tier of the approved wooden buoy (* = approved Spearfishing art). Item sprite only, no worn "
           "graphic. Foam, cloth webbing and a steel ring, after the chemfuel, cloth and component recipe.",
           font=small, fill=(200, 200, 200))

    # Row 1: masters at 300 px with their figures.
    y = 100
    masters = [(k, n, Image.open(out_dir / f"FoamBuoy{k}_master512.png")) for k, (n, _) in CANDIDATES.items()]
    masters.append(("*", "Wooden buoy (approved)", Image.open(HERE.parent / "wooden-buoy/WoodenBuoy_master512.png")))
    for i, (key, name, m) in enumerate(masters):
        x = 30 + i * 410
        bg = tile(SAND, 50, 6, 6)
        bg.alpha_composite(m.convert("RGBA").resize((300, 300), Image.LANCZOS))
        sheet.alpha_composite(bg, (x, y + 30))
        d.text((x, y), f"{key}  {name}", font=label, fill=(255, 230, 160))
        tex = dict(items)[key] if key in CANDIDATES else wooden
        d.text((x, y + 340), f"outline {outline_px(tex):.1f} px at 128 px/cell; saturation p90 {sat_p90(tex):.2f}",
               font=small, fill=(200, 200, 200))

    # Row 2: 1.5x the texture (192 px per cell) on sand and sea.
    y = 480
    d.text((30, y), "1.5x (192 px per cell), on sand and on open sea", font=label, fill=(240, 240, 240))
    for row, bg in enumerate((SAND, SEA)):
        s = strip(items, 192, bg, per=2)
        sheet.alpha_composite(s.crop((0, 0, min(s.width, W - 60), 192)), (30, y + 32 + row * 200))
    for i, (name, _) in enumerate(items):
        d.text((30 + i * 384 + 288, y + 32 + 400), name, font=small, fill=(220, 220, 220), anchor="mt")

    # Row 3: game size, normal zoom (64 px per cell), beside the wooden buoy and the wooden fins.
    y = 960
    d.text((30, y), "Game size, normal zoom (64 px per cell), on sand and on open sea, beside the wooden buoy and fins",
           font=label, fill=(240, 240, 240))
    near = items + [("fins*", fins)]
    for row, bg in enumerate((SAND, SEA)):
        sheet.alpha_composite(strip(near, 64, bg, per=3), (30, y + 32 + row * 74))
    for i, (name, _) in enumerate(near):
        d.text((30 + i * 192 + 96, y + 32 + 150), name, font=small, fill=(220, 220, 220), anchor="mt")

    # Row 4: zoomed in (128 px per cell, the texture's own size) on open sea.
    y = 1190
    d.text((30, y), "Zoomed in (128 px per cell) on open sea", font=label, fill=(240, 240, 240))
    sheet.alpha_composite(strip(items, 128, SEA, per=2), (30, y + 32))
    for i, (name, _) in enumerate(items):
        d.text((30 + i * 256 + 192, y + 32 + 136), name, font=small, fill=(220, 220, 220), anchor="mt")

    sheet_path = Path(sheet_path)
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(sheet_path)


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, (_, make) in CANDIDATES.items():
        master = make()
        master.save(out_dir / f"FoamBuoy{key}_master512.png")
        export(master).save(out_dir / f"FoamBuoy{key}.png")
    if len(sys.argv) > 2:
        contact_sheet(out_dir, sys.argv[2])
