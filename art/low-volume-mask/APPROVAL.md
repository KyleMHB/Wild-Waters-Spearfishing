# Low-volume mask: approval record

- **Pieces:**
  - The item sprite `Textures/Things/Spearfishing/Apparel/LowVolumeMask/LowVolumeMask.png`. It is 128x128, Graphic_Single, drawSize 1, fixed colour, no mask, with a 4 px outline at the 8x master's scale.
  - The worn views `LowVolumeMask_south.png`, `LowVolumeMask_east.png` and `LowVolumeMask_north.png` in the same folder. They are 128x128 head textures on vanilla's head frame with a 3 px outline. West mirrors east in game. The def reads them through `wornGraphicPath` on the EyeCover layer, at the glass mask's draw layers (63 since 2026-11-17, over the hair; first 61; and 66 from behind).
  - The textures are the mask only, as the glass mask's are. No head, hair or snorkel is in them.
- **Approved:** 2026-11-17, by the author, relayed by the orchestrator (gear tiers ticket 03, Comments).
- **Author's words:** "as recommended, except for 05 must be B". The recommendation for this ticket was A twin, so A twin is approved. The "05 must be B" part is about ticket 05 (the neoprene wetsuit), not this mask.
- **Compared:** three candidates: A twin (two lenses with a steel bridge, charcoal rubber strap), B lowvisor (one long, shallow lens) and C twin-hivis (A's lenses with a hazard-yellow strap and skirt rim). They sat beside the approved glass mask, as the item at 1.5x and 1x, worn south, east and north at 1.5x, south with the approved snorkel, and face down with and without the snorkel. A was chosen.
  - The contact sheet is `work/contact-sheets/low-volume-mask.png` in the main checkout (SHA-256 `180c260436c87b7574ccf48f539c9f1aafaba5d4339a4478288cd5d2dfdfd2de`). The script regenerates it byte for byte.
  - On the sheet, the south and east tiles used a plain stand-in head that the script draws (the snorkel sheet's), because vanilla's south and east head textures had no offline dump. The north and face-down tiles used vanilla's `Male_Average_Normal` north head, tinted, with stand-in hair, only on the sheet. The face-down tiles were offline composites of the approved face-down look C, not in-game captures. No vanilla art is committed.
- **Source:** `low_volume_mask_art.py` in this folder draws everything procedurally with Pillow 12.3. No reference images, vanilla, DLC, Waves or third-party art went into the textures.
  - Run `python -I low_volume_mask_art.py <out_dir> [<vanilla_head_north.png>]`. The optional head is used only on the contact sheet.
  - It writes every candidate, the contact sheet and the four game textures.
  - The candidate A files kept here are `LowVolumeMask_A_twin.png` and its `_south`, `_east` and `_north` views. They are byte-identical to the game textures.
  - Script SHA-256 `55b9c48d4f15d8163e396274d1b94b92e9c8193fb87b145b1eed577bddfa9736` (working tree, CRLF line endings, as the other records hash their scripts).
- **Export recipe:**
  - **Item:** `export(item("A", master=True))`, the glass mask's and fins' recipe. It crops the 8x master to its alpha bounds and scales it uniformly with Lanczos so the longer side is 100 px. The result is centred on a transparent 128x128 canvas.
  - **Worn views:** `worn("A")`, already at game size.
- **Exported textures (SHA-256):**
  - `LowVolumeMask.png` `1c9986d5a364b3198b250abbe9a16d1752470f6636f55369f20861c0d08ed1fa`
  - `LowVolumeMask_south.png` `14b3c2c97dd47674273b69bf83245772910c812b718f4eca91e73f1771680ad8`
  - `LowVolumeMask_east.png` `b7fe5b6178060a16fd3dcefe3e93f46f6969c91814a917aa97229590240cecf5`
  - `LowVolumeMask_north.png` `5dcc0ab4f747cb0fd3cb23d94ee54f9da1f0f97e8052a8d91dbea8af739af952`

- **North view redrawn, approved (2026-11-17):** in game the north view (also drawn turned for a face-down floater) read as a dark block over the back of the head: the two straps and the back pad each had a 3 px outline, and the outlines merged. The north view is now one thin charcoal strap across the back at y 66-72, as the glass mask's back is drawn, with no back pad or side buckles. The author approved it after the in-game recapture (`work/gear-look-2/`): "Approve all three". The item, south and east textures are unchanged (same hashes above).
  - New `LowVolumeMask_north.png` (and `LowVolumeMask_A_twin_north.png`) `39a6aabacf3808d600587c919ca2c10ded9e93a82562c252bbbafa01bfdc1872`; the hash above is the first draw's.
  - Script SHA-256 `bc786140466f66253c329f700c112c006f50693346329b3e36f5fe69b7ad4cb7` (working tree, CRLF). The regenerated contact sheet is `work/lvm-look/contact-sheet.png` in the main checkout, beside an offline before/after `work/lvm-look/north-before-after.png`.

Approval is final: a change to these pixels, the framing or the colour is a new candidate that needs a new approval.
