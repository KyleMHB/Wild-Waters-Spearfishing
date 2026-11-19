"""Procedural candidates for the urchin barren look (threat events ticket 02, part 1).

An urchin barren is reef or kelp in the sea that urchins have grazed bare (GLOSSARY "Urchin barren"). It is drawn the way the
reef and kelp overlays are: a 512x512 RGBA texture that tiles every 8x8 cells (64 px per cell), alpha-blended under the water
surface by a SectionLayer_FloorOverlay, with the patch edges faded and deep cells at 0.7 strength. Colour is what shows
through the water and alpha is how strongly. No black outline: it is under the surface, like the reef.

The decisions ask for "the reef overlay drained of colour with a scatter of small dark urchins". The three candidates differ in
structure, because each structure means different part 2 code:

- A coralline rock: one texture for every barren cell, whatever grew there. The reef's rock shelves, drawn pale pink-grey
  (the crust of coralline algae that real barrens show), over a faint pale wash, with urchins. One new layer.
- B drained floor: one texture per floor. The approved reef, brown kelp and olive kelp overlays each drained of colour,
  lightened and thinned, over a faint pale wash, with urchins. Three textures; the layer picks one by the cell's old mark.
- C urchins over the floor: one texture drawn on top of the unchanged reef or kelp overlay: a pale wash that dulls what is
  under it, and denser urchins. The reef and kelp layers keep drawing barren cells, so barren kelp would still sway.

Urchins are dark purple-black discs about 6 px across at 64 px per cell (3 px at normal zoom), with a soft spine halo and a
small highlight to the upper left (light from the upper left). Fine spines would vanish at game size. Every urchin is drawn at
its wrapped offsets and every noise field is periodic, so the tile repeats without seams.

Usage: python -I urchin_barren_art.py <out_dir> [<sheet.png>]

Writes UrchinBarren-<candidate>.png (B: one per floor) into out_dir; each is its own 512 px master, the game texture's size and
tiling, so there is no separate master. Never writes to Textures/. The sheet imports the artificial reef script's water model
(sea fills, floor fade, font) and reads the approved reef and kelp masters; the candidate PNGs depend on the masters only for B.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

N = 512
CELL = 64  # texture pixels per cell
ART = Path(__file__).resolve().parent.parent

URCHIN_BODY = np.array([0.12, 0.07, 0.14])
URCHIN_SPINES = np.array([0.16, 0.10, 0.17])
URCHIN_SHINE = np.array([0.40, 0.28, 0.42])
URCHIN_R = 3.0  # body radius in texture px
URCHIN_ALPHA = 0.92

CORALLINE = np.array([0.74, 0.62, 0.64])  # pale pink-grey crust
DRAINED = np.array([0.66, 0.64, 0.60])  # neutral pale stone
WASH = np.array([0.70, 0.67, 0.60])  # pale grazed floor between the rock


def periodic_noise(seed, low, high):
    """Smooth noise that tiles: random phases on frequencies between low and high cycles per tile (as reef_art.py)."""
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


def to_image(rgb, alpha):
    rgba = np.dstack([np.clip(rgb, 0, 1), np.clip(alpha, 0, 1)])
    return Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), "RGBA")


def load(name):
    return np.asarray(Image.open(name).convert("RGBA"), dtype=float) / 255


def place_urchins(seed, per_cell, clump_seed, clump):
    """Urchin centres: a dart throw with a wrapped minimum spacing, thinned by a tiling density field so they gather in
    groups as grazing fronts do. clump 0 is even; 1 leaves the sparse parts nearly empty."""
    rng = np.random.default_rng(seed)
    density = smoothstep(-1.2, 1.2, periodic_noise(clump_seed, 2, 6))
    keep = (1 - clump) + clump * density
    target = int(per_cell * (N / CELL) ** 2)
    spacing = 2 * URCHIN_R + 2.0
    points = []
    tries = 0
    while len(points) < target and tries < target * 60:
        tries += 1
        p = rng.random(2) * N
        if rng.random() > keep[int(p[1]), int(p[0])] ** 1.5:
            continue
        if points:
            d = np.abs(np.array(points) - p)
            d = np.minimum(d, N - d)
            if (np.hypot(d[:, 0], d[:, 1]) < spacing).any():
                continue
        points.append(p)
    radii = URCHIN_R * (0.8 + 0.4 * rng.random(len(points)))
    return np.array(points), radii


def urchin_layer(points, radii):
    """RGB and alpha of the urchins alone: antialiased discs with a spine halo and a highlight, drawn wrapped."""
    rgb = np.zeros((N, N, 3))
    alpha = np.zeros((N, N))
    y, x = np.mgrid[0:N, 0:N] + 0.5
    for (cx, cy), r in zip(points, radii):
        reach = int(r + 4)
        for ox in (-N, 0, N):
            for oy in (-N, 0, N):
                px, py = cx + ox, cy + oy
                x0, x1 = max(int(px) - reach, 0), min(int(px) + reach + 1, N)
                y0, y1 = max(int(py) - reach, 0), min(int(py) + reach + 1, N)
                if x0 >= x1 or y0 >= y1:
                    continue
                sx, sy = x[y0:y1, x0:x1], y[y0:y1, x0:x1]
                d = np.hypot(sx - px, sy - py)
                body = np.clip(r + 0.5 - d, 0, 1)
                halo = np.clip(r + 1.8 - d, 0, 1) * 0.55 * (1 - body)
                shine = np.clip(r * 0.45 + 0.5 - np.hypot(sx - (px - r * 0.35), sy - (py - r * 0.35)), 0, 1) * body
                colour = (URCHIN_BODY * (1 - shine[..., None]) + URCHIN_SHINE * shine[..., None]) * body[..., None] \
                    + URCHIN_SPINES * halo[..., None]
                a = body * URCHIN_ALPHA + halo
                old = alpha[y0:y1, x0:x1]
                new = a + old * (1 - a)  # urchins never overlap by spacing; this only joins halos
                rgb[y0:y1, x0:x1] = (colour + rgb[y0:y1, x0:x1] * (old * (1 - a))[..., None]) / np.maximum(new, 1e-6)[..., None]
                alpha[y0:y1, x0:x1] = new
    return rgb, alpha


def stack(under_rgb, under_a, over_rgb, over_a):
    """Porter-Duff 'over' of two straight-alpha layers."""
    a = over_a + under_a * (1 - over_a)
    rgb = (over_rgb * over_a[..., None] + under_rgb * (under_a * (1 - over_a))[..., None]) / np.maximum(a, 1e-6)[..., None]
    return rgb, a


def wash(seed, strength):
    """A faint pale grazed floor over the whole tile, mottled so it is not a flat sheet."""
    m = periodic_noise(seed, 6, 30)
    a = strength * (0.85 + 0.15 * np.tanh(m))
    rgb = WASH[None, None, :] * (0.95 + 0.05 * np.tanh(m))[..., None]
    return rgb, a


def with_urchins(base_rgb, base_a, seed, per_cell, clump):
    u_rgb, u_a = urchin_layer(*place_urchins(seed, per_cell, seed + 1, clump))
    return to_image(*stack(base_rgb, base_a, u_rgb, u_a))


def coralline_rock():
    """A: the reef's rock shelves in pale coralline pink-grey over a faint wash, with urchins; one texture for all."""
    reef = load(ART / "reef" / "ReefOverlay_master512.png")
    lum = reef[..., :3].mean(axis=2)
    cover = reef[..., 3] / max(reef[..., 3].max(), 1e-6)
    # Keep the reef's lighting: its rock is lit from the upper left, so relative brightness carries over.
    light = (lum - lum[cover > 0.5].mean()) * 4.0
    rock_rgb = CORALLINE[None, None, :] * (1 + light)[..., None]
    rock_a = cover * 0.62
    w_rgb, w_a = wash(71, 0.16)
    rgb, a = stack(w_rgb, w_a, rock_rgb, rock_a)
    return with_urchins(rgb, a, 72, 6.0, 0.6)


