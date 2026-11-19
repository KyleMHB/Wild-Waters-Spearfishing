"""Procedural candidates for the "Restore sea floor" designator (fish recovery ticket 06, part 1).

Two pieces per candidate, both 64x64 RGBA, drawn at 4x (256 px masters) and reduced with Lanczos:

- Icon: the orders-menu designator button art (vanilla's slot is `UI/Designators/<Name>`, 64x64). Drawn like the mod's approved
  items (fry pail, foam buoy): a black exterior contour about 2.5 px at 64 px, black 1.5 px lines between materials, a few
  broad shapes lit from the upper left, muted colour.
- Mark: the designation drawn on each designated cell (vanilla's slot is `Designations/<Name>`, one cell, drawn above the
  map). It sits over Waves' water, sea floor, reef and kelp, so it is a simple light glyph with the same black contour and
  full opacity, unlike the artificial reef, which is under the surface.

The idea: a diver moving coral and kelp cuttings onto bare sea floor to restore it.

Usage: python -I restoration_art.py <out_dir> [<sheet.png>]

Writes Restoration-<key>-Icon.png, -Mark.png and their _master256 files into out_dir. Never writes to Textures/. The sheet
reuses the artificial reef script's water model (scene) only; the candidate PNGs do not depend on it.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

S = 256  # master size; exports are S // 4
OUT = 64
EXT = 10  # exterior contour on the master: 2.5 px at 64
MAT = 6  # line between materials on the master: 1.5 px at 64

# Muted palette, saturation kept at or under about 0.6 (vanilla production and resources sit near 0.4-0.6).
SAND = (184, 164, 124)
CORAL = (206, 116, 98)
KELP = (122, 132, 66)
STEEL = (128, 134, 140)
GLOVE = (64, 84, 108)
ARROW = (226, 222, 206)
GLYPH = (236, 232, 220)


# --- Shape masks on the 256 master ---------------------------------------------------------------------------------

def canvas():
    return Image.new("L", (S, S), 0)


def as_mask(img):
    return np.asarray(img, dtype=np.uint8) > 127


def ellipse(cx, cy, rx, ry):
    img = canvas()
    ImageDraw.Draw(img).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    return as_mask(img)


def mound(cx, cy, rx, ry):
    """A sand mound: the top half of an ellipse with a flat base."""
    m = ellipse(cx, cy, rx, ry)
    y = np.arange(S)[:, None]
    return m & (y <= cy + ry * 0.35)


def polygon(points):
    img = canvas()
    ImageDraw.Draw(img).polygon([tuple(p) for p in points], fill=255)
    return as_mask(img)


def stroke(points, width):
    """A round-capped, round-jointed polyline."""
    img = canvas()
    d = ImageDraw.Draw(img)
    d.line([tuple(p) for p in points], fill=255, width=int(width), joint="curve")
    r = width / 2
    for x, y in points:
        d.ellipse((x - r, y - r, x + r, y + r), fill=255)
    return as_mask(img)


def union(*masks):
    out = np.zeros((S, S), bool)
    for m in masks:
        out |= m
    return out


def grow(mask, r):
    return ndimage.distance_transform_edt(~mask) <= r


def sprig(bx, by, h, w, lean=0.0):
    """A branching coral cutting standing on (bx, by), height h, branch width w."""
    top = (bx + lean * h, by - h)
    trunk = [(bx, by), (bx + lean * h * 0.5, by - h * 0.5), top]
    left = [(bx + lean * h * 0.45, by - h * 0.45), (bx - h * 0.30, by - h * 0.70), (bx - h * 0.34, by - h * 0.92)]
    right = [(bx + lean * h * 0.3, by - h * 0.28), (bx + h * 0.30, by - h * 0.52), (bx + h * 0.36, by - h * 0.76)]
    twig = [(bx - h * 0.20, by - h * 0.62), (bx - h * 0.06, by - h * 0.86)]
    return union(stroke(trunk, w), stroke(left, w * 0.85), stroke(right, w * 0.85), stroke(twig, w * 0.7))


def kelp_blade(bx, by, h, w, bend=1.0):
    """A kelp frond: a tapered, gently S-curved blade rising from (bx, by)."""
    t = np.linspace(0, 1, 24)
    cx = bx + bend * w * 0.9 * np.sin(t * np.pi * 1.2)
    cy = by - h * t
    half = w * 0.5 * np.sin(np.pi * np.clip(t * 0.9 + 0.08, 0, 1)) + 1
    left = list(zip(cx - half, cy))
    right = list(zip(cx + half, cy))[::-1]
    return polygon(left + right)


# --- Rendering -----------------------------------------------------------------------------------------------------

def shade(mask):
    """Broad light from the upper left over a part's own pillow-shaped height."""
    h = ndimage.distance_transform_edt(mask)
    h = np.minimum(h, 18) / 18
    h = ndimage.gaussian_filter(h, 3)
    gy, gx = np.gradient(h)
    return np.clip(-(gx + gy) * 14, -1, 1)


