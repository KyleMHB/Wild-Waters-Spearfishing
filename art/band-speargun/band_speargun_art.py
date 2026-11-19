"""Band speargun candidates for Spearfishing (gear tiers ticket 01). Same method as the approved pole spears
(art/pole-spear/pole_spear_art.py, art/steel-pole-spear/steel_pole_spear_art.py): flat two-tone shapes drawn at 8x, a 3 px black
outward outline at 128 px per cell (1.5 px at 64), reduced to a 128x128 canvas, horizontal with the muzzle and tip to the right.
The speargun reuses the spears' steel and wood colours so the tiers read as one family.

Parts, kept to a handful so they survive game zoom: a long stock, a pistol grip, a muzzle block, a steel shaft lying on top of the
stock with a small point past the muzzle, and the rubber band stretched from the muzzle back to its notch on the shaft.

  A  wooden stock (the spears' wood), grey polymer grip and muzzle.
  B  blue-grey anodised aluminium stock, dark grey grip and muzzle.

Usage: python -I band_speargun_art.py <out_dir> [vanilla_textures_dir]
  Writes BandSpeargun_A.png and BandSpeargun_B.png (128x128). With the extracted vanilla art source's Textures root (for example
  E:/AI/rimworld-lora/extracted), also writes contact_sheet.png beside the approved steel-tipped pole spear, vanilla guns and a
  vanilla body holding each weapon at the game's angles. Vanilla pixels go only into the sheet, never into the textures.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 8
S = 128
INK = (12, 10, 10, 255)

WOOD_LIGHT, WOOD_MID = (164, 122, 78, 255), (132, 94, 58, 255)        # the pole spears' shaft
STEEL_LIGHT, STEEL_DARK = (206, 210, 212, 255), (150, 156, 162, 255)  # the steel-tipped spear's head
BAND_LIGHT, BAND_DARK = (178, 76, 54, 255), (140, 56, 40, 255)        # red latex band, as dark as the buoy's ochre
POLY_LIGHT, POLY_DARK = (112, 116, 122, 255), (84, 88, 94, 255)       # grey polymer grip and muzzle
GRIP_LIGHT, GRIP_DARK = (84, 86, 90, 255), (62, 64, 68, 255)          # darker polymer, to part from B's blue-grey stock
ALU_LIGHT, ALU_MID = (112, 128, 146, 255), (84, 98, 114, 255)         # blue-grey anodised aluminium stock


def with_outline(layer, px):
    alpha = layer.getchannel("A").point(lambda v: 255 if v > 127 else 0)
    ring = alpha.filter(ImageFilter.MaxFilter(px * 2 + 1))
    base = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    base.paste(Image.new("RGBA", layer.size, INK), (0, 0), ring)
    base.alpha_composite(layer)
    return base


def speargun(stock_light, stock_mid, part_light, part_dark):
    W = S * SS
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def u(v):
        return v * SS

    def ux(v):
        return (v - 2) * SS  # drawn 2 px left of the x coordinates below, so the point's outline clears the canvas edge

    cy = 66  # the stock's centre line, in 128 px units; the shaft and band sit above it

    def rect(x0, y0, x1, y1, fill):
        d.rectangle([ux(x0), u(y0), ux(x1), u(y1)], fill=fill)

    def poly(pts, fill):
        d.polygon([(ux(x), u(y)) for x, y in pts], fill=fill)

    # Pistol grip under the rear of the stock, raked back.
    poly([(31, cy + 3), (41, cy + 3), (37, cy + 18), (27, cy + 17)], part_dark)
    poly([(31, cy + 3), (36, cy + 3), (32, cy + 17.5), (27, cy + 17)], part_light)
    # Stock: two-tone, light along the top as on the spears' shaft.
    rect(14, cy - 4, 100, cy + 4, stock_mid)
    rect(14, cy - 4, 100, cy - 1.5, stock_light)
    # Muzzle block, where the band is fixed.
    rect(96, cy - 6, 104, cy + 5, part_dark)
    rect(96, cy - 6, 104, cy - 2.5, part_light)
    # Steel shaft on top of the stock, running past the muzzle to a small point.
    rect(8, cy - 8, 114, cy - 4.5, STEEL_DARK)
    rect(8, cy - 8, 114, cy - 6.5, STEEL_LIGHT)
    poly([(124, cy - 6.25), (112, cy - 10.5), (114, cy - 6.25)], STEEL_LIGHT)
    poly([(124, cy - 6.25), (112, cy - 2), (114, cy - 6.25)], STEEL_DARK)
    # Rubber band: stretched from the muzzle's side back to the shaft's notch, crossing above the shaft.
    poly([(101, cy - 3.5), (101, cy + 1.5), (58, cy - 9), (58, cy - 14)], BAND_DARK)
    poly([(101, cy - 3.5), (101, cy - 1), (58, cy - 11.5), (58, cy - 14)], BAND_LIGHT)
    # The band's steel wishbone, hooked into the notch.
    rect(55, cy - 14.5, 59, cy - 9, STEEL_LIGHT)

    out = with_outline(img, 3 * SS)  # 3 px at 128 px per cell = 1.5 px at 64, as the spears
    return out.resize((S, S), Image.LANCZOS)


CANDIDATES = {
    "A": ("wooden stock", lambda: speargun(WOOD_LIGHT, WOOD_MID, POLY_LIGHT, POLY_DARK)),
    "B": ("aluminium stock", lambda: speargun(ALU_LIGHT, ALU_MID, GRIP_LIGHT, GRIP_DARK)),
}


# ---- Contact sheet (reference composite only; not part of the textures) ------------------------------------------------------

SAND, SEA, GROUND = (214, 198, 158, 255), (46, 92, 120, 255), (120, 112, 92, 255)
SKIN = (234, 200, 166)


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
    shade = tuple(max(0, c - 10) for c in bg[:3]) + (255,)
    for i in range(cells_w):
        for j in range(cells_h):
            if (i + j) % 2:
                d.rectangle((i * cell_px, j * cell_px, (i + 1) * cell_px - 1, (j + 1) * cell_px - 1), fill=shade)
    return img


def scaled(img, px):
    return img.resize((px, px), Image.LANCZOS)


def tinted(img, rgb):
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    r = r.point(lambda v: v * rgb[0] // 255)
    g = g.point(lambda v: v * rgb[1] // 255)
    b = b.point(lambda v: v * rgb[2] // 255)
    return Image.merge("RGBA", (r, g, b, a))


def held(pawn, weapon, facing, aiming, offset, cell):
    """A vanilla body and head with the weapon drawn as RimWorld's PawnRenderUtility does for a drafted pawn: carried at aim
    angle 143 (217 facing west) 0.22 cells below the body, 0.2 cells out to the side facing east; aiming east, 0.4 cells out
    with the weapon level. Rotation is aimAngle - 90 + equippedAngleOffset, clockwise on screen."""
    size = cell * 3
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx = cy = size / 2
    body, head = pawn[facing]
    body_px = round(cell * 1.5)
    b = scaled(body, body_px)
    h = scaled(head, body_px)
    head_dx = 0.06 if facing == "east" else 0.0
    if aiming:
        angle, wx, wy = 0 + offset, 0.4, 0.0
    else:
        angle = 143 - 90 + offset
        wx, wy = (0.2 if facing == "east" else 0.0), 0.22
    w = scaled(weapon, cell)
    w = w.rotate(-angle, resample=Image.BICUBIC, expand=True)
    canvas.alpha_composite(b, (round(cx - body_px / 2), round(cy - body_px / 2)))
    canvas.alpha_composite(h, (round(cx - body_px / 2 + head_dx * cell), round(cy - body_px / 2 - 0.34 * cell)))
    canvas.alpha_composite(w, (round(cx + wx * cell - w.width / 2), round(cy + wy * cell - w.height / 2)))
    return canvas


def contact_sheet(out_dir, vanilla, steel_spear):
    title, label, small = font(30), font(20), font(16)
    cands = [(f"{k}  {name}", Image.open(out_dir / f"BandSpeargun_{k}.png").convert("RGBA")) for k, (name, _) in CANDIDATES.items()]
    items = [("steel-tipped pole spear*", steel_spear)] + cands
    W, H = 1640, 1740
    sheet = Image.new("RGBA", (W, H), (36, 38, 42, 255))
    d = ImageDraw.Draw(sheet)
    d.text((30, 20), "Band speargun: candidates (pick one)", font=title, fill=(240, 240, 240))
    d.text((30, 60), "128x128 at 128 px per cell, muzzle to the right, 3 px black outward outline (1.5 px at 64), as the approved "
           "spears.  * = approved Spearfishing art.", font=small, fill=(200, 200, 200))

    # Row 1: 1.5x (192 px per cell) on sand.
    y = 100
    d.text((30, y), "1.5x (192 px per cell) on sand", font=label, fill=(240, 240, 240))
    for i, (name, img) in enumerate(items):
        x = 30 + i * 420
        bg = tile(SAND, 64, 6, 3)
        bg.alpha_composite(scaled(img, 192), (96, 0))
        sheet.alpha_composite(bg, (x, y + 34))
        d.text((x, y + 34 + 196), name, font=label, fill=(255, 230, 160))

    # Row 2: game size (64 px per cell) on sand and sea, beside vanilla guns of the same role.
    y = 380
    d.text((30, y), "Game size (64 px per cell), on sand and on sea. Vanilla for reference: revolver, shotgun, recurve bow.",
           font=label, fill=(240, 240, 240))
    refs = [(n, Image.open(vanilla / f"Things/Item/Equipment/WeaponRanged/{f}.png").convert("RGBA"))
            for n, f in (("revolver", "Revolver"), ("shotgun", "Shotgun"), ("recurve bow", "BowRecurve"))]
    row = [("steel spear*", steel_spear)] + [(k, img) for k, (_, img) in zip(CANDIDATES, cands)] + refs
    per = 3
    for r, bg in enumerate((SAND, SEA)):
        strip = tile(bg, 64, len(row) * per, 1)
        for i, (_, img) in enumerate(row):
            strip.alpha_composite(scaled(img, 64), (i * per * 64 + 64, 0))
        sheet.alpha_composite(strip, (30, y + 34 + r * 74))
    for i, (name, _) in enumerate(row):
        d.text((30 + i * per * 64 + 96, y + 34 + 150), name, font=small, fill=(220, 220, 220), anchor="mt")

    # Rows 3 and 4: held by a vanilla body at the game's angles, at 1.5x and then at game size.
    root = vanilla / "Things/Pawn/Humanlike"
    pawn = {f: (tinted(Image.open(root / f"Bodies/Naked_Male_{f}.png"), SKIN),
                tinted(Image.open(root / f"Heads/Male/Male_Average_Normal_{f}.png"), SKIN)) for f in ("south", "east")}
    views = [("south, carried", "south", False), ("east, carried", "east", False), ("aiming east", "east", True)]
    # The spears' def sets equippedAngleOffset -25; vanilla guns leave it at 0, assumed here for the speargun.
    offsets = [-25] + [0] * len(cands)
    y = 600
    d.text((30, y), "Held by a drafted pawn at the game's angles (vanilla body for reference). Spear offset -25; speargun 0, "
           "as vanilla guns.", font=label, fill=(240, 240, 240))
    d.text((30, y + 30), "1.5x (96 px per cell)", font=small, fill=(200, 200, 200))
    d.text((970, y + 30), "Game size (64 px per cell)", font=small, fill=(200, 200, 200))
    for row_i, ((name, img), off) in enumerate(zip(items, offsets)):
        yy = y + 54 + row_i * 360
        d.text((30, yy), name, font=label, fill=(255, 230, 160))
        x = 30
        for cell in (96, 64):
            for vname, facing, aiming in views:
                bg = tile(GROUND, cell, 3, 3)
                bg.alpha_composite(held(pawn, img, facing, aiming, off, cell))
                sheet.alpha_composite(bg, (x, yy + 28))
                d.text((x + cell * 1.5, yy + 28 + cell * 3 + 4), vname, font=small, fill=(220, 220, 220), anchor="mt")
                x += cell * 3 + 8
            x = 970
    sheet.convert("RGB").save(out_dir / "contact_sheet.png")


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, (_, make) in CANDIDATES.items():
        make().save(out_dir / f"BandSpeargun_{key}.png")
    if len(sys.argv) > 2:
        repo = Path(__file__).resolve().parents[2]
        steel = Image.open(repo / "Textures/Things/Spearfishing/Weapon/SteelPoleSpear.png").convert("RGBA")
        contact_sheet(out_dir, Path(sys.argv[2]), steel)
