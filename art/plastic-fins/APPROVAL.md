# Plastic fins: approval record

- **Piece:** plastic fins item sprite, `Textures/Things/Spearfishing/Apparel/PlasticFins.png` (128x128, Graphic_Single, drawSize 1, fixed colour, no mask). No worn graphic, as the wooden fins.
- **Approved:** 2026-11-17, by the author, relayed by the orchestrator (gear tiers ticket 02).
- **Author's words:** "as recommended, except for 05 must be B". The exception is about ticket 05 (neoprene wetsuit); for these fins it means the recommendation: candidate A, and worn graphic option (a), item only.
- **Compared:** three candidates on `work/contact-sheets/plastic-fins.png`, each beside the approved wooden fins: A closed pocket in blue, B open heel and strap in yellow, C split blade in teal. A was chosen. The worn views drawn for the sheet are dropped.
- **Source:** `plastic_fins_art.py` in this folder draws everything procedurally with Pillow 12.3. No reference images, vanilla, DLC or third-party art went into any texture; Ludeon's extracted art is read only to draw the body on the contact sheet.
  - Run `python -I plastic_fins_art.py <out_dir>`. It writes every candidate; A is `PlasticFins_A_pocket_master512.png` and `PlasticFins_A_pocket.png`.
  - Script SHA-256 `9ef4571ac0731d564e9d7bab386c1a33ce3e43aa6ec621d60c21678447244b6d`.
  - Master kept here: `PlasticFins_master512.png` (candidate A, `item_master("pocket", ...)`), SHA-256 `50dbc5ac6f69bf5fc0d3ce82c83a1df4a93a1a01a363cc2d741ed9da6074852b`.
- **Export recipe:** `export(master, fill=100)`, the wooden fins' recipe: crop to alpha bounds, uniform Lanczos scale so the longer side is 100 px, centre on a transparent 128x128 canvas.
- **Exported texture:** SHA-256 `4f12d80ca6e06bfa54dbab36f192bc58c3f3b4105d65f968455327d972e387ec`.

Approval is final: a change to these pixels, framing or colour is a new candidate that needs a new approval.
