# Changelog

<!-- Agent read route: read only the newest relevant release; locate older versions by searching `^## ` headings. -->

## 2026-11-18

### Added

- Added the artificial reef, a steel frame built on bare sea floor from the Misc tab for 40 steel, after the Spearfishing and Smithing research. A constructor swims out to build it. Over 15 days it crusts over in three visible stages, then the frame disappears and its cell becomes reef, with no steel back. It never spreads. It goes only on ocean floor that is not already reef or kelp.
- Added habitat restoration. The **Restore sea floor** order in the Orders tab marks bare sea floor and needs the Spearfishing research. A colonist on Spearfishing work, with no spear, swims to a marked cell beside reef or kelp and moves cuttings onto it using Plants, and the cell becomes the same kind of floor. Marked cells further out wait until restoration reaches them. Each restored cell then spreads to one marked bare cell beside it about every 15 days. Natural reef and artificial reef never spread.
- Added the hatchery, a powered 2x2 building in the Production tab for 100 steel and 2 components, using 120 W while it has feed and fry to raise, after the Spearfishing and Electricity research. Haulers fill it with hay, kibble or raw plant food, and it fills a pail of 30 fry every 3 days from 240 feed. A hauler releases the fry into the sea, lake or river chosen with **Choose water**, and they join its fish stock at once, never past capacity. A message reports each release and any fish lost to a full water. With Odyssey, a release raises Odyssey's fish population by the same share.
- Added two threat events, urchins and invasive predators, as small Misc storyteller events with a letter naming the water. Each needs fish stock management on and its own setting, **Urchin events** or **Invasive predator events**, both on by default and greyed out while management is off. Neither fires in the first 15 days, within 30 days of the last of its kind, or while one of its kind is active on the map, and each comes about once a year per map. Threats only slow regrowth and never take fish from the stock or lower capacity.
- Added urchin barrens. An urchin outbreak strikes only the sea, where reef or kelp shows, and grazes a connected patch of 10 to 20 reef and kelp cells. Barren cells look pale and drained, with small dark urchins, and they stop counting toward their water's reef share and lose reef's catch bonus. The barren grows by one reef or kelp cell beside it every 3 days.
- Added culling urchins as Spearfishing work. A diver with no order and no spear swims to a barren cell and works for about 7 seconds, using and training Melee. The job comes before trips and restoring, and pacifists can't do it. A culled cell shows bare sea floor and gets its reef or kelp back 5 days later. Culling the last barren cell ends the outbreak with a letter, and the culled cells keep their own 5 days. **Restore sea floor** refuses a culled cell, saying it is already growing back. Barren cells under a bridge or landfill can't be culled or spread, and get their reef or kelp back when the outbreak ends.
- Added invasive predators: lionfish at sea and snakeheads in lakes and rivers. An outbreak gives one body of fishing water a predator count, starting at about a tenth of its maximum of one predator per 24 fish of capacity (100 for a full sea) and nearing the maximum over about a season. The count cuts the water's regrowth by up to half, in proportion to the count, after the reef and kelp boost. Each fish a diver catches in that water is a predator with a chance of the count over its maximum, and each predator caught lowers the count by one and lands like any other catch. A letter says when the last one is culled. Odyssey's line fishing doesn't cull them.
- Added a line to the zone's inspect panel while its water has predators, such as "Invasive lionfish: 40, cutting regrowth by 20%", and a line about the cut in the regrowth tooltip.

### Changed

- Changed reef and kelp to speed up their water's regrowth while fish stock management is on. Regrowth is multiplied by 1 plus the share of the water's cells that are reef or kelp, so water that is all reef regrows twice as fast. The base rate is lower, so a sea with typical natural reef still regrows at most about 60 fish a day. Seas with less reef than usual regrow a little slower than before and seas with more regrow faster. Flat regrowth with fish stock management off is unchanged.
- Changed the regrowth tooltip in the zone's inspect panel to show the base regrowth and how much reef and kelp add.
- Changed the **Fish stock management** setting to also cover the artificial reef, habitat restoration and the hatchery. Turning it off hides the reef and hatchery from the Architect menu, cancels their blueprints and unfinished frames with the usual refund, clears Restore sea floor marks, pauses reef growth and restoration spreading, and leaves built hatcheries idle. Floor that has already become reef stays reef.
- Changed turning off **Fish stock management** to also end any urchin or predator outbreak at once, with no letter. Barren and culled cells get their reef or kelp back and the predator count drops to zero. Turning it back on brings no outbreak back. Turning off a threat's own setting does the same for that threat.
- Changed the Workshop page, README and mod description to describe fish recovery, the two threats and what turning fish stock management off removes.
- Changed kelp to sway in the swell: the forest bends along the current with a quick push and a slow drain, as a swell rolling through it, and deep kelp moves less than shallow.
- Changed the dive art in lakes and rivers to draw over Living Waters' water veil, so divers, their shadows and fish show there as they do at sea.
- Changed item and research descriptions to name the research each item needs in the same way, the research description to list what else it opens, and the Spearfishing work type to mention restoring sea floor and culling urchins. The **Dive visuals** setting's tooltip now says it also turns off the face-down look and the dive sounds.
- Renamed the mod to Wild Waters: Spearfishing, the first mod in the Wild Waters series. Its packageId changed from `kylemhb.spearfishing` to `kylemhb.wildwaters.spearfishing`.

