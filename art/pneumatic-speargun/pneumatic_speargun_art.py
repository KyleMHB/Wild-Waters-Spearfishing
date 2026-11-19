"""Pneumatic speargun candidates for Spearfishing (gear tiers ticket 07). Same method as the approved band speargun
(art/band-speargun/band_speargun_art.py, candidate B) and the pole spears: flat two-tone shapes drawn at 8x, a 3 px black outward
outline at 128 px per cell (1.5 px at 64), reduced to a 128x128 canvas, horizontal with the muzzle and tip to the right.

A pneumatic speargun has no band: the shaft sits inside a thick air barrel and only its point shows past the muzzle. That thick
barrel, with no red band across it, is what sets it apart from the band speargun at game size. The shaft and point reuse the band
speargun's steel colours and point geometry, so the tiers read as one family. Plasteel is vanilla's stuff colour (160,178,181).

  A  plasteel barrel, dark grip, muzzle cap and end cap.
  B  graphite barrel with plasteel caps and grip, and a cyan pressure window.
  C  plasteel, a slimmer barrel over a separate air reservoir tube (a different silhouette).

Usage: python -I pneumatic_speargun_art.py <out_dir> [vanilla_textures_dir]
  Writes PneumaticSpeargun_A/B/C.png (128x128). With the extracted vanilla art source's Textures root (for example
  E:/AI/rimworld-lora/extracted), also writes contact_sheet.png beside the approved band speargun (B, drawn live by its own script),
  vanilla guns and a vanilla body holding each weapon at the game's angles. Vanilla pixels go only into the sheet, never into the
  textures.
"""
import sys
from pathlib import Path

# -I leaves the script's folder off sys.path; the band speargun's script supplies the shared helpers and the approved tier below.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "band-speargun"))

from PIL import Image, ImageDraw  # noqa: E402

import band_speargun_art as band  # noqa: E402
from band_speargun_art import (GROUND, SAND, SEA, SKIN, SS, S, STEEL_DARK, STEEL_LIGHT, font, held, scaled, tile,  # noqa: E402
                               tinted, with_outline)

PLASTEEL_LIGHT, PLASTEEL_MID = (184, 202, 205, 255), (144, 162, 166, 255)  # vanilla plasteel (160,178,181), light along the top
GRIP_LIGHT, GRIP_DARK = band.GRIP_LIGHT, band.GRIP_DARK                    # the band speargun's dark polymer
GRAPHITE_LIGHT, GRAPHITE_MID = (88, 92, 100, 255), (62, 65, 72, 255)       # B's dark barrel
GAUGE_LIGHT, GAUGE_DARK = (120, 196, 204, 255), (78, 150, 162, 255)        # B's cyan window, saturation under 0.6
RESERVOIR_GAP = (96, 110, 114, 255)                                       # C's shade between barrel and reservoir


def speargun(barrel_light, barrel_mid, part_light, part_dark, window=False, reservoir=False):
    W = S * SS
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def u(v):
        return v * SS

    def ux(v):
        return (v - 2) * SS  # 2 px left, as the band speargun, so the point's outline clears the canvas edge

    cy = 64  # the barrel's centre line, in 128 px units: ranged weapons keep the barrel vertically centred

    def rect(x0, y0, x1, y1, fill):
        d.rectangle([ux(x0), u(y0), ux(x1), u(y1)], fill=fill)

    def poly(pts, fill):
        d.polygon([(ux(x), u(y)) for x, y in pts], fill=fill)

    if reservoir:
        top, bottom = cy - 6, cy + 1     # slimmer barrel, with the reservoir tube underneath
    else:
        top, bottom = cy - 7, cy + 7     # one thick air barrel
    grip_top = bottom if not reservoir else cy + 1

    # Pistol grip, raked back as on the band speargun, set further forward under the barrel.
    poly([(36, grip_top), (46, grip_top), (42, grip_top + 15), (32, grip_top + 14)], part_dark)
    poly([(36, grip_top), (41, grip_top), (37, grip_top + 14.5), (32, grip_top + 14)], part_light)
    # Air reservoir under the front half of the barrel (C only).
    if reservoir:
        rect(48, cy + 1, 90, cy + 8, barrel_mid)
        rect(48, cy + 1, 90, cy + 3, RESERVOIR_GAP)
        rect(88, cy + 1, 93, cy + 8, part_dark)
    # Barrel: two-tone, light along the top.
    rect(16, top, 96, bottom, barrel_mid)
    rect(16, top, 96, top + (bottom - top) * 0.35, barrel_light)
    # Rear end cap, slightly proud of the barrel.
    rect(10, top - 1, 18, bottom + 1, part_dark)
    rect(10, top - 1, 18, top + 2.5, part_light)
    # Muzzle cap, tapering to the shaft.
    poly([(94, top - 1), (103, top + 2), (103, bottom - 2), (94, bottom + 1)], part_dark)
    poly([(94, top - 1), (103, top + 2), (103, top + 4), (94, top + 2.5)], part_light)
    # Pressure window on the barrel's side, just ahead of the grip (B only).
    if window:
        rect(52, cy - 2, 64, cy + 3, GAUGE_DARK)
        rect(52, cy - 2, 64, cy, GAUGE_LIGHT)
    # Steel shaft out of the muzzle to the band speargun's point.
    sy = (top + bottom) / 2 - 1.75 + 0.5
    rect(101, sy, 114, sy + 3.5, STEEL_DARK)
    rect(101, sy, 114, sy + 1.5, STEEL_LIGHT)
    mid = sy + 1.75
    poly([(124, mid), (112, mid - 4.25), (114, mid)], STEEL_LIGHT)
    poly([(124, mid), (112, mid + 4.25), (114, mid)], STEEL_DARK)

    out = with_outline(img, 3 * SS)  # 3 px at 128 px per cell = 1.5 px at 64, as the spears and the band speargun
    return out.resize((S, S), Image.LANCZOS)