def drained(master_name, seed, thin):
    """B: an approved overlay drained of colour, lightened and thinned by `thin`, over a faint wash, with urchins."""
    src = load(ART / master_name)
    lum = src[..., :3].mean(axis=2)
    cover = src[..., 3]
    shown = cover > 0.3
    light = (lum - lum[shown].mean()) * 3.0
    rgb_d = DRAINED[None, None, :] * (1 + light)[..., None]
    a_d = cover * thin
    w_rgb, w_a = wash(seed, 0.14)
    rgb, a = stack(w_rgb, w_a, rgb_d, a_d)
    return with_urchins(rgb, a, seed + 1, 6.0, 0.6)


def drained_reef():
    return drained("reef/ReefOverlay_master512.png", 81, 1.1)


def drained_kelp_brown():
    return drained("kelp/KelpOverlayBrown_master512.png", 83, 0.55)


def drained_kelp_olive():
    return drained("kelp/KelpOverlayOlive_master512.png", 85, 0.6)


def urchins_over():
    """C: drawn over the unchanged reef or kelp: a pale wash to dull it, and denser urchins."""
    w_rgb, w_a = wash(91, 0.34)
    return with_urchins(w_rgb, w_a, 92, 8.0, 0.75)


# Candidate key -> {floor it covers: texture maker}; "any" means one texture over reef and both kelps.
CANDIDATES = {
    "A-coralline-rock": {"any": coralline_rock},
    "B-drained-floor": {"Reef": drained_reef, "KelpBrown": drained_kelp_brown, "KelpOlive": drained_kelp_olive},
    "C-urchins-over-floor": {"any": urchins_over},
}
LABELS = {"A-coralline-rock": "A  coralline rock", "B-drained-floor": "B  drained floor",
          "C-urchins-over-floor": "C  urchins over the floor"}