def render(parts, ext=EXT, mat=MAT):
    """parts: [(mask, rgb)] back to front. Black exterior contour outside the union, black lines between parts."""
    rgb = np.zeros((S, S, 3))
    body = union(*(m for m, _ in parts))
    alpha = grow(body, ext)
    for mask, colour in parts:
        rgb[grow(mask, mat) & body] = 0  # the line where this part covers the ones behind it
        light = shade(mask)
        col = np.array(colour) / 255 * (0.86 + 0.24 * light)[..., None]
        rgb[mask] = np.clip(col[mask], 0, 1)
    out = np.dstack([rgb, alpha.astype(float)])
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA")


def export(master):
    return master.resize((OUT, OUT), Image.LANCZOS)


def down_arrow(cx, top, h, w):
    shaft = stroke([(cx, top), (cx, top + h * 0.55)], w * 0.42)
    head = polygon([(cx - w * 0.6, top + h * 0.45), (cx + w * 0.6, top + h * 0.45), (cx, top + h)])
    return shaft | head


# --- Candidates ----------------------------------------------------------------------------------------------------

def icon_a():
    """A, cutting and arrow: a coral cutting and a kelp blade set into a sand mound, an arrow pointing down at the spot."""
    floor = mound(128, 222, 104, 44)
    coral = sprig(116, 206, 112, 17, lean=0.05)
    kelp = kelp_blade(176, 210, 96, 22, bend=0.6)
    arrow = down_arrow(56, 34, 74, 40)
    return render([(floor, SAND), (kelp, KELP), (coral, CORAL), (arrow, ARROW)])


def mark_a():
    coral = sprig(150, 214, 128, 22, lean=0.04)
    ground = stroke([(96, 220), (204, 220)], 16)
    arrow = down_arrow(72, 34, 92, 54)
    return render([(ground | coral | arrow, GLYPH)], ext=EXT * 0.8)


def frame_box(x0, y0, x1, y1, w):
    return stroke([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], w)


def icon_b():
    """B, nursery frame: a low steel frame on sand with cuttings tied along its rungs, the way reef nurseries grow them."""
    floor = mound(128, 222, 112, 46)
    frame = frame_box(40, 120, 216, 214, 15) | stroke([(40, 167), (216, 167)], 11)
    corals = union(sprig(78, 167, 72, 14, lean=0.04), sprig(176, 167, 66, 14, lean=-0.04))
    kelp = kelp_blade(128, 170, 104, 22, bend=0.5)
    return render([(floor, SAND), (kelp, KELP), (corals, CORAL), (frame, STEEL)])


def mark_b():
    frame = frame_box(38, 120, 218, 222, 18)
    coral = sprig(128, 196, 150, 22)
    return render([(frame | coral, GLYPH)], ext=EXT * 0.8)


def glove_hand():
    """A diver's gloved hand reaching down from the upper right, fingers closed round a cutting's base."""
    cuff = polygon([(208, 14), (240, 44), (222, 68), (188, 40)])
    palm = polygon([(190, 38), (226, 70), (186, 120), (146, 112), (138, 84), (158, 54)])
    fingers = union(stroke([(150, 96), (126, 116), (118, 132)], 22),
                    stroke([(158, 110), (138, 130), (134, 146)], 20))
    thumb = stroke([(150, 70), (126, 80), (112, 98)], 22)
    return cuff, palm | fingers | thumb


