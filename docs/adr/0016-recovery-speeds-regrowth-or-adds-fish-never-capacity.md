# Recovery speeds regrowth or adds fish, never capacity

Decided with the author on 2026-11-18.

The recovery methods of fish stock management (ADR 0015) work through two levers only. Reef and kelp, natural or made by the player (the artificial reef, habitat restoration), speed the regrowth of their body of fishing water a little per cell, up to a cap for each body. The hatchery adds fish straight to the stock when its fry are released, never past capacity. Nothing raises capacity, so the cap of ADR 0013 stays the one number that limits food and the fish-balance figures for a full sea still bound what any colony can take.

Natural reef and kelp speed regrowth too, not only the reef the player builds; otherwise a sunk artificial reef would beat a real one. This changes ADR 0013's statement that reef decides only where dives succeed: reef and kelp now also decide how fast their water recovers, and every existing coastal map regrows faster than the fish-balance numbers (about 60 fish a day for a full sea) assumed. Those numbers are retuned in the recovery spec.

Updated 2026-11-18 after fish recovery ticket 01: the retune is done (see ADR 0013's revision). The per-body cap is the multiplier (1 + reef share), at most double for water that is all reef. The base logistic rate fell from 0.1 to about 0.078, so a sea at the median natural share of 28% still peaks at about 60 fish a day. Not every map regrows faster than before: a sea with less reef and kelp than the median now regrows a little slower (about 53 a day on the measured temperate map) and one with more regrows faster.

## Considered Options

- Recovery raises capacity: simplest to explain, but painting reef would raise the food cap, which ADR 0013 removed for painted zones.
- Only the player's reef speeds regrowth: keeps today's numbers, but a built reef would outperform natural reef.
- The hatchery speeds regrowth instead of adding fish: no direct feed-to-fish conversion, but releasing fry would have no visible result.
