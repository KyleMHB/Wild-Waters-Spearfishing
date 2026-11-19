"""Procedural candidates for the artificial reef (fish recovery ticket 02, part 1).

The artificial reef is a 1x1 building sunk on bare sea floor; it stays under the surface until it turns into reef about 15
days later. Each candidate is a 64x64 RGBA texture (one cell at 64 px per cell), drawn at 4x and reduced.

- The colour is greyscale so it can take the stone or steel it is built from: RimWorld multiplies a stuff-made building's
  texture by the stuff colour. The preview multiplies by the vanilla stuffProps colours below.
- It is seen through the water like the approved reef overlay, so it has no black vanilla outline: a soft dark edge and a
  faint contact shadow to the lower right (light from the upper left) instead, and body alpha below 1 so the sea shows through.
- `crust()` models how a candidate could look partway to reef: a reef-coloured growth over the top surfaces. Whether the
  building has growth stages at all is a part 2 decision; the sheet labels it as a proposal.

Usage: python artificial_reef_art.py <out_dir> [--sheet <sheet.png>] [--textures <Textures dir>]

--textures writes the approved pick, C with its growth stages (art/artificial-reef/APPROVAL.md), into the mod's texture
folder: Things/Spearfishing/Building/ArtificialReef/ArtificialReef.png (built), _HalfWay and _NearlyReef. Each is the 256 px
master, with crust() at 0 / 0.5 / 0.9 for the stages, reduced to 64 px with Lanczos; still greyscale, as the game tints them.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 256  # master pixels per cell; the texture is S // 4
OUT = 64
BODY_ALPHA = 0.8
SHADOW_ALPHA = 0.32


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def grid(fill=1.0):
    """Cell coordinates 0..1, y down; fill > 1 enlarges the shapes drawn in them about the centre."""
    y, x = np.mgrid[0:S, 0:S]
    return 0.5 + ((x + 0.5) / S - 0.5) / fill, 0.5 + ((y + 0.5) / S - 0.5) / fill


def blur(a, radius):
    img = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "L")
    return np.asarray(img.filter(ImageFilter.GaussianBlur(radius)), dtype=float) / 255


def shade(height):
    """Light from the upper left: positive where the surface faces up-left."""
    gy, gx = np.gradient(height)
    return np.clip(-(gx + gy) * S * 0.9, -1, 1)


def noise(seed, scale):
    rng = np.random.default_rng(seed)
    small = rng.random((scale, scale))
    img = Image.fromarray((small * 255).astype(np.uint8), "L").resize((S, S), Image.BICUBIC)
    return np.asarray(img, dtype=float) / 255


def compose(height, cover, albedo, seed):
    """Greyscale RGBA master: lit body, soft dark rim, contact shadow down-right; no black outline."""
    light = shade(blur(height, 3))
    grey = albedo * (0.78 + 0.32 * light) * (0.85 + 0.15 * height)
    grey *= 0.92 + 0.08 * noise(seed, 24)  # weathering, faint at game size
    rim = 1 - smoothstep(0.0, 0.06, blur(cover, 6) - 0.5)  # darkens a band just inside the edge
    grey *= 1 - 0.35 * rim * cover
    shift = int(S * 0.045)
    shadow = blur(np.roll(np.roll(cover, shift, 0), shift, 1), 8) * (1 - cover)
    alpha = cover * BODY_ALPHA + shadow * SHADOW_ALPHA
    grey = np.where(cover > 0, grey, 0.0)
    rgb = np.clip(np.dstack([grey] * 3), 0, 1)
    master = Image.fromarray((np.dstack([rgb, np.clip(alpha, 0, 1)]) * 255 + 0.5).astype(np.uint8), "RGBA")
    return master, height, cover


def box(x, y, x0, y0, x1, y1):
    return ((x >= x0) & (x < x1) & (y >= y0) & (y < y1)).astype(float)


def stone_blocks():
    """A: a cairn of cut stone blocks, three on the floor and one laid across them, gaps left for fish."""
    x, y = grid(1.18)
    height = np.zeros((S, S))
    cover = np.zeros((S, S))
    albedo = np.zeros((S, S))
    blocks = [  # (x0, y0, x1, y1, top height, albedo)
        (0.14, 0.16, 0.46, 0.44, 0.45, 0.78),
        (0.54, 0.20, 0.86, 0.48, 0.45, 0.74),
        (0.24, 0.56, 0.62, 0.84, 0.45, 0.76),
        (0.30, 0.30, 0.72, 0.62, 0.95, 0.92),  # the top block, across the others
    ]
    for x0, y0, x1, y1, h, a in blocks:
        b = box(x, y, x0, y0, x1, y1)
        # Bevel each block so its edges catch the light.
        edge = np.minimum.reduce([x - x0, x1 - x, y - y0, y1 - y])
        top = h * (0.85 + 0.15 * smoothstep(0, 0.04, edge))
        put = b * (top >= height)
        height = np.where(put > 0, top, height)
        albedo = np.where(put > 0, a, albedo)
        cover = np.maximum(cover, b)
    # Dark joints where a block sits on another.
    return compose(height, cover, albedo, 31)


def reef_ball():
    """B: a cast concrete reef ball, a dome with round holes for fish to shelter in."""
    x, y = grid()
    r = np.hypot(x - 0.5, y - 0.5) / 0.41
    cover = (r < 1).astype(float)
    height = np.sqrt(np.clip(1 - r * r, 0, 1))
    albedo = np.full((S, S), 0.85)
    holes = [(0.5, 0.5, 0.075)] + [(0.5 + 0.22 * np.cos(a), 0.5 + 0.22 * np.sin(a), 0.06)
                                   for a in np.radians([20, 92, 164, 236, 308])]
    for hx, hy, hr in holes:
        d = np.hypot(x - hx, y - hy) / hr
        inside = smoothstep(1.0, 0.75, d)
        albedo = albedo * (1 - 0.8 * inside)
        height = height - 0.25 * inside
        lip = smoothstep(1.35, 1.0, d) * (1 - inside)
        albedo = albedo * (1 + 0.08 * lip)
    return compose(height, cover, albedo, 32)


def steel_frame():
    """C: a welded steel pyramid frame: square base, corner legs to a top ring, one crossbar each side."""
    x, y = grid(1.1)
    w = 0.075  # bar width; about 2.4 px at 32 px per cell
    lo, hi = 0.13, 0.87
    top0, top1 = 0.38, 0.62

    def bar(ax, ay, bx, by, h0, h1):
        dx, dy = bx - ax, by - ay
        t = np.clip(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0, 1)
        d = np.hypot(x - (ax + t * dx), y - (ay + t * dy))
        on = (d < w / 2).astype(float)
        return on, (h0 + (h1 - h0) * t) * on

    corners = [(lo, lo), (hi, lo), (hi, hi), (lo, hi)]
    tops = [(top0, top0), (top1, top0), (top1, top1), (top0, top1)]
    bars = []
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        bars.append(bar(*a, *b, 0.25, 0.25))  # base square
        bars.append(bar(*tops[i], *tops[(i + 1) % 4], 1.0, 1.0))  # top ring
        bars.append(bar(*a, *tops[i], 0.25, 1.0))  # leg
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        tmid = ((tops[i][0] + tops[(i + 1) % 4][0]) / 2, (tops[i][1] + tops[(i + 1) % 4][1]) / 2)
        bars.append(bar(*mid, *tmid, 0.25, 1.0))  # crossbar up each face
    cover = np.zeros((S, S))
    height = np.zeros((S, S))
    for on, h in bars:
        cover = np.maximum(cover, on)
        height = np.maximum(height, h)
    # Round each bar so it reads as a tube.
    height = height + 0.15 * blur(cover, 2)
    albedo = np.full((S, S), 0.82)
    return compose(height, cover, albedo, 33)


CANDIDATES = {"A-stone-blocks": stone_blocks, "B-reef-ball": reef_ball, "C-steel-frame": steel_frame}
LABELS = {"A-stone-blocks": "A  stone blocks", "B-reef-ball": "B  reef ball", "C-steel-frame": "C  steel frame"}


def export(master):
    return master.resize((OUT, OUT), Image.LANCZOS)


# --- Preview model -------------------------------------------------------------------------------------------------
# Plain sea fills sampled from a noon capture of Waves' water, as the kelp sheet uses. Stuff colours from RimWorld 1.6/1.7
# Data/Core/Defs stuffProps (Steel in Items_Resource_Stuff.xml, stone blocks in Various_Stone.xml), read 2026-11-18.
SEA = {"Shallow ocean": (47, 89, 91), "Deep ocean": (32, 68, 81)}
FLOOR_STRENGTH = {"Shallow ocean": 1.0, "Deep ocean": 0.7}  # SectionLayer_FloorOverlay's shallow and deep strength
STUFF = {"Steel": (105, 105, 105), "Granite": (105, 95, 97), "Sandstone": (126, 104, 94), "Marble": (132, 135, 132),
         "Limestone": (158, 153, 135)}
REEF_RGB = np.array([0.13, 0.16, 0.14])  # the approved reef overlay's rock-shadow colour, a little lifted
CELL_PX = 32  # normal play zoom
SCENE = (12, 7)  # cells
REEF_CELLS = {(0, 1), (1, 1), (0, 2), (1, 2), (2, 2), (0, 3), (1, 3), (2, 3), (0, 4), (1, 4), (0, 5), (1, 5), (2, 4)}
KELP_CELLS = {(9, 1), (10, 1), (11, 1), (9, 2), (10, 2), (11, 2), (10, 3), (11, 3), (9, 4), (10, 4), (11, 4), (11, 5),
              (10, 5)}
BUILT = [(4, 3), (6, 2), (7, 5)]  # bare cells holding an artificial reef; one stands beside nothing


def crust(master, cover_height, amount, seed=40):
    """The master partway to reef: reef-coloured growth spreading over the top surfaces as amount goes 0..1."""
    height, cover = cover_height
    rgba = np.asarray(master, dtype=float) / 255
    n = noise(seed, 18) * 0.6 + noise(seed + 1, 48) * 0.4
    grow = smoothstep(1.05 - amount, 1.2 - amount, n + 0.25 * height) * cover
    texture = (0.8 + 0.5 * noise(seed + 2, 40))[..., None]
    rgb = rgba[..., :3] * (1 - grow[..., None]) + REEF_RGB * texture * grow[..., None]
    # Growth is as faint as the reef overlay (alpha about 0.55), so the build fades toward the reef it becomes.
    alpha = rgba[..., 3] * (1 - (1 - 0.55 / BODY_ALPHA) * grow * amount)
    return Image.fromarray((np.dstack([rgb, alpha]) * 255 + 0.5).astype(np.uint8), "RGBA")


def tinted(sprite, stuff):
    a = np.asarray(sprite, dtype=float) / 255
    rgb = a[..., :3] * (np.array(stuff) / 255)
    return Image.fromarray((np.dstack([rgb, a[..., 3]]) * 255 + 0.5).astype(np.uint8), "RGBA")


def over(base, sprite):
    """Alpha-blend an RGBA image onto an RGB float array (in place)."""
    s = np.asarray(sprite, dtype=float) / 255
    a = s[..., 3:4]
    return base * (1 - a) + s[..., :3] * a


def floor_layer(cells, overlay, strength, w, h, px):
    """SectionLayer_FloorOverlay's look: the overlay tiled every 8 cells, faded by mean-of-four-cells corner alpha."""
    marks = np.zeros((h, w))
    for cx, cy in cells:
        marks[cy, cx] = 1
    padded = np.pad(marks, 1)
    corners = (padded[:-1, :-1] + padded[1:, :-1] + padded[:-1, 1:] + padded[1:, 1:]) / 4
    fade = Image.fromarray((corners * 255).astype(np.uint8), "L").resize((w * px + 1, h * px + 1), Image.BILINEAR)
    fade = np.asarray(fade.crop((0, 0, w * px, h * px)), dtype=float) / 255
    tile = overlay.resize((8 * px, 8 * px), Image.LANCZOS)
    tiled = Image.new("RGBA", (w * px, h * px))
    for ox in range(0, w * px, tile.width):
        for oy in range(0, h * px, tile.height):
            tiled.paste(tile, (ox, oy))
    t = np.asarray(tiled, dtype=float) / 255
    a = t[..., 3] * fade * strength
    return t[..., :3], a


