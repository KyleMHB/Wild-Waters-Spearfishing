# Urchin barren: approval record

**Status:** approved 2026-11-18: candidate B, drained floor. The other candidates stay here for history. Ticket: `.scratch/threat-events/issues/02-urchin-barrens.md`, part 1.

## Piece

The look of an urchin barren: reef or kelp in the sea that urchins have grazed bare (GLOSSARY "Urchin barren"). It is drawn like the reef and kelp overlays (`art/reef`, `art/kelp`): a 512x512 RGBA texture that tiles every 8x8 cells at 64 px per cell, alpha-blended under the water surface by a `SectionLayer_FloorOverlay` at Waves' sea-life render queue, with patch edges faded and deep cells at 0.7 strength. It has no outline, like the reef. The decisions ask for "the reef overlay drained of colour with a scatter of small dark urchins".

## Candidates

The three differ in structure, not only in look, because each means different part 2 code.

| Key | Name | Look | Textures | What it means in part 2 |
| --- | --- | --- | --- | --- |
| A | Coralline rock | The reef's rock shelves redrawn pale pink-grey (the coralline crust real barrens show) over a faint pale wash, with urchins. The same over reef and both kelps. | `UrchinBarren-A-coralline-rock.png` | One texture and one new layer. Reef and kelp layers skip barren cells. |
| B | Drained floor | Each approved overlay drained of colour, lightened and thinned (kelp more than reef) over a faint pale wash, with urchins. Shows what grew there. | `UrchinBarren-B-drained-floor-Reef.png`, `-KelpBrown.png`, `-KelpOlive.png` | Three textures. The layer picks one by the cell's old mark, which the barren keeps anyway for recovery. Reef and kelp layers skip barren cells. |
| C | Urchins over the floor | A pale wash that dulls the unchanged reef or kelp under it, with denser urchins. | `UrchinBarren-C-urchins-over-floor.png` | One texture, drawn above the reef and kelp layers, which keep drawing barren cells. Barren kelp would still sway under the urchins. |

Urchins in all three: dark purple-black discs about 6 px across at 64 px per cell (3 px at normal zoom), a soft spine halo and a small highlight to the upper left, gathered in loose groups by a tiling density field. Fine spines vanish at game size, so there are none. A and B average 6 urchins a cell, C 8.

## Contact sheet

`work/contact-sheets/urchin-barren-candidates.png` in the main checkout (ignored). Rows: the healthy approved look, then each candidate. For reef, brown kelp and olive kelp, in shallow and deep ocean, it shows:

- a patch of 11x7 cells at 32 px per cell (normal zoom) with a barren eating into its right side, the healthy and barren parts sharing a border;
- a close-up of 4x3 cells at 64 px per cell, left half healthy, right half barren.

The sheet is a model, not a game capture. It uses the artificial reef sheet's water model (flat sea fills sampled from Waves' water at noon, `SectionLayer_FloorOverlay`'s corner fade and deep strength 0.7) and plain alpha blending.

## Source

`urchin_barren_art.py` in this folder, procedural with fixed seeds (Pillow 12.3, NumPy 2.3). A and B start from the approved reef and kelp masters in `art/reef` and `art/kelp`; no reference images and no vanilla, Waves, Living Waters or third-party art. Every noise field is periodic and every urchin is drawn at its wrapped offsets, so the tile repeats without seams (checked 2026-11-18: edge-to-edge differences match neighbouring-row differences).

- Run `python -I art/urchin-barren/urchin_barren_art.py art/urchin-barren E:/Coding/Rimworld/Spearfishing/work/contact-sheets/urchin-barren-candidates.png`. Leave out the sheet path to write the candidates only. It never writes to `Textures/`, and a rerun gives byte-identical PNGs.
- Export: each PNG is its own master, already the game texture's size and tiling, so there is no separate master.

Hashes (SHA-256) at this version:

- `urchin_barren_art.py`: `bc79045bea868817553b1cbfae74cbc502e8cb94023f9aefa53829ae6b223047`
- `UrchinBarren-A-coralline-rock.png`: `ea46e94d84e1e002c417315ccc8a7de53f70018bc25e919c4b9a99d59df99842`
- `UrchinBarren-B-drained-floor-Reef.png`: `0b5c7d31c4cbda64bc0171bd3cf7029a23833c3ca184a6e20913690e4e7afc51`
- `UrchinBarren-B-drained-floor-KelpBrown.png`: `cb145a7e1fef8054778874f578ea66bf05efcddd399a9186b0bad031216929e0`
- `UrchinBarren-B-drained-floor-KelpOlive.png`: `a93867489abfa087d65b4a6fa738b2d8e8e6ac52ebc941d190cecf028f5d560e`
- `UrchinBarren-C-urchins-over-floor.png`: `091ee1c130a2f817299927ea0836a321fa16438a9773ebfce38b896069640770`

## Culled cells

A culled cell shows plain bare sea floor (nothing drawn) until its reef or kelp returns about 5 days later. The author answered this through the orchestrator on 2026-11-18.

## Pick

Pick: B, drained floor with dark urchins, 2026-11-18, by the author through the orchestrator.

## Approval

- **In the game:** the three B textures are copied unchanged to `Textures/Spearfishing/Terrain/`. `SectionLayer_UrchinBarren` draws each over barren cells whose kept floor matches it, at the reef overlay's render queue, edge fade and deep strength. The barren replaces the reef or kelp look on those cells rather than drawing over it, so barren kelp doesn't sway.
  - `UrchinBarren-B-drained-floor-Reef.png` becomes `UrchinBarrenReef.png`: `0b5c7d31c4cbda64bc0171bd3cf7029a23833c3ca184a6e20913690e4e7afc51`
  - `UrchinBarren-B-drained-floor-KelpBrown.png` becomes `UrchinBarrenKelpBrown.png`: `cb145a7e1fef8054778874f578ea66bf05efcddd399a9186b0bad031216929e0`
  - `UrchinBarren-B-drained-floor-KelpOlive.png` becomes `UrchinBarrenKelpOlive.png`: `a93867489abfa087d65b4a6fa738b2d8e8e6ac52ebc941d190cecf028f5d560e`
- **Seen in the game:** pending. On 2026-11-18 no in-game run was possible: since the RimWorld 1.7.5013 update, every harness launch hung while waiting for the map.

Approval is final: a change to these pixels, the tile size or the colour is a new candidate that needs a new approval.
