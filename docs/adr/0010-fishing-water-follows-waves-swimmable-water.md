# Fishing water follows Waves' swimmable water, so deep lakes and rivers count

Spearfishing zones, dive trips, snorkeling and the fins' swim speed work on any cell that is fishing water and that Waves' swim-cell test lets colonists swim in. Fishing water is ocean (shallow and deep), deep lake (`WaterDeep`) and deep river (`WaterMovingChestDeep`), compared as terrain defs, not by name. The Waves bridge answers one question for every caller, `IsSwimmableFishingWater`, and gives the zone tool a reason when it says no.

We chose this so that our water matches what players already see in Waves: if a colonist can swim there, they can fish there. A list of our own would drift from Waves and refuse water that Waves treats as swimmable, or accept water Waves won't let anyone enter. The terrain list is still needed on top of the swim test, because the fish stock, reef and catch need to know what kind of water a cell is.

Some water is left out even where it looks deep enough:

- Shallow freshwater (`WaterShallow`, `WaterMovingShallow`) and marsh: wading water, too shallow to swim or dive in.
- Frozen water: a temporary ice terrain over lake or sea water. A colonist can't dive through ice, so the zone tool says "frozen" instead of "land".
- Odyssey's toxic terrain (any water def with a toxic buildup factor): no one should dive in it. Biotech pollution is not refused, since Odyssey's toxfish come from polluted water.
- Water under a natural (cave) roof, which also covers modded cave water: no light to spear by, and no open surface to rest at.

## Consequences

- Rivers behave like lakes. Spearfishing adds no current; any push or path cost comes from vanilla and Waves.
- Freshwater holds fewer fish: bare-floor capacity only (1 for `WaterMovingChestDeep`, 1.5 for `WaterDeep`). There is no lake reef. (Amended by ADR 0013: each lake and river is its own body of fishing water holding one fish per cell, the same as the sea, so a small lake holds fewer fish by its size, not its terrain.) Map generation, the reef overlay and the reef grid stay sea-only, and a reef byte under freshwater is ignored.
- With Odyssey, a lake or river catch is the water body's freshwater species. Without it, the catch is the generic raw fish, as in the sea.
- The cave-roof rule applies to the sea too, so a sea cave is no longer zoneable.

## Considered Options

- Keep sea only: simplest, but colonies inland, where Waves lets pawns swim in lakes and rivers, would have no use for the mod.
- Accept any water Waves' swim test passes, with no terrain list: picks up modded look-alike terrain by accident, and the stock can't tell lake from sea.
