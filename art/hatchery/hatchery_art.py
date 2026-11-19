"""Procedural candidate designs for Spearfishing's hatchery building and its fry batch item (fish recovery ticket 04, part 1).

Same method as the approved buoys and fins (art/wooden-buoy/buoy_art.py): a few broad shapes with smooth upper-left light, a
black exterior contour and black material lines, drawn at 4x and reduced. The buoy helpers are fixed to a square 512 canvas, so
this script carries its own copies that take any canvas size.

- Hatchery: a powered land building holding fish-rearing tanks. South view only (Graphic_Single, rotatable false); north and
  east views are derived after the pick if the chosen footprint needs them. Exported at 128 px per cell, so a 2x2 is 256x256
  and a 3x2 is 384x256; the master is 4x that. The contour aims at vanilla's building figure (2-3 px at 64 px per cell, so
  4-6 px at 128), not at the mod's thinner item outline. The feed inlet is a small lid, so it fits a hopper-fed or a
  self-storing building alike (part 2 decides).
- Fry batch: an item, 128x128, Graphic_Single, drawSize 1, exported with the buoys' recipe (export(fill=100)).

Procedural only: no reference images, vanilla, Waves, DLC or third-party art go into the masters or exports. The contact sheet
shows a vanilla pawn dump from work/vanilla-ref for scale only, when it is present.

Usage: python -I hatchery_art.py <out_dir> [sheet_path|-] [refined_sheet_path]
  Writes Hatchery{A,B,C,C2}_master.png and Hatchery{A,B,C,C2}.png, FryBatch{A,B,C,A2}_master512.png and
  FryBatch{A,B,C,A2}.png to out_dir; with sheet_path, the candidates' contact sheet ("-" skips it); with
  refined_sheet_path, the before/after sheet for the author's picks (C2 refines C, A2 refines A). It never writes to
  Textures/.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

M = 4            # master pixels per exported pixel
CELL = 128 * M   # master pixels per cell
LINE = 18        # exterior contour width at master scale: 4.5 px at 128 px per cell, 2.25 px at 64
MAT_LINE = 12    # material line width at master scale: 3 px at 128 px per cell, 1.5 px at 64

STEEL = np.array([182, 188, 192], float)     # the steel pole spear's steel family
FRAME = np.array([118, 124, 130], float)     # darker steel for the base frame
SLATE = np.array([84, 100, 116], float)      # the foam buoy's webbing slate, for housings
WATER = np.array([62, 136, 152], float)      # tank water, saturation 0.59
FRY = np.array([30, 70, 84], float)          # young fish seen through the water
LIGHT = np.array([110, 178, 96], float)      # a dim green power light
FEED = np.array([176, 150, 96], float)       # the feed lid, a hay-coloured tin
PLASTIC = np.array([196, 120, 70], float)    # the foam buoy's orange, a little darker, for the tub
BAG = np.array([170, 204, 212], float)       # clear bag over water
FRAME_DARK = np.array([82, 88, 96], float)   # refined: a darker steel frame, so the bright tank rim stands off it
ACCENT = np.array([203, 111, 63], float)     # refined: the foam buoy's orange (its median), as on the band speargun
WATER_TOP = np.array([112, 176, 188], float) # refined pail: water seen from above, lighter than the tank's deep water


# ---- Drawing helpers (the buoy helpers, for any canvas size) ------------------------------------------------------------------

class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3))
        self.alpha = np.zeros((h, w))

    def mask(self, draw):
        m = Image.new("L", (self.w, self.h), 0)
        draw(ImageDraw.Draw(m))
        return np.array(m, float) / 255.0

    def poly(self, pts):
        return self.mask(lambda d: d.polygon(pts, fill=255))

    def ellipse(self, cx, cy, rx, ry):
        return self.mask(lambda d: d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255))

    def rrect(self, x0, y0, x1, y1, r):
        return self.mask(lambda d: d.rounded_rectangle((x0, y0, x1, y1), r, fill=255))

    def stroke(self, pts, width):
        def draw(d):
            d.line(pts, fill=255, width=width, joint="curve")
            for x, y in (pts[0], pts[-1]):
                d.ellipse((x - width / 2, y - width / 2, x + width / 2, y + width / 2), fill=255)
        return self.mask(draw)

    def shade(self, mask, base, strength=0.28, highlight=0.10, invert=False):
        """Rounded body lit from the upper left; invert for a recessed surface such as water inside a rim."""
        yy, xx = np.mgrid[0:self.h, 0:self.w].astype(float)
        ys, xs = np.nonzero(mask > 0.5)
        if len(xs) == 0:
            return np.zeros((self.h, self.w, 3))
        cx, cy = xs.mean(), ys.mean()
        rx, ry = max(np.ptp(xs) / 2, 1), max(np.ptp(ys) / 2, 1)
        u, v = (xx - cx) / rx, (yy - cy) / ry
        g = np.clip((u + v) / 1.6, -1, 1)
        light = 1.0 + strength * g if invert else 1.0 - strength * g
        hu, hv = (0.30, 0.34) if invert else (-0.38, -0.42)
        light += highlight * np.exp(-(((u - hu) ** 2 + (v - hv) ** 2) / 0.08))
        return np.clip(base[None, None, :] * light[..., None], 0, 255)

    def part(self, mask, color, line=LINE):
        """Paint a part over what is there: a black contour ring outside its fill, then its fill."""
        if line:
            r = line
            outer = np.clip(r + 1 - ndimage.distance_transform_edt(mask < 0.5), 0, 1)
            outer = np.maximum(outer, mask)
        else:
            outer = mask
        ring = np.clip(outer - mask, 0, 1)
        self.rgb = self.rgb * (1 - ring[..., None])
        self.alpha = np.maximum(self.alpha, outer)
        self.rgb = self.rgb * (1 - mask[..., None]) + color * mask[..., None]

    def tint(self, mask, color):
        """Paint inside the existing fill with no line: fry under the water surface."""
        self.rgb = self.rgb * (1 - mask[..., None]) + color * mask[..., None]

    def image(self):
        a = (np.clip(self.alpha, 0, 1) * 255).astype(np.uint8)
        return Image.fromarray(np.dstack([self.rgb.astype(np.uint8), a]), "RGBA")


def clip(m, *outside):
    for o in outside:
        m = m * (1 - o)
    return np.clip(m, 0, 1)


def fry_shapes(c, spots, size):
    """Small fish silhouettes under the water: an oval body and a forked tail, no outline."""
    m = np.zeros((c.h, c.w))
    for x, y, ang in spots:
        a = math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)

        def rot(px, py):
            return (x + px * ca - py * sa, y + px * sa + py * ca)
        body = [rot(size * 0.5 * math.cos(t), size * 0.2 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40)]
        tail = [rot(-size * 0.35, 0), rot(-size * 0.72, -size * 0.2), rot(-size * 0.62, 0), rot(-size * 0.72, size * 0.2)]
        m = np.maximum(m, c.poly(body))
        m = np.maximum(m, c.poly(tail))
    return m


def water_with_fry(c, water, spots, size, color=WATER):
    c.part(water, c.shade(water, color, strength=0.22, highlight=0.12, invert=True), line=MAT_LINE)
    c.tint(clip(fry_shapes(c, spots, size) * water), FRY)


def light(c, x, y, r=26):
    m = c.ellipse(x, y, r, r)
    c.part(m, c.shade(m, LIGHT, strength=0.2, highlight=0.25), line=MAT_LINE)


# ---- Hatchery candidates --------------------------------------------------------------------------------------------------------

def hatchery_a():
    """Four round tanks (2x2): one round tank per cell on a steel frame, piped to a small pump in the middle."""
    S = 2 * CELL
    c = Canvas(S, S)
    plate = c.rrect(40, 70, S - 40, S - 30, 70)
    c.part(plate, c.shade(plate, FRAME, strength=0.18))
    centres = [(300, 320), (S - 300, 320), (300, S - 270), (S - 300, S - 270)]
    hub = c.rrect(S / 2 - 80, S / 2 - 60, S / 2 + 80, S / 2 + 90, 24)
    for x, y in centres:
        pipe = clip(c.stroke([(x, y), (S / 2, S / 2 + 15)], 54), hub)
        c.part(pipe, c.shade(pipe, STEEL, strength=0.2), line=MAT_LINE)
    for i, (x, y) in enumerate(centres):
        rim = c.ellipse(x, y, 214, 214)
        c.part(rim, c.shade(rim, STEEL))
        water = c.ellipse(x + 6, y + 8, 166, 166)
        spots = [(x - 50, y - 30, 20 + 70 * i), (x + 60, y + 50, 200 + 40 * i)]
        water_with_fry(c, water, spots, 92)
    c.part(hub, c.shade(hub, SLATE, strength=0.22))
    light(c, S / 2, S / 2 + 15)
    return c.image()


def hatchery_b():
    """Raceway rack (3x2): three long troughs side by side under a header pipe, with a pump and a feed lid on top."""
    W, H = 3 * CELL, 2 * CELL
    c = Canvas(W, H)
    plate = c.rrect(40, 70, W - 40, H - 30, 60)
    c.part(plate, c.shade(plate, FRAME, strength=0.18))
    xs = [110, 110 + 452, 110 + 904]
    for i, x0 in enumerate(xs):
        rim = c.rrect(x0, 230, x0 + 412, H - 80, 46)
        c.part(rim, c.shade(rim, STEEL))
        water = c.rrect(x0 + 42, 272, x0 + 370, H - 122, 26)
        spots = [(x0 + 150, 430, 80 + 30 * i), (x0 + 260, 640, 260 - 40 * i), (x0 + 140, 780, 100)]
        water_with_fry(c, water, spots, 96)
    header = c.rrect(80, 120, W - 80, 186, 30)
    c.part(header, c.shade(header, STEEL, strength=0.2), line=MAT_LINE)
    pump = c.rrect(W / 2 - 150, 92, W / 2 + 150, 236, 26)
    c.part(pump, c.shade(pump, SLATE, strength=0.22))
    light(c, W / 2 + 96, 164)
    lid = c.ellipse(W / 2 - 50, 164, 58, 46)
    c.part(lid, c.shade(lid, FEED, strength=0.22), line=MAT_LINE)
    return c.image()


def hatchery_c():
    """Pond tank (2x2): one large round tank with an aerator bridge to a central feeder, and a pump box in one corner."""
    S = 2 * CELL
    c = Canvas(S, S)
    plate = c.rrect(40, 70, S - 40, S - 30, 90)
    c.part(plate, c.shade(plate, FRAME, strength=0.18))
    cx, cy = S / 2, S / 2 + 20
    pump = c.rrect(S - 250, S - 230, S - 80, S - 70, 26)
    c.part(pump, c.shade(pump, SLATE, strength=0.22))
    light(c, S - 165, S - 150)
    rim = clip(c.ellipse(cx - 30, cy - 30, 420, 420), pump)
    c.part(rim, c.shade(rim, STEEL))
    water = clip(c.ellipse(cx - 24, cy - 22, 362, 362), pump)
    spots = [(cx - 200, cy - 120, 30), (cx + 150, cy - 170, 160), (cx - 120, cy + 190, 300), (cx + 190, cy + 120, 220)]
    water_with_fry(c, water, spots, 104)
    bridge = clip(c.stroke([(cx - 30 - 400, cy - 30), (cx - 30 + 400, cy - 30)], 58))
    c.part(bridge, c.shade(bridge, STEEL, strength=0.2), line=MAT_LINE)
    hub = c.ellipse(cx - 30, cy - 30, 96, 96)
    c.part(hub, c.shade(hub, SLATE, strength=0.25))
    lid = c.ellipse(cx - 30, cy - 30, 52, 52)
    c.part(lid, c.shade(lid, FEED, strength=0.22), line=MAT_LINE)
    return c.image()


HATCHERIES = {
    "A": ("Four round tanks", "2x2", hatchery_a),
    "B": ("Raceway rack", "3x2", hatchery_b),
    "C": ("Pond tank", "2x2", hatchery_c),
}


def hatchery_c2():
    """Refined pond tank (2x2), after the author picked C: the tank sits on the plate's centre, the aerator bridge runs
    straight across it to two mirrored pump/power boxes at 3 and 9 o'clock, so nothing pulls the eye to a corner. Darker
    frame, smaller fry, a larger feeder with an orange collar (the foam buoy's orange) as the one accent."""
    S = 2 * CELL
    c = Canvas(S, S)
    plate = c.rrect(40, 70, S - 40, S - 30, 90)
    c.part(plate, c.shade(plate, FRAME_DARK, strength=0.18))
    cx, cy = S / 2, (70 + S - 30) / 2       # the plate's centre, so the tank is centred on what the eye sees
    bw, bh = 96, 120                        # box half width and half height: 48x60 px at 128 px per cell
    boxes = [c.rrect(x - bw, cy - bh, x + bw, cy + bh, 28) for x in (40 + bw + 14, S - 40 - bw - 14)]
    both = np.maximum(*boxes)
    rim = clip(c.ellipse(cx, cy, 384, 384), both)
    c.part(rim, c.shade(rim, STEEL))
    water = clip(c.ellipse(cx, cy, 326, 326), both)
    ring = 236
    spots = [(cx + ring * math.cos(math.radians(a)), cy + ring * math.sin(math.radians(a)), a + 100)
             for a in (-70, -10, 55, 115, 170, 230)]
    water_with_fry(c, water, spots, 62)
    bridge = clip(c.stroke([(cx - 330, cy), (cx + 330, cy)], 60), both)
    c.part(bridge, c.shade(bridge, STEEL, strength=0.2), line=MAT_LINE)
    hub = c.ellipse(cx, cy, 138, 138)
    c.part(hub, c.shade(hub, SLATE, strength=0.25))
    collar = c.ellipse(cx, cy, 104, 104)
    c.part(collar, c.shade(collar, ACCENT, strength=0.22), line=MAT_LINE)
    lid = c.ellipse(cx, cy, 76, 76)
    c.part(lid, c.shade(lid, FEED, strength=0.22), line=MAT_LINE)
    for box, x in zip(boxes, (40 + bw + 14, S - 40 - bw - 14)):
        c.part(box, c.shade(box, SLATE, strength=0.22))
        light(c, x, cy - 50, r=34)
        vent = c.rrect(x - 50, cy + 30, x + 50, cy + 52, 10)
        c.part(vent, np.zeros((S, S, 3)) + 30, line=0)
        vent = c.rrect(x - 50, cy + 72, x + 50, cy + 94, 10)
        c.part(vent, np.zeros((S, S, 3)) + 30, line=0)
    return c.image()


REFINED_HATCHERIES = {"C2": ("Pond tank, refined", "2x2", hatchery_c2)}


# ---- Fry batch candidates (512 master, exported to 128) ----------------------------------------------------------------------

def fry_a():
    """Fry pail: a steel pail of water seen from above at an angle, two fry in it, with a wire handle."""
    c = Canvas(512, 512)
    body = np.maximum(np.maximum(c.poly([(86, 210), (426, 210), (390, 400), (122, 400)]), c.ellipse(256, 400, 134, 56)),
                      c.ellipse(256, 210, 170, 70))
    handle = clip(c.stroke([(92, 214), (120, 120), (256, 78), (392, 120), (420, 214)], 18), body)
    c.part(handle, c.shade(handle, FRAME, strength=0.2), line=MAT_LINE)
    c.part(body, c.shade(body, STEEL, strength=0.30))
    water = c.ellipse(256, 214, 140, 52)
    water_with_fry(c, water, [(214, 206, 10), (300, 222, 190)], 70)
    return c.image()


def fry_b():
    """Fry bag: a knotted clear bag, two thirds water, with two fry, tied with cord."""
    c = Canvas(512, 512)
    pts = []
    for k in range(100):
        t = 2 * math.pi * k / 100
        x = 150 * math.sin(t)
        y = -math.cos(t)
        r = 1.0 if y > -0.2 else 1.0 - 0.75 * ((-y - 0.2) / 0.8) ** 1.2
        pts.append((256 + x * r, 300 + 170 * y))
    bag = c.poly(pts)
    knot = c.ellipse(256, 128, 34, 26)
    ears = np.maximum(c.poly([(256, 128), (196, 64), (226, 54)]), c.poly([(256, 128), (316, 64), (286, 54)]))
    c.part(clip(ears, knot), c.shade(ears, BAG, strength=0.15), line=MAT_LINE)
    c.part(bag, c.shade(bag, BAG, strength=0.18, highlight=0.08))
    water = clip(bag * (np.mgrid[0:512, 0:512][0] > 236))
    water_with_fry(c, water, [(220, 330, 15), (300, 392, 200)], 74)
    c.part(knot, c.shade(knot, FEED, strength=0.2), line=MAT_LINE)
    return c.image()


def fry_c():
    """Fry tub: a low orange carry tub, open on top with water and fry, a hand slot at each end."""
    c = Canvas(512, 512)
    tub = c.rrect(48, 140, 464, 392, 54)
    c.part(tub, c.shade(tub, PLASTIC, strength=0.28))
    front = c.rrect(48, 330, 464, 392, 40) * tub
    c.part(clip(front), c.shade(tub, PLASTIC * 0.80, strength=0.18), line=MAT_LINE)
    water = c.rrect(96, 178, 416, 316, 30)
    water_with_fry(c, water, [(200, 230, 5), (310, 262, 170), (250, 290, 350)], 70)
    for x in (70, 442):
        slot = c.rrect(x - 12, 210, x + 12, 290, 10)
        c.part(slot, np.zeros((512, 512, 3)) + 20, line=0)
    return c.image()


FRY_BATCHES = {"A": ("Fry pail", fry_a), "B": ("Fry bag", fry_b), "C": ("Fry tub", fry_c)}


def fry_a2():
    """Refined fry pail, after the author picked A: the same steel pail and wire handle, a lighter water surface seen from
    above, and five tiny fry instead of two fish. Exported smaller (REFINED_FILL) so it sits inside one cell."""
    c = Canvas(512, 512)
    body = np.maximum(np.maximum(c.poly([(86, 210), (426, 210), (390, 400), (122, 400)]), c.ellipse(256, 400, 134, 56)),
                      c.ellipse(256, 210, 170, 70))
    handle = clip(c.stroke([(92, 214), (120, 120), (256, 78), (392, 120), (420, 214)], 18), body)
    c.part(handle, c.shade(handle, FRAME, strength=0.2), line=MAT_LINE)
    c.part(body, c.shade(body, STEEL, strength=0.30))
    water = c.ellipse(256, 214, 140, 52)
    spots = [(196, 200, 15), (250, 230, 190), (300, 196, 170), (330, 226, 10), (226, 186, 200)]
    water_with_fry(c, water, spots, 40, color=WATER_TOP)
    return c.image()


REFINED_FRY_BATCHES = {"A2": ("Fry pail, refined", fry_a2)}
REFINED_FILL = 86   # was 100: the pail now stands no taller than the raw fish stack at game size


# ---- Export ---------------------------------------------------------------------------------------------------------------------

def export_building(master):
    """Uniform 1/M reduction of the whole footprint canvas, so the art keeps its place on the cells."""
    return master.resize((master.width // M, master.height // M), Image.LANCZOS)


def export_item(master, fill=100):
    """The buoys' recipe: fit the alpha bounds into `fill` px of a 128 canvas, centred, uniform Lanczos scale."""
    crop = master.crop(master.getbbox())
    scale = fill / max(crop.size)
    size = (max(1, round(crop.size[0] * scale)), max(1, round(crop.size[1] * scale)))
    out = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    out.alpha_composite(crop.resize(size, Image.LANCZOS), ((128 - size[0]) // 2, (128 - size[1]) // 2))
    return out


# ---- Measurements reported on the sheet (foam_buoy_art.py's) -------------------------------------------------------------------

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


# ---- Contact sheet --------------------------------------------------------------------------------------------------------------

SOIL, CONCRETE, SAND = (118, 98, 72, 255), (150, 150, 146, 255), (214, 198, 158, 255)


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
    shade = tuple(max(0, v - 10) for v in bg[:3]) + (255,)
    for i in range(cells_w):
        for j in range(cells_h):
            if (i + j) % 2:
                d.rectangle((i * cell_px, j * cell_px, (i + 1) * cell_px - 1, (j + 1) * cell_px - 1), fill=shade)
    return img


def scaled(tex, factor):
    return tex.resize((max(1, round(tex.width * factor)), max(1, round(tex.height * factor))), Image.LANCZOS)


def contact_sheet(out_dir, sheet_path):
    out_dir = Path(out_dir)
    halls = [(k, n, fp, Image.open(out_dir / f"Hatchery{k}.png").convert("RGBA")) for k, (n, fp, _) in HATCHERIES.items()]
    frys = [(k, n, Image.open(out_dir / f"FryBatch{k}.png").convert("RGBA")) for k, (n, _) in FRY_BATCHES.items()]
    raw_fish = Image.open(REPO / "Textures/Things/Spearfishing/Item/RawFish/RawFish_c.png").convert("RGBA")
    buoy = Image.open(REPO / "Textures/Things/Spearfishing/Apparel/FoamBuoy.png").convert("RGBA")
    pawn_path = Path("E:/Coding/Rimworld/Spearfishing/work/vanilla-ref/composite_Male.png")
    pawn = Image.open(pawn_path).convert("RGBA") if pawn_path.exists() else None

    W, H = 1720, 1780
    title, label, small = font(30), font(20), font(16)
    sheet = Image.new("RGBA", (W, H), (36, 38, 42, 255))
    d = ImageDraw.Draw(sheet)
    d.text((30, 20), "Hatchery and fry batch: candidates (pick one of each)", font=title, fill=(240, 240, 240))
    d.text((30, 60), "Fish recovery ticket 04, part 1. Procedural, fixed colour, south view only (rotation views come after the "
           "pick). * = approved Spearfishing art.", font=small, fill=(200, 200, 200))
    d.text((30, 80), "No vanilla building on the sheet: no extracted vanilla art source was at hand, so that comparison is "
           "pending.", font=small, fill=(200, 200, 200))

    # Row 1: the hatcheries at their texture size, 128 px per cell, on concrete.
    y = 100
    d.text((30, y), "Hatchery, 128 px per cell (the texture's own size, zoomed in), on concrete", font=label,
           fill=(240, 240, 240))
    x = 30
    for key, name, fp, tex in halls:
        cw, ch = tex.width // 128, tex.height // 128
        bg = tile(CONCRETE, 128, cw, ch)
        bg.alpha_composite(tex)
        sheet.alpha_composite(bg, (x, y + 64))
        d.text((x, y + 34), f"{key}  {name} ({fp})", font=label, fill=(255, 230, 160))
        o = outline_px(tex)
        d.text((x, y + 64 + tex.height + 6), f"outline {o:.1f} px at 128 px/cell, {o / 2:.1f} at 64",
               font=small, fill=(200, 200, 200))
        d.text((x, y + 64 + tex.height + 26), f"saturation p90 {sat_p90(tex):.2f}", font=small, fill=(200, 200, 200))
        x += tex.width + 60

    # Row 2: game size, normal zoom (64 px per cell), on soil, with a vanilla pawn for scale.
    y = 470
    d.text((30, y), "Game size, normal zoom (64 px per cell), on soil" + (", with a vanilla pawn for scale (sheet only)" if pawn
           else ""), font=label, fill=(240, 240, 240))
    strip = tile(SOIL, 64, 22, 3)
    x = 64
    for key, name, fp, tex in halls:
        g = scaled(tex, 0.5)
        strip.alpha_composite(g, (x, 32))
        if pawn is not None:
            p = scaled(pawn, 64 * 1.5 / 128)  # a humanlike body is a 128 px texture drawn over 1.5 cells
            strip.alpha_composite(p, (x + g.width - 8, 192 - p.height - 4))
        ImageDraw.Draw(strip).text((x + g.width // 2, 2), key, font=small, fill=(250, 240, 210), anchor="mt")
        x += g.width + 3 * 64
    sheet.alpha_composite(strip.crop((0, 0, min(strip.width, W - 60), strip.height)), (30, y + 32))

    # Row 3: fry batches at 1.5x on sand and soil, beside the approved raw fish and foam buoy.
    y = 740
    d.text((30, y), "Fry batch item, 1.5x (192 px per cell), on sand and on soil, beside raw fish* and the foam buoy*",
           font=label, fill=(240, 240, 240))
    items = [(f"{k}  {n}", t, 128) for k, n, t in frys] + [("raw fish* (stack of 4)", raw_fish, 64), ("foam buoy*", buoy, 128)]
    for row, bg in enumerate((SAND, SOIL)):
        s = tile(bg, 192, 9, 1)
        for i, (_, t, ppc) in enumerate(items):
            g = scaled(t, 192 / ppc)
            s.alpha_composite(g, (i * 336 + (192 - g.width) // 2, (192 - g.height) // 2))
        sheet.alpha_composite(s.crop((0, 0, min(s.width, W - 60), 192)), (30, y + 32 + row * 200))
    for i, (name, _, _) in enumerate(items):
        d.text((30 + i * 336 + 96, y + 32 + 400), name, font=small, fill=(220, 220, 220), anchor="mt")
    for i, (key, name, tex) in enumerate(frys):
        d.text((30 + i * 336 + 96, y + 32 + 422), f"sat p90 {sat_p90(tex):.2f}", font=small, fill=(170, 170, 170),
               anchor="mt")

    # Row 4: fry batches at game size beside the same, on sand and soil.
    y = 1240
    d.text((30, y), "Fry batch item, game size (64 px per cell), on sand and on soil", font=label, fill=(240, 240, 240))
    for row, bg in enumerate((SAND, SOIL)):
        s = tile(bg, 64, 16, 1)
        for i, (_, t, ppc) in enumerate(items):
            g = scaled(t, 64 / ppc)
            s.alpha_composite(g, (64 + i * 192 + (64 - g.width) // 2, (64 - g.height) // 2))
        sheet.alpha_composite(s, (30, y + 32 + row * 72))
    for i, (name, _, _) in enumerate(items):
        d.text((30 + 64 + i * 192 + 32, y + 32 + 148), name.split("  ")[0], font=small, fill=(220, 220, 220), anchor="mt")

    # Row 5: a hatchery at game size with each fry batch beside it, as it will sit when a batch is ready.
    y = 1460
    d.text((30, y), "Game size: each hatchery with each fry batch on the cell beside it", font=label, fill=(240, 240, 240))
    s = tile(CONCRETE, 64, 24, 4)
    x = 32
    for key, name, fp, tex in halls:
        g = scaled(tex, 0.5)
        s.alpha_composite(g, (x, 64))
        for j, (fk, _, ft) in enumerate(frys):
            f = scaled(ft, 0.5)
            s.alpha_composite(f, (x + g.width + j * 64, 64 + (64 - f.height) // 2 if j % 2 == 0 else 128))
        ImageDraw.Draw(s).text((x + g.width // 2, 20), f"{key} + fry A B C", font=small, fill=(30, 30, 30), anchor="mt")
        x += g.width + 4 * 64
    sheet.alpha_composite(s.crop((0, 0, min(s.width, W - 60), s.height)), (30, y + 32))

    sheet_path = Path(sheet_path)
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(sheet_path)


def arrow(d, x, y, length=50):
    d.line((x, y, x + length, y), fill=(240, 200, 120), width=5)
    d.polygon([(x + length + 14, y), (x + length - 4, y - 12), (x + length - 4, y + 12)], fill=(240, 200, 120))


def refined_sheet(out_dir, sheet_path):
    """Before and after for the author's picks: old C and A beside refined C2 and A2, at 128 px per cell and at game size."""
    out_dir = Path(out_dir)
    old_c, new_c = (Image.open(out_dir / f"Hatchery{k}.png").convert("RGBA") for k in ("C", "C2"))
    old_a, new_a = (Image.open(out_dir / f"FryBatch{k}.png").convert("RGBA") for k in ("A", "A2"))
    raw_fish = Image.open(REPO / "Textures/Things/Spearfishing/Item/RawFish/RawFish_c.png").convert("RGBA")
    buoy = Image.open(REPO / "Textures/Things/Spearfishing/Apparel/FoamBuoy.png").convert("RGBA")
    pawn_path = Path("E:/Coding/Rimworld/Spearfishing/work/vanilla-ref/composite_Male.png")
    pawn = Image.open(pawn_path).convert("RGBA") if pawn_path.exists() else None

    W, H = 1500, 1720
    title, label, small = font(30), font(20), font(16)
    sheet = Image.new("RGBA", (W, H), (36, 38, 42, 255))
    d = ImageDraw.Draw(sheet)
    d.text((30, 20), "Hatchery C and fry pail A: before and after refinement", font=title, fill=(240, 240, 240))
    d.text((30, 60), "Fish recovery ticket 04, part 1. Picked by the author; refined versions await approval. "
           "* = approved Spearfishing art. Pawn is a vanilla dump, for scale only.", font=small, fill=(200, 200, 200))

    # Row 1: 128 px per cell.
    y = 100
    d.text((30, y), "128 px per cell (the textures' own size)", font=label, fill=(240, 240, 240))
    x = 30
    for name, tex, bg, cells in (("C  before", old_c, CONCRETE, 2), ("C2  after", new_c, CONCRETE, 2),
                                 ("A  before", old_a, SAND, 1), ("A2  after", new_a, SAND, 1)):
        t = tile(bg, 128, cells, cells)
        t.alpha_composite(tex)
        sheet.alpha_composite(t, (x, y + 64))
        d.text((x, y + 36), name, font=label, fill=(255, 230, 160))
        o = outline_px(tex)
        d.text((x, y + 64 + t.height + 6), f"outline {o:.1f} px at 128, {o / 2:.1f} at 64", font=small,
               fill=(200, 200, 200))
        d.text((x, y + 64 + t.height + 26), f"saturation p90 {sat_p90(tex):.2f}", font=small, fill=(200, 200, 200))
        if name.startswith(("C ", "A ")):
            arrow(d, x + t.width + 14, y + 64 + t.height // 2)
            x += t.width + 100
        else:
            x += t.width + 90

    # Row 2: game size (64 px per cell) with pawn, raw fish and foam buoy; then the same strip at 2x, nearest neighbour.
    def game_strip(bg):
        s = tile(bg, 64, 17, 3)
        sd = ImageDraw.Draw(s)
        x = 32
        for key, tex in (("C", old_c), ("C2", new_c)):
            g = scaled(tex, 0.5)
            s.alpha_composite(g, (x, 32))
            if pawn is not None:
                p = scaled(pawn, 64 * 1.5 / 128)  # a humanlike body is a 128 px texture drawn over 1.5 cells
                s.alpha_composite(p, (x + g.width - 8, 192 - p.height - 4))
            sd.text((x + g.width // 2, 2), key, font=small, fill=(250, 240, 210), anchor="mt")
            x += g.width + 2 * 64
        x = 9 * 64
        for key, tex, ppc in (("A", old_a, 128), ("A2", new_a, 128), ("fish*", raw_fish, 64), ("buoy*", buoy, 128)):
            g = scaled(tex, 64 / ppc)
            s.alpha_composite(g, (x + (64 - g.width) // 2, 64 + (64 - g.height) // 2))
            sd.text((x + 32, 40), key, font=small, fill=(250, 240, 210), anchor="mt")
            x += 2 * 64
        return s

    y = 486
    d.text((30, y), "Game size, normal zoom (64 px per cell), on soil and on concrete", font=label, fill=(240, 240, 240))
    soil = game_strip(SOIL)
    sheet.alpha_composite(soil, (30, y + 32))
    sheet.alpha_composite(game_strip(CONCRETE), (30, y + 32 + 200))
    y = 936
    d.text((30, y), "The soil strip enlarged 2x with nearest neighbour, to show its game-size pixels", font=label,
           fill=(240, 240, 240))
    big = soil.resize((soil.width * 2, soil.height * 2), Image.NEAREST)
    sheet.alpha_composite(big.crop((0, 0, 9 * 128, 384)), (30, y + 32))
    sheet.alpha_composite(big.crop((9 * 128, 64, big.width, 272)), (30, y + 32 + 400))
    d.text((30, H - 100), "Refined C2: tank centred on the plate; mirrored pump/power boxes at 3 and 9 o'clock on the "
           "bridge ends; darker frame; larger feeder with an orange collar; smaller fry.", font=small, fill=(200, 200, 200))
    d.text((30, H - 76), f"Refined A2: exported at fill {REFINED_FILL} (was 100); lighter water surface; five tiny fry; "
           "same steel pail and wire handle.", font=small, fill=(200, 200, 200))

    sheet_path = Path(sheet_path)
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(sheet_path)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for key, (_, _, make) in {**HATCHERIES, **REFINED_HATCHERIES}.items():
        master = make()
        master.save(out / f"Hatchery{key}_master.png")
        export_building(master).save(out / f"Hatchery{key}.png")
    for key, (_, make) in FRY_BATCHES.items():
        master = make()
        master.save(out / f"FryBatch{key}_master512.png")
        export_item(master).save(out / f"FryBatch{key}.png")
    for key, (_, make) in REFINED_FRY_BATCHES.items():
        master = make()
        master.save(out / f"FryBatch{key}_master512.png")
        export_item(master, fill=REFINED_FILL).save(out / f"FryBatch{key}.png")
    if len(sys.argv) > 2 and sys.argv[2] != "-":
        contact_sheet(out, sys.argv[2])
    if len(sys.argv) > 3:
        refined_sheet(out, sys.argv[3])
