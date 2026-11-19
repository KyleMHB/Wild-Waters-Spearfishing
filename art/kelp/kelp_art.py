"""Procedural, tileable kelp forest overlay candidates for Spearfishing (ticket 38).

Kelp is the cold-water counterpart of reef, drawn the same way: each candidate is a 512x512 RGBA texture covering 8x8 cells
(64 px per cell) that repeats seamlessly, alpha-blended over Waves' water body by a section layer like SectionLayer_Reef.
Colour is what shows through the water and alpha is how strongly. Strands lean along one current direction and sway.
Every random field is periodic over the tile (band-limited noise made in the frequency domain, warps sampled with wrap, and
drawn strands repeated across the edges), so the left/right and top/bottom edges match.

B2 (brown, cold water) and B (green, slightly warmer water) are the approved masters; A and C are kept so the record shows
what was compared. See APPROVAL.md.

The sheet puts each candidate, tiled at game scale over plain shallow and deep sea, beside the approved reef overlay.
The sea colours are flat fills sampled from an in-game capture of Waves' water at noon; no game or mod texture is used.

Usage: python kelp_art.py <out_dir> [--sheet <sheet.png>]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import map_coordinates

N = 512
# Strands lean this way (radians, image space: x right, y down); a gentle diagonal reads as current, not as a grid.
CURRENT = np.radians(-28)


def periodic_noise(seed, low, high, stretch=1.0):
    """Smooth noise that tiles: random phases on frequencies between low and high cycles per tile.

    stretch > 1 keeps mainly frequencies across the current, so the noise forms streaks along it.
    """
    rng = np.random.default_rng(seed)
    f = np.fft.fftfreq(N) * N
    fx, fy = np.meshgrid(f, f)
    along = fx * np.cos(CURRENT) + fy * np.sin(CURRENT)
    across = -fx * np.sin(CURRENT) + fy * np.cos(CURRENT)
    r = np.hypot(along * stretch, across)
    spectrum = (rng.normal(size=(N, N)) + 1j * rng.normal(size=(N, N))) * ((r >= low) & (r <= high)) / np.maximum(r, 1)
    n = np.real(np.fft.ifft2(spectrum))
    return (n - n.mean()) / n.std()


def warp(field, seed, amount):
    """Bend a tiling field by a smooth tiling displacement, so straight streaks sway like strands in a current."""
    dx = periodic_noise(seed, 2, 6) * amount
    dy = periodic_noise(seed + 1, 2, 6) * amount
    y, x = np.mgrid[0:N, 0:N].astype(float)
    return map_coordinates(field, [y + dy, x + dx], order=1, mode="grid-wrap")


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


def kelp_shadow():
    """A: dark green strand shadows through the water, the kelp sibling of the approved rock-shadow reef."""
    beds = smoothstep(-0.3, 0.5, periodic_noise(31, 3, 8))
    strands = warp(periodic_noise(32, 18, 44, stretch=5), 33, 10)
    streak = smoothstep(0.1, 0.9, strands) * beds
    height = smoothstep(0.0, 1.4, strands) * beds
    light = shade(height)[..., None]
    rgb = np.array([0.07, 0.15, 0.08]) * (1 + 0.6 * light) + np.array([0.03, 0.05, 0.01]) * height[..., None]
    alpha = 0.18 * beds + 0.42 * streak
    return to_image(rgb, alpha)


def _strand_layer(seed, count, scale=2):
    """Draw swaying stipes with blades at scale x the tile size, repeated across the edges, and return coverage 0..1."""
    rng = np.random.default_rng(seed)
    S = N * scale
    canvas = Image.new("L", (S, S), 0)
    tips = Image.new("L", (S, S), 0)
    draw, tip_draw = ImageDraw.Draw(canvas), ImageDraw.Draw(tips)
    along = np.array([np.cos(CURRENT), np.sin(CURRENT)])
    across = np.array([-along[1], along[0]])
    for _ in range(count):
        start = rng.uniform(0, S, 2)
        length = rng.uniform(0.18, 0.34) * S
        sway, phase = rng.uniform(0.02, 0.06) * S, rng.uniform(0, 2 * np.pi)
        lean = rng.normal(0, 0.12)
        width = rng.uniform(3, 6) * scale
        steps = 40
        t = np.linspace(0, 1, steps)
        points = (start + np.outer(t * length, along + lean * across)
                  + np.outer(np.sin(t * 2.4 * np.pi + phase) * sway * t, across))
        for ox in (-S, 0, S):
            for oy in (-S, 0, S):
                p = points + (ox, oy)
                if p[:, 0].max() < -40 or p[:, 0].min() > S + 40 or p[:, 1].max() < -40 or p[:, 1].min() > S + 40:
                    continue
                for k in range(steps - 1):
                    w = width * (1 - 0.5 * t[k])
                    draw.line([tuple(p[k]), tuple(p[k + 1])], fill=255, width=max(1, int(w)))
                    if k % 4 == 2:
                        # A blade either side of the stipe, trailing with the current.
                        for side in (-1, 1):
                            b = p[k] + across * side * w * 1.6 + along * w * 1.2
                            r = w * 1.3
                            draw.ellipse([b[0] - r, b[1] - r * 0.6, b[0] + r, b[1] + r * 0.6], fill=255)
                tip = p[-8:]
                tip_draw.line([tuple(q) for q in tip], fill=255, width=max(1, int(width * 0.8)))
    def down(img):
        return np.asarray(img.resize((N, N), Image.LANCZOS), dtype=float) / 255
    return down(canvas), down(tips)


def kelp_fronds():
    """B: separate swaying fronds, olive-green stipes and blades with lighter tips near the surface, sea floor between."""
    strand, tip = _strand_layer(41, 70)
    floor = 0.10 * smoothstep(-0.5, 0.8, periodic_noise(42, 4, 10))
    light = shade(strand * 0.6)[..., None]
    hue = smoothstep(-1.2, 1.2, periodic_noise(43, 3, 9))[..., None]
    body = np.array([0.13, 0.22, 0.09]) * (1 - hue) + np.array([0.20, 0.24, 0.10]) * hue
    rgb = body * (0.9 + 0.35 * light) + np.array([0.12, 0.12, 0.03]) * tip[..., None]
    floor_rgb = np.array([0.08, 0.12, 0.08])
    a = strand * 0.72
    alpha = a + floor * (1 - a)
    rgb = (rgb * a[..., None] + floor_rgb * (floor * (1 - a))[..., None]) / np.maximum(alpha, 1e-6)[..., None]
    return to_image(rgb, alpha)


def kelp_canopy():
    """C: a dense dark forest with a lighter, swaying canopy of strands lying on top and gaps of open water."""
    mass = periodic_noise(51, 3, 9) * 0.9 + periodic_noise(52, 12, 28) * 0.3
    cover = smoothstep(-0.4, 0.3, mass)
    gaps = smoothstep(0.8, 1.3, warp(periodic_noise(53, 10, 26, stretch=3), 54, 8))
    canopy = smoothstep(0.3, 1.1, warp(periodic_noise(55, 20, 50, stretch=6), 56, 12)) * cover
    height = smoothstep(-0.4, 1.2, mass) * 0.5 + canopy * 0.6
    light = shade(height)[..., None]
    dark = np.array([0.05, 0.11, 0.06])
    leaf = np.array([0.16, 0.26, 0.11])
    rgb = (dark * (1 - canopy[..., None]) + leaf * canopy[..., None]) * (1 + 0.5 * light)
    alpha = (cover * 0.55 + canopy * 0.2) * (1 - 0.8 * gaps)
    return to_image(rgb, alpha)


def _wrapped(draw_at, S):
    """Call draw_at(offset) for the tile and its eight neighbours, so shapes crossing an edge reappear on the other side."""
    for ox in (-S, 0, S):
        for oy in (-S, 0, S):
            draw_at(np.array([ox, oy], dtype=float))


def _strap(centre, width):
    """Polygon of a strap-shaped blade around a centreline, width given per point."""
    d = np.gradient(centre, axis=0)
    normal = np.stack([-d[:, 1], d[:, 0]], axis=1) / np.maximum(np.linalg.norm(d, axis=1), 1e-6)[:, None]
    left, right = centre + normal * width[:, None] / 2, centre - normal * width[:, None] / 2
    return [tuple(p) for p in np.vstack([left, right[::-1]])], left


def kelp_fronds_b2():
    """B2: Cape Town kelp (Ecklonia maxima) from above, in dark brown, after the user picked B.

    Floating bulbs, each trailing a fan of long strap blades along the current, with its stem running back into darker
    water. Blades overlap into mats with open water between. Under them, faint split-fan kelp (Laminaria pallida).
    Thin blade edges and tips catch the light in warm amber; the deep parts are near black-brown.
    """
    rng = np.random.default_rng(61)
    scale = 3
    S = N * scale
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    along = np.array([np.cos(CURRENT), np.sin(CURRENT)])
    across = np.array([-along[1], along[0]])

    def rot(v, angle):
        c, s = np.cos(angle), np.sin(angle)
        return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])

    # Alpha in this image is relative strength; the whole layer is scaled by BLADE_ALPHA below.
    under, stem, deep = (40, 27, 15, 80), (32, 21, 11, 150), (26, 17, 9, 220)

    # Split-fan kelp underneath: short fans of fingers in dark brown, faint through the water.
    for _ in range(46):
        root = rng.uniform(0, S, 2)
        heading = rot(along, rng.normal(0, 0.6))
        fingers = rng.integers(4, 7)
        reach = rng.uniform(14, 24) * scale

        def fan(o, root=root, heading=heading, fingers=fingers, reach=reach):
            for k in range(fingers):
                tip = root + rot(heading, (k - (fingers - 1) / 2) * 0.22) * reach + o
                draw.line([tuple(root + o), tuple(tip)], fill=under, width=2 * scale)
        _wrapped(fan, S)

    bulbs = []
    for _ in range(58):
        bulbs.append((rng.uniform(0, S, 2), rng.uniform(0, 2 * np.pi), rng.normal(0, 0.15)))

    # Stems first, so every blade lies over them: from the bulb back against the current into deeper water.
    for root, phase, lean in bulbs:
        length = rng.uniform(40, 80) * scale
        t = np.linspace(0, 1, 16)
        path = root - np.outer(t * length, rot(along, lean)) + np.outer(np.sin(t * 3 + phase) * 6 * scale, across)
        _wrapped(lambda o, path=path: draw.line([tuple(p + o) for p in path], fill=stem, width=3 * scale), S)

    for root, phase, lean in bulbs:
        blades = rng.integers(5, 9)
        for k in range(blades):
            spread = (k - (blades - 1) / 2) / max(blades - 1, 1) * rng.uniform(0.45, 0.7)
            heading = rot(along, lean + spread)
            length = rng.uniform(90, 150) * scale
            sway = rng.uniform(4, 10) * scale
            t = np.linspace(0, 1, 30)
            centre = (root + np.outer(t * length, heading)
                      + np.outer(np.sin(t * 2.2 * np.pi + phase + k) * sway * t, across))
            width = (rng.uniform(3.5, 5.5) * scale) * (0.3 + 0.7 * np.minimum(t * 8, 1)) * (1 - 0.45 * t ** 2)
            body = np.array([rng.uniform(44, 60), rng.uniform(30, 38), rng.uniform(14, 20)])
            base_colour = tuple(int(c) for c in body) + (235,)
            tip_colour = tuple(int(c) for c in body * 0.55 + np.array([150, 104, 38]) * 0.45) + (235,)
            edge_colour = tuple(int(c) for c in body * 0.65 + np.array([140, 98, 36]) * 0.35) + (235,)
            poly, left = _strap(centre, width)
            tip_poly, _ = _strap(centre[25:], width[25:])

            def blade(o, poly=poly, left=left, tip_poly=tip_poly, base_colour=base_colour, tip_colour=tip_colour,
                      edge_colour=edge_colour):
                draw.polygon([(x + o[0], y + o[1]) for x, y in poly], fill=base_colour)
                # Light from the top-left: the thin edge on the upper side catches it, more towards the tip.
                draw.line([tuple(p + o) for p in left[14:]], fill=edge_colour, width=scale)
                draw.polygon([(x + o[0], y + o[1]) for x, y in tip_poly], fill=tip_colour)
            _wrapped(blade, S)

        r = 2.6 * scale
        _wrapped(lambda o, root=root: draw.ellipse([root[0] + o[0] - r, root[1] + o[1] - r, root[0] + o[0] + r,
                                                    root[1] + o[1] + r], fill=(96, 66, 28, 255),
                                                   outline=deep, width=scale), S)

    small = img.resize((N, N), Image.LANCZOS)
    a = np.asarray(small, dtype=float) / 255
    BLADE_ALPHA = 0.85
    return to_image(a[..., :3], a[..., 3] * BLADE_ALPHA)


CANDIDATES = {"A-kelp-shadow": kelp_shadow, "B-kelp-fronds": kelp_fronds, "C-kelp-canopy": kelp_canopy,
              "B2-kelp-fronds-brown": kelp_fronds_b2}

# Contact sheet: plain sea fills sampled from a noon capture of Waves' water (shallow near the surf, deep further out).
SEA = {"Shallow ocean": (47, 89, 91), "Deep ocean": (32, 68, 81)}
STRENGTH = {"Shallow ocean": 1.0, "Deep ocean": 0.7}  # SectionLayer_Reef's shallow and deep strength
CELL_PX = 32  # game scale for the sheet: a cell at a normal play zoom, half the texture's 64 px per cell
PATCH_CELLS = (20, 12)


def patch_strength(seed):
    """A blob of patch cells with SectionLayer_Reef's fade: each corner is the mean of its four cells, interpolated."""
    w, h = PATCH_CELLS
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:h, 0:w]
    blob = ((x - w / 2 + 0.5) / (w * 0.42)) ** 2 + ((y - h / 2 + 0.5) / (h * 0.40)) ** 2
    cells = (blob + rng.uniform(-0.25, 0.25, blob.shape) < 1).astype(float)
    padded = np.pad(cells, 1)
    corners = (padded[:-1, :-1] + padded[1:, :-1] + padded[:-1, 1:] + padded[1:, 1:]) / 4
    img = Image.fromarray((corners * 255).astype(np.uint8), "L")
    # Corners sit on the cell grid; a (w+1)x(h+1) corner grid stretched over the patch is the bilinear vertex fade.
    up = img.resize((w * CELL_PX + 1, h * CELL_PX + 1), Image.BILINEAR).crop((0, 0, w * CELL_PX, h * CELL_PX))
    return np.asarray(up, dtype=float) / 255


