# Foam buoy: approval record

- **Piece:** foam buoy item sprite, `Textures/Things/Spearfishing/Apparel/FoamBuoy.png` (128x128, Graphic_Single, drawSize 1, fixed colour, no mask). Item only: no worn graphic, like the wooden buoy.
- **Approved:** 2026-11-17, by the author through the orchestrator.
- **Author's words:** "as recommended, except for 05 must be B". For this ticket (06) that means the recommendation: candidate A, torpedo float, at the wooden buoy's export size.
- **Source:** `FoamBuoy_master512.png` (candidate A, drawn by `foam_buoy_art.py`, `candidate_a`), SHA-256 `2ea8939c455c322d10e1cea7205e834bad7ff06bfacf21a6d230fd3a6de297ac`.
- **Export recipe:** `buoy_art.py` `export(master, fill=100)`: crop to alpha bounds, uniform Lanczos scale so the longer side is 100 px, centre on a transparent 128x128 canvas.
- **Exported texture:** SHA-256 `694f4044fb844865f3a18a26056f380a5f81124ccf29bb4f48e3808f9f851e1c`.

Approval is final: a change to these pixels, framing or colour is a new candidate that needs a new approval.
