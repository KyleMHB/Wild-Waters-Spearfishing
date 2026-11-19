"""Procedural candidate designs for Spearfishing's plastic fins (gear tiers, industrial).

Same method and framing as the approved wooden fins (art/wooden-fins/fins_art.py): the item is drawn at 4x (512 px) as a
splayed paddle pair of a few broad shapes with smooth upper-left light, a black exterior contour and black material lines,
then reduced with the fins' export recipe (longest side 100 px on a 128 canvas). The tier reads through material, not a new
silhouette: smooth moulded plastic with no grain, a coloured blade and a dark rubber foot pocket behind a material line.

Worn views are optional (the wooden fins have none; see the sheet's question): 128x128 body textures for the Male body,
_south, _east and _north, drawn at 4x and reduced, with a 3 px outline at 128. They sit at the feet of vanilla's naked body
frame (body alpha bounds about x 38-90, y 43-108).

Usage: python -I plastic_fins_art.py <out_dir> [<vanilla art source root>]
  Writes PlasticFins_<X>_<name>_master512.png, PlasticFins_<X>_<name>.png (item export) and
  PlasticFins_<X>_<name>_Male_<dir>.png (worn). With the vanilla art source root (the folder holding Things/Pawn/...), it
  also writes contact_sheet.png. Vanilla pixels are used only on the sheet, never in a texture.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 512          # master canvas
OUT = 128        # exported texture
LINE = 14        # exterior contour at master scale, as the wooden fins
MAT_LINE = 10    # material line at master scale, as the wooden fins
WORN_LINE = 24   # worn views: ring of 12 px at 4x = 3 px at 128, as the glass mask and wetsuit worn views

RUBBER = np.array([62, 66, 72], float)       # foot pocket: dark grey rubber, kept clear of the black outline
RUBBER_IN = np.array([40, 43, 48], float)    # inside of the foot opening
STEEL = np.array([176, 182, 188], float)     # buckle

# Blade plastics: saturation at or under 0.7 so they do not glow on sand.
CANDIDATES = {
    "A": ("pocket", "closed pocket, blue", np.array([66, 120, 162], float), np.array([46, 88, 124], float)),
    "B": ("strap", "open heel and strap, yellow", np.array([200, 166, 70], float), np.array([156, 124, 48], float)),
    "C": ("split", "split blade, teal", np.array([56, 142, 138], float), np.array([38, 104, 102], float)),
}


# ---- Geometry and rendering (the wooden fins' helpers) ----------------------------------------------------------------------

def blade_outline(length, width_heel, width_tip, n=60):
    """Points of one blade, heel at y=0 pointing up (-y), centred on x=0, with a gently bowed square tip."""
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        w = width_heel + (width_tip - width_heel) * (t ** 0.8)
        left.append((-w / 2, -t * length))
        right.append((w / 2, -t * length))
    wt = width_tip / 2
    tip = [(-wt + 2 * wt * a, -length - 10 * math.sin(math.pi * a)) for a in (i / 20 for i in range(21))]
    hw = width_heel / 2
    heel = [(hw * math.cos(math.pi * i / 20), hw * 0.8 * math.sin(math.pi * i / 20)) for i in range(21)]
    return left + tip + right[::-1] + heel


def transform(pts, cx, cy, angle_deg):
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def mask_of(pts, size=S):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m, float) / 255.0


def ellipse_mask(cx, cy, rx, ry, angle=0.0, size=S):
    pts = [(rx * math.cos(2 * math.pi * k / 60), ry * math.sin(2 * math.pi * k / 60)) for k in range(60)]
    return mask_of(transform(pts, cx, cy, angle), size)


def dilate(m, r):
    img = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8))
    return np.array(img.filter(ImageFilter.MaxFilter(r * 2 + 1)), float) / 255.0


def blur(m, r):
    img = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8))
    return np.array(img.filter(ImageFilter.GaussianBlur(r)), float) / 255.0


def shade(mask, base, size=S, strength=0.22):
    """Broad light from the upper left of the part: smooth moulded plastic, no grain."""
    yy, xx = np.mgrid[0:size, 0:size].astype(float)
    ys, xs = np.nonzero(mask > 0.5)
    if len(xs) == 0:
        return np.zeros((size, size, 3))
    cx, cy = xs.mean(), ys.mean()
    span = max(np.ptp(xs), np.ptp(ys), 1)
    g = ((xx - cx) + (yy - cy)) / (span * 0.75)
    light = 1.0 - strength * np.clip(g, -1, 1)
    return np.clip(base[None, None, :] * light[..., None], 0, 255)


class Canvas:
    def __init__(self, size=S):
        self.size = size
        self.rgb = np.zeros((size, size, 3))
        self.alpha = np.zeros((size, size))

    def part(self, mask, color, line=LINE):
        """Paint a part over what is there: a black contour ring outside its fill, then its fill."""
        outer = dilate(mask, line // 2) if line else mask
        ring = np.clip(outer - mask, 0, 1)
        self.rgb = self.rgb * (1 - ring[..., None])
        self.alpha = np.maximum(self.alpha, outer)
        self.rgb = self.rgb * (1 - mask[..., None]) + color * mask[..., None]

    def darken(self, m, amount):
        self.rgb = self.rgb * (1 - amount * np.clip(m, 0, 1)[..., None])

    def image(self):
        a = (np.clip(self.alpha, 0, 1) * 255).astype(np.uint8)
        return Image.fromarray(np.dstack([np.clip(self.rgb, 0, 255).astype(np.uint8), a]), "RGBA")


# ---- Item sprite: a splayed pair, as the approved paddle pair ----------------------------------------------------------------

def blade_mask(cx, cy, angle, length, wh, wt, split):
    m = mask_of(transform(blade_outline(length, wh, wt), cx, cy, angle))
    if split:
        # A wedge slit from the tip to just past half way: the blade flexes in two halves.
        slit = [(-wt * 0.14, -length - 14), (wt * 0.14, -length - 14), (0, -length * 0.52)]
        m = np.clip(m - mask_of(transform(slit, cx, cy, angle)), 0, 1)
    return m


def fin(c, cx, cy, angle, kind, plastic, rail, length=330, wh=104, wt=150):
    split = kind == "split"
    m = blade_mask(cx, cy, angle, length, wh, wt, split)
    col = shade(m, plastic)
    # Moulded rails: a darker band of the same plastic along each long edge (a value change, no black line).
    inner = np.clip(m - dilate(1 - m, 1), 0, 1)
    core = 1 - dilate(1 - m, 15)
    railm = np.clip(inner - core, 0, 1)
    if split:
        railm = railm * (1 - mask_of(transform([(-wt, -length - 20), (wt, -length - 20), (wt, -length * 0.88), (-wt, -length * 0.88)],
                                                cx, cy, angle)))
    railm = blur(railm, 2) * m
    col = col * (1 - railm[..., None]) + shade(m, rail)[...] * railm[..., None]
    c.part(m, col)

    # Rubber foot pocket over the heel, behind a black material line.
    if kind == "strap":
        lo, hi = -length * 0.10, -length * 0.38   # open heel: the pocket starts in front of the heel
    else:
        lo, hi = 20, -length * 0.38              # closed pocket wraps the heel
    band = mask_of(transform([(-wt, lo), (wt, lo), (wt, hi), (-wt, hi)], cx, cy, angle))
    pocket = np.clip(m * band, 0, 1)
    pocket = np.clip(pocket - dilate(1 - m, 7), 0, 1)  # keep the blade's own contour outside the pocket
    c.part(pocket, shade(pocket, RUBBER, strength=0.18), line=MAT_LINE)
    # Foot opening: a soft darker hollow, rubber inside rubber, so no black line.
    oy = (lo + hi) / 2 + (8 if kind == "strap" else 18)
    hole = ellipse_mask(*transform([(0, oy)], cx, cy, angle)[0], wh * 0.26, length * 0.07, angle) * pocket
    c.rgb = c.rgb * (1 - blur(hole, 5)[..., None]) + RUBBER_IN * blur(hole, 5)[..., None]

    if kind == "strap":
        # Heel strap: a rubber loop behind the open heel, with a small steel buckle on the outer side.
        loop = Image.new("L", (S, S), 0)
        d = ImageDraw.Draw(loop)
        pts = [(wh * 0.42 * math.cos(math.pi * i / 24), lo + wh * 0.62 * math.sin(math.pi * i / 24)) for i in range(25)]
        d.line(transform(pts, cx, cy, angle), fill=255, width=20, joint="curve")
        lm = np.array(loop, float) / 255.0 * (1 - pocket)
        c.part(lm, shade(lm, RUBBER, strength=0.12), line=MAT_LINE)
        side = 1 if cx > S / 2 else -1
        bx, by = transform([(side * wh * 0.40, lo + 6)], cx, cy, angle)[0]
        buckle = mask_of(transform([(-11, -9), (11, -9), (11, 9), (-11, 9)], bx, by, angle))
        c.part(buckle, shade(buckle, STEEL), line=MAT_LINE)
    return m


def item_master(kind, plastic, rail):
    c = Canvas()
    fin(c, 196, 430, -9, kind, plastic, rail)
    fin(c, 318, 430, 9, kind, plastic, rail)
    return c.image()


def export(master, fill=100):
    """The wooden fins' approved recipe: fit the alpha bounds into `fill` px of the 128 canvas, centred, uniform Lanczos."""
    crop = master.crop(master.getbbox())
    scale = fill / max(crop.size)
    size = (max(1, round(crop.size[0] * scale)), max(1, round(crop.size[1] * scale)))
    small = crop.resize(size, Image.LANCZOS)
    out = Image.new("RGBA", (OUT, OUT), (0, 0, 0, 0))
    out.alpha_composite(small, ((OUT - size[0]) // 2, (OUT - size[1]) // 2))
    return out


# ---- Worn views (Male body frame, 4x) ----------------------------------------------------------------------------------------

def q(*v):
    return [x * 4 for x in v]


def worn_fin_south(c, x, kind, plastic, rail):
    """Toes toward the camera: the blade runs down the screen from the foot, short and foreshortened."""
    blade = mask_of(q(x - 6, 104, x + 6, 104, x + 9, 123, x - 9, 123))
    if kind == "split":
        blade = np.clip(blade - mask_of(q(x - 1.6, 124, x + 1.6, 124, x, 114)), 0, 1)
    col = shade(blade, plastic)
    c.part(blade, col, line=WORN_LINE)
    pocket = mask_of(q(x - 7, 98, x + 7, 98, x + 7, 108, x - 7, 108)) if kind != "strap" else mask_of(q(x - 7, 101, x + 7, 101, x + 7, 108, x - 7, 108))
    c.part(pocket, shade(pocket, RUBBER, strength=0.12), line=MAT_LINE)


def worn_fin_east(c, dy, kind, plastic, rail, far=False):
    """Side view: the blade runs forward (east) from the foot. Nothing handed, so it reads the same mirrored to west."""
    y = 104 + dy
    blade = mask_of(q(62, y - 4, 96, y - 6, 97, y + 4, 62, y + 4))
    if kind == "split":
        blade = np.clip(blade - mask_of(q(98, y - 1.2, 98, y + 0.4, 86, y - 0.4)), 0, 1)
    p = plastic * (0.8 if far else 1.0)
    c.part(blade, shade(blade, p), line=WORN_LINE)
    x0 = 52 if kind != "strap" else 56
    pocket = mask_of(q(x0, y - 6, 68, y - 6, 70, y + 4, x0, y + 4))
    c.part(pocket, shade(pocket, RUBBER * (0.85 if far else 1.0), strength=0.12), line=MAT_LINE)
    if kind == "strap":
        strap = mask_of(q(51, y - 4, 57, y - 4, 57, y + 2, 51, y + 2))
        c.part(strap, shade(strap, RUBBER, strength=0.1), line=MAT_LINE)


def worn_fin_north(c, x, kind):
    """Back view: the toes and blades point away, behind the body; only the heels of the pockets show."""
    pocket = mask_of(q(x - 7, 100, x + 7, 100, x + 6, 110, x - 6, 110))
    c.part(pocket, shade(pocket, RUBBER, strength=0.12), line=WORN_LINE)
    if kind == "strap":
        strap = mask_of(q(x - 6, 106, x + 6, 106, x + 6, 109, x - 6, 109))
        c.part(strap, RUBBER * 0.8, line=MAT_LINE)


def worn(kind, plastic, rail, direction):
    c = Canvas()
    if direction == "south":
        for x in (54, 74):
            worn_fin_south(c, x, kind, plastic, rail)
    elif direction == "east":
        worn_fin_east(c, -3, kind, plastic, rail, far=True)
        worn_fin_east(c, 1, kind, plastic, rail)
    else:
        for x in (55, 73):
            worn_fin_north(c, x, kind)
    return c.image().resize((OUT, OUT), Image.LANCZOS)


# ---- Contact sheet -----------------------------------------------------------------------------------------------------------

def font(size):
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def tile(bg, cell_px, cells_w, cells_h):
    img = Image.new("RGBA", (cell_px * cells_w, cell_px * cells_h), bg)
    d = ImageDraw.Draw(img)
    darker = tuple(max(0, v - 10) for v in bg[:3]) + (255,)
    for i in range(cells_w):
        for j in range(cells_h):
            if (i + j) % 2:
                d.rectangle((i * cell_px, j * cell_px, (i + 1) * cell_px - 1, (j + 1) * cell_px - 1), fill=darker)
    return img


SAND = (214, 198, 158, 255)


def pawn(vanilla, direction, fins=None):
    """Vanilla Male body and head with an optional worn fins texture over the body: 128x160, head 29 px above the body
    (0.34 cells at 128 px per 1.5 cells). Reference composite for the sheet only."""
    root = vanilla / "Things/Pawn/Humanlike"
    body = Image.open(root / f"Bodies/Naked_Male_{direction}.png").convert("RGBA")
    head = Image.open(root / f"Heads/Male/Male_Average_Normal_{direction}.png").convert("RGBA")
    c = Image.new("RGBA", (128, 160), (0, 0, 0, 0))
    c.alpha_composite(body, (0, 32))
    if fins is not None:
        c.alpha_composite(fins, (0, 32))
    c.alpha_composite(head, (0, 3))
    return c


def contact_sheet(out_dir, vanilla, wooden):
    W, H = 1720, 1440
    title, label, small = font(30), font(20), font(16)
    sheet = Image.new("RGBA", (W, H), (36, 38, 42, 255))
    d = ImageDraw.Draw(sheet)
    d.text((30, 18), "Plastic fins: candidates (pick one)", font=title, fill=(240, 240, 240))
    d.text((30, 58), "Same paddle pair and framing as the approved wooden fins (100 px on a 128 canvas). Industrial tier: moulded "
                     "plastic blade with darker rails, dark rubber foot pocket.", font=small, fill=(200, 200, 200))
    d.text((30, 80), "Question: the wooden fins have no worn graphic by design. (a) Item only, matching the wooden fins: the worn "
                     "views below are dropped.", font=small, fill=(255, 220, 150))
    d.text((30, 102), "(b) Worn graphic: Part 2 draws every body type, and the wooden fins stay bare-footed unless they get a worn "
                      "graphic too.", font=small, fill=(255, 220, 150))
    d.text((30, 124), "While swimming, Waves draws the pawn face down at the waterline, so worn fins would only show on land.",
           font=small, fill=(200, 200, 200))

    headers = [(30, "Item at 1.5x (192 px)"), (260, "Game size, 64 px per cell: candidate, wooden fins*"),
               (700, "Worn on Male, 1.5x: south, east, north"), (1330, "Worn at game size (96 px)")]
    for x, t in headers:
        d.text((x, 160), t, font=small, fill=(220, 220, 220))

    rows = [(k, f"{k}  {name}", Image.open(out_dir / f"PlasticFins_{k}_{CANDIDATES[k][0]}.png").convert("RGBA"),
             [Image.open(out_dir / f"PlasticFins_{k}_{CANDIDATES[k][0]}_Male_{dr}.png").convert("RGBA") for dr in ("south", "east", "north")])
            for k, (_, name, _, _) in CANDIDATES.items()]
    rows.append(("*", "Wooden fins* (approved; no worn graphic, bare feet)", wooden, [None, None, None]))

    y = 190
    for key, name, item, worns in rows:
        d.text((30, y), name, font=label, fill=(255, 230, 160) if key != "*" else (190, 220, 255))
        top = y + 30
        bg = tile(SAND, 48, 4, 4)
        bg.alpha_composite(item.resize((192, 192), Image.LANCZOS))
        sheet.alpha_composite(bg, (30, top))
        # Game size: the 128 texture over one 64 px cell, candidate then wooden fins, one item per two cells.
        strip = tile(SAND, 64, 6, 3)
        strip.alpha_composite(item.resize((64, 64), Image.LANCZOS), (64, 64))
        strip.alpha_composite(wooden.resize((64, 64), Image.LANCZOS), (256, 64))
        sheet.alpha_composite(strip, (260, top))
        for i, (dr, f) in enumerate(zip(("south", "east", "north"), worns)):
            p = pawn(vanilla, dr, f)
            big = tile(SAND, 48, 4, 5).crop((0, 0, 192, 240))
            big.alpha_composite(p.resize((192, 240), Image.LANCZOS))
            sheet.alpha_composite(big, (700 + i * 205, top - 20))
            g = Image.new("RGBA", (96, 120), SAND)
            g.alpha_composite(p.resize((96, 120), Image.LANCZOS))
            sheet.alpha_composite(g, (1330 + i * 120, top + 40))
        y += 300
    sheet.convert("RGB").save(out_dir / "contact_sheet.png")


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, (kind, _, plastic, rail) in CANDIDATES.items():
        master = item_master(kind, plastic, rail)
        master.save(out_dir / f"PlasticFins_{key}_{kind}_master512.png")
        export(master).save(out_dir / f"PlasticFins_{key}_{kind}.png")
        for direction in ("south", "east", "north"):
            worn(kind, plastic, rail, direction).save(out_dir / f"PlasticFins_{key}_{kind}_Male_{direction}.png")
    if len(sys.argv) > 2:
        repo = Path(__file__).resolve().parents[2]
        wooden = Image.open(repo / "Textures/Things/Spearfishing/Apparel/WoodenFins.png").convert("RGBA")
        contact_sheet(out_dir, Path(sys.argv[2]), wooden)
