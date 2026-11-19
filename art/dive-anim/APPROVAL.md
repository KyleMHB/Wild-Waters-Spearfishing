# Dive shadow and surface animations: approval record

- **Look:**
  - **Dive shadow:** while a pawn is under the water, a dark head-and-shoulders shape (look C's shoulders plus a head) draws under Waves' surface at their spot. It shrinks and fades as they go down, holds small at the bottom, and grows and darkens as they come up.
  - **Going under:** one pale ripple spreads out from the head and fades, over 0.8 s.
  - **While down:** a small cluster of three bubbles rises and pops as a tiny ring, every 1.4 s.
  - **Coming up:** the same single ripple as going under.

  No glow, so none of it reads as Waves' night plankton.
- **Approved:** 2026-11-15, by the author through the orchestrator, over two sheets.
- **Author's words:**
  - Round one (shadow approved, animations sent back): "Going under I like the shadow gonig down, but a ring should spread from them diving down, like a ripple, outward. The same should happen when they come up. With maybe some bubble animations coming up from them when they are down there."
  - Round two picks: going under "1: one ripple"; bubbles "2: small cluster"; coming up "1: one ripple".
- **Compared:**
  - Round one: the dive shadow at five depths; going under A ring pulls in, B bubble burst, C ring in and bubbles; coming up A double ripple, B ring opens and spray, C spray crown.
  - Round two: going under 1 one ripple or 2 two ripples; bubbles 1 one at a time or 2 small cluster; coming up 1 one ripple or 2 two ripples.

  Frames are composited at game scale over in-game captures of a face-down pawn and the same view with that pawn under the water.
- **Shipped textures:** white shapes the renderer tints, scales and fades.
  - `Textures/Spearfishing/Dive/DiveShadow.png`, SHA-256 `2c9f8e886060779b266a1fcbf96f15bf7172c759f39bfc1aa0b4fa2d633f34e8`. Removed on 2026-11-16: ticket 26's pawn-shaped shadow replaces it (see below).
  - `Textures/Spearfishing/Dive/Ripple.png`, SHA-256 `e964eeb1714f09edcaaa23643f12bcb97e4b2c3d8700f2fa3ed6d5fc6b472fec`
  - `Textures/Spearfishing/Dive/Bubble.png`, SHA-256 `d9812043edb3d35be07801f1d05c7f42b073b39791fae7af9f52ef1074073cd8`
- **Source:** `dive_anim_art.py` in this folder drew the shapes and the frames (`python -I dive_anim_art.py <out_dir> [<frame> <background> <head_x> <head_y>]`, Pillow 12.3). The droplet and spray-crown shapes were not chosen and are not shipped. The script is kept as the record of what was compared.
- **Contact sheets:** made with the Templates `contact-sheet` tool into the ignored `work/contact-sheets/`:
  - round one `dive-anim.png`, SHA-256 `64cd35914c0c7e63287b92430c59a2fdf9ebff1ae59c57f70520c43c12ad0f5e`;
  - round two `dive-anim-v2.png`, SHA-256 `b3fac4cdf8efcc8d2a56a717e66c499ad7e2aac6d6d76a3e48dc09bff86e20cc`.

Approval is final. A new shape or timing is a new candidate and needs a new approval. The in-game capture for review is in ticket 20's Comments.

## Approved on 2026-11-16: pawn-shaped dive shadow (ticket 26)

- **Look:** a solid silhouette of a vanilla pawn seen from behind: the average (male) body with a rounded top, no shoulders, hips that curve like vanilla's outline, and an egg-shaped head. One shape for every body type. The game turns it by heading with the head leading, keeps ticket 22's 0.3-cell offset, and shrinks and fades it by depth as before. Its edge follows the water's depth: crisp over shallow water, softer over deep.
- **Approved:** 2026-11-16, by the author through the orchestrator, on the v2 sheet.
- **Author's words:**
  - On ticket 22's shadows: "the shadow doesnt look like a pawn from rimworld, pawns dond have shoulder, look at the body shape paws have and fix it. Other than that the direction and everything else of the dive shadows look good on A."
  - On the surface size: "size at top should be the size of the pawn basically". The silhouette fills 0.84 of its texture's height, so `DiveShadowSurfaceSize` is 1.35 and the shadow is about a pawn's 1.14 cells tall at the surface.
  - On deep softness, the author followed the recommendation: soft stays at 2.8 px rather than the 3.6 px candidate.
- **Shipped textures:** three blur levels of the same white silhouette, 64 by 64, which the renderer tints, scales, fades and crossfades by `SwimDepthAt` at the diver's cell.
  - `Textures/Spearfishing/Dive/DiveShadowPawn_Crisp.png` (0.8 px blur), SHA-256 `215276502869fe7a7739cb321da358ae5b04f7dd3755d55c106a6a8291892510`
  - `Textures/Spearfishing/Dive/DiveShadowPawn_Medium.png` (1.6 px), SHA-256 `c5bf65fc959d87d5510e812a7ad7f9d626762e59f4588f7b67f455884f585834`
  - `Textures/Spearfishing/Dive/DiveShadowPawn_Soft.png` (2.8 px), SHA-256 `ce0e4cade447d2dbf245db7b207fd67581647e5670b348f7822e8e8709a0b48b`
- **Source:** `dive_shadow_pawn_art.py` in this folder draws the silhouette parametrically from proportions measured on vanilla's north textures (no traced pixels, no vanilla texture committed). The blur levels come from `art/depth_blur.py` (`BLUR_LEVELS`), which ticket 27 shares for fish. Command: `python art/dive-anim/dive_shadow_pawn_art.py Textures`, Pillow 12.3.
- **Contact sheets:** in the ignored `work/contact-sheets/`: `dive-shadow-pawn.png` (round one), `dive-shadow-pawn-v2.png` (approved, smoothed hips, size and softness strips) and the work-only outline checks `dive-shadow-pawn-reference.png` and `dive-shadow-pawn-reference-v2.png`.
- **Removed:** `DiveShadow.png` (look A) and `DiveShadowSwim.png` (provisional B). Nothing else used them.

## Provisional, awaiting approval (ticket 22)

Superseded on 2026-11-16 by ticket 26's approved shadow; `DiveShadowSwim.png` is removed. Kept as the record of what was compared.

Not approved. The orchestrator asked the ticket 22 agent to pick a provisional shadow so the game could turn it to the way the diver swims. The author has not seen it. It stays provisional until they approve it, and may be replaced.

- **Look:** a top-down swimmer facing north, head leading and torso trailing, so the head points the way of travel at any angle. The game turns it by heading. At the bottom of a dive it is 0.85 of surface size and almost as dark as at the surface over the shallowest water, and 0.55 at 22% alpha over the deepest, as before.
- **Picked:** candidate B, `Textures/Spearfishing/Dive/DiveShadowSwim.png`, SHA-256 `44de39abd06d77029d5105de0a873bd51b04cf1045ba82ff90d5eee3e5f48e05`. A white shape on 64 by 64 pixels, drawn at 8x supersampling with a 1.6 pixel blur: head ellipse x 23 to 41, y 3 to 21; shoulders rounded rectangle x 9 to 55, y 18 to 32, radius 7; torso polygon (14,26), (50,26), (40,58), (24,58); hips ellipse x 24 to 40, y 52 to 61.
- **Rejected:** candidate A, the approved `DiveShadow.png` turned by heading. Seen from above it has no clear front, and at diagonals and at east or west it reads as a clover.
- **Contact sheets:** made with the Templates `contact-sheet` tool into the ignored `work/contact-sheets/`. Each shows eight headings at shallow (0.85, 50% alpha), middle (0.70, 36%) and deep (0.55, 22%) bottom sizes.
  - A: `dive-heading-A1.png`, SHA-256 `0de922b5ac81e2c5537ea83c25e77c854006ffca37de5550de885eb073593d7f`; `dive-heading-A2.png`, SHA-256 `2adcdfb00fd2a14ea9c6d477365696f6e2b8d975237f4068525035977fa755cb`.
  - B: `dive-heading-B1.png`, SHA-256 `06fa6dde5313ec4d7713d29ac30e1d3f074117b22282c609ae643021d242ecf6`; `dive-heading-B2.png`, SHA-256 `f4664f3e8124a8b0835cce36c096b44bc557c5e753704b6880ea028207aa8f0f`.
- **To undo:** point `DiveShadowTexPath` in `Source/Visuals/DiveVisuals.cs` back at `Spearfishing/Dive/DiveShadow` and delete `DiveShadowSwim.png`. The approved `DiveShadow.png` is unchanged.

## Rejected on 2026-11-16 (ticket 22)

The author reviewed both heading sheets (`dive-heading-A1/A2`, `dive-heading-B1/B2`) and rejected both shapes, verbatim: "the shadow doesnt look like a pawn from rimworld, pawns dond have shoulder, look at the body shape paws have and fix it. Other than that the direction and everything else of the dive shadows look good on A."

- A (`DiveShadow.png`, head and shoulders, turned by heading) and B (`DiveShadowSwim.png`, top-down swimmer with shoulders) are both rejected as shapes. A's turning, offset and depth sizing are approved.
- Asked how to replace it, the author chose a solid fill of vanilla's average body and head outline seen from behind (north), one shape for every body type, turned by heading with the head leading. Ticket 26 draws it. Until it is approved, the build keeps B as a placeholder.
- The same day the author asked for the shadow's edge to follow depth like the fish: crisper in shallow water, blurrier in deep (ticket 27).
