# Thermal wetsuit: approval record

- **Pieces:**
  - The item sprite `Textures/Things/Spearfishing/Apparel/ThermalWetsuit/ThermalWetsuit.png`. It is 128x128, Graphic_Single, drawSize 1, with a 4 px outline at the 8x master's scale.
  - The worn views `ThermalWetsuit_<BodyType>_<dir>.png` in the same folder, for Male, Female, Thin, Hulk and Fat, facing south, east and north. They are 128x128 body textures for the OnSkin layer, read through `wornGraphicPath`. Apparel defaults to adults, so there is no Child set.
  - The colour is in the textures: pale synthread grey with an amber heated core and collar. The suit is a fixed material (a `costList` of synthread, plasteel and an advanced component), so it has no stuff and no tint.
- **Approved:** 2026-11-17, by the author, relayed by the orchestrator.
- **Author's words:** "B heated core (Recommended)". That chose candidate B, the recommendation.
- **Compared:** three candidates in the neoprene wetsuit's rendering, told apart by panels: A slate yoke, B heated core, C slate flanks and chest band. Each was shown as the item at 2x and game size, and worn on Male, Female, Thin, Hulk and Fat facing south, east and north with a bald vanilla head and the approved glass mask, beside the approved neoprene wetsuit. The suit is sealed, so no candidate has the neoprene suit's back zip, and none has a seam on the east view.
- **Source:** `thermal_wetsuit_art.py` in this folder draws everything procedurally with Pillow 12.3 and NumPy 2.3. It is a copy of `art/neoprene-wetsuit/neoprene_wetsuit_art.py` with only the palette and panels changed.
  - Each worn view fills the vanilla naked body's silhouette for its body type. Only the alpha is used, so the suit fits the body; no vanilla colour pixels go into it. No other reference, DLC or third-party art went into it.
  - Run `python -I thermal_wetsuit_art.py <Things/Pawn/Humanlike/Bodies dir of Ludeon's art source> <out_dir> Male Female Thin Hulk Fat`.
  - It writes every candidate, plus the approved game textures `ThermalWetsuit.png` and `ThermalWetsuit_<BodyType>_<dir>.png`.
  - `thermal_sheet.py` made the contact sheet: `python -I thermal_sheet.py <thermal out_dir> <neoprene out_dir> <repo root> <Things/Pawn/Humanlike dir> <sheet.png>`.
  - The candidate B files kept here are `ThermalWetsuit_B_core.png` and its Male `_south`, `_east` and `_north` views. They are byte-identical to the shipped item and Male views.
  - Script SHA-256: `thermal_wetsuit_art.py` `21557874c10739e1ec999af92c8a31eb2e9bc73ad787eb004804888d17e227ce`; `thermal_sheet.py` `cf4acbfd93dceb7736d74ad72d283fc3ed9fd9d5608f4fc5ce982a9c20671acc`.
- **Contact sheet:** `work/contact-sheets/thermal-wetsuit-candidates.png` in the ignored `work/` folder.
- **Export recipe:**
  - **Item:** `export(item("B", master=True))`, the basic wetsuit's recipe. It crops the 8x master to its alpha bounds and scales it uniformly with Lanczos so the longer side is 100 px. The result is centred on a transparent 128x128 canvas.
  - **Worn views:** `worn("B", body, direction)`. The heated core is built from each body's silhouette (`core_panel`): its sides are inset from each row's edges and its top and bottom follow the suit's shoulder and hem contours, so it follows the taper, waist and bulge of every body type. It takes the suit's shade band as well as its own lip (`lined_on_body`). The back (north) is a narrower, shorter heating pad, so north and south now differ for every body type; the side (east) panel runs to the front edge and tapers towards the back.
- **Exported textures (SHA-256):**
  - `ThermalWetsuit.png` `a48d2a84c80c3493413e3ec7148782faecc1cbb7bd1a90e623fee5ac5c62271f`
  - `ThermalWetsuit_Male_south.png` `480c0e0d1397de8a15a21dac7e7f314249f58493971cbe5771c7d44b0ffafb24`
  - `ThermalWetsuit_Male_east.png` `f59ef207291494a0f58114d2202ac21ce27dda8901ed0db37efdbd6a4ed96d1a`
  - `ThermalWetsuit_Male_north.png` `f6cb585cfaaf2ded213babefebb508c93de1933e15c054e6530cc5caab57786b`
  - `ThermalWetsuit_Female_south.png` `c821b7e376565727474c1884b07809efb775919f75ffca2afe0e2ce8a8fb1806`
  - `ThermalWetsuit_Female_east.png` `f4467f8eabb334678717a618745e607118a85e53f3c2a17fe9a65694ebc71a59`
  - `ThermalWetsuit_Female_north.png` `8698c5fa59674148e5816731b9752f03011590e5f4064baf816418925dee3962`
  - `ThermalWetsuit_Thin_south.png` `fa567eb63f7deb3f8b983919f0caec847d611b583f53c65ee5d5bb4daffcdfaa`
  - `ThermalWetsuit_Thin_east.png` `d778ca657290bac7ff26a59e02156b076dcfb6ebd96530e21d958c29438fd074`
  - `ThermalWetsuit_Thin_north.png` `e0919c3d578f12924f5513b9770cf5f5bf90615dccc4d3a1df5b4401d1917400`
  - `ThermalWetsuit_Hulk_south.png` `516708bf68ebfcffdb28474ee34dff15e5684c94aaad4e11da0e4d786eb6eb4a`
  - `ThermalWetsuit_Hulk_east.png` `f6aa01495b8acb70cdebaff8d501bb4f04d7daff5401ec4aec0a95eecb579469`
  - `ThermalWetsuit_Hulk_north.png` `f406a72c9d6237f1fa14dff1d9f61321c5e17b01cac7d6b7f63139339944559d`
  - `ThermalWetsuit_Fat_south.png` `bb97b0cd340389b077e3e121618f511eaabccd7b03885075151e3c5a6a116df4`
  - `ThermalWetsuit_Fat_east.png` `16ed0e048aeb8f04d5f7626810f4bce8713bcbb7b52be4c666395d5e7aa082af`
  - `ThermalWetsuit_Fat_north.png` `ab09a64e702d67c2e2cc612a1bad5e49913f039374983e8081a706d380d82791`

- **Revision, 2026-11-17 (worn views only, re-approved):** the in-game capture (`work/gear-look/worn-ThermalWetsuit.png`) showed the core as a flat rectangle pasted on every body type, with north identical to south. The worn views were redrawn as above; colours, the item sprite and the design intent (B, heated core) are unchanged. The author re-approved the worn views after the in-game recapture (`work/gear-look-2/`): "Approve all three".

Approval is final: a change to these pixels, the framing or the colour is a new candidate that needs a new approval.
