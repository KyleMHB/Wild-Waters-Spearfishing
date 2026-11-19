"""Ticket 18 candidates: what shows of a pawn floating face down besides the head the game already draws.

White shapes the renderer tints and fades, like art/dive-visuals:
  SunkBody.png   64x128  a whole body lying face down under the water, head end at the top (candidate B)
  Shoulders.png  64x64   just the shoulders and upper back, under the water (candidate C)
  Waterline.png  64x64   a flat ring where the head meets the water (candidates A and C)

Usage: python -I face_down_art.py <out_dir> [<frame> <background> <head_x> <head_y> <label>]...
Each frame group is an in-game capture with a face-down pawn, a capture of the same view with that pawn under the water
(so no head), and the head's centre in pixels. The candidates are composited into the frames: shapes over the water,
the captured head pasted back on top, as the game draws them (water, then the shapes at Waves' sea-life queue, then
the pawn).
"""
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
SS = 8
N = 64


def white_shape(draw_fn, w=N, h=N, blur=0.0):
    a = Image.new("L", (w * SS, h * SS), 0)
    draw_fn(ImageDraw.Draw(a), SS)
    if blur:
        a = a.filter(ImageFilter.GaussianBlur(blur * SS))
    a = a.resize((w, h), Image.LANCZOS)
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    img.putalpha(a)
    return img


def sunk_body(d, u):
    # Seen from above, face down, head end at the top: broad shoulders, a tapering back, legs together. Three bold parts.
    d.rounded_rectangle([4 * u, 8 * u, 60 * u, 32 * u], radius=12 * u, fill=255)  # shoulders and arms close in
    d.polygon([(10 * u, 22 * u), (54 * u, 22 * u), (46 * u, 72 * u), (18 * u, 72 * u)], fill=255)  # back
    d.rounded_rectangle([18 * u, 64 * u, 46 * u, 122 * u], radius=10 * u, fill=255)  # legs


def shoulders(d, u):
    d.rounded_rectangle([6 * u, 18 * u, 58 * u, 40 * u], radius=11 * u, fill=255)
    d.ellipse([16 * u, 26 * u, 48 * u, 54 * u], fill=255)


def waterline(d, u):
    d.ellipse([4 * u, 14 * u, 60 * u, 50 * u], fill=255)
    d.ellipse([12 * u, 20 * u, 52 * u, 44 * u], fill=0)


TEX = {
    "SunkBody": white_shape(sunk_body, N, 2 * N, blur=1.6),
    "Shoulders": white_shape(shoulders, blur=1.6),
    "Waterline": white_shape(waterline, blur=0.4),
}
for name, img in TEX.items():
    img.save(OUT / f"{name}.png")

# In-game tuning the candidates use, in cells and 0-1 alpha. The shapes' tint is the fish shadow's.
SHADOW = (8, 20, 26)
RING = (215, 240, 255)
CELL = 103  # capture pixels per cell (the 12-cell sea strip spans about 1,235 px)
CANDIDATES = {
    "A head + waterline": [("Waterline", RING, 0.45, 1.0, 1.0, 0.10)],
    "B faint sunk body": [("SunkBody", SHADOW, 0.32, 1.1, 2.0, 0.92)],
    "C shoulders + waterline": [("Shoulders", SHADOW, 0.5, 0.95, 0.95, 0.38), ("Waterline", RING, 0.45, 1.0, 1.0, 0.10)],
}


def tinted(img, rgb, alpha):
    t = Image.new("RGBA", img.size, rgb + (0,))
    t.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    return t


def composite(frame, background, hx, hy, parts):
    # The head sits near the top, so a whole sunk body fits below it.
    ox, oy = 130, 90
    box = (hx - ox, hy - oy, hx + ox, hy + 210)
    fr = Image.open(frame).convert("RGBA").crop(box)
    bg = Image.open(background).convert("RGBA").crop(box)
    # Head pixels: where the face-down capture differs from the capture with the pawn under the water.
    diff = ImageChops.difference(fr.convert("RGB"), bg.convert("RGB")).convert("L").point(lambda v: 255 if v > 22 else 0)
    head = diff.filter(ImageFilter.MaxFilter(3))
    out = bg.copy()
    for name, rgb, alpha, w, h, dz in parts:
        tex = TEX[name].resize((int(w * CELL), int(h * CELL)), Image.LANCZOS)
        # dz: cells below the head centre to the shape's centre.
        x = ox - tex.width // 2
        y = oy + int(dz * CELL) - tex.height // 2
        pad = 2 * CELL
        big = Image.new("RGBA", (out.width + 2 * pad, out.height + 2 * pad), (0, 0, 0, 0))
        big.alpha_composite(tinted(tex, rgb, alpha), (x + pad, y + pad))
        out.alpha_composite(big.crop((pad, pad, pad + out.width, pad + out.height)))
    out.paste(fr, (0, 0), head)
    return out.resize((out.width * 2, out.height * 2), Image.LANCZOS)


groups = sys.argv[2:]
for i in range(0, len(groups), 5):
    frame, background, hx, hy, label = groups[i:i + 5]
    for cand, parts in CANDIDATES.items():
        composite(frame, background, int(hx), int(hy), parts).save(OUT / f"{label}_{cand[0]}.png")
    composite(frame, background, int(hx), int(hy), []).save(OUT / f"{label}_now.png")