def icon_c():
    """C, diver's hand: a gloved hand lowering a coral cutting to a bare sand patch; a kelp cutting already planted."""
    floor = mound(110, 226, 100, 40)
    kelp = kelp_blade(50, 214, 84, 20, bend=0.5)
    coral = sprig(116, 196, 92, 16, lean=0.08)
    cuff, hand = glove_hand()
    return render([(floor, SAND), (kelp, KELP), (coral, CORAL), (cuff, STEEL), (hand, GLOVE)])


def mark_c():
    """The C glyph tests one colour accent: coral-pink tips over the light sprig, on a light ground line."""
    ground = stroke([(60, 220), (196, 220)], 16)
    coral = sprig(128, 212, 160, 22)
    tips = union(*(ellipse(x, y, 15, 15) for x, y in ((128, 52), (74, 66), (186, 90))))
    return render([(ground | coral, GLYPH), (tips, CORAL)], ext=EXT * 0.8)


CANDIDATES = {
    "A": ("cutting and arrow", icon_a, mark_a),
    "B": ("nursery frame", icon_b, mark_b),
    "C": ("diver's hand", icon_c, mark_c),
}


# --- Measurements --------------------------------------------------------------------------------------------------

def outline_px(img):
    """Median black run inward from the alpha edge along rows and columns (every channel <= 25), at 64 px per cell."""
    a = np.asarray(img, dtype=float)
    solid = a[..., 3] > 127
    black = solid & (a[..., :3].max(axis=2) <= 25)
    runs = []
    for arr_s, arr_b in ((solid, black), (solid.T, black.T)):
        for row_s, row_b in zip(arr_s, arr_b):
            idx = np.flatnonzero(row_s)
            if idx.size == 0:
                continue
            for start, step in ((idx[0], 1), (idx[-1], -1)):
                n, i = 0, start
                while 0 <= i < row_s.size and row_b[i]:
                    n, i = n + 1, i + step
                runs.append(n)
    return float(np.median(runs))


def saturation_p90(img):
    a = np.asarray(img, dtype=float) / 255
    keep = (a[..., 3] > 0.5) & (a[..., :3].max(axis=2) > 0.1)
    rgb = a[..., :3][keep]
    mx, mn = rgb.max(axis=1), rgb.min(axis=1)
    return float(np.percentile((mx - mn) / np.maximum(mx, 1e-6), 90))


# --- Sheet ---------------------------------------------------------------------------------------------------------

def font(size):
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def over(base, sprite):
    s = np.asarray(sprite, dtype=float) / 255
    a = s[..., 3:4]
    return base * (1 - a) + s[..., :3] * a