## 2026-11-17

### Added

- Added industrial and spacer diving gear, unlocked by vanilla research with no new research projects. Each item also needs the Spearfishing research, and its description says what unlocks it.
  - Machining: the band speargun and the low-volume mask, made at the machining table.
  - Biofuel refining: plastic fins, the neoprene wetsuit and the foam buoy, made at a tailor bench, and the dry snorkel, which also needs Machining and is made at the machining table.
  - Advanced fabrication: the pneumatic speargun, long carbon fins and the rebreather, made at the fabrication bench.
  - Recon armor: the thermal wetsuit, made at the fabrication bench.
- Added the band and pneumatic spearguns, with dive power 1.0 and 1.15 against the steel-tipped pole spear's 0.85. Speargun dives use and train Shooting. In a fight a speargun fires one hard shot at 5 or 6 cells, reloads slowly and needs no ammo.
- Added plastic fins and long carbon fins, which raise swim speed by 40% and 60% against the wooden fins' 25%. Swimmers tire more slowly in each pair than in the pair below.
- Added the low-volume mask, which raises dive success by 35% against the glass mask's 20%.
- Added the dry snorkel and the rebreather, which make snorkeling more enjoyable and longer than the wooden snorkel and cut a spear diver's rest at the surface between dives by a quarter and by 40%. The rebreather takes the snorkel's place and is worn with a mask.
- Added the neoprene and thermal wetsuits, which let divers work water down to -5 °C and -20 °C, against the basic wetsuit's 5 °C.
- Added the foam buoy, which holds 10 fish on the stringer against the wooden buoy's 8, weighs less and keeps an exhausted diver afloat in the same way.
- Added shark encounters. At most once per trip, on a random dive over deep ocean, a shark may bite the diver, take the whole catch and leave, and the diver heads home. A diver holding a speargun may drive it off on a Shooting check and keep the catch. Sharks never come in shallow ocean, lakes or rivers, or while snorkeling, and the shark is a shadow drawn in the water, never an animal. A message reports each bite or drive-off.
- Added the **Shark chance per trip** setting, from 0 to 20% with a default of 1%. Setting it to 0 turns sharks off.
- Added the **Fish stock management** setting, on by default. With it on, fish regrow fastest when the water is about half full and slowly when it is nearly empty or nearly full, never below 0.25% of capacity a day, and the zone's inspect panel shows how many fish its water regrows a day, with a tooltip. With it off, the water regrows a flat 2.5% of its capacity a day and divers stop at a quarter. Switching it keeps every body of water's fish.
- Added a fish-down limit to each spearfishing zone while fish stock management is on. Divers stop when the water falls below it. It is half by default, and the zone's buttons move it from 10% to 90% in 10% steps. Zones on the same water keep their own limits, and the inspect panel shows the limit and says when the water is below it.

### Changed

- Changed the wooden fins and the basic wetsuit to raise Waves' own swimming stamina and insulation in cold water, so they combine with swim gear from other mods. Spearfishing now needs RimWorld: Waves 1.3.0 or later.
- Changed the fish stock to belong to each body of water. The sea, each deep lake and each deep river has one stock, shared by every spearfishing zone on it, so painting more zones adds no fish. Water holds one fish per cell, up to 2400, and a full coastal sea regrows at most about 60 fish a day. A catch lowers the whole body's stock instead of the water around the dive spot. Landfill, bridges and other terrain changes reshape the water without refilling it. Saves from before this change start every body of water full.
- Changed reef and kelp to make dives succeed more often instead of holding more fish. Dives over them succeed half again as often as over bare floor, and divers head for them when they can reach them. Deep water no longer holds more fish than shallow.
- Changed the catch rate to about half. A skilled diver with starting gear lands about 15 fish per 8 hours of trips, and about 45 with the best gear.
- Changed harder difficulties to lower the catch chance, as they lower Odyssey's fishing yield. The chance falls by a tenth on Blood and dust and by a fifth on Losing is fun.
- Changed Odyssey support to share the fish both ways. A catch by either spearfishing or line fishing lowers both populations by the same share, so line fishing the water empty stops divers too. A lake where Odyssey placed no fish stays fishable by divers.
- Changed the Workshop page, README and mod description to list every item with its tier, research and bench, to describe sharks and the shark setting, and to describe the shared fish stock, fish stock management and the fish-down limit.

