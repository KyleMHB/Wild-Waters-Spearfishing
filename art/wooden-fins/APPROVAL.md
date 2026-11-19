# Wooden fins: approval record

- **Piece:** wooden fins item sprite, `Textures/Things/Spearfishing/Apparel/WoodenFins.png` (128x128, Graphic_Single, drawSize 1, fixed colour, no mask).
- **Approved:** 2026-11-15, by the author through the orchestrator's question dialog.
- **Author's words:** master design "A paddle pair", no other changes requested; export size "Shrink to ~100 px (Recommended)".
- **Source:** `WoodenFins_master512.png` (candidate A, drawn by `fins_art.py`, `candidate_a`), SHA-256 `5b5bf0d99c4b4b1d4388166fd862aea1674c5ce23d2af5ea5d9d102027ab727d`.
- **Export recipe:** `fins_art.py` `export(master, fill=100)`: crop to alpha bounds, uniform Lanczos scale so the longer side is 100 px, centre on a transparent 128x128 canvas.
- **Exported texture:** SHA-256 `9295c23fc894527d0eec5d0ce68f54c6b03bfe578aa83a5d73fa81af726df263`.

Approval is final: a change to these pixels, framing or colour is a new candidate that needs a new approval.
