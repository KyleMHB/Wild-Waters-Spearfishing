# Steel-tipped pole spear: approval record

- **Piece:** the steel-tipped pole spear, `Textures/Things/Spearfishing/Weapon/SteelPoleSpear.png`.
  - 128x128 RGBA at 128 px per cell, horizontal with the tip to the right.
  - 3 px black outward outline, which is 1.5 px at 64 px per cell.
  - Read by `Spearfishing_SteelPoleSpear` as `Graphic_Single` with `equippedAngleOffset` -25.
- **Approved:** 2026-11-15, by the author, relayed by the orchestrator.
- **Author's words:** "Approve", in answer to "Approve the steel-tipped pole spear (sheet just sent)?".
- **Earlier rounds:**
  - **Round 1:** steel bands on the haft. Three takes were rejected. The author explained that a banded pole spear has a rubber band at the back to shoot it forward, "not bands on the haft".
  - **Round 2:** three takes with a sling loop at the butt. The author dropped the sling idea and chose "Simpler: just a steel point". Offered a wooden speargun instead, they answered "No, steel-tipped pole spear".
- **Compared:** the approved pole spear v4 beside this candidate, shown at 1.5x, at game size and held at 25 degrees.
- **Source:**
  - `SteelPoleSpear_A.png` in this folder, drawn by `steel_pole_spear_art.py`.
  - To regenerate it byte for byte with Pillow 12.3, run `python -I steel_pole_spear_art.py <out_dir>`.
  - It is the approved v4 drawing (`art/pole-spear/pole_spear_art.py`) with unchanged geometry, shaft colours, framing and outline. Only the head is recoloured steel: light (206, 210, 212) and dark (150, 156, 162).
  - Procedural. No reference images, vanilla, DLC or third-party art went into it.
  - Script SHA-256 `28c037f276c2460c6ebe6a9e5d4d060964a7bebea3becfffb74dd34d49580c9c`.
- **Export recipe:** the master is already at the game texture's size, so it was copied unchanged and renamed to `SteelPoleSpear.png`.
- **Exported texture:** SHA-256 `3d233ea7a172fad7305648b57425e61a6a6b565b15c1336810c937f0c318fb43`.

Approval is final: a change to these pixels, the framing or the colour is a new candidate that needs a new approval.
