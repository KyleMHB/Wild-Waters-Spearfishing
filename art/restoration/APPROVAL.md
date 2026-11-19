# Restore sea floor icon and mark: approval record

**Status:** approved 2026-11-18: candidate A, cutting and arrow, for both the icon and the mark. Ticket: `.scratch/fish-recovery/issues/06-restoration-icon-and-mark.md`. The other candidates stay here for history.

## Pieces

- **Icon:** the "Restore sea floor" button in the orders menu, replacing `UI/Designators/ExtractTree`. 64x64 RGBA, the size of vanilla designator icons and of the loose designator PNGs in other mods. Fixed colour, no mask. Drawn like the approved items (fry pail, foam buoy): a black exterior contour, black lines between materials, a few broad shapes lit from the upper left.
- **Mark:** the designation drawn on each marked cell, replacing `Designations/ExtractTree`. 64x64 RGBA, one cell. A designation is drawn above the map, so the mark is a light glyph with a black contour at full opacity. It is unlike the artificial reef, which sits under the surface without an outline. Only bare sea floor can be marked (`Designator_RestoreSeaFloor.CanDesignateCell`), but the mark sits beside reef and kelp, so the sheet shows it over all three.

## Candidates

The idea: a diver moving coral and kelp cuttings onto bare sea floor to restore it.

| Key | Name | Icon | Mark | Icon files | Mark files |
| --- | --- | --- | --- | --- | --- |
| A | Cutting and arrow | A coral cutting and a kelp blade set into a sand mound, with a light arrow pointing down at the spot | A light coral sprig on a ground line with a down arrow beside it | `Restoration-A-cutting-and-arrow-Icon.png`, `_master256` | `Restoration-A-cutting-and-arrow-Mark.png`, `_master256` |
| B | Nursery frame | A low steel frame on sand with two coral cuttings and a kelp blade tied along its rung, like a reef nursery | A light square frame with a coral sprig rising out of it | `Restoration-B-nursery-frame-Icon.png`, `_master256` | `Restoration-B-nursery-frame-Mark.png`, `_master256` |
| C | Diver's hand | A blue dive-gloved hand reaching down from the upper right, lowering a coral cutting onto a sand patch where a kelp cutting is already planted | A light coral sprig on a ground line with coral-pink tips: the one mark that tests a colour accent | `Restoration-C-divers-hand-Icon.png`, `_master256` | `Restoration-C-divers-hand-Mark.png`, `_master256` |

Measured on the 64 px exports (the median black run inward from the alpha edge, every channel 25 or below, and the saturation p90 of coloured pixels):

| Key | Icon outline | Icon saturation p90 | Mark outline | Mark saturation p90 |
| --- | --- | --- | --- | --- |
| A | 2.0 px | 0.53 | 2.0 px | 0.07 |
| B | 2.0 px | 0.51 | 2.0 px | 0.07 |
| C | 3.0 px | 0.51 | 2.0 px | 0.53 |

All are inside vanilla's 2–3 px for buildings and resources. C's icon measures wider where the lines between the glove, cuff and cutting meet its contour.

## Contact sheet

`work/contact-sheets/restoration-candidates.png` in the main checkout (ignored). For each candidate it shows:

- the icon at 64 px on a plain model of a menu button, and at 2x;
- the mark at 64 px per cell over bare sea floor, reef and brown kelp;
- the mark over a drag of 8x4 cells across reef, bare floor and kelp at 32 px per cell (normal zoom), in shallow and deep ocean.

The sheet is a model, not a game capture. It uses the artificial reef sheet's water model: flat sea fills sampled from Waves' water at noon, the approved reef and brown kelp overlays, and plain alpha blending. The mark is drawn on top at full opacity. The menu button is a plain model, not vanilla's.

No vanilla designator icon or mark is on the sheet. Vanilla's textures ship inside the game's asset files, and no extracted copy of Ludeon's art source was at hand. That comparison is pending: downloading the art source needs the author's permission.

