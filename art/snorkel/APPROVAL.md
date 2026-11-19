# Snorkel: approval record

- **Pieces:**
  - The item sprite `Textures/Things/Spearfishing/Apparel/Snorkel/Snorkel.png`. It is 128x128, Graphic_Single, drawSize 1, fixed colour, no mask, with a 4 px outline at the 8x master's scale.
  - The worn views `Snorkel_south.png`, `Snorkel_east.png` and `Snorkel_north.png` in the same folder. They are 128x128 head textures on vanilla's head frame with a 3 px outline. West mirrors east in game. The def reads them through `wornGraphicPath` on the EyeCover layer.
- **Approved:** 2026-11-15, by the author, relayed by the orchestrator.
- **Author's words:** "A, tube moved back". In the east view (and so the mirrored west), the tube moved from the middle of the head to its back edge, so it doesn't cover the face. The item, south and north views are kept as drawn. No further approval was needed for that exact change.
- **Compared:** three candidates: A plain wood, B banded reed and C red cap. Each was shown as the item and worn south, east and north, with the approved glass mask on a plain stand-in head that the script draws (not vanilla art). A was chosen.
- **Source:** `snorkel_art.py` in this folder draws everything procedurally with Pillow 12.3. No reference images, vanilla, DLC or third-party art went into it.
  - Run `python -I snorkel_art.py <out_dir>`.
  - It writes every candidate, the preview tiles and the four game textures.
  - The candidate A files kept here are `Snorkel_A_plain.png` and its `_south`, `_east` and `_north` views, with the approved east view.
  - Script SHA-256 `bad2ae6f2487bab949b9cb1015a554b49e0c831bfafb25d21e361767b7360af1`.
- **Export recipe:**
  - **Item:** `export(item("A", master=True))`, the glass mask's and fins' recipe. It crops the 8x master to its alpha bounds and scales it uniformly with Lanczos so the longer side is 100 px. The result is centred on a transparent 128x128 canvas.
  - **Worn views:** `worn("A")`, already at game size.
- **Exported textures (SHA-256):**
  - `Snorkel.png` `4d2d06fa65a04c6c0f5113f47e2711bcb3b2560eaffef7d79f19816360b0b361`
  - `Snorkel_south.png` `04b0b9df5d9be343d1d852f7fb4713156adfa86c98bd63287828a76ddf1502cb`
  - `Snorkel_east.png` `801fe69b4bab4ed351df5e177b8d44a0a175ae1ccd6ee598ea1f18c921c06211`
  - `Snorkel_north.png` `8560743dc06651c83948db9defd7cafb3f7af817344ee14bcc6fed39f18a351a`

Approval is final: a change to these pixels, the framing or the colour is a new candidate that needs a new approval.
