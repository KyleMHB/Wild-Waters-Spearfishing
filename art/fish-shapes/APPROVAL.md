# Fish shoal shapes: approval record

## Approved (ticket 23)

Approved by the author on 2026-11-16: "Fish a looks good." The agent picked look A while the author was away; the author has since reviewed both sheets and chose A.

Follow-up the same day (ticket 27): "Depth should actually determine how crisp the edge is, shallower sharper, deeper blurrier." The shallowest water should be about as crisp as look B, middle depth look A, and the deepest softer than A, easing smoothly with depth. Ticket 27 adds the extra blur levels and records them below.

- **Look:** four bold top-down outlines facing east (head to the right), in the soft-edged style of the approved fish shadow, plus that shadow unchanged as the generic outline. The renderer tints, scales, fades and bends them.
  - **Slim** (mackerel-like): drawn 0.55 cells long, full shoal 8 fish.
  - **Stocky** (bream-like): 0.6 cells, full shoal 5.
  - **Large** (broad head, swept-back pectoral fins): 0.85 cells, full shoal 3.
  - **Long** (eel-like): 1.0 cell, shoals of 1-2.
  - **Generic:** `FishShadow.png` (since ticket 27 `FishShadow_Medium.png`), 0.6 cells, full shoal 6.

  Over the shallowest water a fish draws at full size and 50% alpha; over the deepest at 72% size and 28% alpha. The tail sway is a bent mesh, not a texture: the tail tip shifts sideways by up to 0.09 of the fish's length.
- **Picked:** look A, a 1.6 pixel blur at 8x supersampling on 64 by 64 pixels. Ticket 27 renamed these textures to `Fish<Shape>_Medium.png` with the same pixels (see below).
  - `Textures/Spearfishing/Dive/FishSlim.png`, SHA-256 `62d7bd633619a829360026bebc1fe826382d22de49c9dcca545725a788e913e8`
  - `Textures/Spearfishing/Dive/FishStocky.png`, SHA-256 `95235efd240fdf47c4e57ff6a2acce0233fd1ec81fe9aac1b3bb4f127e902833`
  - `Textures/Spearfishing/Dive/FishLarge.png`, SHA-256 `ba3c641d5c8f1abb2b7851edd8e877aeca8c058529e5c2cf7f88dd9337b00ff6`
  - `Textures/Spearfishing/Dive/FishLong.png`, SHA-256 `d280085249470f55dac4a32a9bef4bb54a734364ab50c170709acdd29d7c5199`
- **Rejected:** look B, the same shapes with a 0.8 pixel blur. Crisper, but it no longer matches the approved fish shadow and reads as cut-out shapes at game scale.
- **Source:** `fish_shapes_art.py` in this folder draws both looks and the panels (`python -I fish_shapes_art.py <out_dir> [<texture_dir>]`, Pillow 12.3). With a texture folder it writes look A's textures there.
- **Contact sheets:** made with the Templates `contact-sheet` tool into the ignored `work/contact-sheets/`. Each shows every outline alone, a shoal of each at game scale, six tail-sway frames, and sizes over shallow and deep water.
  - A: `fish-shapes-A.png`, SHA-256 `0cebc2a1f6b590f0f035bb4a41d3481c312f1b3b5909a9c7ab59aad2584a330a`
  - B: `fish-shapes-B.png`, SHA-256 `270bed7a2a5870ea3e6e0d2cd03948739844bfbfe1c5679e0defd5a8db1b264f`
- **To undo:** superseded by ticket 27's undo below. Look B is the same 0.8 pixel blur as ticket 27's crisp level.

## Approved on 2026-11-16: depth blur levels (ticket 27)