DRAWN_OVER = {"C-urchins-over-floor"}  # drawn on top of the reef or kelp layer, which keeps drawing the cell


def file_name(key, floor):
    return f"UrchinBarren-{key}.png" if floor == "any" else f"UrchinBarren-{key}-{floor}.png"


# --- Contact sheet -------------------------------------------------------------------------------------------------

FLOORS = [("Reef", "reef/ReefOverlay_master512.png", "reef"), ("KelpBrown", "kelp/KelpOverlayBrown_master512.png",
                                                                "brown kelp"),
          ("KelpOlive", "kelp/KelpOverlayOlive_master512.png", "olive kelp")]
SCENE_W, SCENE_H = 11, 7  # cells at 32 px
# A floor patch with a barren eating into its right side; the healthy and barren parts share a border.
PATCH = {(x, y) for x in range(1, 10) for y in range(1, 6)} | {(2, 0), (3, 0), (6, 6), (7, 6), (0, 3), (10, 2), (10, 3)}
BARREN = {(x, y) for x in range(5, 10) for y in range(2, 6)} | {(6, 1), (7, 1), (10, 3), (4, 4), (7, 6)}
CLOSE_W, CLOSE_H = 4, 3  # cells at 64 px: two healthy columns, two barren


def compose(water, sea, floor_tex, barren_tex, over, patch, barren, w, h, px):
    """The sea, the floor overlay on its cells and the barren on its own, each with SectionLayer_FloorOverlay's fade."""
    base = np.ones((h * px, w * px, 3)) * (np.array(water.SEA[sea]) / 255)
    strength = water.FLOOR_STRENGTH[sea]
    floor_cells = patch if over else patch - barren
    layers = [(floor_cells, floor_tex)]
    if barren_tex is not None:
        layers.append((barren, barren_tex))
    for cells, tex in layers:
        rgb, a = water.floor_layer(cells, tex, strength, w, h, px)
        base = base * (1 - a[..., None]) + rgb * a[..., None]
    return base


