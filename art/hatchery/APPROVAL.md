# Hatchery and fry batch: approval record

**Status:** approved 2026-11-18. The refined hatchery C2 and fry pail A2 are in the game as `Textures/Things/Spearfishing/Building/Hatchery.png` and `Textures/Things/Spearfishing/Item/FryBatch.png`. The other candidates stay here for history.

## Pieces

- **Hatchery:** the building sprite, fixed colour, no mask. Exported at 128 px per cell, so a 2x2 is 256x256 and a 3x2 is 384x256. Only the south view is drawn, as `Graphic_Single` with `rotatable` false. If the chosen footprint needs rotation, the north and east views are derived from the picked design afterwards. The feed lid is small and neutral, so the art works for a hopper-fed building or one with its own storage; part 2 decides which.
- **Fry batch:** the carried item sprite, 128x128, `Graphic_Single`, drawSize 1, fixed colour, no mask.

## Candidates

| Key | Piece | Name | Footprint | Exported texture | Master |
| --- | --- | --- | --- | --- | --- |
| A | Hatchery | Four round tanks: one round tank per cell on a steel frame, piped to a small pump with a power light in the middle | 2x2 | `HatcheryA.png` | `HatcheryA_master.png` |
| B | Hatchery | Raceway rack: three long troughs under a header pipe, with a pump, power light and feed lid along the top | 3x2 | `HatcheryB.png` | `HatcheryB_master.png` |
| C | Hatchery | Pond tank: one large round tank with an aerator bridge to a central feeder, and a pump box in one corner | 2x2 | `HatcheryC.png` | `HatcheryC_master.png` |
| A | Fry batch | Fry pail: a steel pail of water with two fry and a wire handle | 1x1 | `FryBatchA.png` | `FryBatchA_master512.png` |
| B | Fry batch | Fry bag: a knotted clear bag, two thirds water, with two fry | 1x1 | `FryBatchB.png` | `FryBatchB_master512.png` |
| C | Fry batch | Fry tub: a low orange carry tub, open on top, with water, fry and a hand slot at each end | 1x1 | `FryBatchC.png` | `FryBatchC_master512.png` |

The candidates' files stay for history. C is superseded by C2 and A by A2 (see [Refined](#refined)); hatcheries A and B and fry batches B and C were not picked.

Measured on the exports, in vanilla terms (64 px per cell): the hatchery outline is 2.5 px (A and C) and 2.0 px (B), inside vanilla's 2–3 px for buildings. Saturation p90 is 0.60 for all three hatcheries and 0.60–0.65 for the fry batches.

## Contact sheet

`work/contact-sheets/hatchery-candidates.png` in the main checkout (ignored). It shows:

- the hatcheries at 128 px per cell on concrete;
- the hatcheries at normal zoom on soil, beside a vanilla pawn dump from `work/vanilla-ref` (sheet only, for scale);
- the fry batches at 1.5x and at game size, beside the approved raw fish and foam buoy;
- each hatchery with each fry batch beside it.

No vanilla building is on the sheet, because no extracted copy of Ludeon's art source was at hand. That comparison is pending: downloading the art source needs the author's permission.

## Source

`hatchery_art.py` in this folder draws everything procedurally with Pillow 12.3, NumPy and SciPy. No reference images, vanilla, Waves, DLC or third-party art went into the masters or exports. Its method follows the approved buoys' `buoy_art.py`: a few broad shapes, upper-left light, and a black exterior contour with black material lines. It keeps its own helpers, sized to any canvas.

- Run `python -I art/hatchery/hatchery_art.py art/hatchery E:/Coding/Rimworld/Spearfishing/work/contact-sheets/hatchery-candidates.png`. It never writes to `Textures/`.
- Building export: a uniform 1/4 Lanczos reduction of the whole footprint canvas.
- Item export: the buoys' `export(fill=100)`. It crops to the alpha bounds, scales uniformly with Lanczos so the longer side is 100 px, and centres the result on a transparent 128x128 canvas.

## Pick