## Source

`restoration_art.py` in this folder draws everything procedurally with Pillow 12.3, NumPy and SciPy. No reference images, and no vanilla, Waves, DLC or third-party art, went into the masters or exports. The sheet reads the approved reef and kelp overlay masters from `art/reef` and `art/kelp`, and imports only the water model from `art/artificial-reef/artificial_reef_art.py`.

- Run `python -I art/restoration/restoration_art.py art/restoration E:/Coding/Rimworld/Spearfishing/work/contact-sheets/restoration-candidates.png`. Leave out the sheet path to write the candidates only. It never writes to `Textures/`, and a rerun gives byte-identical PNGs.
- Export: each 256 px master reduced uniformly to 64 px with Lanczos. The masters use a 10 px exterior contour (2.5 px at 64) and 6 px lines between materials (1.5 px at 64); the marks use an 8 px contour.

Hashes (SHA-256) of the exports at this version:

- `Restoration-A-cutting-and-arrow-Icon.png`: `96262ea940d52e27ded7a5ac399db710631874b3daa7024e0791c011171367bd`
- `Restoration-A-cutting-and-arrow-Mark.png`: `09f463ba0457bb950cb281bf3b0fdda79a6b2f6b1b7a126f19cb753cd9cd4109`
- `Restoration-B-nursery-frame-Icon.png`: `a69fa0b5bfbdf3123c80ddc30dd3b2ddc7157b189a2229448e7aef4d660c4773`
- `Restoration-B-nursery-frame-Mark.png`: `f11f65e1a6c937f8b7138b9f1c9fbfa8a223749eb4acf3b2605104be87ab8bac`
- `Restoration-C-divers-hand-Icon.png`: `220f23e30278caabdc0b9d8bf763e246478a14a243106d21678a8d1a3c06f705`
- `Restoration-C-divers-hand-Mark.png`: `bd3595887ed9d93521b30ad14b92cd9f85c5ba1ef9bd017626b297a3bea37c3d`

The icon and the mark may be picked from different candidates.

## Pick

Pick: A for both the icon and the mark, 2026-11-18, by the author through the orchestrator. Author's words: "A for both".

## Approval

- **In the game:** `Restoration-A-cutting-and-arrow-Icon.png` copied unchanged to `Textures/UI/Designators/Spearfishing_RestoreSeaFloor.png` (the designator's `icon`), and `Restoration-A-cutting-and-arrow-Mark.png` to `Textures/Designations/Spearfishing_RestoreSeaFloor.png` (the `Spearfishing_RestoreSeaFloor` designation's `texturePath`).
- **Hashes (SHA-256) of the approved version:**
  - `Restoration-A-cutting-and-arrow-Icon.png` and `UI/Designators/Spearfishing_RestoreSeaFloor.png`: `96262ea940d52e27ded7a5ac399db710631874b3daa7024e0791c011171367bd`
  - `Restoration-A-cutting-and-arrow-Mark.png` and `Designations/Spearfishing_RestoreSeaFloor.png`: `09f463ba0457bb950cb281bf3b0fdda79a6b2f6b1b7a126f19cb753cd9cd4109`
  - `Restoration-A-cutting-and-arrow-Icon_master256.png`: `ab0bb96165f44af8629b1d8e1b32cda5f49f1dff011908c1e0d9fbbfa5c37fb6`
  - `Restoration-A-cutting-and-arrow-Mark_master256.png`: `07c58c924071392c733a72f461757474501ce570487e50a7a4995f10b3f84be1`
  - `restoration_art.py`: `b46e01b1e9eafe7fc9436f46a6de9678860a415eb7644115a0278b3a4cd86bea`

- **Seen in the game:** `work/contact-sheets/restoration-ingame.png` in the main checkout (ignored), from the `spearfishing-restoration` batch on 2026-11-18: three marks on bare deep ocean at about vanilla's closest zoom.

Approval is final: a change to these pixels or their size is a new candidate that needs a new approval.
