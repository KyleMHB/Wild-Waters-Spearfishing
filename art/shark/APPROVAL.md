# Shark shadow: approval record

- **Pieces:** the shark encounter's shadow (gear tiers ticket 11), `Textures/Spearfishing/Dive/SharkShadow_Crisp.png`, `SharkShadow_Medium.png` and `SharkShadow_Soft.png`. Each is 256x256, a white top-down shark on transparent, facing east like the fish, at the depth blur levels of `art/depth_blur.py` (crisp 0.8, medium 1.6 and soft 2.8 texels). The renderer (`Source/Visuals/DiveVisuals.cs`) tints it with the dive shadows' `ShadowColor`, scales, fades, bends and turns it.
- **Status:** second candidate, **approved** 2026-11-17 by the author after the in-game recapture (`work/gear-look-2/`): "Approve all three". It replaces the first approved look (2026-11-17, ticket 11), which the in-game capture (`work/gear-look/shark-stills.png`, ignored) showed faint and about 1 cell long over deep ocean, lost among the fish shadows.
- **What changed from the first look:**
  - **Length:** 2.35 cells of canvas over deep ocean, a body of about 2.2 cells (a 2 to 3 m shark beside a pawn), scaled from there by the dive shadow's bottom-of-dive size. The first look was 2.5 cells at the surface scale, about 1 cell over deep ocean.
  - **Darkness:** material alpha 0.70 over deep water, up to 0.85 as it rises for the bite, against 0.30 and 0.50 before. Deep fish are 0.28 and the deep diver 0.22.
  - **Silhouette:** a pointed snout, larger swept pectoral fins, a crescent tail with the upper lobe longer, and a dorsal ridge and spine at full texture alpha over a body at 190/255, so the tint shows a darker line down the back.
  - **Texture size:** 256 instead of 128, so the blur levels stay close to the deep dive shadow's texels per cell (about 109 against 116).
  - **Unchanged:** the motion, timing, sway and the bite's `Ripple`.
- **Preview:** `work/shark-look-preview.png` (ignored), before and after at the stills' 66 px per cell beside fish shadows and the swimmer.
- **Source:** `shark_art.py` in this folder draws the shark procedurally with Pillow. No reference images, vanilla, Waves, DLC or third-party art went into it; the sheet reads the approved dive shadow from `Textures/` and writes nothing back except, when asked, the three game textures.
  - Run `python -I art/shark/shark_art.py <out_dir> [<texture_dir>]` with an out folder under `work/`; with `Textures/Spearfishing/Dive` as the texture folder it exports the game textures, which are then copied here as the masters.
  - Script SHA-256 (LF line endings) `4f7a41b91d3fda6c5362607a9f1cebe3e61eb4ebbf493c586be78c26a02abc48`.
- **Exported textures (SHA-256), byte for byte the masters in this folder:**
  - `SharkShadow_Crisp.png` `1d50b880a8f9070342be206c5011ab1247f3762adf9bc636cc110011facb5086`
  - `SharkShadow_Medium.png` `6cd00dee2297025c39dae0ab89ceac631cd20e960f6e13d659395ab9c0c23330`
  - `SharkShadow_Soft.png` `cc3c7e3e1f301325429459c18aaad9718128e89638ddac4c440779dfe9a14fdb`

Once approved, approval is final: a change to these pixels, the shape, the size or the alpha is a new candidate that needs a new approval.
