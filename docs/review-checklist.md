# First-release review checklist

This is the first release's checklist, kept as it was used. It covers only the first release's gear. The gear tiers' items (band and pneumatic spearguns, plastic and long carbon fins, low-volume mask, dry snorkel, rebreather, neoprene and thermal wetsuits, foam buoy) and the shark were reviewed item by item instead: each has the author's approval in `art/<item>/APPROVAL.md`, with stills and a shark clip from `python tools/spear_test.py run spearfishing-gear-look --seed 1` (and `spearfishing-gear-look-spearguns`). A later release that needs one whole-mod review starts a new checklist from this one.

The single in-game review of visuals, art and feel for ticket 14. Tick each item, note anything that needs fixing, and record each fix as a new ticket in `.scratch/spearfishing/issues/`. Automated cases do not cover anything on this list.

## Getting a test game quickly

Deploy first: `powershell -ExecutionPolicy Bypass -File deploy.ps1`.

**Option A: a harness scene, left open.** Each of these runs one batch in a fresh game and leaves it paused when it finishes. Close the game to finish the harness cleanup.

- Dive visuals and the face-down look, a diver mid-trip and a snorkeler in mask and snorkel: `python tools/spear_test.py run spearfishing-visuals --seed 1 --keep-open`
- Snorkeling and work-trip recreation: `python tools/spear_test.py run spearfishing-recreation --seed 1 --keep-open`
- Reef on a generated coast: `python tools/spear_test.py run spearfishing-reefgen --seed 1 --keep-open`. This batch clears the map's reef grid before it ends, so look at the reef while it runs, or use option B.
- Buoy and floating home: `python tools/spear_test.py run spearfishing-buoy --seed 1 --keep-open`
- Wetsuit: `python tools/spear_test.py run spearfishing-wetsuit --seed 1 --keep-open`

**Option B: your own colony.** Start a new game on a coastal tile (the world map shows coasts), temperate forest for warm water, with a large map so the reef has room. Turn on development mode, then:

1. Use the debug action that finishes all research, or finish Spearfishing (medieval, after Smithing).
2. Spawn one of each item with the "Spawn thing" debug action: `Spearfishing_PoleSpear`, `Spearfishing_SteelPoleSpear`, `Spearfishing_WoodenFins`, `Spearfishing_WoodenBuoy`, `Spearfishing_GlassMask`, `Spearfishing_Snorkel`, `Spearfishing_BasicWetsuit`. Put them in a stockpile so colonists pick them up, or force-wear them.
3. Paint a spearfishing zone on swimmable sea a few cells past the beach, give a colonist a spear and enable Spearfishing in the Work tab.
4. For snorkeling, set a colonist's schedule to recreation and lower their recreation need with the debug tools. No zone or gear is needed.

## Recorded capture

