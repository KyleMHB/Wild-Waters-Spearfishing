# Fins speed swimmers through Move Speed, not path cost

Swim speed raises a pawn's ordinary Move Speed while they are in swimmable sea, through a stat part, instead of scaling the deep-water path cost Waves sets. Path cost is resolved for every cell of every path search for every pawn on the map, so a per-pawn hook there would put Spearfishing in the hottest code in the game, and RimWorld 1.6 rebuilt pathfinding in ways that may make such a hook costly or impossible. A Move Speed stat part runs only when a pawn's speed is read and needs no Waves patch.

## Consequences

- Fins help less than a straight speed multiplier would: Move Speed shortens the walking part of each step, while Waves' fixed deep-water cost is added on top unchanged. Tuning should account for this.
- Pathfinding doesn't know about fins, so a diver plans routes as if they had none and may take a land detour that is no longer the fastest.
- Swim speed drops out of the Waves hook request.

## Considered Options

- Scale Waves' deep-water path cost per pawn where path cost is resolved: exact, and pathfinding sees fins, but it patches the hottest code path and depends on 1.6's pathfinding internals.
- Per-pawn path grids: exact, but memory and rebuild cost grow with every diver.
