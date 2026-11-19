"""Procedural candidate designs for Spearfishing's wooden buoy item sprite (128x128, Graphic_Single, 128 px per cell).

Same method as the approved wooden fins (art/wooden-fins/fins_art.py): each candidate is drawn at 4x (512 px) as a few broad
shapes with smooth upper-left light, a black exterior contour and black material lines, then reduced to 128 px. The user asked
for bold, simple shapes with little fine detail, so each design is three parts at most and carries no grain or carving.

Usage: python buoy_art.py <out_dir> [sheet_refs_dir]
  Writes BuoyA/B/C_master512.png, BuoyA/B/C.png (exports) and, with the reference folder, contact_sheet.png.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 512          # master canvas
OUT = 128        # exported texture
LINE = 14        # exterior contour at master scale, as the fins
MAT_LINE = 10    # material line at master scale, as the fins

WOOD = np.array([150, 104, 62], float)      # the fins' mid wood
PALE_WOOD = np.array([176, 134, 86], float)  # lighter, peeled wood
ROPE = np.array([196, 170, 118], float)      # the fins' plant-fibre cord
OCHRE = np.array([168, 66, 40], float)       # red ochre paint, so the float shows at sea


def poly_mask(pts):
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m, float) / 255.0


def ellipse_mask(cx, cy, rx, ry, angle=0.0, n=120):
    a = math.radians(angle)
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
    return poly_mask(pts)


def ring_mask(cx, cy, r_out, r_in, ry_scale=1.0):
    return np.clip(ellipse_mask(cx, cy, r_out, r_out * ry_scale) - ellipse_mask(cx, cy, r_in, r_in * ry_scale), 0, 1)


def band(cx, cy, angle, half_len, half_w):
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    pts = [(-half_len, -half_w), (half_len, -half_w), (half_len, half_w), (-half_len, half_w)]
    return poly_mask([(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts])


def stroke_mask(points, width):
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    d.line(points, fill=255, width=width, joint="curve")
    for x, y in (points[0], points[-1]):
        d.ellipse((x - width / 2, y - width / 2, x + width / 2, y + width / 2), fill=255)
    return np.array(m, float) / 255.0


def dilate(m, r):
    img = Image.fromarray((m * 255).astype(np.uint8))
    return np.array(img.filter(ImageFilter.MaxFilter(r * 2 + 1)), float) / 255.0


def round_shade(mask, base, strength=0.30, highlight=0.10):
    """Rounded body lit from the upper-left: brightest towards the 10-11 o'clock edge, darkest at the lower right."""
    yy, xx = np.mgrid[0:S, 0:S].astype(float)
    ys, xs = np.nonzero(mask > 0.5)
    if len(xs) == 0:
        return np.zeros((S, S, 3))
    cx, cy = xs.mean(), ys.mean()
    rx, ry = max(np.ptp(xs) / 2, 1), max(np.ptp(ys) / 2, 1)
    u, v = (xx - cx) / rx, (yy - cy) / ry
    g = np.clip((u + v) / 1.6, -1, 1)
    light = 1.0 - strength * g
    # One broad soft highlight, not a streak.
    hl = np.exp(-(((u + 0.38) ** 2 + (v + 0.42) ** 2) / 0.10))
    light += highlight * hl
    return np.clip(base[None, None, :] * light[..., None], 0, 255)


def cord(mask):
    yy, xx = np.mgrid[0:S, 0:S].astype(float)
    return ROPE[None, None, :] * (0.88 + 0.12 * np.sin((xx + yy) / 7.0))[..., None] * mask[..., None] + 0 * mask[..., None]