### Fixed

- Fixed the Workshop page and README, which said the glass mask keeps divers down longer. With Waves' Rest drain a skilled diver's dive is cut short first, so masks are described by their catch bonus alone.

## 2026-11-16

### Added

- Added kelp forests beside the reef on new coastal maps. Kelp holds as many fish as reef. Coasts colder than 15°C on average get brown kelp, coasts from 15 to 22°C get olive kelp, and warmer coasts keep reef alone. Existing maps are unchanged.
- Added swim, dive and bubble sounds made from retuned RimWorld sounds: a quiet stroke while swimming at the surface, a splash going under and coming up, and soft bubbles in time with the dive bubbles. They play for pawns in view and follow the dive visuals setting.

### Changed

- Changed the dive shadow to the shape of a pawn seen from behind, about a pawn's size at the surface. Its edge is crisp over shallow water and softer over deep water.
- Changed the shoal fish edges to follow the water's depth, crisp over shallow water and softer over deep water. A fish crossing into deeper or shallower water now changes its size, fade and blur over half a second instead of at the cell edge.
- Changed shoal fish to swim on their own instead of turning with the shoal as one block. Each fish faces the way it swims and keeps to a believable speed, so a turning shoal bends. When a diver comes close, each fish darts away on its own line before the shoal regroups.

## 2026-11-15

First release, version 0.1.0, for RimWorld 1.6 and 1.7. Requires Harmony and RimWorld: Waves.

### Added

- Added the spearfishing zone, which goes on sea, deep lake and deep river water that Waves lets colonists swim in, with its fish stock and capacity in the inspect panel. The zone tool says why it refuses a cell: land, too shallow, frozen, toxic, marsh or under a cave roof.
- Added a fish stock that belongs to the water. Reef and deep water hold more fish, lakes and rivers hold fewer than the sea and have no reef, a catch lowers the stock around the dive spot, and fished-out water recovers over about five days.
- Added reef under the water, placed in coastal ocean when a new map is generated. Each map keeps reef in its own per-cell grid, and the sea floor stays ordinary ocean.
- Added the Spearfishing work type. Divers with a spear swim out and dive for 20 to 60 seconds at a time at normal game speed, longer as their skill grows. A tired diver cuts the dive short. Under the water they swim about the zone and come up where the dive ends. They keep their catch on a stringer and leave raw fish on the shore for haulers. They head home when the stringer is full, the zone runs low, or before Rest or the cold become dangerous, and a drafted diver keeps the catch. In a zone that reaches far out to sea, divers fish the part they can safely swim home from.
- Added the wooden pole spear, wooden fins and wooden buoy, which need no research, and the Spearfishing research, which unlocks the steel-tipped pole spear, the glass mask, the snorkel and the basic wetsuit.
- Added snorkeling as a recreation activity. Colonists swim out to swimmable sea, lake or river water near shore, float, freedive now and then, drifting under the water and coming up somewhere new, and swim home, with no gear, zone, spear or catch, so pacifists can snorkel too.
- Added the snorkel, which gives 35% more recreation while snorkeling and stretches a session from 1 hour to 1.6 hours.
- Added the Swimming recreation type for snorkeling and work trips. Work dives give a little of it, and recreation holds level while a work diver is in the water.
- Added dive visuals. A diver vanishes under the water during a dive and a catch shows a small burst. Shoals of fish shadows, shaped by species, swim around anyone in the water, with fewer fish where the water is fished out. A spearfisher sneaks up on a shoal, which scatters when they get close and regroups nearby, and snorkelers get circled. Their own shadow sinks and fades under the surface, stays larger and darker over shallow water near the shore, and turns to face the way they swim. A snorkeler vanishes the same way on a freedive. Snorkelers and divers resting at the surface are drawn face down, showing the back of the head with the mask strap and snorkel. A mod setting turns all of these off.
- Added removal-safe saves. The mod saves spearfishing zones outside RimWorld's zone list and saves a diver's current job as a vanilla wait job. A save then loads without the mod with its sea, stockpiles and other zones intact, and shows only one-time missing-def errors.
- Added optional support for Odyssey, whose fish species and fish population catches use, and for Dubs Bad Hygiene, where time in the sea on a trip or while snorkeling counts as a wash.
