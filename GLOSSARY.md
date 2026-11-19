# Wild Waters: Spearfishing

An add-on for RimWorld: Waves that lets colonists dive and spear fish in the sea and in deep lakes and rivers, with craftable gear that improves their swimming.

## Language

**Fish stock**:
The fish population of one body of fishing water (the sea, a lake or a river), shared by every spearfishing zone on it, from which every catch is drawn. With Odyssey, it and Odyssey's fish population are fished down by the same share.
_Avoid_: Fish count, fish pool, spawns

**Capacity**:
The most fish a body of fishing water holds when untouched, in proportion to its size up to the same cap for any body of water, so a small lake holds fewer fish than the sea. Painting more zones on it never raises it.
_Avoid_: Max fish, richness

**Depletion**:
How far the fish stock of a body of fishing water has been fished below its capacity; it belongs to the water, not to any zone, and a catch anywhere on that water adds to it.
_Avoid_: Overfishing level, damage

**Regrowth**:
The fish a body of fishing water gains back each day until it is full: fastest at about half full, slow when nearly empty or nearly full, and faster the more of the water is reef or kelp (up to double for water that is all reef), and slower while threat events stand (urchin barren cells don't count as reef or kelp, and invasive predators cut it by up to half); the same number each day, whatever the floor, when fish stock management is turned off in the settings.
_Avoid_: Respawn, refill

**Fish-down limit**:
The share of its capacity a spearfishing zone leaves in the water: its divers stop when the water's fish stock falls below it. Half by default, where regrowth is fastest. Each zone has its own, even on shared water. Part of fish stock management, on by default; with it turned off, divers stop at a fixed point.
_Avoid_: Quota, stop threshold

**Shark encounter**:
A rare event where a shark bites a diver in deep ocean and takes their catch; a diver with a speargun may drive it off first and keep the catch. Rolled once per spearfishing trip, on a random dive over deep ocean (once the stringer holds a number of fish picked for the trip), at the shark chance set in the mod settings. The shark is a shadow drawn by the dive visuals, never an animal that can be hunted. Never in shallow ocean, lakes or rivers, or while snorkeling.
_Avoid_: Shark attack, shark raid

**Catch**:
The fish a diver takes from the fish stock and brings ashore.
_Avoid_: Haul, kill, yield

**Fishing water**:
Water Waves lets colonists swim in that is sea (shallow or deep ocean), deep lake (`WaterDeep`) or deep river (`WaterMovingChestDeep`). Shallow freshwater, marsh, frozen, toxic and cave water are not fishing water (ADR 0010).
_Avoid_: Swimmable sea (sea is only the ocean part)

**Body of fishing water**:
Fishing water joined edge to edge: the sea, a lake or a river. Each has one fish stock and one capacity, shared by every spearfishing zone on it; water joined only at a corner is two bodies.
_Avoid_: Water body (Odyssey's, which need not match ours), pool

**Spearfishing zone**:
A zone the player paints on fishing water; divers fish only inside one. It holds no fish of its own: it shows the fish stock of the body of fishing water under most of its cells, and each catch comes from the body the diver is in.
_Avoid_: Fishing area, fishing spot

**Reef**:
Sea floor of rock or coral where fish are densest, so dives over it succeed more often and divers head for it when they can reach it; it does not add to the fish stock, but with fish stock management on it speeds its water's regrowth by its share of the water's cells. Placed in the coastal ocean of every new map, whatever its temperature; the water above it is ordinary sea.
_Avoid_: Coral, rocks

**Kelp**:
Sea floor of seaweed forest beside the reef, where fish are as dense as over reef and which speeds regrowth like reef. Placed in the coastal ocean of new maps whose average yearly temperature is under 22°C, on floor that is not reef: brown kelp under 15°C, olive kelp from 15 to 22°C. The colour is its only difference.
_Avoid_: Seaweed, weed bed

**Artificial reef**:
A steel frame a constructor builds on bare sea floor (Construction work, a fixed cost in steel) that turns its cell to reef after 15 days and then disappears. Like natural reef, that cell then speeds its water's regrowth; it never spreads. It exists only with fish stock management on (ADR 0015).
_Avoid_: Fish attractor, reef block

**Habitat restoration**:
Spearfishing work, using Plants, of moving cuttings from existing reef or kelp to bare sea floor next to it, on sea floor the player has marked with the "Restore sea floor" order; the cell takes its neighbour's kind. Restored floor slowly spreads on its own within the marked area, while natural reef and the artificial reef never spread. It costs labour, not materials, and exists only with fish stock management on (ADR 0015).
_Avoid_: Replanting, reef farming

**Hatchery**:
A powered building on land that raises fry from animal feed (hay, kibble, raw plant food); a hauler carries each full batch to the body of fishing water chosen on the hatchery and releases it there, adding to its fish stock but never past capacity. It exists only with fish stock management on (ADR 0015).
_Avoid_: Fish farm, aquaculture, sea cage

**Fry**:
Young fish from a hatchery, carried in batches and released into a body of fishing water, where they count as fish stock.
_Avoid_: Fingerlings, spawn

**Threat event**:
A small storyteller event that slows a body of fishing water's regrowth until divers cull it: an urchin barren or invasive predators. Each needs fish stock management and its own switch on (ADR 0015), never fires in the first 15 days or while one of its kind is active on the map, and never takes fish from the stock or lowers capacity (ADR 0017). Turning management or its switch off ends it at once, and turning it back on brings nothing back.
_Avoid_: Disaster, raid

**Invasive predators**:
Non-native predatory fish (lionfish at sea, snakeheads in lakes and rivers) that arrive in one body of fishing water by a threat event; one body per map at a time. They are a count kept with that water, not animals on the map. The count starts at about a tenth of its maximum (one per 24 fish of capacity) and grows toward it over about a season, cutting the water's regrowth, after the reef boost, by up to half in proportion to count over maximum (ADR 0017). Ordinary spearfishing culls them: each fish a diver catches there is a predator with chance count over maximum, lowering the count by one and landing like any catch. Odyssey's line fishing never culls them. The zone's inspect panel shows the count and the cut.
_Avoid_: Pest fish, invaders

**Urchin barren**:
Reef or kelp cells in the sea that urchins have grazed bare, after an urchin threat event struck a patch of 10 to 20 of them. Barren cells keep their reef or kelp mark underneath but count as bare floor: they leave their water's reef share and lose reef's catch bonus. The barren as a whole grows by one neighbouring reef or kelp cell every 3 days until divers cull it (Spearfishing work, using Melee, with no order needed). A culled cell shows bare floor and gets its reef or kelp back 5 days later. Culling the last barren cell that shows ends the outbreak with a letter (a switch turned off ends it with none), and the culled cells keep their own 5 days; barren cells under a bridge or landfill can't be culled and get their reef or kelp back when the outbreak ends.
_Avoid_: Urchin infestation, dead reef

**Diver**:
A colonist on a spearfishing trip, which is always work.
_Avoid_: Swimmer, fisher

**Trip**:
A diver's outing from shore to a spearfishing zone, a run of dives, and the swim home with the catch. Trips are always Spearfishing work; relaxing in the sea is snorkeling.
_Avoid_: Run, session

**Dive**:
One breath-hold descent by a diver, 20 to 60 seconds at normal game speed, longer with skill, and cut short when the diver is tired. The diver swims about under the water, attempts a fish at intervals and surfaces where the dive ends.
_Avoid_: Attempt, shot (an attempt is a catch roll within a dive)

**Snorkeling**:
Recreation in fishing water, sea, lake or river: a colonist floats face down near shore and now and then freedives, with no spear and no catch.
_Avoid_: Swimming for fun, fun spearfishing, recreational diving

**Snorkeler**:
A colonist who is snorkeling; unlike a diver, they fish for nothing.
_Avoid_: Diver, swimmer

**Freedive**:
A breath-hold descent a snorkeler makes to look around, half as long as a dive at the same skill, drifting under the water and surfacing where it ends, with no attempt at a fish.
_Avoid_: Dive (which always includes attempts at a fish)

**Snorkel**:
A breathing tube, worn alone or with a mask, that makes snorkeling more enjoyable and lets a snorkeler stay out longer.
_Avoid_: Breathing tube, scuba

**Rebreather**:
A small spacer-tier breathing unit held in the mouth, in the snorkel's place: worn with a mask, never with a snorkel. Like a better dry snorkel, it shortens the rest at the surface between spear dives and improves snorkeling; it does not lengthen dives.
_Avoid_: Full-face mask, diving helmet, scuba, air tank

**Stringer**:
What a diver keeps fish on during a trip; when it is full, the diver heads ashore.
_Avoid_: Bag, inventory

**Buoy**:
A float a diver wears at the waist as apparel and tows; it holds the stringer, adds to its capacity and keeps an exhausted diver afloat instead of drowning.
_Avoid_: Float, marker

**Spear**:
Any weapon a diver fishes with; it is a real weapon and can be used in a fight. The first release has the wooden pole spear and the medieval steel-tipped pole spear, both using Melee. The industrial tier adds the band speargun and the spacer tier the pneumatic speargun, ranged weapons that use Shooting.
_Avoid_: Fishing tool

**Swimming**:
The recreation type of snorkeling and of work trips, added by the mod because Waves defines none. Snorkeling gives it at vanilla's rate or better; work trips give a little on every dive. Ordinary swimming gives none.
_Avoid_: Diving recreation, fun

**Sea life**:
The fish and other creatures that Waves draws under the water; they are scenery, never the thing a diver catches.
_Avoid_: Fish (when meaning the drawn shadows), targets

**Shoal**:
A group of fish shadows that our dive visuals draw around a pawn in the water: a leader and its followers. Up to three per swimmer, fewer fish where the stock is low. Visual only: a catch comes from the fish stock, never from a shoal.
_Avoid_: School, fish stock (the gameplay count)
