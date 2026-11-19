"""Raw fish textures for Spearfishing (approved master, see APPROVAL.md). Procedural PIL drawing: a snapper-shaped fish in
blue-grey, in three stack sizes for Graphic_StackCount.
Usage: python -I raw_fish_art.py <out_dir>. Writes RawFish_a.png, RawFish_b.png and RawFish_c.png (64x64)."""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

CAND = Path(sys.argv[1])
CAND.mkdir(parents=True, exist_ok=True)
SS = 8  # supersampling factor
INK = (12, 10, 10, 255)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def solid(mask_img):
    return mask_img.getchannel("A").point(lambda v: 255 if v > 127 else 0)


def with_outline(layer, px):
    """Outward outline layer: black silhouette grown by px (at SS scale) placed under the art."""
    ring = solid(layer).filter(ImageFilter.MaxFilter(px * 2 + 1))
    base = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    base.paste(Image.new("RGBA", layer.size, INK), (0, 0), ring)
    base.alpha_composite(layer)
    return base


# ---------------------------------------------------------------------------------------------------------------- fish
# Snapper body shape (deep body, round tail, dorsal and anal fins) in the mackerel palette (blue-grey back, pale belly).
BACK, BELLY, FIN = (70, 98, 112), (200, 200, 190), (64, 80, 88, 255)
LENGTH, DEPTH = 33, 15.5  # cells of 64 px; smaller than revision 1 so the stack sizes differ like vanilla meat's


def fish_layer(canvas=64):
    W = canvas * SS
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    L, D = LENGTH * SS, DEPTH * SS
    cx, cy = W / 2, W / 2
    x0 = cx - L / 2
    top, bottom = [], []
    n = 160
    for i in range(n + 1):
        t = i / n  # 0 at the tail stalk, 1 at the nose
        h = D / 2 * (math.sin(math.pi * (t ** 0.8)) ** 0.9) * (0.25 + 0.75 * min(1, t * 2.2)) + D * 0.06 * (1 - t)
        x = x0 + L * 0.18 + t * L * 0.82
        top.append((x, cy - h * 1.05))
        bottom.append((x, cy + h * 0.95))
    body = top + bottom[::-1]
    sx, ty = x0 + L * 0.2, D * 0.42
    tail = [(sx + 2 * SS, cy - D * 0.08), (x0 + L * 0.02, cy - ty * 0.85), (x0 - L * 0.01, cy - ty * 0.3),
            (x0 - L * 0.01, cy + ty * 0.3), (x0 + L * 0.02, cy + ty * 0.85), (sx + 2 * SS, cy + D * 0.08)]
    dx = x0 + L * 0.48
    dorsal = [(dx, cy - D * 0.44), (dx + L * 0.10, cy - D * 0.66), (dx + L * 0.24, cy - D * 0.45)]
    anal = [(dx + L * 0.02, cy + D * 0.40), (dx + L * 0.09, cy + D * 0.57), (dx + L * 0.16, cy + D * 0.40)]
    d = ImageDraw.Draw(img)
    for poly in (tail, dorsal, anal):
        d.polygon(poly, fill=FIN)

    mask = Image.new("L", (W, W), 0)
    ImageDraw.Draw(mask).polygon(body, fill=255)
    # Soft vertical shading, back to belly, with a little shadow at the lower edge; then blurred so the change is smooth.
    grad = Image.new("RGBA", (W, W))
    gd = ImageDraw.Draw(grad)
    y_top, y_bot = cy - D * 0.55, cy + D * 0.5
    for y in range(W):
        t = min(1, max(0, (y - y_top) / (y_bot - y_top)))
        if t < 0.6:
            c = lerp(BACK, BELLY, (t / 0.6) ** 1.8)
        else:
            c = lerp(BELLY, lerp(BELLY, (58, 66, 74), 0.4), (t - 0.6) / 0.4)
        gd.line([(0, y), (W, y)], fill=c + (255,))
    # A broad soft highlight on the upper front (light from the upper left of the image).
    hi = Image.new("L", (W, W), 0)
    ImageDraw.Draw(hi).ellipse([x0 + L * 0.42, cy - D * 0.38, x0 + L * 0.82, cy - D * 0.05], fill=40)
    hi = hi.filter(ImageFilter.GaussianBlur(3 * SS))
    grad.paste(Image.new("RGBA", (W, W), (228, 236, 240, 255)), (0, 0), hi)
    # Darken toward the tail stalk a touch, softly.
    shade = Image.new("L", (W, W), 0)
    ImageDraw.Draw(shade).rectangle([0, 0, x0 + L * 0.32, W], fill=55)
    shade = shade.filter(ImageFilter.GaussianBlur(4 * SS))
    grad.paste(Image.new("RGBA", (W, W), (44, 58, 68, 255)), (0, 0), shade)
    grad = grad.filter(ImageFilter.GaussianBlur(1.2 * SS))
    img.paste(grad, (0, 0), mask)

    d = ImageDraw.Draw(img)
    gx = x0 + L * 0.80
    d.arc([gx - D * 0.35, cy - D * 0.34, gx + D * 0.05, cy + D * 0.32], start=-60, end=60, fill=(42, 56, 64, 255), width=int(1.3 * SS))
    ex, ey, er = x0 + L * 0.90, cy - D * 0.10, D * 0.085
    d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=INK)
    d.ellipse([ex - er * 0.4, ey - er * 0.6, ex + er * 0.05, ey - er * 0.15], fill=(225, 225, 215, 255))
    return img


def place(layer, angle, dx, dy):
    rotated = layer.rotate(angle, resample=Image.BICUBIC, center=(layer.width / 2, layer.height / 2))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(rotated, (int(dx * SS), int(dy * SS)))
    return out


def stack(single, poses, margin=2):
    """Outlined fish composed back to front, then centred so nothing touches the canvas edge."""
    W = single.width
    art = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    for angle, dx, dy in poses:
        art.alpha_composite(with_outline(place(single, angle, dx, dy), 2 * SS))  # 2 px at 64 px per cell
    l, t, r, b = solid(art).getbbox()
    if l < margin * SS or t < margin * SS or r > W - margin * SS or b > W - margin * SS or True:
        centred = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        centred.alpha_composite(art.crop((l, t, r, b)), ((W - (r - l)) // 2, (W - (b - t)) // 2))
        art = centred
    return art.resize((64, 64), Image.LANCZOS)


POSES = {
    "a": [(18, 0, 0)],
    "b": [(30, -5, -4), (6, 5, 4)],
    "c": [(26, -6, -8), (20, 7, -7), (16, -7, 5), (12, 6, 7)],
}
single = fish_layer()
for suffix, poses in POSES.items():
    img = stack(single, poses)
    img.save(CAND / f"RawFish_{suffix}.png")
    box = img.getbbox()
    assert box[0] >= 1 and box[1] >= 1 and box[2] <= 63 and box[3] <= 63, (suffix, box)