- **Look:** every fish outline (the four shapes and the generic one) at three edge blur levels from `art/depth_blur.py` (`BLUR_LEVELS`, shared with ticket 26's dive shadow): crisp 0.8 px (look B's blur), medium 1.6 px (look A, unchanged) and soft 2.8 px. The game crossfades a fish's two neighbouring levels by the swim depth under it, crisp over the shallowest water, medium at half depth and soft over the deepest. The depth, and with it ticket 23's size and alpha, eases over half a second, so a fish changes gradually instead of at a cell edge. The speared fish's dart keeps the medium level.
- **Approved:** 2026-11-16, by the author through the orchestrator.
- **Author's words:** "Approve as is".
- **Shipped textures:** white shapes, 64 by 64, which the renderer tints, scales, fades, bends and crossfades. Each `_Medium` file is byte-identical to the single texture it replaces.
  - `Textures/Spearfishing/Dive/FishShadow_Crisp.png`, SHA-256 `86417e57f72c6d880e983d0c5331daaaa0dca15e9832752ce48b1396ab266e9f`
  - `Textures/Spearfishing/Dive/FishShadow_Medium.png`, SHA-256 `0bbfa4318e408899b1ab97735e652c3b83fcda4c257af06caacace1917145e33`
  - `Textures/Spearfishing/Dive/FishShadow_Soft.png`, SHA-256 `cafb74ba7a79d7aadab89dba2abf8e8723dda7dbe7ac5def4806fbfd9c5d6fff`
  - `Textures/Spearfishing/Dive/FishSlim_Crisp.png`, SHA-256 `9df7a27247f957894dc6c63fcfaf63982fe31bf5019c4e2f49ab0ebcb10e6217`
  - `Textures/Spearfishing/Dive/FishSlim_Medium.png`, SHA-256 `62d7bd633619a829360026bebc1fe826382d22de49c9dcca545725a788e913e8`
  - `Textures/Spearfishing/Dive/FishSlim_Soft.png`, SHA-256 `99c83d1da4f4972146a71b993444e67274fda9ffe527240ccb319a40a1f91ae8`
  - `Textures/Spearfishing/Dive/FishStocky_Crisp.png`, SHA-256 `cedd0361bbd90cdcd7ff4eac2878069649f38ac92ceb552fc297cf724b78f100`
  - `Textures/Spearfishing/Dive/FishStocky_Medium.png`, SHA-256 `95235efd240fdf47c4e57ff6a2acce0233fd1ec81fe9aac1b3bb4f127e902833`
  - `Textures/Spearfishing/Dive/FishStocky_Soft.png`, SHA-256 `b5026f9e6f54de64ca7254382dc38567afe32dcfb35e110ce76550fd9c740b9e`
  - `Textures/Spearfishing/Dive/FishLarge_Crisp.png`, SHA-256 `3e8e2bcbcdb00c64c17328c8c0dfde7bd52fc128972a2a0e380813952a9942f4`
  - `Textures/Spearfishing/Dive/FishLarge_Medium.png`, SHA-256 `ba3c641d5c8f1abb2b7851edd8e877aeca8c058529e5c2cf7f88dd9337b00ff6`
  - `Textures/Spearfishing/Dive/FishLarge_Soft.png`, SHA-256 `c472c05854a977cc914f9789f9c59d9b7e7061c2ebf92e5ee17081f6c2b2caae`
  - `Textures/Spearfishing/Dive/FishLong_Crisp.png`, SHA-256 `6c0a7e87d8d95e42e529b684643f6637c2310a0af4ceffd2455d3283a39161fe`
  - `Textures/Spearfishing/Dive/FishLong_Medium.png`, SHA-256 `d280085249470f55dac4a32a9bef4bb54a734364ab50c170709acdd29d7c5199`
  - `Textures/Spearfishing/Dive/FishLong_Soft.png`, SHA-256 `782d18c856609932ed7fc1e6f144991a1fb4e9649d73f0ec2c4944f568b062ea`
- **Source:** `fish_shapes_art.py` in this folder redraws the generic outline from `art/dive-visuals/dive_art.py`'s shadow A so it can take every level, and writes all fifteen textures. Command: `python -I art/fish-shapes/fish_shapes_art.py work/fish-shapes Textures/Spearfishing/Dive`, Pillow 12.3.
- **Contact sheet:** `fish-shapes-depth-blur.png` in the ignored `work/contact-sheets/`, SHA-256 `d95e878df9b12c3081a15d3f8f5db6efd2fffcfa43b35594c060eabdb163c989`.
- **Removed on 2026-11-16:** `FishShadow.png`, `FishSlim.png`, `FishStocky.png`, `FishLarge.png` and `FishLong.png`. Their pixels live on unchanged as the `_Medium` files.
- **To undo:** for one blur level everywhere, set `BlurLevels` in `Source/Visuals/FishShoals.cs` to `{ "Medium", "Medium" }` (or rename the `_Medium` files back and drop the level suffix from the texture paths), then delete the `_Crisp` and `_Soft` files. To drop the shapes as well, point every `TexPaths` entry at the generic outline.
