"""Ticket 20 candidates: the dive shadow and the going-under and coming-up animations.

White shapes the renderer tints, scales and fades, like art/dive-visuals and art/face-down:
  DiveShadow.png  64x64  head and shoulders seen from above, under the water (the shoulders shape of look C plus a head)
  Ripple.png      64x64  a thin round ring
  Bubble.png      64x64  a small hollow bubble
  Droplet.png     64x64  a soft round drop
  SprayCrown.png  64x64  eight short radial dashes
DiveShadow, Ripple and Bubble were approved and ship in Textures/Spearfishing/Dive (APPROVAL.md); Droplet and SprayCrown
were not chosen.

Usage: python -I dive_anim_art.py <out_dir> [<frame> <background> <head_x> <head_y>]
With a frame group (an in-game capture with a face-down pawn, the same view with that pawn under the water, and the head's
centre in pixels) it also writes the candidate frames, composited at game scale over the capture: water, then the shapes,
then the captured head where the pawn is at the surface. Each frame is captioned with its time.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
SS = 8
N = 64


def white_shape(draw_fn, blur=0.0):
    a = Image.new("L", (N * SS, N * SS), 0)
    draw_fn(ImageDraw.Draw(a), SS)
    if blur:
        a = a.filter(ImageFilter.GaussianBlur(blur * SS))
    a = a.resize((N, N), Image.LANCZOS)
    img = Image.new("RGBA", (N, N), (255, 255, 255, 0))
    img.putalpha(a)
    return img


def dive_shadow(d, u):
    # Look C's shoulders, moved down to make room for a round head above them.
    d.ellipse([21 * u, 4 * u, 43 * u, 28 * u], fill=255)
    d.rounded_rectangle([6 * u, 24 * u, 58 * u, 44 * u], radius=10 * u, fill=255)
    d.ellipse([16 * u, 30 * u, 48 * u, 58 * u], fill=255)


def ripple(d, u):
    d.ellipse([3 * u, 3 * u, 61 * u, 61 * u], fill=255)
    d.ellipse([8 * u, 8 * u, 56 * u, 56 * u], fill=0)


def bubble(d, u):
    d.ellipse([8 * u, 8 * u, 56 * u, 56 * u], fill=255)
    d.ellipse([20 * u, 20 * u, 44 * u, 44 * u], fill=0)
    d.ellipse([18 * u, 16 * u, 28 * u, 26 * u], fill=255)  # a highlight, so it reads as a bubble, not a ring


def droplet(d, u):
    d.ellipse([12 * u, 12 * u, 52 * u, 52 * u], fill=255)


def spray_crown(d, u):
    c = 32 * u
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        x0, y0 = c + math.cos(a) * 17 * u, c + math.sin(a) * 17 * u
        x1, y1 = c + math.cos(a) * 29 * u, c + math.sin(a) * 29 * u
        d.line([(x0, y0), (x1, y1)], fill=255, width=6 * u)
        d.ellipse([x1 - 3 * u, y1 - 3 * u, x1 + 3 * u, y1 + 3 * u], fill=255)
        d.ellipse([x0 - 3 * u, y0 - 3 * u, x0 + 3 * u, y0 + 3 * u], fill=255)


TEX = {
    "DiveShadow": white_shape(dive_shadow, blur=1.6),
    "Ripple": white_shape(ripple, blur=0.3),
    "Bubble": white_shape(bubble, blur=0.3),
    "Droplet": white_shape(droplet, blur=0.6),
    "SprayCrown": white_shape(spray_crown, blur=0.3),
}
for name, img in TEX.items():
    img.save(OUT / f"{name}.png")

# Look C's approved pieces (art/face-down), for the frames at the surface.
FACE_DOWN = Path(__file__).resolve().parent.parent / "face-down"
TEX["Shoulders"] = Image.open(FACE_DOWN / "Shoulders.png").convert("RGBA")
TEX["Waterline"] = Image.open(FACE_DOWN / "Waterline.png").convert("RGBA")

SHADOW = (8, 20, 26)
RING = (215, 240, 255)
CELL = 103  # capture pixels per cell

# A draw: (texture, tint, alpha, size in cells, x and z offset from the head centre in cells, z positive to the south).
LOOK_C = [("Shoulders", SHADOW, 0.5, 0.95, 0, 0.38), ("Waterline", RING, 0.45, 1.0, 0, 0.10)]
SHADOW_OFFSET = 0.3


def ease_out(k):
    return 1 - (1 - k) ** 2


def dive_shadow_at(depth):
    # depth 0 just under the surface, 1 at the bottom of the dive.
    size = 1.0 + (0.55 - 1.0) * depth
    alpha = 0.55 + (0.22 - 0.55) * depth
    return ("DiveShadow", SHADOW, alpha, size, 0, SHADOW_OFFSET)


def shadow_during(t):
    # In these frames the shadow shrinks as over the first 1.2 s of a dive; the animations run 0.6 s.
    return dive_shadow_at(min(1.0, max(0.0, t / 1.2)))


def under_ring_pulls_in(t):
    k = t / 0.6
    out = [shadow_during(t)]
    if k < 1:
        out.append(("Waterline", RING, 0.45 * (1 - k), 1.0 - 0.8 * ease_out(k), 0, 0.10))
    return out


BUBBLES = [(-0.5, -0.2), (0.45, -0.35), (0.1, -0.55), (-0.25, 0.45), (0.5, 0.25)]


def bubbles(t, start, length, count=5, reach=0.55):
    k = (t - start) / length
    if k < 0 or k >= 1:
        return []
    out = []
    for i, (bx, bz) in enumerate(BUBBLES[:count]):
        r = math.hypot(bx, bz)
        f = (0.15 + reach * ease_out(k)) / r
        out.append(("Bubble", RING, 0.85 * (1 - k * k), 0.16 + 0.08 * k, bx * f, -0.1 + bz * f))
    return out


def under_bubble_burst(t):
    return [shadow_during(t)] + bubbles(t, 0, 0.6)


def under_ring_and_bubbles(t):
    k = t / 0.35
    out = [shadow_during(t)]
    if k < 1:
        out.append(("Waterline", RING, 0.45 * (1 - k), 1.0 - 0.8 * ease_out(k), 0, 0.10))
    return out + bubbles(t, 0.2, 0.4, count=3, reach=0.35)


def up_double_ripple(t):
    out = []
    for delay in (0, 0.15):
        k = (t - delay) / 0.45
        if 0 <= k < 1:
            out.append(("Ripple", RING, 0.75 * (1 - k), 0.5 + 0.9 * ease_out(k), 0, 0.05))
    return out + [("Shoulders", SHADOW, 0.5 * min(1, t / 0.3), 0.95, 0, 0.38)] + \
        ([("Waterline", RING, 0.45 * min(1, (t - 0.3) / 0.3), 1.0, 0, 0.10)] if t > 0.3 else [])


def up_ring_opens_spray(t):
    k = min(1.0, t / 0.6)
    out = [("Shoulders", SHADOW, 0.5 * min(1, t / 0.3), 0.95, 0, 0.38),
           ("Waterline", RING, 0.45 + 0.35 * (1 - k), 0.25 + 0.75 * ease_out(k), 0, 0.10)]
    if k < 1:
        for i in range(6):
            a = math.radians(i * 60 + 30)
            r = 0.3 + 0.55 * ease_out(k)
            out.append(("Droplet", RING, 0.9 * (1 - k), 0.14 - 0.05 * k, math.cos(a) * r, -0.1 + math.sin(a) * r * 0.8))
    return out


def up_spray_crown(t):
    k = min(1.0, t / 0.6)
    out = list(LOOK_C) if t >= 0.6 else [("Shoulders", SHADOW, 0.5 * min(1, t / 0.3), 0.95, 0, 0.38)]
    if k < 1:
        out.append(("SprayCrown", RING, 0.9 * (1 - k * k), 0.6 + 0.8 * ease_out(k), 0, -0.05))
    return out


TIMES = [0, 0.15, 0.3, 0.45, 0.6]
# (label, kind, frames as (caption, draws, head shown)).
ROWS = [
    ("Dive shadow", [(f"depth {d:.0%}", [dive_shadow_at(d)], False) for d in (0, 0.25, 0.5, 0.75, 1.0)]),
    ("Under A ring pulls in", [("at surface", LOOK_C, True)] + [(f"{t:.2f} s", under_ring_pulls_in(t), False) for t in TIMES[1:]]),
    ("Under B bubble burst", [("at surface", LOOK_C, True)] + [(f"{t:.2f} s", under_bubble_burst(t), False) for t in TIMES[1:]]),
    ("Under C ring in + bubbles", [("at surface", LOOK_C, True)] + [(f"{t:.2f} s", under_ring_and_bubbles(t), False) for t in TIMES[1:]]),
    ("Up A double ripple", [(f"{t:.2f} s", up_double_ripple(t), True) for t in TIMES]),
    ("Up B ring opens + spray", [(f"{t:.2f} s", up_ring_opens_spray(t), True) for t in TIMES]),
    ("Up C spray crown", [(f"{t:.2f} s", up_spray_crown(t), True) for t in TIMES]),
]


# Second sheet, after the user's direction on the first: "a ring should spread from them diving down, like a ripple, outward.
# The same should happen when they come up. With maybe some bubble animations coming up from them when they are down there."
RIPPLE_SECONDS = 0.8


def ripples(t, count):
    out = []
    for i in range(count):
        k = (t - 0.2 * i) / RIPPLE_SECONDS
        if 0 <= k < 1:
            out.append(("Ripple", RING, 0.8 * (1 - k), (0.5 + 1.2 * ease_out(k)) * (1 - 0.2 * i), 0, 0.05))
    return out


def under_ripple(t, count):
    return [shadow_during(t)] + ripples(t, count)


def up_ripple(t, count):
    return list(LOOK_C) + ripples(t, count)


def rising_bubble(age, dx, dz):
    # Seen from above: small and faint deep down, larger and paler as it nears the surface, then a tiny ring as it pops.
    rise, pop = 0.7, 0.2
    if age < 0:
        return []
    if age < rise:
        k = age / rise
        return [("Bubble", RING, 0.35 + 0.55 * k, 0.08 + 0.12 * k, dx, dz - 0.15 * k)]
    k = (age - rise) / pop
    return [("Ripple", RING, 0.7 * (1 - k), 0.2 + 0.2 * k, dx, dz - 0.15)] if k < 1 else []


def bubbles_single(t):
    # One bubble every 0.8 s, each from a slightly different spot over the shadow.
    out = [dive_shadow_at(1.0)]
    spots = [(0.05, 0.05), (-0.12, 0.15), (0.12, 0.1)]
    for n in range(3):
        dx, dz = spots[n]
        out += rising_bubble(t - 0.8 * n + 0.45, dx, dz)
    return out


def bubbles_cluster(t):
    # Three small bubbles a moment apart, every 1.4 s.
    out = [dive_shadow_at(1.0)]
    for i, (dx, dz) in enumerate([(0.0, 0.1), (-0.12, 0.2), (0.1, 0.25)]):
        out += rising_bubble(t - 0.12 * i, dx, dz)
    return out


RTIMES = [0, 0.2, 0.4, 0.6, 0.8]
BTIMES = [0, 0.25, 0.5, 0.75, 1.0]
ROWS_V2 = [
    ("Under 1 one ripple", [("at surface", LOOK_C, True)] + [(f"{t:.1f} s", under_ripple(t, 1), False) for t in RTIMES[1:]]),
    ("Under 2 two ripples", [("at surface", LOOK_C, True)] + [(f"{t:.1f} s", under_ripple(t, 2), False) for t in RTIMES[1:]]),
    ("Bubbles 1 one at a time", [(f"{t:.2f} s", bubbles_single(t), False) for t in BTIMES]),
    ("Bubbles 2 small cluster", [(f"{t:.2f} s", bubbles_cluster(t), False) for t in BTIMES]),
    ("Up 1 one ripple", [(f"{t:.1f} s", up_ripple(t, 1), True) for t in RTIMES]),
    ("Up 2 two ripples", [(f"{t:.1f} s", up_ripple(t, 2), True) for t in RTIMES]),
]


def tinted(img, rgb, alpha):
    t = Image.new("RGBA", img.size, rgb + (0,))
    t.putalpha(img.getchannel("A").point(lambda v: int(v * max(0.0, min(1.0, alpha)))))
    return t


def composite(fr, bg, hx, hy, draws, head_shown, caption):
    half = CELL
    box = (hx - half, hy - half + CELL // 5, hx + half, hy + half + CELL // 5)
    frc = fr.crop(box)
    out = bg.crop(box)
    ox, oy = hx - box[0], hy - box[1]
    for name, rgb, alpha, size, dx, dz in draws:
        px = max(1, int(size * CELL))
        tex = TEX[name].resize((px, px), Image.LANCZOS)
        x = ox + int(dx * CELL) - px // 2
        y = oy + int(dz * CELL) - px // 2
        layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
        layer.alpha_composite(tinted(tex, rgb, alpha), (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))
        out.alpha_composite(layer)
    if head_shown:
        # Head pixels: where the face-down capture differs from the capture with the pawn under the water, near the head.
        diff = ImageChops.difference(frc.convert("RGB"), bg.crop(box).convert("RGB")).convert("L").point(lambda v: 255 if v > 22 else 0)
        near = Image.new("L", out.size, 0)
        ImageDraw.Draw(near).ellipse([ox - 50, oy - 50, ox + 50, oy + 50], fill=255)
        mask = ImageChops.multiply(diff.filter(ImageFilter.MaxFilter(3)), near)
        out.paste(frc, (0, 0), mask)
    out = out.resize((out.width * 2, out.height * 2), Image.LANCZOS)
    d = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("arialbd.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    d.rectangle([0, 0, out.width, 32], fill=(0, 0, 0, 150))
    d.text((10, 4), caption, fill=(255, 255, 255, 255), font=font)
    return out


if len(sys.argv) >= 6:
    frame, background, hx, hy = sys.argv[2:6]
    fr = Image.open(frame).convert("RGBA")
    bg = Image.open(background).convert("RGBA")
    for r, (label, frames) in enumerate(ROWS):
        for c, (caption, draws, head) in enumerate(frames):
            composite(fr, bg, int(hx), int(hy), draws, head, caption).save(OUT / f"{r}{label[0]}_{c}.png")
    for r, (label, frames) in enumerate(ROWS_V2):
        for c, (caption, draws, head) in enumerate(frames):
            composite(fr, bg, int(hx), int(hy), draws, head, caption).save(OUT / f"v2_{r}_{c}.png")
