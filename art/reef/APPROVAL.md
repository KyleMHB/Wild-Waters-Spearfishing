# Reef overlay: approval record

- **Piece:** reef overlay, `Textures/Spearfishing/Terrain/ReefOverlay.png` (512x512 RGBA, tiles every 8x8 cells at 64 px per cell). `SectionLayer_Reef` draws it translucent over reef cells at Waves' sea-life render queue, with vertex alpha fading patch edges and deep reef at 0.7 strength.
- **Approved:** 2026-11-15, by the author through the orchestrator's question dialog.
- **Author's words:** master design "B rock shadow"; deep reef strength "Keep 0.7".
- **Compared:** candidates A coral heads, B rock shadow and C coral garden, each reviewed in game at noon under Waves beside bare ocean (run `20261115-181336-spearfishing-reef-s1-ffd99651`).
- **Source:** `ReefOverlay_master512.png`, drawn by `reef_art.py` `rock_shadow()` (fixed seeds 11-13; `python reef_art.py <out_dir>` regenerates it byte for byte as `ReefOverlay-B-rock-shadow.png`). Procedural; no reference images or Waves textures used. SHA-256 `f140784cf4c71723417f8864a1bf9730d780bc1bc771cd9356b12db4de701102`.
- **Export recipe:** copied unchanged; the master is already the game texture's size and tiling.
- **Exported texture:** SHA-256 `f140784cf4c71723417f8864a1bf9730d780bc1bc771cd9356b12db4de701102`.

Approval is final: a change to these pixels, the tile size or the colour is a new candidate that needs a new approval.
