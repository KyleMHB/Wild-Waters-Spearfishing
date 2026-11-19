# Face-down floater: approval record

- **Look:** a pawn floating at the surface at their spot (a snorkeler, or a diver resting between dives) is drawn from behind (north view) whichever way they face, with worn headgear, and with no body, sunk as the game sinks a swimmer's head. Look C adds a dark sunk-shoulders shape under the water and a pale waterline ring around the head. The glass mask's strap and the snorkel tube show over the hair: from behind they draw at layers 66 and 67, above hair (62).
- **Approved:** look C, 2026-11-15, by the author through the orchestrator. This replaces the first choice, "Head only", from earlier the same day.
- **Author's words:** "the shoulders + ring look great" (choosing "C: shoulders + ring" from the sheet below).
- **Compared:** one contact sheet, rows no gear, glass mask, and mask with snorkel; columns:
  - head only (first chosen);
  - A, head and a pale waterline ring;
  - B, head and a faint dark sunk body;
  - C, head, sunk shoulders and the waterline ring (chosen).

  The heads are in-game captures of the face-down draw from harness runs `20261115-222844-spearfishing-visuals-s1` (no gear) and `20261115-223812-spearfishing-visuals-s1` (mask, mask and snorkel). The shapes were composited at game scale.
- **Shipped textures:** white shapes the renderer tints and fades.
  - `Textures/Spearfishing/Dive/Shoulders.png`, SHA-256 `d190558e506f1d791ef896c777e31803784308cacdb74e4a1b97cf436f8df346`
  - `Textures/Spearfishing/Dive/Waterline.png`, SHA-256 `459fd2b195fba99c208348c53ca3e1ac7c2d49ffe32ae0e98e2861497f8820b9`
- **Source:** `face_down_art.py` in this folder drew the candidate shapes and the composites (`python -I face_down_art.py <out_dir> [<frame> <background> <head_x> <head_y> <label>]...`, Pillow 12.3). The sunk-body shape (B) was not chosen and is not shipped.
- **Contact sheet:** made with the Templates `contact-sheet` tool into the ignored `work/contact-sheets/face-down.png`, SHA-256 `c487af8ebfbbe5ef04bc99acdc9d39a605c8b4f7e6aa5e4f04fa93149d609113`.

Approval is final. Changing the look again is a new candidate and needs a new approval. The in-game capture for review is in ticket 20's Comments.
