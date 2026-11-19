# Pneumatic speargun: approval record

- **Piece:** the pneumatic speargun, `Textures/Things/Spearfishing/Weapon/PneumaticSpeargun.png`.
  - 128x128 RGBA at 128 px per cell, horizontal with the muzzle and point to the right, the barrel vertically centred.
  - 3 px black outward outline, which is 1.5 px at 64 px per cell.
  - Read by `Spearfishing_PneumaticSpeargun` as `Graphic_Single` with `equippedAngleOffset` 0, as the band speargun and vanilla guns use and as the contact sheet assumed.
- **Approved:** 2026-11-17, by the author, relayed by the orchestrator.
- **Author's words:** "B graphite, cyan window". The recommendation was A (plasteel barrel), so the author overrode it.
- **Picked:** candidate B, a dark graphite barrel with plasteel end cap, grip and muzzle cap, and a small cyan pressure window. Candidates A (plasteel barrel, dark caps) and C (plasteel, slimmer barrel over an air reservoir) were not chosen.
- **Compared:** A, B and C beside the approved band speargun B, at 1.5x and at game size (64 px per cell) on sand and sea, with the vanilla charge rifle and revolver for scale, and each held by a drafted vanilla body (south carried, east carried, aiming east). Sheet: `work/contact-sheets/pneumatic-speargun.png` (local, not committed).
- **Source:**
  - `PneumaticSpeargun_B.png` in this folder, drawn by `pneumatic_speargun_art.py`.
  - The script imports `art/band-speargun/band_speargun_art.py` for shared helpers and colours, so both scripts must stay side by side. To regenerate the texture byte for byte with Pillow 12.3, run `python -I pneumatic_speargun_art.py <out_dir>`.
  - Procedural. No reference images, vanilla, DLC or third-party art went into the textures; vanilla pixels go only into the contact sheet, when the script is given the extracted vanilla art folder.
  - The shaft and point reuse the band speargun's steel colours and point geometry. The plasteel is vanilla's plasteel stuff colour (160, 178, 181), lightened along the top.
  - Script SHA-256 `a52c8517c1d89ba179f6fd3b88a414da9ab84c7493ea97e0994dfc24fb2b72b4`; the imported band speargun script, SHA-256 `c6957e103d864469ed840756eb1ed26e1e9c369aa57637c00af99675eeb7522f`.
- **Export recipe:** the master is already at the game texture's size, so it was copied unchanged and renamed to `PneumaticSpeargun.png`.
- **Exported texture:** SHA-256 `0311d1941590ed1a1c0bc37040c579887d4a09ba37909ee919b91ea0b9fc155f`, the same bytes as the approved candidate on the contact sheet.
- **Not covered:** the projectile in flight uses vanilla's `Things/Projectile/Arrow_Small` by path (a reference to the game's own texture, not a copy). The held angles on the sheet were modelled, not captured in game, and ticket 35's swimmer hold (the speargun drawn at the swimmer's side) was not shown on the sheet.

Approval is final: a change to these pixels, the framing or the colour is a new candidate that needs a new approval.
