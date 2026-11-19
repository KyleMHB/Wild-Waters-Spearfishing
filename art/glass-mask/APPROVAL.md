# Glass mask: approval record

- **Pieces:**
  - The item sprite `Textures/Things/Spearfishing/Apparel/GlassMask/GlassMask.png`. It is 128x128, Graphic_Single, drawSize 1, fixed colour, no mask, with a 4 px outline at the 8x master's scale.
  - The worn views `GlassMask_south.png`, `GlassMask_east.png` and `GlassMask_north.png` in the same folder. They are 128x128 head textures on vanilla's head frame with a 3 px outline. The def reads them through `wornGraphicPath` on the EyeCover layer.
- **Approved:** 2026-11-15, by the author, relayed by the orchestrator.
- **Author's words:** "C wide visor" for the design. For the worn graphic: "Yes, show it (Recommended)". For the export size, the orchestrator said to keep about 100 px, matching the fins.
- **Compared:** three candidates: A porthole (one round lens), B twin goggles and C wide visor. They sat beside the approved wooden fins and vanilla's ClothMask worn views, shown at 1.5x, at game size and worn south, east and north on a vanilla head. C was chosen.
- **Source:** `glass_mask_art.py` in this folder draws everything procedurally with Pillow 12.3. No reference images, vanilla, DLC or third-party art went into it. The vanilla head was used only to place the worn views on the sheet.
  - Run `python -I glass_mask_art.py <out_dir>`.
  - It writes every candidate, plus the four game textures.
  - The candidate C files kept here are `GlassMask_C_visor.png` and its `_south`, `_east` and `_north` views.
  - Script SHA-256 `a112a392e53a7cb28fe2d569448c3ea94d6b5ae4aba45448e76ea4b5254830e4`.
- **Export recipe:**
  - **Item:** `export(item_c(master=True))`, the fins' recipe. It crops the 8x master to its alpha bounds and scales it uniformly with Lanczos so the longer side is 100 px. The result is centred on a transparent 128x128 canvas.
  - **Worn views:** copied unchanged from the candidates and renamed.
- **Exported textures (SHA-256):**
  - `GlassMask.png` `0b2c520b0e271ca9c110c4f01231eaf589648fd77f136407d235fd4e88e02de5`
  - `GlassMask_south.png` `46f4ee84bd96af98315aece519d4ddd80084850272104b633ff7fb820a01b0f9`
  - `GlassMask_east.png` `2c9955110b9d5bd008dca41f837efca94865ac6dcfdb1b7d27ab8d5db3e79c5c`
  - `GlassMask_north.png` `6f6dea6c24fb971fa1f993bd8ef3e7d583a60b55bcd87d219a2105181b0ce705`

Approval is final: a change to these pixels, the framing or the colour is a new candidate that needs a new approval.