def scene(sprite, sea_name, reef, kelp, w=SCENE[0], h=SCENE[1], reef_cells=REEF_CELLS, kelp_cells=KELP_CELLS,
          built=BUILT, px=CELL_PX):
    base = np.ones((h * px, w * px, 3)) * (np.array(SEA[sea_name]) / 255)
    for cells, overlay in ((reef_cells, reef), (kelp_cells, kelp)):
        rgb, a = floor_layer(cells, overlay, FLOOR_STRENGTH[sea_name], w, h, px)
        base = base * (1 - a[..., None]) + rgb * a[..., None]
    if sprite is not None:
        small = sprite.resize((px, px), Image.LANCZOS)
        for cx, cy in built:
            region = base[cy * px:(cy + 1) * px, cx * px:(cx + 1) * px]
            base[cy * px:(cy + 1) * px, cx * px:(cx + 1) * px] = over(region, small)
    return Image.fromarray((np.clip(base, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


def font(size):
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(made, path):
    here = Path(__file__).parent.parent
    reef = Image.open(here / "reef" / "ReefOverlay_master512.png").convert("RGBA")
    kelp = Image.open(here / "kelp" / "KelpOverlayBrown_master512.png").convert("RGBA")
    sw, sh = SCENE[0] * CELL_PX, SCENE[1] * CELL_PX
    close = 2 * 64  # close-ups: 2x2 cells at the texture's own 64 px per cell, the build centred
    grow_w = 3 * 2 * CELL_PX  # growth stages: 3x3 cells at 2x play zoom
    gap, left, title_h, head_h = 16, 170, 92, 40
    stuff_names = ["Steel", "Granite", "Sandstone", "Marble"]
    stages = [("built", 0.0), ("half way", 0.5), ("nearly reef", 0.9), ("reef", None)]
    row_h = sh + 34 + grow_w + 24 + gap * 2
    W = left + len(stuff_names) * (close + gap) + 14 + len(stages) * (grow_w + gap)
    H = title_h + head_h + len(made) * (row_h + gap) + 50
    out = Image.new("RGB", (W, H), (24, 26, 28))
    d = ImageDraw.Draw(out)
    d.text((16, 12), "Artificial reef candidates (fish recovery ticket 02)", fill=(235, 235, 235), font=font(28))
    d.text((16, 52), "Granite build in the scenes, beside the approved reef (left) and brown kelp (right). "
           "Awaiting the author's pick.", fill=(185, 185, 185), font=font(17))
    d.text((16, H - 34), f"Model, not a game capture: flat sea fill, plain alpha blend. Scenes at {CELL_PX} px per cell; "
           "build at full strength in both depths (deep strength is a part 2 choice); stuff tint = texture x vanilla "
           "stuffProps colour. Growth stages are a proposal.", fill=(160, 160, 160), font=font(15))
    y = title_h + head_h
    for name, (master, hc) in made.items():
        sprite = export(master)
        d.text((16, y + sh // 2 - 14), LABELS[name], fill=(235, 235, 235), font=font(22))
        granite = tinted(sprite, STUFF["Granite"])
        for i, sea in enumerate(SEA):
            x = left + i * (sw + gap)
            d.text((x, y - 26), f"{sea}, {CELL_PX} px per cell", fill=(200, 200, 200), font=font(16))
            out.paste(scene(granite, sea, reef, kelp), (x, y))
        y2 = y + sh + 34
        for i, stuff in enumerate(stuff_names):
            x = left + i * (close + gap)
            d.text((x, y2 - 24), f"{stuff}, 64 px", fill=(200, 200, 200), font=font(15))
            tile = scene(tinted(sprite, STUFF[stuff]), "Shallow ocean", reef, kelp, w=2, h=2, reef_cells=set(),
                         kelp_cells=set(), built=[], px=64)
            base = np.asarray(tile, dtype=float) / 255
            region = base[32:96, 32:96]
            base[32:96, 32:96] = over(region, tinted(sprite, STUFF[stuff]))
            out.paste(Image.fromarray((base * 255 + 0.5).astype(np.uint8), "RGB"), (x, y2))
        gx0 = left + len(stuff_names) * (close + gap) + 14
        for j, (stage, amount) in enumerate(stages):
            x = gx0 + j * (grow_w + gap)
            d.text((x, y2 - 24), stage, fill=(200, 200, 200), font=font(15))
            px = 2 * CELL_PX
            if amount is None:  # the build is gone; its cell is one reef cell with the usual edge fade
                img = scene(None, "Shallow ocean", reef, kelp, w=3, h=3, reef_cells={(1, 1)}, kelp_cells=set(),
                            built=[], px=px)
            else:
                grown = crust(master, hc, amount)
                img = scene(tinted(grown, STUFF["Granite"]), "Shallow ocean", reef, kelp, w=3, h=3,
                            reef_cells=set(), kelp_cells=set(), built=[(1, 1)], px=px)
            out.paste(img, (x, y2))
        d.text((gx0, y2 + grow_w + 4), "growth, granite, shallow, 64 px per cell (proposal)",
               fill=(150, 150, 150), font=font(13))
        y += row_h + gap
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print(path)


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    made = {}
    for name, make in CANDIDATES.items():
        master, height, cover = make()
        made[name] = (master, (height, cover))
        master.save(out_dir / f"ArtificialReef-{name}_master256.png")
        export(master).save(out_dir / f"ArtificialReef-{name}.png")
        print(out_dir / f"ArtificialReef-{name}.png")
    if "--textures" in sys.argv:
        tex = Path(sys.argv[sys.argv.index("--textures") + 1]) / "Things/Spearfishing/Building/ArtificialReef"
        tex.mkdir(parents=True, exist_ok=True)
        master, hc = made["C-steel-frame"]
        for suffix, amount in (("", None), ("_HalfWay", 0.5), ("_NearlyReef", 0.9)):
            img = master if amount is None else crust(master, hc, amount)
            export(img).save(tex / f"ArtificialReef{suffix}.png")
            print(tex / f"ArtificialReef{suffix}.png")
    if "--sheet" in sys.argv:
        sheet(made, Path(sys.argv[sys.argv.index("--sheet") + 1]))
