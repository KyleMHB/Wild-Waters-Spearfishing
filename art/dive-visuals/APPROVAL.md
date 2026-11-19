# Dive visuals: approval record

- **Pieces:** the fish shadow, `Textures/Spearfishing/Dive/FishShadow.png`, and the spear burst, `Textures/Spearfishing/Dive/SpearBurst.png`. Both are 64x64 RGBA white shapes with no outline, which `Source/Visuals/DiveVisuals.cs` tints and fades. The shadow faces east and is drawn 0.75 cells wide in a dark blue-green at 45% opacity, at Waves' sea-life render queue. The burst is pale blue-white and grows from 0.5 to 1.6 cells while it fades out over 0.6 s.
- **Approved:** 2026-11-15, by the author through the orchestrator.
- **Author's words:**
  - Fish shadow: "B plump, soft edge".
  - Burst: "A ring".
  - Name label: "Keep the label (Recommended)". The diver's body hides while under the water and the name label stays.
  - Size, opacity and burst timing were left unchanged.
- **Compared:** one contact sheet showing:
  - shadows A (plump, hard edge), B (plump, soft edge) and C (slim, soft edge);
  - bursts A (ring), B (droplets) and C (four-point splash star);
  - in-game frames from harness run `20261115-190840-spearfishing-visuals-s1`, taken with the placeholder art.
- **Source:**
  - `ShadowB.png` and `BurstA.png` in this folder, drawn by `dive_art.py`.
  - `python -I dive_art.py <out_dir>` regenerates them byte for byte with Pillow 12.3. Frame paths after `<out_dir>` are optional and only feed the contact sheet.
  - The art is procedural, with no reference images, DLC, Waves or third-party art.
  - Script SHA-256 `ad72b3cbde729bc2e3350931ba04cfe8d9efa30cbc5ee541f0c4f80b815a9c03`.
- **Export recipe:** each master is copied unchanged and renamed, `ShadowB.png` to `FishShadow.png` and `BurstA.png` to `SpearBurst.png`. The masters are already the game textures' size.
- **Exported textures:**

| File | SHA-256 |
| --- | --- |
| `Textures/Spearfishing/Dive/FishShadow.png` | `0bbfa4318e408899b1ab97735e652c3b83fcda4c257af06caacace1917145e33` |
| `Textures/Spearfishing/Dive/SpearBurst.png` | `62442b02a63d714918669bd3f3f39fca8ebbe0ceb5586454d8ba0b56bb206319` |

Approval is final. A change to these pixels, the tint or the timing is a new candidate and needs a new approval. In-game confirmation is the ticket 14 review.
