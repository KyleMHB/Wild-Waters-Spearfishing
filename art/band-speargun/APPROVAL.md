# Band speargun: approval record

- **Piece:** the band speargun, `Textures/Things/Spearfishing/Weapon/BandSpeargun.png`.
  - 128x128 RGBA at 128 px per cell, horizontal with the muzzle and point to the right.
  - 3 px black outward outline, which is 1.5 px at 64 px per cell.
  - Read by `Spearfishing_BandSpeargun` as `Graphic_Single` with `equippedAngleOffset` 0, as vanilla guns use and as the contact sheet assumed.
- **Approved:** 2026-11-17, by the author, relayed by the orchestrator.
- **Author's words:** "as recommended, except for 05 must be B", in answer to the gear-tier art picks. The recommendation for this piece was B, so B stands. The "05" exception is about ticket 05 (neoprene wetsuit), not this piece.
- **Picked:** candidate B, the blue-grey anodised aluminium stock with a dark grey grip and muzzle. Candidate A (wooden stock) was not chosen.
- **Compared:** A and B beside the approved steel-tipped pole spear, at 1.5x and at game size (64 px per cell) on sand and sea, with the vanilla revolver, shotgun and recurve bow for scale, and each held by a drafted vanilla body (south carried, east carried, aiming east). Sheet: `work/contact-sheets/band-speargun.png` (local, not committed).
- **Source:**
  - `BandSpeargun_B.png` in this folder, drawn by `band_speargun_art.py`.
  - To regenerate it byte for byte with Pillow 12.3, run `python -I band_speargun_art.py <out_dir>`.
  - Procedural. No reference images, vanilla, DLC or third-party art went into the textures; vanilla pixels go only into the contact sheet, when the script is given the extracted vanilla art folder.
  - The shaft reuses the steel-tipped pole spear's head colours: light (206, 210, 212) and dark (150, 156, 162).
  - Script SHA-256 `c6957e103d864469ed840756eb1ed26e1e9c369aa57637c00af99675eeb7522f`.
- **Export recipe:** the master is already at the game texture's size, so it was copied unchanged and renamed to `BandSpeargun.png`.
- **Exported texture:** SHA-256 `b7eb958e57fc7ee6e592c6427919244ba9d7325c2a34557798924d8c7c839e6a`, the same bytes as the approved candidate on the contact sheet.
- **Not covered:** the projectile in flight uses vanilla's `Things/Projectile/Arrow_Small` by path (a reference to the game's own texture, not a copy). The held angles on the sheet were modelled, not captured in game, and ticket 35's swimmer hold (the speargun drawn at the swimmer's side) was not shown on the sheet.

Approval is final: a change to these pixels, the framing or the colour is a new candidate that needs a new approval.
