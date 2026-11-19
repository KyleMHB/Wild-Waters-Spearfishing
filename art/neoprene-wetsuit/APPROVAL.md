# Neoprene wetsuit: approval record

- **Pieces:**
  - The item sprite `Textures/Things/Spearfishing/Apparel/NeopreneWetsuit/NeopreneWetsuit.png`. It is 128x128, Graphic_Single, drawSize 1, with a 4 px outline at the 8x master's scale.
  - The worn views `NeopreneWetsuit_<BodyType>_<dir>.png` in the same folder, for Male, Female, Thin, Hulk and Fat, facing south, east and north. They are 128x128 body textures for the OnSkin layer, read through `wornGraphicPath`. Apparel defaults to adults, so there is no Child set.
  - The colour is in the textures: charcoal neoprene with a muted blue yoke, collar and zip pull. The suit is a fixed material (a `costList` of chemfuel, cloth and a component), so it has no stuff and no tint.
- **Approved:** 2026-11-17, by the author, relayed by the orchestrator.
- **Author's words:** "as recommended, except for 05 must be B". That chose candidate B (chest yoke) over the recommended A (side panels).
- **Compared:** three candidates in the basic wetsuit's rendering, told apart by panels: A side panels, B chest yoke, C chest band and knee pads. Each was shown as the item at 2x and game size, and worn on Male, Female, Thin, Hulk and Fat facing south, east and north with a bald vanilla head and the approved glass mask, beside the approved basic wetsuit. All three share the back zip on the north view and have no seam on the east view, following the author's rule for the basic suit.
- **Source:** `neoprene_wetsuit_art.py` in this folder draws everything procedurally with Pillow 12.3.
  - Each worn view fills the vanilla naked body's silhouette for its body type. Only the alpha is used, so the suit fits the body; no vanilla colour pixels go into it. No other reference, DLC or third-party art went into it.
  - Run `python -I neoprene_wetsuit_art.py <Things/Pawn/Humanlike/Bodies dir of Ludeon's art source> <out_dir> Male Female Thin Hulk Fat`.
  - It writes every candidate, plus the approved game textures `NeopreneWetsuit.png` and `NeopreneWetsuit_<BodyType>_<dir>.png`.
  - `neoprene_sheet.py` made the contact sheet: `python -I neoprene_sheet.py <out_dir> <repo root> <Things/Pawn/Humanlike dir> <sheet.png>`.
  - The candidate B files kept here are `NeopreneWetsuit_B_yoke.png` and its Male `_south`, `_east` and `_north` views. They are byte-identical to the shipped item and Male views.
  - Script SHA-256: `neoprene_wetsuit_art.py` `441f81060e2b4afc044e328601f95465cbc812161943da464a9067619c67be15`; `neoprene_sheet.py` `22e28f56c57ac185bcd142d37897de72f0ed606f252de554b59eb8c970d5be2e`.
- **Contact sheet:** `work/contact-sheets/neoprene-wetsuit-candidates.png` in the ignored `work/` folder.
- **Export recipe:**
  - **Item:** `export(item("B", master=True))`, the basic wetsuit's recipe. It crops the 8x master to its alpha bounds and scales it uniformly with Lanczos so the longer side is 100 px. The result is centred on a transparent 128x128 canvas.
  - **Worn views:** `worn("B", body, direction)` unchanged.
- **Exported textures (SHA-256):**
  - `NeopreneWetsuit.png` `3e0fa811a53f8300854d9d68347c68a07c351dc2707f6b61e0efecbbfc5499e9`
  - `NeopreneWetsuit_Male_south.png` `b4dc37f24a1fda4d02a3caaec25864afaa48adb4f8cca26a4ca6ead16a25550c`
  - `NeopreneWetsuit_Male_east.png` `556002d8b0d866ae2f65906ca2050672eab2bc7a311102dd3997cbcd8cf7cd28`
  - `NeopreneWetsuit_Male_north.png` `aa7942a3a02b2d6c0e7c598e13fa8e6a725ce03bf2bb298633aac4bab63b02e7`
  - `NeopreneWetsuit_Female_south.png` `8fc40acefa16bd9690303b1a19bdcf5c0572c6ef81f8c2217fdad00b189793bb`
  - `NeopreneWetsuit_Female_east.png` `cc9ceda3d5e69a08be937a25202a22d7d7ab6ee6ece413de36bd45059493166d`
  - `NeopreneWetsuit_Female_north.png` `c6a19d3c42650b23961fd8a4c7e9688e565df0c5e89a09df6fbfafd4715a0aec`
  - `NeopreneWetsuit_Thin_south.png` `7defbad30239648a56e4dfd0d3fed837d7285b0023d0afaa1d4294e51498af7b`
  - `NeopreneWetsuit_Thin_east.png` `4cd1a3b9a6a67a836942eb3e08e134162d992b8e6b9b6c88c68e1877371ff4ec`
  - `NeopreneWetsuit_Thin_north.png` `0cf6d6af7e457d433b9b8cadad2dcb8fc57ea95d1f4b246d15f73d74d14ad0aa`
  - `NeopreneWetsuit_Hulk_south.png` `eceabab30b226000692746bb05a5bf142368c4f1fed1cd98e67dcec242d83086`
  - `NeopreneWetsuit_Hulk_east.png` `775832939962ceaddff932c0a3b878d57de5ae0440bebdc12306bf65e3c84d69`
  - `NeopreneWetsuit_Hulk_north.png` `376cc66f9382fb112e945a1bddac416d54013a970d4454b4875829ce14504c9b`
  - `NeopreneWetsuit_Fat_south.png` `794852bb7754c3b974e3833bb7243ef65ba5299792fe8109f4ed2778d150cab0`
  - `NeopreneWetsuit_Fat_east.png` `bb4b0c88f2ef90f7771bc9f58cb91278ee33bd4f118143c8349d44d34b6039e2`
  - `NeopreneWetsuit_Fat_north.png` `1be020d45a2a18b9cd9b4e1f16e9d3db36ef58b905f40da1ef97fd0537a2150b`

Approval is final: a change to these pixels, the framing or the colour is a new candidate that needs a new approval.
