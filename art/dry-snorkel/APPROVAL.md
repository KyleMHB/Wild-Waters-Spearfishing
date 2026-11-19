# Dry snorkel: approval record

- **Pieces:**
  - The item sprite `Textures/Things/Spearfishing/Apparel/DrySnorkel/DrySnorkel.png`. It is 128x128, Graphic_Single, drawSize 1, fixed colour, no mask, with a 4 px outline at the 8x master's scale.
  - The worn views `DrySnorkel_south.png`, `DrySnorkel_east.png` and `DrySnorkel_north.png` in the same folder. They are 128x128 head textures on vanilla's head frame with a 3 px outline. West mirrors east in game. The def reads them through `wornGraphicPath` on the EyeCover layer, as the wooden snorkel does.
- **Approved:** 2026-11-17, by the author, relayed by the orchestrator (gear tiers ticket 04's Comments).
- **Author's words:** "as recommended, except for 05 must be B". The words cover the whole gear-tier art round. For this ticket they mean the recommended candidate, C.
- **Compared:** three candidates on the wooden snorkel's J shape and worn placement: A yellow tube, B blue tube, and C dark grey tube with an orange dry valve. Each was shown as the item at 1.5x and at game size, worn south, east and north with the approved glass mask on a plain stand-in head that the script draws (not vanilla art), and floating face down. They sat beside the approved wooden snorkel. C was chosen, the only candidate whose valve reads at game size.
- **Contact sheet:** `work/contact-sheets/dry-snorkel.png` (ignored), SHA-256 `779cdc65cb18af388eeedc810511a80c6e8844dde0deef0ad7cff79a9c31dc18`. The script with the export added still writes that sheet byte for byte.
- **Source:** `dry_snorkel_art.py` in this folder draws everything procedurally with Pillow. No reference images, vanilla, Waves, DLC or third-party art went into it. The sheet reads the approved wooden snorkel, glass mask, shoulders and waterline from `Textures/` and writes nothing back.
  - Run `python -I dry_snorkel_art.py <out_dir> [<sheet_path>]`.
  - It writes every candidate, the four game textures and, with a sheet path, the contact sheet.
  - The candidate C files kept here are `DrySnorkel_C_black-orange.png` and its `_south`, `_east` and `_north` views. They are byte for byte the game textures.
  - Script SHA-256 (as committed, LF line endings) `51b9ec76b76ebe6dba6f63e54cd46b8aaa5c3eca66479340e7a62dfe5266d3a8`. The Part 1 script, before the export lines were added, was `9806656ac02c67e7fa30ad18c4f0ad3a32a3571c663af0d2b101d8699977ef90`.
- **Export recipe:**
  - **Item:** `export(item("C", master=True))`, the wooden snorkel's recipe. It crops the 8x master to its alpha bounds and scales it uniformly with Lanczos so the longer side is 100 px. The result is centred on a transparent 128x128 canvas.
  - **Worn views:** `worn("C")`, already at game size.
- **Exported textures (SHA-256):**
  - `DrySnorkel.png` `d77f268e3d49d020d0ccec78f97d6e4ad8f77d107ce5c62e712de53cd0cfd4d1`
  - `DrySnorkel_south.png` `3fb37c319b8b0a7fabf8993cc41e8f8e4acf6adb60bdd81c888fc2a39d6e6b52`
  - `DrySnorkel_east.png` `9faa44be704d0f0184806b6715de728788a86ec92cfafa5c69e94404bce090af`
  - `DrySnorkel_north.png` `ffddbb39df71c4658807e20c4f7031291b6cd87af2e1d327461979f1b3a0c756`

Approval is final: a change to these pixels, the framing or the colour is a new candidate that needs a new approval.
