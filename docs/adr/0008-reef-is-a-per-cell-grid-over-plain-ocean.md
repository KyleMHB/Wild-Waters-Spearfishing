# Reef is a per-cell grid over plain ocean, not a terrain

Amends ADR 0004: a cell's capacity now comes from its terrain (depth) and the map's reef grid, not from a reef terrain.

Amended by ADR 0013: the depletion grid is gone and reef no longer changes capacity; the reef grid stays, for where fish are densest.

Reef is stored as one more per-cell grid on each map, beside the depletion grid, and the sea floor under it stays vanilla ocean terrain. The reef overlay is drawn from the grid, map generation writes the grid rather than changing terrain, and capacity reads it.

We chose this so that a player can remove the mod from a save. As terrain, every reef cell would load as Soil without the mod, leaving islands of land in the sea. As a grid, removing the mod drops one unknown map component and the sea is untouched. It also removes a Waves patch: reef cells are vanilla ocean, so Waves already treats them as sea, swimmable and full of sea life without the `ShoreField.Classify` redirect.

## Consequences

- Saves gain one byte per map cell for reef, saved like the depletion grid. Bare sea is all zeros and compresses to very little.
- Reef can't be placed with the terrain tools. Dev tools and a later artificial reef write to the grid instead.
- Anything that reads reef asks the grid, never the terrain def.
- Kelp (ticket 38, 2026-11-16) shares this grid: the byte is 2 for brown kelp and 3 for olive kelp, so kelp adds no saved field and older saves, which hold only 0 and 1, load unchanged.

## Considered Options

- Keep reef as terrain and add a "prepare for removal" button that turns reef back into ocean: small, but removal is only safe if the player remembers to press it first.
- Keep reef as terrain and document that removal isn't supported: no work, but trying the mod becomes risky.
