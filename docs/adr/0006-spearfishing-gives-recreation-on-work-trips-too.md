# Spearfishing gives recreation on work trips too

Superseded in part by ADR 0007: the recreation activity is now snorkeling, not spearfishing. Recreation from work trips stands.

Spearfishing is both a recreation activity, picked in a pawn's recreation time like any vanilla one, and a job that adds a little recreation on every dive. Vanilla gives recreation only during recreation time, so this is a deliberate exception: diving should feel like something colonists enjoy, not only a chore.

## Consequences

- Work trips use the same recreation type as the activity, so tolerance applies and a pawn who dives every day gets less out of it over time.
- The amount per work dive is a balance risk: too high and divers stop needing recreation time, which in a big modpack reads as a free mood boost. Tune it low and revisit after players have tried it. The first release gives 0.004 per dive before tolerance.
- Recreation also doesn't fall while a work diver is in the water. Without that, recreation decay outran the per-dive gain on long trips far from shore, and a trip could end slightly down. The user chose this on 2026-11-15. It adds no recreation and no tolerance, and recreation falls as usual on land. Snorkeling (ADR 0007) gains at vanilla's rate or better and doesn't need it.
- Both the activity and the job share one dive loop, so gear, safety exits and catches behave the same either way.

## Considered Options

- Recreation activity only: matches vanilla exactly, but a work trip feels like any other chore.
- Recreation from work trips only: simplest, but breaks the vanilla rule with nothing in recreation time to show for it.
- A small mood buff after a good dive instead of recreation on work trips: doesn't replace the need, but isn't what the user wants.