2026-11-18: the author picked hatchery C and fry pail A, in their words: "hatchery c pail A but I'd like to refine them".

Asked three follow-up questions (1: hatchery C's look; 2: a darker steel frame with a small orange accent, and a larger feeder and pump/power box; 3: pail A a little smaller, tiny fry, a lighter water surface, same steel and handle), the author answered: "1 smaller fry, but mostly tha the corner light makes the big circle off centre, 2 yes, 3 yes". The extra rearing trays suggested in question 1 were not asked for and were not added.

## Refined

| Key | Refines | Change | Exported texture | Master |
| --- | --- | --- | --- | --- |
| C2 | Hatchery C | The tank is centred on the plate. The single corner pump box is replaced by two mirrored, larger pump/power boxes at 3 and 9 o'clock on the aerator bridge's ends, each with a power light, so nothing pulls the eye to a corner. Darker steel frame. Larger central feeder with an orange collar in the foam buoy's orange (203, 111, 63), the one accent. Six smaller fry. | `HatcheryC2.png` (256x256, 2x2) | `HatcheryC2_master.png` |
| A2 | Fry batch A | Same steel pail and wire handle. Lighter water surface, so it reads as water seen from above. Five tiny fry instead of two fish. Exported at fill 86 instead of 100, so its bounds are 78x86 px of 128, no taller than the raw fish stack (112x88 at the same scale). | `FryBatchA2.png` (128x128) | `FryBatchA2_master512.png` |

Measured on the exports, in vanilla terms (64 px per cell): C2's outline is 2.5 px, as C's was, inside vanilla's 2–3 px for buildings; A2's is 2.0 px. Saturation p90 is 0.60 for C2 and 0.41 for A2 (C and A were both 0.60).

Before/after sheet: `work/contact-sheets/hatchery-refined.png` in the main checkout (ignored). It shows C beside C2 and A beside A2 at 128 px per cell, and all four at game size on soil and concrete beside a vanilla pawn dump (scale only), the approved raw fish and the foam buoy, with a 2x nearest-neighbour enlargement of the game-size strip.

Run `python -I art/hatchery/hatchery_art.py art/hatchery - E:/Coding/Rimworld/Spearfishing/work/contact-sheets/hatchery-refined.png` to rebuild every candidate and the refined pair (the old candidates come out byte-identical) and the before/after sheet; `-` skips the candidates' sheet.

Hashes (SHA-256) at this version:

- `HatcheryC2.png`: `cfe057efa8fedb44d24023774c58825845c223e585bcebb915d25b1a2c776da4`
- `FryBatchA2.png`: `710cac395e9d00f7b26fed7f5e4d44839ad02481add6f018a353234e2bb5fa77`

## Approval

- **Approved:** 2026-11-18, by the author through the orchestrator: hatchery C2 and fry pail A2.
- **Author's words:** "Approve both".
- **In the game:** `HatcheryC2.png` copied unchanged to `Textures/Things/Spearfishing/Building/Hatchery.png` (Graphic_Single, drawSize 2x2, not rotatable), and `FryBatchA2.png` to `Textures/Things/Spearfishing/Item/FryBatch.png` (Graphic_Single, drawSize 1).
- **Hashes (SHA-256) of the approved version:**
  - `HatcheryC2.png` and `Hatchery.png`: `cfe057efa8fedb44d24023774c58825845c223e585bcebb915d25b1a2c776da4`
  - `FryBatchA2.png` and `FryBatch.png`: `710cac395e9d00f7b26fed7f5e4d44839ad02481add6f018a353234e2bb5fa77`
  - `HatcheryC2_master.png`: `929b4680263c4455e2562a619a800d2446886cc376a453b28eaa9df5d26cf17c`
  - `FryBatchA2_master512.png`: `62dc904f352d7e96d9ba0f97bbf4d9d50c33bba08f15f81c055c21bdc10c9baa`
  - `hatchery_art.py`: `89de1444b1a69f0e6f2b48a71bd462e3f7cd6f9aa93e7bad434bf8c338523c28`
