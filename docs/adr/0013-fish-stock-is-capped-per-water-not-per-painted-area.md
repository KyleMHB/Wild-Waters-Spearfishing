# Fish stock is capped per water, not by painted area

Supersedes ADR 0004 (one capped stock per body of water replaces the per-cell grid) and ADR 0003 (with Odyssey, its population limits dives too, not only the other way round). Decided with the author on 2026-11-17.

Spearfishing is meant to be a main food source for a coastal colony, but only with several divers and good gear. Before this, each cell held its own fish and recovered about 19% of its capacity a day, so a zone's catch grew with the water painted and divers were limited only by their working hours: one skilled diver fed about four colonists indefinitely. Now every spearfishing zone on the same water draws from one shared total, and painting more water does not raise it. Reef and kelp still matter, but they decide where fish are dense and how likely a dive is to succeed there, not how many fish the water holds. With Odyssey active, spearfishing and line fishing draw on one shared total: when either has fished the water down, both feel it.

"The same water" is one body of fishing water: the sea, each lake and each river keep separate totals, and a body of water holds fish in proportion to its size up to a cap, so a small lake holds fewer fish than the sea but is still worth a diver. Odyssey's size curve, which leaves water under a few hundred cells nearly empty, was rejected because it would make most lakes and rivers not worth fishing. With Odyssey, the two populations are shared by fraction rather than by count: every catch, by either method, lowers both by the same share of their maximum, and a dive reads whichever is more fished down. Our total stays larger than Odyssey's, so spearfishing can still be a main food source, and neither DLC's numbers are rewritten.

A catch no longer thins the spot it came from: the per-cell depletion grid of ADR 0004 is dropped, and each body of fishing water keeps one number for how far it is fished down. Once the total is capped, that number is what decides the food, and moving divers between spots would be busywork that changes nothing. The reef and kelp grid (ADR 0008) stays, because it decides where dives succeed more often. Old saves ignore their depletion grid and start each body of water full.

With fish stock management turned off (it is on by default, ADR 0015), regrowth is flat, as in Odyssey: a body of water regrows the same number of fish each day until it is full, and divers stop at a fixed point when it is fished down. The interview first chose logistic regrowth, shown by a regrowth line in the zone's inspect panel and controlled by a per-zone fish-down limit; ADR 0014 moved those into a separate management add-on, and ADR 0015 brought them back as optional settings.

The regrowth is 2.5% of capacity a day, the same share Odyssey's water bodies regrow. Because the two stocks are shared by fraction and a dive reads the more fished-down one, any faster share of ours would leave Odyssey's population always the lower, and with Odyssey on divers would only ever get Odyssey's rate. Matching the share keeps the two in step on every body of water. To keep a full coastal sea at about 60 fish a day, it holds about 2400 fish, so a fished-out sea takes about 40 days to refill; the fixed stop keeps divers from fishing it below a quarter. The cap was first 1600 (40 a day); on 2026-11-17 the author raised it to 2400 after the best gear was kept at about 45 fish a day (fish-balance ticket 04), so that one best-gear diver no longer takes a whole sea's regrowth. Water under 2400 cells is unchanged.

Revised 2026-11-18 by ADR 0016 (fish recovery ticket 01): with fish stock management on, reef and kelp now also speed their water's regrowth, by (1 + the share of the water's cells that are reef or kelp), so they no longer decide only where dives succeed. The logistic rate dropped from 0.1 to about 0.078 so a sea with the typical natural share (28%, the median measured on four new coastal maps) still peaks at about 60 fish a day, 2.5% of capacity; water with more reef regrows faster, and with Odyssey the keep-pace rule (ADR 0015) carries the difference over. The flat 2.5% with management off is unchanged.

## Considered Options

- Keep the per-cell grid as well, so overfishing one spot costs extra on top of the cap: keeps spot rotation, but the total already limits the food, so rotation is busywork.
- Keep the per-cell grid for looks only, thinning the drawn shoals: a saved grid that no catch depends on.
- Keep per-cell capacity and slow recovery a lot: simplest, but painting a larger zone still raises the cap.
- Per-cell capacity, capped by how far divers can practically swim from shore: no new rule, but the cap depends on map shape and diver gear, not on a number we can tune.
- One total per map: fishing out the sea would also empty an inland lake.
- With Odyssey, use Odyssey's population as the total: its ocean regrows about 15 fish a day, about 2 colonists, so spearfishing could only ever be a supplement with the DLC on.
- With Odyssey, raise Odyssey's own population and regrowth: changes line fishing's balance for players who never asked for it.
- With Odyssey, keep the drain one-way (spearfishing lowers Odyssey's population, Odyssey never limits dives): Odyssey players would get two separate fish supplies from the same water.
- Logistic regrowth with a per-zone fish-down limit: overfishing has a lasting cost, but it needs managing; now an optional setting (ADR 0015).
- Regrowth in proportion to what is left: fastest when nearly full, so the best play is to barely fish.
