"""Procedural, tileable reef overlay candidates for Spearfishing (ticket 03).

Each candidate is a 512x512 RGBA texture covering 8x8 cells (64 px per cell) that repeats seamlessly: all noise is
band-limited periodic noise made in the frequency domain, so the left/right and top/bottom edges match.
The overlay is alpha-blended over Waves' water body, so colour is what shows through the water and alpha is how strongly.
Candidate B (rock_shadow) is the approved master; A and C are kept so the record shows what was compared. See APPROVAL.md.

Usage: python reef_art.py <out_dir>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

N = 512


def periodic_noise(seed, low, high):
    """Smooth noise that tiles: random phases on frequencies between low and high cycles per tile."""
    rng = np.random.default_rng(seed)
    f = np.fft.fftfreq(N) * N
    fx, fy = np.meshgrid(f, f)
    r = np.hypot(fx, fy)
    spectrum = (rng.normal(size=(N, N)) + 1j * rng.normal(size=(N, N))) * ((r >= low) & (r <= high)) / np.maximum(r, 1)
    n = np.real(np.fft.ifft2(spectrum))
    return (n - n.mean()) / n.std()


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def shade(height):
    """Light from the top-left, as RimWorld paints it: positive where the surface faces up-left."""
    gy, gx = np.gradient(np.pad(height, 1, mode="wrap"))
    gx, gy = gx[1:-1, 1:-1], gy[1:-1, 1:-1]
    return np.clip(-(gx + gy) * 12, -1, 1)


def to_image(rgb, alpha):
    rgba = np.dstack([np.clip(rgb, 0, 1), np.clip(alpha, 0, 1)])
    return Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), "RGBA")


def palette_mix(index, colours):
    """Pick a colour per pixel from a smooth 0..1 index, blending between neighbouring palette entries."""
    colours = np.array(colours, dtype=float)
    pos = np.clip(index, 0, 0.999) * (len(colours) - 1)
    i = np.floor(pos).astype(int)
    t = (pos - i)[..., None]
    return colours[i] * (1 - t) + colours[np.minimum(i + 1, len(colours) - 1)] * t


def coral_heads():
    """A: rounded coral heads and rock in muted ochre, rose and sage, with sand gaps between clusters."""
    mass = periodic_noise(1, 4, 12)
    detail = periodic_noise(2, 20, 48)
    heads = mass * 0.8 + detail * 0.45
    cover = smoothstep(0.05, 0.35, heads)
    height = smoothstep(-0.2, 1.4, heads)
    hue = smoothstep(-1.5, 1.5, periodic_noise(3, 6, 16))
    base = palette_mix(hue, [(0.58, 0.46, 0.33), (0.62, 0.42, 0.42), (0.40, 0.48, 0.38), (0.55, 0.52, 0.40)])
    light = shade(height)[..., None]
    rim = (1 - smoothstep(0.05, 0.45, heads))[..., None] * 0.45
    rgb = base * (0.85 + 0.35 * light) * (1 - rim)
    sand = np.array([0.66, 0.62, 0.50])
    sand_alpha = 0.18 * smoothstep(-1.0, 0.0, heads)
    alpha = np.maximum(cover * 0.72, sand_alpha)
    rgb = np.where(cover[..., None] > sand_alpha[..., None] / 0.72, rgb, sand)
    return to_image(rgb, alpha)


def rock_shadow():
    """B: dark rock shelves seen as shadows through the water, in the manner of Waves' shadow-only sea life."""
    mass = periodic_noise(11, 4, 10) * 0.9 + periodic_noise(12, 16, 36) * 0.35
    cover = smoothstep(-0.1, 0.4, mass)
    holes = smoothstep(0.9, 1.3, periodic_noise(13, 24, 60))
    height = smoothstep(-0.1, 1.6, mass)
    light = shade(height)[..., None]
    rgb = np.array([0.10, 0.13, 0.12]) * (1 + 0.6 * light) + np.array([0.05, 0.04, 0.02]) * height[..., None]
    alpha = cover * 0.55 * (1 - 0.6 * holes)
    return to_image(rgb, alpha)


def coral_garden():
    """C: brighter branching coral (rose, violet, gold) over a pale sand floor that lightens the whole reef."""
    clusters = periodic_noise(21, 4, 12)
    branches = np.abs(periodic_noise(22, 28, 56))
    coral = smoothstep(0.0, 0.5, clusters) * smoothstep(0.75, 0.3, branches)
    hue = smoothstep(-1.4, 1.4, periodic_noise(23, 6, 14))
    colour = palette_mix(hue, [(0.78, 0.45, 0.50), (0.58, 0.44, 0.66), (0.82, 0.66, 0.34), (0.86, 0.52, 0.40)])
    light = shade(smoothstep(0.55, 0.0, branches) * smoothstep(0.0, 0.6, clusters))[..., None]
    colour = colour * (0.85 + 0.3 * light)
    sand = np.array([0.80, 0.72, 0.52]) * (0.95 + 0.08 * periodic_noise(24, 40, 80)[..., None])
    sand_alpha = 0.22
    a = coral * 0.85
    alpha = a + sand_alpha * (1 - a)
    rgb = (colour * a[..., None] + sand * (sand_alpha * (1 - a))[..., None]) / alpha[..., None]
    return to_image(rgb, alpha)


CANDIDATES = {"A-coral-heads": coral_heads, "B-rock-shadow": rock_shadow, "C-coral-garden": coral_garden}

if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, make in CANDIDATES.items():
        make().save(out / f"ReefOverlay-{name}.png")
        print(out / f"ReefOverlay-{name}.png")
