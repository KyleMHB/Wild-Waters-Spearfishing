# Long carbon fins: approval record

- **Piece:** long carbon fins item sprite, `Textures/Things/Spearfishing/Apparel/LongCarbonFins.png` (128x128, Graphic_Single, drawSize 1, fixed colour, no mask). No worn graphic, as the wooden and plastic fins.
- **Approved:** 2026-11-17, by the author, relayed by the orchestrator (gear tiers ticket 08), after two rounds.
- **Author's words:**
  - Round 1, not approved: "Pockets should def not be plasteel as thats where your foot goes. Cabron fins should be black, with black foot pockets". On the size question they chose the larger export.
  - Round 2: "cabon fins I choose A". The recommendation had been C; A was chosen.
- **Compared:** three round-2 candidates on `work/contact-sheets/long-carbon-fins-r2.png`, each beside plastic fins A and the wooden fins: A gloss blade and matte rubber pocket, B with a weave hint on the blade, C with lighter edge rails. A was chosen: a cool blue-black carbon blade with one broad soft gloss band, and a matte black rubber foot pocket behind a black material line.
- **Source:** `long_carbon_fins_art.py` in this folder draws everything procedurally with Pillow 12.3. It loads `art/plastic-fins/plastic_fins_art.py` for the shared helpers and `export`. No reference images, vanilla, DLC or third-party art went into any texture.
  - Run `python -I long_carbon_fins_art.py <out_dir>`. It writes every candidate; A is `LongCarbonFins_A_gloss_master512.png` and `LongCarbonFins_A_gloss.png`.
  - Script SHA-256 `5b0be70c159c9d66e920e303903c2b22aa91c3a020c7815b2d05b7bc1d0d53ba`.
  - Helper script `art/plastic-fins/plastic_fins_art.py` SHA-256 `9ef4571ac0731d564e9d7bab386c1a33ce3e43aa6ec621d60c21678447244b6d`, the hash its own approval records.
  - Master kept here: `LongCarbonFins_master512.png` (candidate A, `item_master(weave=False, rails=False)`), SHA-256 `dc13d4bab0a6a85a92f22d9a7180cafd28c2aa09c4b1d8a8331b60e230e5cf57`.
- **Export recipe:** `export(master, fill=112)`: crop to alpha bounds, uniform Lanczos scale so the longer side is 112 px, centre on a transparent 128x128 canvas. This departs from the other fins' 100 px fill on purpose: the author chose the larger export so the long fins read longer. The exported pair's bounds are 84x112 px.
- **Exported texture:** SHA-256 `85356efaa0cd9642f6da9dc6640746744de285355b553df5df64bbe23c7feb6c`.

Approval is final: a change to these pixels, framing or colour is a new candidate that needs a new approval.
