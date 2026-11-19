# Basic wetsuit: approval record

- **Pieces:**
  - The item sprite `Textures/Things/Spearfishing/Apparel/Wetsuit/Wetsuit.png`. It is 128x128, Graphic_Single, drawSize 1, with a 4 px outline at the 8x master's scale.
  - The worn views `Wetsuit_<BodyType>_<dir>.png` in the same folder, for Male, Female, Thin, Hulk and Fat, facing south, east and north. They are 128x128 body textures for the OnSkin layer, read through `wornGraphicPath`. Apparel defaults to adults, so there is no Child set.
  - Every texture is greyscale. The suit is stuffed (Leathery, 60), and RimWorld tints it by the leather's colour.
- **Approved:** 2026-11-15, by the author, relayed by the orchestrator.
- **Author's words:**
  - For the design: "seemed but the side view shouldnt have a seem". That chose candidate A (seamed), with no seam on the east (side) worn view. The south and north views and the icon keep the seam as drawn.
  - For the colour: "Leather-tinted (Recommended)".
- **Compared:** three candidates, A seamed, B belted and C panelled. Each was shown as an icon in plain, bear and heavy leather, and worn on Male facing south, east and north with a vanilla head and the approved glass mask. A vanilla T-shirt and the bare body were shown as references.
- **Source:** `wetsuit_art.py` in this folder draws everything procedurally with Pillow 12.3.
  - Each worn view fills the vanilla naked body's silhouette for its body type. Only the alpha is used, so the suit fits the body; no vanilla colour pixels go into it. No other reference, DLC or third-party art went into it.
  - Run `python -I wetsuit_art.py <Things/Pawn/Humanlike/Bodies dir of Ludeon's art source> <out_dir> Male Female Thin Hulk Fat`.
  - It writes every candidate, plus the approved game textures.
  - The candidate A files kept here are `Wetsuit_A_seamed.png` and its Male `_south`, `_east` and `_north` views.
  - Script SHA-256 `59b8016d84bcb3c2038c6c429cc29ae5e4720a6aaa003b331137999f872b438c`.
- **Export recipe:**
  - **Item:** `export(item("A", master=True))`, the fins' and glass mask's recipe. It crops the 8x master to its alpha bounds and scales it uniformly with Lanczos so the longer side is 100 px. The result is centred on a transparent 128x128 canvas.
  - **Worn views:** `worn("A", body, direction)` unchanged.
  - Some south and north views are byte-identical. Those bodies' silhouettes are the same front and back, and the seam is centred.
- **Exported textures (SHA-256):**
  - `Wetsuit.png` `7c08901d2123c4f829da0181c2bb857cd82ae48663b2ef0fc69516b0970760a7`
  - `Wetsuit_Male_south.png` `2d13ac98fa979ff0bc8f9d84b2f874d7319864106c859f862ade7784d8fffa2d`
  - `Wetsuit_Male_east.png` `e887c4f930c6e9d0778e2a4ac72696592ac9990d5d01895a7455513ef468b208`
  - `Wetsuit_Male_north.png` `2fa88c4def4ffb4db35b6e8f48a3033a2535889b378704d7d8e1f4bf5738c1fc`
  - `Wetsuit_Female_south.png` `da8ea4ea773d579872e3d8f53ad6723c23baffd6e8612fd9f989ef98c2194ca2`
  - `Wetsuit_Female_east.png` `85865f01a7ad9b2c002841229ba4df250a6913077bfc17f5ed4e8069941082b3`
  - `Wetsuit_Female_north.png` `da8ea4ea773d579872e3d8f53ad6723c23baffd6e8612fd9f989ef98c2194ca2`
  - `Wetsuit_Thin_south.png` `ebe4af550efe6b3a0a87e531e587008a03239fce4746ac789d06c49bc2adbe2b`
  - `Wetsuit_Thin_east.png` `d6a52bb0f759d3aeff6b79d5e5b7195a93db062b82e098bf7edfe04fc2859501`
  - `Wetsuit_Thin_north.png` `ebe4af550efe6b3a0a87e531e587008a03239fce4746ac789d06c49bc2adbe2b`
  - `Wetsuit_Hulk_south.png` `704b8c847f3df5c9c5c9d1976511e42a3d00f86f1813fd64474c64b5a29a255e`
  - `Wetsuit_Hulk_east.png` `b0c5749868c7ae303334f6c51b0b0a26bae7ee38796e4c63366ce87d11e2ad85`
  - `Wetsuit_Hulk_north.png` `704b8c847f3df5c9c5c9d1976511e42a3d00f86f1813fd64474c64b5a29a255e`
  - `Wetsuit_Fat_south.png` `25d3bf3c23b184a73dfacc636062d222eea5214aba9e7b865d981491fbdeebfc`
  - `Wetsuit_Fat_east.png` `98c2e622e8e9febfe558cb998d8c37bcce0bd3ad021ff1039e0e5a3131dde484`
  - `Wetsuit_Fat_north.png` `021a5344a1ac20c1592e368dd3f424f97d41369fd6f874ca192731602096dad8`

Approval is final: a change to these pixels, the framing or the colour is a new candidate that needs a new approval.
