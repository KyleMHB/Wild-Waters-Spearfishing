# Wooden buoy: approval record

- **Piece:** wooden buoy item sprite, `Textures/Things/Spearfishing/Apparel/WoodenBuoy.png` (128x128, Graphic_Single, drawSize 1, fixed colour, no mask). Item only: no worn graphic, like the wooden fins.
- **Approved:** 2026-11-15, by the author through the orchestrator.
- **Author's words:** "B cask float". Export at the fins' size, about 100 px on a 128 canvas.
- **Source:** `WoodenBuoy_master512.png` (candidate B, drawn by `buoy_art.py`, `candidate_b`), SHA-256 `e5abc2edcc08a15deef5d7d249e8d6ecd1745f1b7c527b95b844c0274b584745`.
- **Export recipe:** `buoy_art.py` `export(master, fill=100)`: crop to alpha bounds, uniform Lanczos scale so the longer side is 100 px, centre on a transparent 128x128 canvas.
- **Exported texture:** SHA-256 `5d5c5858cf1c377b20799dd7d25137a1409c146b3f497fdcecf45c430aa81f18`.

Approval is final: a change to these pixels, framing or colour is a new candidate that needs a new approval.