CANDIDATES = {
    "A": ("plasteel barrel", lambda: speargun(PLASTEEL_LIGHT, PLASTEEL_MID, GRIP_LIGHT, GRIP_DARK)),
    "B": ("graphite, cyan window", lambda: speargun(GRAPHITE_LIGHT, GRAPHITE_MID, PLASTEEL_LIGHT, PLASTEEL_MID, window=True)),
    "C": ("plasteel, air reservoir", lambda: speargun(PLASTEEL_LIGHT, PLASTEEL_MID, GRIP_LIGHT, GRIP_DARK, reservoir=True)),
}


# ---- Contact sheet (reference composite only; not part of the textures) ------------------------------------------------------

def contact_sheet(out_dir, vanilla, band_b):
    title, label, small = font(30), font(20), font(16)
    cands = [(f"{k}  {name}", Image.open(out_dir / f"PneumaticSpeargun_{k}.png").convert("RGBA"))
             for k, (name, _) in CANDIDATES.items()]
    items = [("band speargun B*", band_b)] + cands
    W, H = 1700, 2130
    sheet = Image.new("RGBA", (W, H), (36, 38, 42, 255))
    d = ImageDraw.Draw(sheet)
    d.text((30, 20), "Pneumatic speargun: candidates (pick one)", font=title, fill=(240, 240, 240))
    d.text((30, 60), "128x128 at 128 px per cell, muzzle to the right, 3 px black outward outline (1.5 px at 64), as the approved "
           "band speargun.  * = approved Spearfishing art (tier below).", font=small, fill=(200, 200, 200))

    # Row 1: 1.5x (192 px per cell) on sand.
    y = 100
    d.text((30, y), "1.5x (192 px per cell) on sand", font=label, fill=(240, 240, 240))
    for i, (name, img) in enumerate(items):
        x = 30 + i * 415
        bg = tile(SAND, 64, 6, 3)
        bg.alpha_composite(scaled(img, 192), (96, 0))
        sheet.alpha_composite(bg, (x, y + 34))
        d.text((x, y + 34 + 196), name, font=label, fill=(255, 230, 160))

    # Row 2: game size (64 px per cell) on sand and sea, beside vanilla guns.
    y = 380
    d.text((30, y), "Game size (64 px per cell), on sand and on sea. Vanilla for reference: charge rifle, revolver.",
           font=label, fill=(240, 240, 240))
    refs = [(n, Image.open(vanilla / f"Things/Item/Equipment/WeaponRanged/{f}.png").convert("RGBA"))
            for n, f in (("charge rifle", "ChargeRifle"), ("revolver", "Revolver"))]
    row = [("band B*", band_b)] + [(k, img) for k, (_, img) in zip(CANDIDATES, cands)] + refs
    per = 3
    for r, bg in enumerate((SAND, SEA)):
        strip = tile(bg, 64, len(row) * per, 1)
        for i, (_, img) in enumerate(row):
            strip.alpha_composite(scaled(img, 64), (i * per * 64 + 64, 0))
        sheet.alpha_composite(strip, (30, y + 34 + r * 74))
    for i, (name, _) in enumerate(row):
        d.text((30 + i * per * 64 + 96, y + 34 + 150), name, font=small, fill=(220, 220, 220), anchor="mt")

    # Held by a vanilla body at the game's angles, at 1.5x and then at game size.
    root = vanilla / "Things/Pawn/Humanlike"
    pawn = {f: (tinted(Image.open(root / f"Bodies/Naked_Male_{f}.png"), SKIN),
                tinted(Image.open(root / f"Heads/Male/Male_Average_Normal_{f}.png"), SKIN)) for f in ("south", "east")}
    views = [("south, carried", "south", False), ("east, carried", "east", False), ("aiming east", "east", True)]
    y = 600
    d.text((30, y), "Held by a drafted pawn at the game's angles (vanilla body for reference). equippedAngleOffset 0, as the band "
           "speargun's sheet and vanilla guns.", font=label, fill=(240, 240, 240))
    d.text((30, y + 30), "1.5x (96 px per cell)", font=small, fill=(200, 200, 200))
    d.text((970, y + 30), "Game size (64 px per cell)", font=small, fill=(200, 200, 200))
    for row_i, (name, img) in enumerate(items):
        yy = y + 54 + row_i * 360
        d.text((30, yy), name, font=label, fill=(255, 230, 160))
        x = 30
        for cell in (96, 64):
            for vname, facing, aiming in views:
                bg = tile(GROUND, cell, 3, 3)
                bg.alpha_composite(held(pawn, img, facing, aiming, 0, cell))
                sheet.alpha_composite(bg, (x, yy + 28))
                d.text((x + cell * 1.5, yy + 28 + cell * 3 + 4), vname, font=small, fill=(220, 220, 220), anchor="mt")
                x += cell * 3 + 8
            x = 970
    sheet.convert("RGB").save(out_dir / "contact_sheet.png")


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, (_, make) in CANDIDATES.items():
        make().save(out_dir / f"PneumaticSpeargun_{key}.png")
    if len(sys.argv) > 2:
        contact_sheet(out_dir, Path(sys.argv[2]), band.CANDIDATES["B"][1]())