def to_rgb(base):
    return Image.fromarray((np.clip(base, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


def sheet(made, path):
    sys.path.insert(0, str(ART / "artificial-reef"))
    import artificial_reef_art as water  # noqa: E402  (the sea fills, floor fade and font only)

    floors = {key: Image.open(ART / name).convert("RGBA") for key, name, _ in FLOORS}
    px = 32
    sw, sh = SCENE_W * px, SCENE_H * px
    cw, ch = CLOSE_W * 64, CLOSE_H * 64
    gap, left, title_h, foot_h, head_h = 14, 130, 96, 64, 62
    block_w = sw + gap + cw + gap * 3
    W = left + 3 * block_w
    seas = list(water.SEA)
    row_h = max(sh, ch) + gap
    cand_h = head_h + len(seas) * row_h + gap
    rows = [("Healthy (approved)", None)] + [(LABELS[k], k) for k in made]
    H = title_h + len(rows) * cand_h + foot_h
    out = Image.new("RGB", (W, H), (24, 26, 28))
    d = ImageDraw.Draw(out)
    d.text((16, 12), "Urchin barren candidates (threat events ticket 02)", fill=(235, 235, 235), font=water.font(28))
    d.text((16, 52), "Each scene: a reef or kelp patch with a barren eating into its right side, 32 px per cell (normal "
           "zoom); beside it a close-up at 64 px per cell, left half healthy, right half barren. Awaiting the author's pick.",
           fill=(185, 185, 185), font=water.font(16))
    d.text((16, H - 50), "Model, not a game capture: flat sea fills sampled from Waves' water at noon, the approved overlays, "
           "SectionLayer_FloorOverlay's corner fade and deep strength 0.7, plain alpha blending. C is drawn over the unchanged "
           "floor; A and B replace it on barren cells.", fill=(160, 160, 160), font=water.font(15))
    close_patch = {(x, y) for x in range(-1, CLOSE_W + 1) for y in range(-1, CLOSE_H + 1)}
    close_barren = {(x, y) for x in range(CLOSE_W // 2, CLOSE_W + 1) for y in range(-1, CLOSE_H + 1)}
    y = title_h
    for label, key in rows:
        d.text((16, y), label, fill=(235, 235, 235), font=water.font(22))
        for f, (floor_key, _, floor_label) in enumerate(FLOORS):
            x = left + f * block_w
            d.text((x, y + 34), f"over {floor_label}", fill=(210, 210, 210), font=water.font(17))
            barren_tex = None
            over = False
            if key is not None:
                textures = made[key]
                barren_tex = textures.get("any") or textures[floor_key]
                over = key in DRAWN_OVER
            for r, sea in enumerate(seas):
                yy = y + head_h + r * row_h
                scene = compose(water, sea, floors[floor_key], barren_tex, over, PATCH,
                                BARREN if key is not None else set(), SCENE_W, SCENE_H, px)
                out.paste(to_rgb(scene), (x, yy))
                # Close-up: render one cell wider all round, so the crop shows no outer patch edge.
                big = compose(water, sea, floors[floor_key], barren_tex, over,
                              {(a + 1, b + 1) for a, b in close_patch},
                              {(a + 1, b + 1) for a, b in close_barren} if key is not None else set(),
                              CLOSE_W + 4, CLOSE_H + 4, 64)
                out.paste(to_rgb(big[2 * 64:(2 + CLOSE_H) * 64, 2 * 64:(2 + CLOSE_W) * 64]), (x + sw + gap, yy))
                if f == 0:
                    d.text((16, yy + 6), sea, fill=(170, 170, 170), font=water.font(14))
        y += cand_h
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print(path)


def seam_check(img):
    """2x2 tiling of a texture, for looking at the joins."""
    out = Image.new("RGBA", (2 * N, 2 * N))
    for ox in (0, N):
        for oy in (0, N):
            out.paste(img, (ox, oy))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    made = {}
    for key, textures in CANDIDATES.items():
        made[key] = {}
        for floor, make in textures.items():
            img = make()
            made[key][floor] = img
            img.save(out_dir / file_name(key, floor))
            print(out_dir / file_name(key, floor))
    if len(sys.argv) > 2:
        sheet(made, Path(sys.argv[2]))
