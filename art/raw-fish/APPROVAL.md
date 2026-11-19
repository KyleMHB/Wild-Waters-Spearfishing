# Raw fish: approval record

- **Piece:** raw fish, `Textures/Things/Spearfishing/Item/RawFish/RawFish_{a,b,c}.png` (64x64 RGBA, 64 px per cell, 2 px black outward outline), read by `Spearfishing_RawFish` as `Graphic_StackCount` (a: one fish, b: two, c: four).
- **Approved:** 2026-11-15, by the author through the orchestrator's question dialog.
- **Author's words:** "Fish are fine, the barbs on the spear are too fine in terms of detail. Rework it" (reply to contact sheet v3). Earlier choices that shaped it: "snapper shape with mullet colour", "Three stack sizes (Recommended)", "Procedural is fine", then "uh sorry make the fish the blue colour not green".
- **Compared:** round 1 candidates A mackerel, B snapper and C mullet beside vanilla raw meat; v2 (snapper shape, mullet colours, smaller, softer); v3 (the same in mackerel blue-grey), approved.
- **Source:** `RawFish_a.png`, `RawFish_b.png` and `RawFish_c.png` in this folder, drawn by `raw_fish_art.py` (`python -I raw_fish_art.py <out_dir>` regenerates them byte for byte with Pillow 12.3). Procedural; no reference images, DLC or third-party art used. Script SHA-256 `8aa3b91719ef83f10b389395367a1d4eef013792f0a31d38416b9da6b091cab0`.
- **Export recipe:** copied unchanged; the masters are already the game textures' size.
- **Exported textures:**

| File | SHA-256 |
| --- | --- |
| `RawFish_a.png` | `f877961e0b0c989f53f738f28180bdac230ad2811cd4753fef72d5d45da94001` |
| `RawFish_b.png` | `8f4203bc26e49123700b1e40e79a7799433b187f746f4f43eb5517da745714d6` |
| `RawFish_c.png` | `0bdfa788cb62b717253ce18456ee6b4bb6d8b6e286e1e92bda3577d2e108a9cf` |

Approval is final: a change to these pixels, the stack layout or the colour is a new candidate that needs a new approval.