def preview(overlay, sea, strength, fade):
    """Tile the overlay at CELL_PX per cell over a flat sea and blend it in with the patch fade."""
    w, h = PATCH_CELLS
    tile = overlay.resize((8 * CELL_PX, 8 * CELL_PX), Image.LANCZOS)
    tiled = Image.new("RGBA", (w * CELL_PX, h * CELL_PX))
    for ox in range(0, w * CELL_PX, tile.width):
        for oy in range(0, h * CELL_PX, tile.height):
            tiled.paste(tile, (ox, oy))
    t = np.asarray(tiled, dtype=float) / 255
    a = t[..., 3] * fade * strength
    base = np.array(sea, dtype=float) / 255
    rgb = base * (1 - a[..., None]) + t[..., :3] * a[..., None]
    return Image.fromarray((rgb * 255 + 0.5).astype(np.uint8), "RGB")


def font(size):
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(columns, path):
    """Rows are sea depths, columns are overlays; each column heading names its overlay."""
    w, h = PATCH_CELLS[0] * CELL_PX, PATCH_CELLS[1] * CELL_PX
    gap, left, top, title_h = 16, 150, 70, 60
    W = left + len(columns) * (w + gap)
    H = title_h + top + len(SEA) * (h + gap) + 40
    out = Image.new("RGB", (W, H), (24, 26, 28))
    d = ImageDraw.Draw(out)
    d.text((16, 14), "Kelp forest overlay candidates (ticket 38)", fill=(235, 235, 235), font=font(28))
    d.text((16, H - 32), f"Game scale {CELL_PX} px per cell; overlay repeats every 8x8 cells; patch edges fade as "
           "SectionLayer_Reef draws them; deep at 0.7 strength. Sea is a flat fill.", fill=(170, 170, 170), font=font(16))
    fade = patch_strength(7)
    for c, (label, overlay) in enumerate(columns):
        x = left + c * (w + gap)
        d.text((x, title_h + 20), label, fill=(235, 235, 235), font=font(24))
        for r, (sea_name, sea) in enumerate(SEA.items()):
            y = title_h + top + r * (h + gap)
            out.paste(preview(overlay, sea, STRENGTH[sea_name], fade), (x, y))
            if c == 0:
                d.text((16, y + h // 2 - 12), sea_name, fill=(200, 200, 200), font=font(20))
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print(path)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    made = {}
    for name, make in CANDIDATES.items():
        made[name] = make()
        made[name].save(out / f"KelpOverlay-{name}.png")
        print(out / f"KelpOverlay-{name}.png")
    reef = Image.open(Path(__file__).parent.parent / "reef" / "ReefOverlay_master512.png").convert("RGBA")
    labels = {"A-kelp-shadow": "A  kelp shadow", "B-kelp-fronds": "B  kelp fronds (original)",
              "C-kelp-canopy": "C  kelp canopy", "B2-kelp-fronds-brown": "B2  brown fronds (Cape Town)"}
    if "--sheet" in sys.argv:  # the first round: reef beside A, B and C
        columns = [("Reef (approved)", reef)] + [(labels[n], made[n]) for n in ("A-kelp-shadow", "B-kelp-fronds",
                                                                              "C-kelp-canopy")]
        sheet(columns, Path(sys.argv[sys.argv.index("--sheet") + 1]))
    if "--b2-sheet" in sys.argv:  # the revision of the user's pick: reef beside B and B2
        columns = [("Reef (approved)", reef)] + [(labels[n], made[n]) for n in ("B-kelp-fronds", "B2-kelp-fronds-brown")]
        sheet(columns, Path(sys.argv[sys.argv.index("--b2-sheet") + 1]))