def marked(scene_img, mark, cells, px):
    base = np.asarray(scene_img, dtype=float) / 255
    small = mark.resize((px, px), Image.LANCZOS)
    for cx, cy in cells:
        region = base[cy * px:(cy + 1) * px, cx * px:(cx + 1) * px]
        base[cy * px:(cy + 1) * px, cx * px:(cx + 1) * px] = over(region, small)
    return Image.fromarray((np.clip(base, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


def button(icon, size=76):
    """A plain model of an orders-menu button: dark square, light rim, icon at its own 64 px. Not vanilla's texture."""
    b = Image.new("RGB", (size, size), (52, 56, 60))
    d = ImageDraw.Draw(b)
    d.rectangle((0, 0, size - 1, size - 1), outline=(110, 114, 118), width=2)
    b.paste(icon, ((size - OUT) // 2, (size - OUT) // 2), icon)
    return b


def sheet(made, path):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "artificial-reef"))
    import artificial_reef_art as water  # noqa: E402  (the sea, reef and kelp model only)

    art = Path(__file__).resolve().parent.parent
    reef = Image.open(art / "reef" / "ReefOverlay_master512.png").convert("RGBA")
    kelp = Image.open(art / "kelp" / "KelpOverlayBrown_master512.png").convert("RGBA")

    px = 32
    sw, sh = 12, 6
    reef_cells = {(x, y) for x in range(0, 4) for y in range(0, 6)}
    kelp_cells = {(x, y) for x in range(8, 12) for y in range(0, 6)}
    drag = [(x, y) for x in range(2, 10) for y in range(1, 5)]  # a drag across reef, bare floor and kelp

    close_px, close_w, close_h = 64, 3, 2
    every = {(x, y) for x in range(close_w) for y in range(close_h)}
    backgrounds = [("bare sea floor", set(), set()), ("reef", every, set()), ("brown kelp", set(), every)]

    gap, left, title_h, foot_h = 18, 250, 100, 84
    icon_w = 76 + gap + 128
    close_tile = close_w * close_px
    scene_w = sw * px
    row_h = max(close_h * close_px, sh * px) + 40
    W = left + icon_w + gap * 2 + 3 * (close_tile + gap) + 2 * (scene_w + gap)
    H = title_h + len(made) * (row_h + gap) + foot_h
    out = Image.new("RGB", (W, H), (24, 26, 28))
    d = ImageDraw.Draw(out)
    d.text((16, 12), "Restore sea floor: icon and mark candidates (fish recovery ticket 06)", fill=(235, 235, 235),
           font=font(28))
    d.text((16, 54), "Icon on a model menu button at 64 px and 2x. Mark at 64 px per cell over bare floor, reef and kelp, "
           "and dragged across all three at 32 px per cell (normal zoom). Awaiting the author's pick.",
           fill=(185, 185, 185), font=font(17))
    y = title_h + 24
    for key, (name, icon, mark, _) in made.items():
        d.text((16, y + 20), f"{key}  {name}", fill=(235, 235, 235), font=font(22))
        x = left
        d.text((x, y - 22), "icon 64 px, 2x", fill=(200, 200, 200), font=font(15))
        out.paste(button(icon), (x, y))
        big = icon.resize((128, 128), Image.NEAREST)
        out.paste(big, (x + 76 + gap, y), big)
        x += icon_w + gap * 2
        for label, rc, kc in backgrounds:
            d.text((x, y - 22), f"mark on {label}, 64 px", fill=(200, 200, 200), font=font(15))
            tile = water.scene(None, "Shallow ocean", reef, kelp, w=close_w, h=close_h, reef_cells=rc, kelp_cells=kc,
                               built=[], px=close_px)
            out.paste(marked(tile, mark, [(cx, cy) for cx in range(close_w) for cy in range(close_h)], close_px), (x, y))
            x += close_tile + gap
        for sea in ("Shallow ocean", "Deep ocean"):
            d.text((x, y - 22), f"{sea}, {px} px per cell: reef | bare | kelp", fill=(200, 200, 200), font=font(15))
            base = water.scene(None, sea, reef, kelp, w=sw, h=sh, reef_cells=reef_cells, kelp_cells=kelp_cells,
                               built=[], px=px)
            out.paste(marked(base, mark, drag, px), (x, y))
            x += scene_w + gap
        y += row_h + gap
    d.text((16, H - 74), "Model, not a game capture: flat sea fill sampled from Waves' water at noon, reef and kelp "
           "overlays as the artificial reef sheet draws them, plain alpha blend; the mark is drawn on top at full "
           "opacity, as a designation is.", fill=(160, 160, 160), font=font(15))
    d.text((16, H - 50), "In the game only bare sea floor can be marked (CanDesignateCell refuses reef and kelp); the "
           "marks on reef and kelp show readability beside them, as the ticket asks. The menu button is a plain model, "
           "not vanilla's.", fill=(160, 160, 160), font=font(15))
    d.text((16, H - 26), "No vanilla designator icon or mark is on the sheet: no extracted copy of Ludeon's art source "
           "was at hand, so that comparison is pending.", fill=(160, 160, 160), font=font(15))
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print(path)


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    made = {}
    for key, (name, make_icon, make_mark) in CANDIDATES.items():
        stem = f"Restoration-{key}-{name.replace(chr(39), '').replace(' ', '-')}"
        pieces = []
        for part, make in (("Icon", make_icon), ("Mark", make_mark)):
            master = make()
            master.save(out_dir / f"{stem}-{part}_master256.png")
            small = export(master)
            small.save(out_dir / f"{stem}-{part}.png")
            pieces.append(small)
            print(f"{stem}-{part}.png  outline {outline_px(small):.1f} px  saturation p90 {saturation_p90(small):.2f}")
        made[key] = (name, pieces[0], pieces[1], stem)
    if len(sys.argv) > 2:
        sheet(made, Path(sys.argv[2]))