class Canvas:
    def __init__(self):
        self.rgb = np.zeros((S, S, 3))
        self.alpha = np.zeros((S, S))

    def part(self, mask, color, line=LINE):
        """Paint a part over what is there: a black contour ring outside its fill, then its fill."""
        outer = dilate(mask, line // 2) if line else mask
        ring = np.clip(outer - mask, 0, 1)
        self.rgb = self.rgb * (1 - ring[..., None])
        self.alpha = np.maximum(self.alpha, outer)
        self.rgb = self.rgb * (1 - mask[..., None]) + color * mask[..., None]

    def image(self):
        a = (np.clip(self.alpha, 0, 1) * 255).astype(np.uint8)
        return Image.fromarray(np.dstack([self.rgb.astype(np.uint8), a]), "RGBA")


def candidate_a():
    """Round float: a plump wooden ball with one cord band round its middle and a short tow loop on top."""
    c = Canvas()
    body = ellipse_mask(256, 290, 168, 156)
    c.part(body, round_shade(body, WOOD))
    loop = np.clip(ring_mask(256, 128, 54, 30) * (1 - body), 0, 1)
    c.part(loop, cord(loop), line=MAT_LINE)
    belt = np.clip(band(256, 290, -4, 180, 17) * body, 0, 1)
    c.part(belt, cord(belt), line=MAT_LINE)
    return c.image()


def candidate_b():
    """Cask float: a short, fat cask on its side, bound with two cord hoops, with a cord tail at one end."""
    c = Canvas()
    # Cask: a rounded box, fuller in the middle.
    pts = []
    for k in range(80):
        t = 2 * math.pi * k / 80
        x = 190 * math.copysign(abs(math.cos(t)) ** 0.55, math.cos(t))
        y = 118 * math.copysign(abs(math.sin(t)) ** 0.8, math.sin(t)) * (1 - 0.10 * abs(math.cos(t)))
        pts.append((256 + x, 300 + y))
    body = poly_mask(pts)
    c.part(body, round_shade(body, PALE_WOOD, strength=0.26))
    for hx in (-92, 92):
        hoop = np.clip(band(256 + hx, 300, 90, 140, 16) * body, 0, 1)
        c.part(hoop, cord(hoop), line=MAT_LINE)
    tail = np.clip(stroke_mask([(446, 300), (470, 250), (452, 196), (478, 150)], 22) * (1 - body), 0, 1)
    c.part(tail, cord(tail), line=MAT_LINE)
    return c.image()


def candidate_c():
    """Ochre spindle: a carved spindle-shaped float, its upper half painted red ochre to show at sea, with a tow loop."""
    c = Canvas()
    angle = -28
    body = ellipse_mask(250, 290, 200, 92, angle)
    c.part(body, round_shade(body, WOOD))
    # Paint: the upper-left half of the spindle, split along its long axis. Paint over wood is a different material, so a line.
    a = math.radians(angle)
    yy, xx = np.mgrid[0:S, 0:S].astype(float)
    side = -(xx - 250) * math.sin(a) + (yy - 290) * math.cos(a)
    paint = np.clip(body * (side < -6), 0, 1)
    c.part(paint, round_shade(body, OCHRE) * paint[..., None] + 0, line=MAT_LINE)
    tip = (250 + 200 * math.cos(a), 290 + 200 * math.sin(a))
    loop = np.clip(ring_mask(tip[0] + 34, tip[1] - 28, 46, 24) * (1 - body), 0, 1)
    c.part(loop, cord(loop), line=MAT_LINE)
    return c.image()


CANDIDATES = {"A": ("Round float", candidate_a), "B": ("Cask float", candidate_b), "C": ("Ochre spindle", candidate_c)}


def export(master, fill=100):
    """Fit the alpha bounds into `fill` px of the 128 canvas, centred, uniform scale (the fins' approved recipe)."""
    box = master.getbbox()
    crop = master.crop(box)
    scale = fill / max(crop.size)
    size = (max(1, round(crop.size[0] * scale)), max(1, round(crop.size[1] * scale)))
    small = crop.resize(size, Image.LANCZOS)
    out = Image.new("RGBA", (OUT, OUT), (0, 0, 0, 0))
    out.alpha_composite(small, ((OUT - size[0]) // 2, (OUT - size[1]) // 2))
    return out


# ---- Contact sheet ---------------------------------------------------------------------------------------------------------

def font(size):
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def load_ref(path):
    path = Path(path)
    if path.suffix.lower() == ".psd":
        from psd_tools import PSDImage
        return PSDImage.open(path).composite().convert("RGBA")
    return Image.open(path).convert("RGBA")


def tile(bg, cell_px, cells_w, cells_h):
    img = Image.new("RGBA", (cell_px * cells_w, cell_px * cells_h), bg)
    d = ImageDraw.Draw(img)
    shade = tuple(max(0, c - 10) for c in bg[:3]) + (255,)
    for i in range(cells_w):
        for j in range(cells_h):
            if (i + j) % 2:
                d.rectangle((i * cell_px, j * cell_px, (i + 1) * cell_px - 1, (j + 1) * cell_px - 1), fill=shade)
    return img


def at_game_scale(img, cell_px, tex_px_per_cell):
    s = cell_px / tex_px_per_cell
    return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)


def contact_sheet(out_dir, refs):
    """refs: list of (label, image, texture px per cell). Rows: masters; game scale on sand and on sea beside the references."""
    W = 1600
    title, label = font(30), font(20)
    small = font(16)
    sheet = Image.new("RGBA", (W, 1060), (36, 38, 42, 255))
    d = ImageDraw.Draw(sheet)
    d.text((30, 20), "Wooden buoy: candidates (pick one)", font=title, fill=(240, 240, 240))
    d.text((30, 60), "Item sprite only: like the approved fins, the buoy has no worn graphic, so it never draws on or beside the pawn.",
           font=small, fill=(200, 200, 200))

    # Row 1: masters at 320 px.
    y = 100
    for i, (key, (name, _)) in enumerate(CANDIDATES.items()):
        x = 30 + i * 480
        m = Image.open(out_dir / f"Buoy{key}_master512.png").resize((320, 320), Image.LANCZOS)
        bg = tile((210, 196, 160, 255), 40, 8, 8)
        bg.alpha_composite(m, (0, 0))
        sheet.alpha_composite(bg, (x, y + 30))
        d.text((x, y), f"{key}  {name}", font=label, fill=(255, 230, 160))

    # Row 2: normal zoom (64 px per cell) on sand, beside the approved Spearfishing art and vanilla, one item per 3 cells.
    y = 500
    d.text((30, y), "Normal zoom (64 px per cell) on sand. * = approved Spearfishing art; the rest are vanilla.",
           font=label, fill=(240, 240, 240))
    items = [(f"{k}", Image.open(out_dir / f"Buoy{k}.png"), 128) for k in CANDIDATES] + refs
    per = 3
    strip = tile((214, 198, 158, 255), 64, len(items) * per, 1)
    for i, (name, img, ppc) in enumerate(items):
        g = at_game_scale(img, 64, ppc)
        strip.alpha_composite(g, (i * per * 64 + 64 + (64 - g.width) // 2, (64 - g.height) // 2))
        d.text((30 + i * per * 64 + 96, y + 36 + 70), name, font=small, fill=(220, 220, 220), anchor="mt")
    sheet.alpha_composite(strip, (30, y + 36))

    # Row 3: zoomed in (128 px per cell) on sand next to the approved fins, then on open sea, where the buoy matters.
    y = 660
    d.text((30, y), "Zoomed in (128 px per cell): on sand beside the approved fins, then on open sea.", font=label, fill=(240, 240, 240))
    near = [(f"{k}", Image.open(out_dir / f"Buoy{k}.png"), 128) for k in CANDIDATES] + refs[:1]
    for row, bg in enumerate(((214, 198, 158, 255), (46, 92, 120, 255))):
        shown = near if row == 0 else near[:3]
        strip = tile(bg, 128, len(shown) * 2 + 1, 1)
        for i, (name, img, ppc) in enumerate(shown):
            g = at_game_scale(img, 128, ppc)
            strip.alpha_composite(g, (i * 2 * 128 + 128 + (128 - g.width) // 2, (128 - g.height) // 2))
            d.text((30 + i * 2 * 128 + 192, y + 36 + row * 170 + 134), name, font=small, fill=(220, 220, 220), anchor="mt")
        sheet.alpha_composite(strip, (30, y + 36 + row * 170))
    sheet.convert("RGB").save(out_dir / "contact_sheet.png")


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, (_, make) in CANDIDATES.items():
        master = make()
        master.save(out_dir / f"Buoy{key}_master512.png")
        export(master).save(out_dir / f"Buoy{key}.png")
    if len(sys.argv) > 2:
        repo = Path(__file__).resolve().parents[2]
        vanilla = Path(sys.argv[2])
        refs = [
            ("fins*", Image.open(repo / "Textures/Things/Spearfishing/Apparel/WoodenFins.png").convert("RGBA"), 128),
            ("pole spear*", Image.open(repo / "Textures/Things/Spearfishing/Weapon/PoleSpear.png").convert("RGBA"), 128),
            ("spear", load_ref(vanilla / "Things/Item/Equipment/WeaponMelee/Spear.png"), None),
            ("barrel", load_ref(vanilla / "Things/Item/Resource/ReinforcedBarrel/ReinforcedBarrel.png"), None),
            ("club", load_ref(vanilla / "Things/Item/Equipment/WeaponMelee/Club.png"), None),
        ]
        # Vanilla textures fill one cell at their own size.
        refs = [(n, img, ppc if ppc else img.width) for n, img, ppc in refs]
        contact_sheet(out_dir, refs)
