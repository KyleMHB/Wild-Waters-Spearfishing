# Rebreather: approval record

- **Pieces:**
  - The item sprite `Textures/Things/Spearfishing/Apparel/Rebreather/Rebreather.png`. It is 128x128, Graphic_Single, drawSize 1, fixed colour, no mask, with a 4 px outline at the 8x master's scale.
  - The worn views `Rebreather_south.png`, `Rebreather_east.png` and `Rebreather_north.png` in the same folder. They are 128x128 head textures on vanilla's head frame with a 3 px outline. West mirrors east in game. The def reads them through `wornGraphicPath` on the EyeCover layer, as the snorkels do.
  - The north view is fully transparent: the head hides the unit, and there is no strap. It is shipped anyway, so the game never falls back to another facing's texture from behind.
- **Approved:** 2026-11-17, by the author, relayed by the orchestrator (gear tiers ticket 09's Comments).
- **Author's words, verbatim:**
  - Design: "a but don add a backstrap". Candidate A, the cylinder, with no head strap or nape clip.
  - Back view: "no strap".
  - Stats: "Better dry snorkel (Recommended)".
  - Name: "Rebreather (Recommended)".
- **Compared (round 3):** three mouth rebreathers in the snorkel's slot, each with a thin rubber head strap and a nape clip: A a short plasteel cylinder with rubber end caps and an orange centre band, B a mouthpiece block with twin cartridges, and C a round puck with a teal ring. Each was shown as the item at 1.5x and at game size, worn south, east and north with the approved low-volume mask A, floating face down, and worn south with the approved glass mask, beside the approved low-volume mask A with dry snorkel C. Round 3's sheet was `work/contact-sheets/mouth-rebreather.png`, SHA-256 `6a37707a76a6bdd4f101e01ddfeeea77a70f8fb5fe5db2c7d3e4bb45b8dde31b`. Rounds 1 and 2, a full-face mask, were not approved; their scripts are under `art/full-face-mask/`.
- **Change after approval:** the strap loop and clip are gone from the item, the strap from the east view, and the strap and clip from the north view, as the author asked. Nothing else changed: the cylinder, its placement and the palette are round 3's A.
- **Final contact sheet:** `work/contact-sheets/rebreather-final.png` (ignored), SHA-256 `aebb37cd1890bd5a5c706e5d065ad94e05f01c79ca8005be26565fa81d07ca7b`. It shows the tier below's row and the strapless A.
- **Source:** `rebreather_art.py` in this folder draws everything procedurally with Pillow 12.3. No reference images, vanilla, Waves, DLC, Subnautica or third-party art went into the textures. The sheet reads the approved glass mask, shoulders and waterline from `Textures/`, the approved low-volume mask and dry snorkel through their own scripts, and an optional vanilla north head dump for the sheet only.
  - Run `python -I art/rebreather/rebreather_art.py work/rebreather E:/Coding/Rimworld/Spearfishing/work/vanilla-ref/head_Male_Average_Normal_north.png`, then copy `work/rebreather/contact_sheet.png` to `work/contact-sheets/rebreather-final.png`.
  - It writes the four game textures into `Textures/` and the same files as `Rebreather_A_cylinder*.png` into the output folder. The copies kept here are byte for byte the game textures.
  - Script SHA-256 (as committed, LF line endings) `8940972122341d46592d1aee1cf674b512e0f8b62ba669349d7a1c6d7dbec88b`. Round 3's script, with B, C and the strap, was `d3348f12c7f1bd00fcd9fa8ac76497872be8f73115fa0aac7df31557bcf81649`.
- **Export recipe:**
  - **Item:** `export(item("A", master=True))`, the tier below's recipe. It crops the 8x master to its alpha bounds and scales it uniformly with Lanczos so the longer side is 100 px. The result is centred on a transparent 128x128 canvas.
  - **Worn views:** `worn("A")`, already at game size.
- **Exported textures (SHA-256):**
  - `Rebreather.png` `b2e7774dabc20224b2a32ab2c5855f1b775737e6530096c04dc55277a63bddc3`
  - `Rebreather_south.png` `075fe14152cc4639876fd9ed0045ecf5574b9a3a4fe7e9f4f53cff80b5f17eca`
  - `Rebreather_east.png` `d87671c3ce0f5d181f147d5f7c5886f907cb3aea9b3020865d7f036a804c23b4`
  - `Rebreather_north.png` `1594258d650464372a84556d099c6f0fad9551bbf0efe58e7403336fee183eee`

The strapless sheet has not been shown to the author. They approved the change in words, not on this sheet. Approval is final: any change to these pixels, the framing or the colour is a new candidate that needs a new approval.
