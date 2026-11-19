# Wild Waters: Spearfishing

A RimWorld add-on for [RimWorld: Waves](https://steamcommunity.com/sharedfiles/filedetails/?id=3831078430) that turns open water into a food source. You paint a spearfishing zone on the sea, a deep lake or a deep river, and divers swim out with a spear, make breath-hold dives and bring raw fish ashore for your stockpiles. In their recreation time, colonists go snorkeling near shore.

For RimWorld 1.6 and 1.7.

## Features

- **Spearfishing zones.** A zone goes on sea, deep lake and deep river water that Waves lets colonists swim in. The zone tool refuses land, shallow water, marsh, frozen and toxic water, and says why. Its inspect panel shows its water's fish stock against its capacity. With fish stock management on, it also shows how many fish the water regrows a day, with a tooltip that shows how much of that comes from reef and kelp and how much invasive predators cut, and the zone's fish-down limit. While predators are in the water, it also shows how many there are.
- **Fish stock.** Each body of fishing water has one fish stock: the sea, each deep lake and each deep river. Every spearfishing zone on it shares that stock, and painting more zones adds no fish. Water holds one fish per cell, up to 2400, so a small lake holds fewer fish than the sea. A catch anywhere lowers the whole body's stock. An ordinary sea regrows at most about 60 fish a day, and more reef and kelp make it regrow faster. Deleting and repainting a zone gives no free refill, and landfill, bridges and other terrain changes reshape the water without refilling it.
- **Fish stock management.** This mod setting is on by default. Fish regrow fastest when the water is about half full and slowly when it is nearly empty or nearly full, and fished-out water still recovers, slowly. Each zone has a fish-down limit, half by default, and its divers stop when the water falls below it. Two zones on the same water keep their own limits. With the setting off, the water regrows 2.5% of its capacity each day, as Odyssey's does, and divers stop at a quarter.
- **Reef and kelp.** New coastal maps get patches of reef, visible under Waves' water. Coasts colder than 15°C on average also get brown kelp forests, coasts from 15 to 22°C get olive kelp, and warmer coasts have reef alone. Fish gather over reef and kelp, so dives there succeed half again as often as over bare floor, and divers head for them when they can reach them. Reef and kelp add no fish to the stock, but with fish stock management on they speed up their water's regrowth. The more of the water is reef or kelp, the faster it regrows, up to twice as fast for water that is all reef. The sea floor under them stays plain ocean, and lakes and rivers have neither. Existing maps have no natural reef or kelp, and every dive there has the bare-floor chance until you add some.
- **Fish recovery.** With fish stock management on, you can help fished-out water recover. Sink an artificial reef, have divers restore bare sea floor next to reef or kelp, or raise fry in a hatchery and release them into any sea, lake or river. The [fish recovery section](#fish-recovery) has the details.
- **Threats.** With fish stock management on, urchins sometimes graze reef and kelp in the sea bare, and invasive predators sometimes arrive in a sea, lake or river. Both slow the water's regrowth, and your divers clear them. Each has its own switch. The [threats section](#threats) has the details.
- **Diving work.** Spearfishing is its own work type. A colonist goes on spearfishing trips only with a spear or speargun equipped. A diver tries for a fish every few seconds under the water. The chance comes from the diver's skill, the weapon, the mask, the sea floor and how fished down the water is, and harder difficulties lower it, as they lower Odyssey's fishing yield. Spear dives use and train Melee, and speargun dives use and train Shooting. A diver heads home when the stringer is full, the water falls below the zone's fish-down limit, or before Rest or the cold become dangerous. With fish stock management off, divers stop at a fixed quarter instead. A drafted or interrupted diver keeps the catch.
- **Gear in four tiers.** Each item comes from the era of its technology, and vanilla research unlocks it. The [gear table](#gear) lists every item.
- **Sharks.** Deep ocean holds a rare shark that bites a diver and takes the catch. A speargun can drive it off. A setting tunes the chance or turns sharks off.
- **Snorkeling.** In their recreation time, colonists swim out to any swimmable sea, lake or river close to shore, float face down and now and then freedive. It needs no gear, zone or research, catches nothing and leaves the fish stock alone, so pacifists can snorkel too. Snorkelers head home when recreation is full, recreation time ends or the session runs out, and they follow the same rest and cold safety rules as divers.
- **Recreation from work.** Each dive on a work trip gives a little Swimming recreation, and recreation doesn't fall while a work diver is in the water.
- **Dive visuals.** A diver disappears under the water during a dive, a few fish shadows circle them, and a catch shows a speared shadow and a small burst. A snorkeler disappears the same way on a freedive. Snorkelers floating at the surface and divers resting between dives are drawn face down, showing the back of the head with the mask strap and snorkel. A shark shows as a shadow that passes, strikes and leaves. The mod draws nothing while nobody is diving or snorkeling.

## Gear

Every item past the Neolithic tier also needs the Spearfishing research (medieval, after Smithing). "Smithy" means a fueled or electric smithy, and "tailor bench" a hand or electric tailor bench.

| Item | Tier | Research | Bench |
| --- | --- | --- | --- |
| Pole spear | Neolithic | None | Crafting spot or smithy |
| Wooden fins | Neolithic | None | Crafting spot or tailor bench |
| Wooden buoy | Neolithic | None | Crafting spot or tailor bench |
| Steel-tipped pole spear | Medieval | Spearfishing | Smithy |
| Glass mask | Medieval | Spearfishing | Smithy |
| Snorkel | Medieval | Spearfishing | Crafting spot or tailor bench |
| Basic wetsuit | Medieval | Spearfishing | Tailor bench |
| Band speargun | Industrial | Spearfishing, Machining | Machining table |
| Low-volume mask | Industrial | Spearfishing, Machining | Machining table |
| Dry snorkel | Industrial | Spearfishing, Biofuel refining, Machining | Machining table |
| Plastic fins | Industrial | Spearfishing, Biofuel refining | Tailor bench |
| Neoprene wetsuit | Industrial | Spearfishing, Biofuel refining | Tailor bench |
| Foam buoy | Industrial | Spearfishing, Biofuel refining | Tailor bench |
| Pneumatic speargun | Spacer | Spearfishing, Advanced fabrication | Fabrication bench |
| Long carbon fins | Spacer | Spearfishing, Advanced fabrication | Fabrication bench |
| Rebreather | Spacer | Spearfishing, Advanced fabrication | Fabrication bench |
| Thermal wetsuit | Spacer | Spearfishing, Recon armor | Fabrication bench |

- **Spears and spearguns.** Dive power is 60% for the pole spear, 85% for the steel-tipped pole spear, 100% for the band speargun and 115% for the pneumatic speargun, and higher dive power lands more fish. All four are real weapons. A speargun fires one hard shot, at 5 cells for the band speargun and 6 for the pneumatic, then reloads slowly. It needs no ammo.
- **Fins.** Wooden fins raise swim speed by 25%, plastic fins by 40% and long carbon fins by 60%, and each pair makes the swimmer tire more slowly than the one before.
- **Masks.** The glass mask raises dive success by 20% and the low-volume mask by 35%, so divers land more fish. Both go with headgear.
- **Snorkels.** The snorkel, dry snorkel and rebreather give 35%, 50% and 60% more recreation while snorkeling, and stretch a session from 1 hour to 1.6, 1.8 and 2 hours. The dry snorkel also cuts a spear diver's rest at the surface between dives by a quarter, and the rebreather by 40%, so they make more dives per trip. Each is worn with a mask, and the rebreather takes the snorkel's place.
- **Wetsuits.** Without one, divers start to chill in water below 15 °C. The basic wetsuit lowers that to 5 °C, the neoprene wetsuit to -5 °C and the thermal wetsuit to -20 °C. Ordinary clothing still gives no warmth in the water.
- **Buoys.** A buoy is worn at the waist. The stringer holds 4 fish, 8 with the wooden buoy and 10 with the lighter foam buoy. An exhausted diver with either buoy floats instead of drowning and swims slowly home.

## Fish recovery

All three need fish stock management on. None of them raises how many fish the water can hold.

- **Artificial reef.** A steel frame you build on bare sea floor, from the Misc tab of the Architect menu. It costs 40 steel and needs the Spearfishing and Smithing research. Any constructor swims out to build it. Over 15 days it crusts over in visible stages, then the frame disappears and its cell becomes reef. No steel comes back. It goes only on sea floor that is not already reef or kelp, never on land, lakes or rivers, and the reef it leaves never spreads.
- **Habitat restoration.** Use **Restore sea floor** in the Orders tab to mark bare sea floor. It needs the Spearfishing research and no materials. A colonist on Spearfishing work swims out to a marked cell beside reef or kelp, moves cuttings onto it using Plants, and the cell becomes the same kind of floor. Marked cells further out wait until restoration reaches them. After that, each restored cell spreads to one marked bare cell beside it about every 15 days, and never outside the marks. Natural reef and artificial reef never spread. Restoring needs no spear, but Spearfishing work is violent, so pacifists can't do it.
- **Hatchery.** A powered 2x2 building on land, from the Production tab. It costs 100 steel and 2 components, uses 120 W while it has feed and fry to raise (none while idle), and needs the Spearfishing and Electricity research and Construction 4. Haulers fill it with hay, kibble or raw plant food. While powered and fed, it fills a pail of 30 fry every 3 days from 240 feed. Use **Choose water** to pick the sea, lake or river the fry go to. By default it is the nearest fishing water. A hauler carries the pail to that water's edge and releases the fry, and the fish join the water's stock at once. Fry that would fill the water past what it can hold are lost, and a message says how many were released. The fish carry about half the nutrition of the feed, so a hatchery turns feed nobody eats into fish.

On an existing map with no natural reef or kelp, an artificial reef gives restoration a place to start.

## Threats

Both threats need fish stock management on, and each has its own switch in the mod settings. Each is a small storyteller event with a letter that names the water. Neither comes in the first 15 days or within 30 days of the last one of its kind, nor while one of its kind is still on the map, and each comes about once a year per map. Threats only slow regrowth. They never take fish from the stock or lower how many fish the water can hold.

- **Urchins.** They strike only the sea, and only where reef or kelp shows, so an existing map with none gets no urchins until an artificial reef or restored floor gives it some. Urchins graze a connected patch of 10 to 20 reef and kelp cells, which turns pale and drained, with small dark urchins over it. These barren cells no longer speed their water's regrowth or give dives reef's better chance. Every 3 days the barren grows by one reef or kelp cell beside it.
- **Culling urchins.** Colonists on Spearfishing work cull barren cells on their own, with no order and no spear. A diver swims to a barren cell and works there for about 7 seconds, using and training Melee. Culling comes before trips and restoring, and pacifists can't do it. A culled cell shows bare sea floor and gets its reef or kelp back 5 days later. The outbreak ends when the last barren cell is culled, with a letter, and cells already culled still take their 5 days. Restore sea floor refuses a culled cell, since it is already growing back. Barren cells under a bridge or landfill can't be culled or spread, and get their reef or kelp back when the outbreak ends.
- **Invasive predators.** Lionfish at sea, snakeheads in lakes and rivers. They arrive in one body of fishing water as a count kept with that water, never as animals on the map, and only one body on a map has them at a time. The water can hold one predator per 24 fish of capacity, so 100 in a full sea. The count starts at about a tenth of that and nears it over about a season. Predators cut the water's regrowth by up to half, in proportion to the count, so 40 of 100 cut it by 20%. The zone's inspect panel shows a line such as "Invasive lionfish: 40, cutting regrowth by 20%".
- **Culling predators.** Ordinary spearfishing in that water culls them. Each fish a diver catches there has a chance of being a predator equal to the count's share of its maximum, and each predator caught lowers the count by one. It still lands like any other catch. Steady fishing at the fish-down limit clears them in one to two weeks, and light fishing only holds the count down. A letter says when the last one is culled.

Turning off fish stock management or a threat's switch ends that threat at once, with no letter. Barren and culled cells get their reef or kelp back, and the predator count drops to zero. Turning it back on brings nothing back.

## Sharks

- At most once per spearfishing trip, on a random dive over deep ocean, a shark may come. The default chance is 1% per trip.
- The shark bites once, injuring the diver, takes the whole catch and leaves. The diver heads home under the trip's usual safety rules.
- A diver holding a speargun may drive the shark off first and keep the catch. Better Shooting gives better odds.
- Sharks never come in shallow ocean, lakes or rivers, or while snorkeling. A message tells you when one bites or is driven off.
- The shark is a shadow in the water, never an animal you can hunt or butcher.
- To turn sharks off, set **Shark chance per trip** to 0 in the mod settings.

## Requirements

- [Harmony](https://steamcommunity.com/sharedfiles/filedetails/?id=2009463077)
- [RimWorld: Waves](https://steamcommunity.com/sharedfiles/filedetails/?id=3831078430) 1.3.0 or later, which provides the swimming. Spearfishing loads after it.

Optional, all supported:

- **Odyssey.** Catches are Odyssey's own fish species for that water. Spearfishing and line fishing share the fish both ways. A catch by either lowers both by the same share, so line fishing the water empty stops divers too. Faster regrowth from reef and kelp and fry from a hatchery raise Odyssey's fish as well, and urchin barrens and invasive predators slow its regrowth the same way. Odyssey's line fishing never culls predators; only spearfishing does. A small lake where Odyssey placed no fish is still fishable by divers. Without Odyssey, every catch is one generic raw fish.
- **Living Waters.** Divers, their shadows and shoals draw under Living Waters' moving lake and river water as they do under Waves' sea, and its own lake fish swim alongside the shoals.
- **Dubs Bad Hygiene** (full or Lite). Time in the water on a trip or while snorkeling raises hygiene at about the rate of washing in open water.

## Installation

Subscribe on the Steam Workshop, or copy the mod folder into `RimWorld/Mods`. Enable Harmony, RimWorld: Waves and Spearfishing, with Spearfishing after Waves.

## Usage

1. Open the Zone menu and choose the spearfishing zone. Paint it on deep water a little way out from the shore, over reef or kelp where you can.
2. Give a colonist a spear or speargun and enable Spearfishing in the Work tab.
3. Make room for raw fish in a stockpile. Divers leave the catch on the shore for haulers.
4. With fish stock management on, select the zone and use **Lower fish-down limit** or **Raise fish-down limit** to change where its divers stop, from 10% to 90% in 10% steps. Lower it in a famine, knowing that water fished low regrows slowly.

Snorkeling needs no setup. Colonists near swimmable water go on their own. Turning off swimming in Waves' settings stops both spearfishing work and snorkeling.

## Configuration

Mod settings have five options:

- **Dive visuals.** Turn it off to keep divers and snorkelers in view, draw floating pawns as Waves draws them, and draw no shadows, bursts or dive sounds. Catches and sharks are the same either way.
- **Fish stock management.** On by default. It turns on regrowth that is fastest at half full and faster over reef and kelp, the regrowth line in the zone's inspect panel, each zone's fish-down limit, the artificial reef, habitat restoration and the hatchery, and the two threats. Turn it off for flat regrowth and a fixed stop at a quarter. Switching it keeps every body of water's fish.

  Turning it off also removes fish recovery. The artificial reef and the hatchery leave the Architect menu, and their blueprints and unfinished frames are cancelled with the usual refund. Restore sea floor marks are cleared. Artificial reefs stop growing and restored floor stops spreading, and a built hatchery stands idle. Sea floor that has already become reef stays reef. Turning it off also ends any urchin or predator outbreak. Turning it back on picks everything up where it stopped, except outbreaks, which don't come back.
- **Urchin events** and **Invasive predator events.** On by default, listed under fish stock management and greyed out while it is off. Turning one off ends that threat on every map at once.
- **Shark chance per trip.** From 0 to 20%, default 1%. Set it to 0 to turn sharks off.

If a Waves update breaks one of the mod's hooks, Spearfishing logs one warning and turns off only the feature that depends on it.

## Adding and removing

You can add Spearfishing to an existing save. Existing maps have no natural reef or kelp, but an artificial reef can give them some.

You can also remove it from a save. The sea, stockpiles, growing zones and other zones load as before. Spearfishing zones, reef, kelp, artificial reefs, restored floor and its marks, urchin barrens, invasive predators, hatcheries, fry pails, gear and raw fish are gone, and a colonist who was diving or snorkeling stops and wanders. Expect a set of one-time errors about missing Spearfishing defs the first time the save loads.

## Building from source

Builds need the .NET SDK and a local RimWorld install.

- Build for 1.7: `dotnet build Source/Spearfishing.csproj -c Release`
- Build for 1.6: `dotnet build Source/Spearfishing.csproj -c Release -p:RimWorldVersion=1.6`
- Copy both builds to `RimWorld/Mods/Spearfishing`: `powershell -ExecutionPolicy Bypass -File deploy.ps1`

## License

Released under the GNU General Public License v3.0 (see `LICENSE`). Commercial use is allowed. Modified versions you distribute must stay under GPLv3 with source.

## AI?

Do I use AI to build my mods? **Yes.**  
Am I obsessive about how I use it and the quality of the results? **Also yes.**

I understand the scepticism.
I've seen the flood of AI-generated mods that look like someone typed a prompt, uploaded whatever came out, and called it done.

That bothers me too.

My workflow involves a lot of iteration, review, and testing. The same care I'd put into building everything by hand. I've spent hundreds of hours building mods. Using AI doesn't lower the standard I expect from my work.

## Links

Support me on Ko-fi.

[![Support me on Ko-fi](https://img.shields.io/badge/Support_me_on_Ko--fi-72a4f2?style=for-the-badge&logo=kofi&logoColor=white)](https://ko-fi.com/I7L525WMJ6)
