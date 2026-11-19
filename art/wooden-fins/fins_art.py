"""Procedural candidate designs for Spearfishing's wooden fins item sprite (128x128, Graphic_Single, 128 px per cell).

Each candidate is drawn at 4x (512 px) as a few broad shapes with smooth upper-left light, a black exterior contour and black
material lines, then reduced to 128 px. Usage: python fins_art.py <out_dir>
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 512          # master canvas
OUT = 128        # exported texture
LINE = 14        # exterior contour at master scale: 3.5 px at 128 = 1.75 px at 64 px per cell
MAT_LINE = 10    # material line at master scale: 2.5 px at 128

WOOD = np.array([150, 104, 62], float)       # mid wood
WOOD_DARK = np.array([112, 74, 42], float)
ROPE = np.array([196, 170, 118], float)      # plant-fibre cord
LEATHER = np.array([120, 84, 58], float)


def blade_outline(length, width_heel, width_tip, tip="straight", n=60):
    """Points of one blade, heel at y=0 pointing up (-y), centred on x=0."""
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        # Width eases from the heel pocket to a broad tip.
        w = width_heel + (width_tip - width_heel) * (t ** 0.8)
        y = -t * length
        left.append((-w / 2, y))
        right.append((w / 2, y))
    tipPts = []
    wt = width_tip / 2
    if tip == "straight":
        for i in range(21):
            a = i / 20
            tipPts.append((-wt + 2 * wt * a, -length - 10 * math.sin(math.pi * a)))
    elif tip == "fork":
        notch = length * 0.16
        tipPts = [(-wt, -length - notch * 0.35), (-wt * 0.15, -length + notch * 0.25), (0, -length + notch * 0.45),
                  (wt * 0.15, -length + notch * 0.25), (wt, -length - notch * 0.35)]
    elif tip == "leaf":
        for i in range(21):
            a = i / 20
            tipPts.append((-wt * (1 - a) + wt * a, -length - (wt * 1.6) * math.sin(math.pi * a)))
    heel = []
    hw = width_heel / 2
    for i in range(21):
        a = math.pi * i / 20
        heel.append((hw * math.cos(a), hw * 0.8 * math.sin(a)))
    return left + tipPts + right[::-1] + heel


def transform(pts, cx, cy, angle_deg):
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def mask_of(pts):
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m, float) / 255.0


def band_mask(cx, cy, angle_deg, half_len, half_w):
    pts = [(-half_len, -half_w), (half_len, -half_w), (half_len, half_w), (-half_len, half_w)]
    return mask_of(transform(pts, cx, cy, angle_deg))


def dilate(m, r):
    img = Image.fromarray((m * 255).astype(np.uint8))
    return np.array(img.filter(ImageFilter.MaxFilter(r * 2 + 1)), float) / 255.0


def shade(mask, base, axis_pts=None, ridge=0.18, grain=None):
    """Broad light from upper-left, an optional soft ridge along the blade axis, and a few soft grain streaks."""
    yy, xx = np.mgrid[0:S, 0:S].astype(float)
    ys, xs = np.nonzero(mask > 0.5)
    if len(xs) == 0:
        return np.zeros((S, S, 3))
    cx, cy = xs.mean(), ys.mean()
    span = max(np.ptp(xs), np.ptp(ys), 1)
    # -1 at the upper-left of the part, +1 at its lower-right.
    g = ((xx - cx) + (yy - cy)) / (span * 0.75)
    light = 1.0 - 0.22 * np.clip(g, -1, 1)
    if axis_pts is not None:
        line = Image.new("L", (S, S), 0)
        ImageDraw.Draw(line).line(axis_pts, fill=255, width=26)
        r = np.array(line.filter(ImageFilter.GaussianBlur(14)), float) / 255.0
        light += ridge * r
    if grain is not None:
        gl = Image.new("L", (S, S), 0)
        d = ImageDraw.Draw(gl)
        for seg in grain:
            d.line(seg, fill=255, width=5)
        gr = np.array(gl.filter(ImageFilter.GaussianBlur(3)), float) / 255.0
        light -= 0.10 * gr
    col = base[None, None, :] * light[..., None]
    return np.clip(col, 0, 255)


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
        a = (self.alpha * 255).astype(np.uint8)
        rgb = self.rgb.astype(np.uint8)
        return Image.fromarray(np.dstack([rgb, a]), "RGBA")


def fin(c, cx, cy, angle, length, wh, wt, tip, strap="rope", strap_at=0.22, grain=True):
    pts = transform(blade_outline(length, wh, wt, tip), cx, cy, angle)
    m = mask_of(pts)
    axis = transform([(0, -length * 0.1), (0, -length * 0.92)], cx, cy, angle)
    gr = None
    if grain:
        gr = [transform([(dx, -length * 0.35), (dx * 1.3, -length * 0.85)], cx, cy, angle) for dx in (-wt * 0.22, wt * 0.24)]
    c.part(m, shade(m, WOOD, axis, grain=gr))
    # Carved foot hollow at the heel: same wood, so a soft value change rather than a black line.
    hollow = Image.new("L", (S, S), 0)
    hy = -length * 0.15
    ell = [(wh * 0.30 * math.cos(2 * math.pi * k / 40), hy + length * 0.13 * math.sin(2 * math.pi * k / 40)) for k in range(40)]
    ImageDraw.Draw(hollow).polygon(transform(ell, cx, cy, angle), fill=255)
    h = np.array(hollow.filter(ImageFilter.GaussianBlur(7)), float) / 255.0 * m
    c.rgb = c.rgb * (1 - 0.30 * h[..., None])
    # Foot strap across the heel pocket.
    sy = -length * strap_at
    bm = band_mask(*transform([(0, sy)], cx, cy, angle)[0], angle, wh * 0.62, 16) * m
    bm = np.clip(bm, 0, 1)
    color = ROPE if strap == "rope" else LEATHER
    if strap == "rope":
        # Twist: soft diagonal stripes on the cord.
        yy, xx = np.mgrid[0:S, 0:S].astype(float)
        stripes = 0.9 + 0.1 * np.sin((xx + yy) / 6.0)
        col = color[None, None, :] * stripes[..., None]
    else:
        col = shade(bm, color)
    c.part(bm, col, line=MAT_LINE)
    return m


def candidate_a():
    """Paddle pair: two broad, square-tipped blades side by side, splayed, cord straps."""
    c = Canvas()
    fin(c, 196, 430, -9, 330, 104, 150, "straight")
    fin(c, 318, 430, 9, 330, 104, 150, "straight")
    return c.image()


def candidate_b():
    """Fish-tail pair: forked tips that echo a fish tail; one fin lies behind and above the other."""
    c = Canvas()
    fin(c, 300, 400, 14, 300, 96, 168, "fork")
    fin(c, 214, 448, -6, 300, 96, 168, "fork")
    return c.image()


def candidate_c():
    """Lashed leaf blades: two long leaf-shaped blades crossed and tied together with cord, as they hang in storage."""
    c = Canvas()
    m1 = fin(c, 150, 440, 28, 360, 82, 124, "leaf")
    m2 = fin(c, 362, 440, -28, 360, 82, 124, "leaf")
    # Cord binding where the blades cross.
    cx, cy = 256, 290
    for dy in (-12, 12):
        bm = band_mask(cx, cy + dy, 0, 44, 8) * np.clip(m1 + m2, 0, 1)
        yy, xx = np.mgrid[0:S, 0:S].astype(float)
        col = ROPE[None, None, :] * (0.9 + 0.1 * np.sin((xx - yy) / 5.0))[..., None]
        c.part(np.clip(bm, 0, 1), col, line=MAT_LINE)
    return c.image()


def export(master, fill=100):
    """Fit the alpha bounds into `fill` px of the 128 canvas, centred, uniform scale (approved: 100)."""
    box = master.getbbox()
    crop = master.crop(box)
    scale = fill / max(crop.size)
    size = (max(1, round(crop.size[0] * scale)), max(1, round(crop.size[1] * scale)))
    small = crop.resize(size, Image.LANCZOS)
    out = Image.new("RGBA", (OUT, OUT), (0, 0, 0, 0))
    out.alpha_composite(small, ((OUT - size[0]) // 2, (OUT - size[1]) // 2))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, fn in [("A-paddle-pair", candidate_a), ("B-fish-tail-pair", candidate_b), ("C-lashed-leaf-blades", candidate_c)]:
        master = fn()
        master.save(out_dir / f"WoodenFins_{name}_master512.png")
        export(master).save(out_dir / f"WoodenFins_{name}_128.png")
        print(name, master.getbbox())