`build.mp4` in run `20261115-223812-spearfishing-visuals-s1`, under `E:\Coding\Templates\tools\rimworld-dev-tests\work\userdata\spear\SpearfishingTests\`. The first 12 s show a diver with no gear. The last 12 s show a snorkeler in mask and snorkel floating beside a diver in a mask, in the approved head-only look.

- [ ] Watch the capture. Floaters read as face down and swimmers as swimming.

## Art

- [ ] Raw fish: on the ground at each stack size, and in a stockpile.
- [ ] Wooden pole spear: on the ground and held by a pawn facing each direction.
- [ ] Steel-tipped pole spear: on the ground and held. Its steel point should read clearly.
- [ ] Wooden fins: on the ground. Fins have no worn graphic by design.
- [ ] Wooden buoy: on the ground. The buoy has no worn graphic by design.
- [ ] Glass mask: on the ground, and worn under a helmet and alone, facing south, east and north.
- [ ] Snorkel: on the ground, and worn facing south, east and north. The east view's tube sits at the back of the head.
- [ ] Snorkel with the glass mask, and under a helmet: all three show and nothing clips badly.
- [ ] Mask strap and snorkel from behind on a long-haired pawn on land: both draw over the hair.
- [ ] Basic wetsuit: on the ground, tinted by its leather, and worn by male, female, thin, hulk and fat bodies facing south, east and north. The east view has no seam.
- [ ] Spearfishing zone: the Zone menu icon is a vanilla placeholder. Decide whether it needs its own.

## Dive visuals

- [ ] A diver disappears under the water for each dive and comes back up to surface. The name label stays visible.
- [ ] Three fish shadows circle a diver at the dive spot and fade in and out with the dive.
- [ ] A catch shows a shadow darting to the spear and a ring burst. Ticket 12's capture did not show a burst, so watch for one here.
- [ ] Two or more divers at once. Ticket 12 never showed this.
- [ ] Turning off **Dive visuals** in the mod settings keeps divers in view and draws nothing extra.
- [ ] Nothing draws while nobody is in the sea.

## Face-down look

- [ ] A diver resting at the surface between dives shows only the back of the head, with the mask strap if worn.
- [ ] A floating snorkeler shows the back of the head with the strap and the snorkel tube, whichever way they face.
- [ ] Long hair from behind: the strap and tube draw over it.
- [ ] A pawn swimming out, drifting or swimming home looks as Waves draws swimmers, not face down.
- [ ] A pawn in a helmet floating face down. Ticket 18 never saw this.
- [ ] With **Dive visuals** off, floaters are drawn as Waves draws them.

## Snorkeling

- [ ] A colonist in recreation time with no spear, gear or zone swims to sea near shore, floats, freedives now and then and comes home. Recreation rises and nothing is caught.
- [ ] A freediving snorkeler disappears under the water and comes back up. Fish shadows circle them, with no burst.
- [ ] A snorkeler with a snorkel stays out longer, about 1.6 hours against 1 hour.
- [ ] The snorkel's stat panel shows snorkeling enjoyment +35% and the longer session.
- [ ] Crafting the snorkel at a crafting spot or tailoring bench, from 15 wood and 5 cloth.
- [ ] Ticket 17 did not observe these: a true pacifist (incapable of violence) snorkeling, the cold exit, the trip ending when recreation time is over, and saving and loading mid-session.
- [ ] A real coast with wading shallows before the swimmable sea. The test arena has deep water against the land.

## Reef under Waves' water

- [ ] Reef patches show under Waves' sea on a newly generated coastal map, with soft edges and a mix of rich and poor stretches.
- [ ] Deep reef reads fainter than shallow reef (0.7 strength).
- [ ] At night the reef darkens with the water. Ticket 03 did not check night lighting.
- [ ] Waves' own fish shadows still draw over the reef. Ticket 03 did not confirm this.
- [ ] Reef is hidden under bridges and floors, and comes back when a bridge is removed. Ticket 19 did not look at this.

## Floating home and safety

- [ ] An exhausted diver with a buoy floats home slowly, gets a message, and is never downed. Let a diver with low Rest stay out to see it.
- [ ] Drafting a floating diver works, and the swim resumes after undrafting.
- [ ] Ticket 08 did not observe these: a floating diver refusing to collapse asleep, a mental break or downing from another cause while floating, saving and loading mid-float, and a diver with no reachable dry land.
- [ ] A tired or cold diver turns home on their own. The rest gate was never seen in game, because the harness keeps pawns rested.

## Wetsuit and gear feel

- [ ] The wetsuit fits under middle and outer clothing, and swaps out a shirt and trousers.
- [ ] In cold water a suited diver keeps working where an unsuited one won't set out.
- [ ] Crafting each item at its bench: the pole spear, fins and buoy at a crafting spot, the steel spear at a smithy, the mask and the wetsuit at a tailoring bench. Tickets 04, 09 and 10 checked only that the recipes exist.
- [ ] A diver caught by a raid fights with their spear.

## Work-trip recreation

- [ ] Work divers' recreation ends each trip a little higher. The needs tab shows a rising arrow while a work diver is in the water.

## Other gaps from earlier tickets

- [ ] Diving moves to a new spot when the water there runs low, and the trip heads home when the whole zone runs low (ticket 04).
- [ ] An interruption other than drafting, such as a fire alarm, keeps the catch (ticket 05).
- [ ] With Odyssey: catches are Odyssey fish, snorkeling and floating home work, and a dive when Odyssey's population is 0 behaves sensibly (tickets 04, 06, 08).
- [ ] With Dubs Bad Hygiene or its Lite version: hygiene rises on a trip and while snorkeling, and nothing breaks. Snorkeling hygiene was never run (ticket 17), and Lite was never run (ticket 16).
- [ ] RimWorld 1.6: the mod has only been compile-checked for 1.6.

## Removing the mod from a save

Ticket 19 checked this automatically with `tools/removal-check/removal_check.py`, on the save from run `20261115-223437-run-all-s1`. That save has a spearfishing zone over deep reef, a stockpile, depleted stock, a diver mid-trip with a fish and all four gear items, raw fish and gear on the ground, and the research done. It had no snorkeler. What the check saw:

- The sea is intact: all 180 deep ocean cells, reef included, are still `WaterOceanDeep`.
- The stockpile is intact. Only the spearfishing zone is gone.
- The diver loads, "Cleaning up invalid job state" ends the trip, and they wander with their gear gone.
- One-time load errors name each missing Spearfishing class and def: the map component, the research, and every gear item and raw fish. Clearing the diver's job with gear missing adds a few more. No errors repeat per tick.
- Work priorities and recreation tolerances are saved by def position. If another mod loads after Spearfishing, its entries could shift by one. This was never tried.

To check it yourself:

- [ ] Make a save with a diver mid-trip and a colonist snorkeling. Turn off Spearfishing (keep Harmony and RimWorld: Waves), restart, load it and accept the mod-list mismatch.
- [ ] The coast, stockpiles and growing zones look and work as before.
- [ ] The diver and the snorkeler stop and wander, with no errors repeating every tick.
- [ ] The errors on that first load are one-time missing-def errors only.
- [ ] Turn Spearfishing back on afterwards.
