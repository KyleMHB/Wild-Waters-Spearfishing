# Fish stock management is optional settings in one mod

Supersedes ADR 0014. Decided with the author on 2026-11-17.

The fish stock management systems stay in Spearfishing rather than a separate add-on, and can be turned off in the mod settings. These are logistic regrowth with the fish-down limit and the regrowth line in the zone's inspect panel, the artificial reef, and the recovery methods. With them off, Spearfishing plays as ADR 0013 describes: one capped stock per body of fishing water, flat regrowth at Odyssey's share, and a fixed stop. One mod means one build, one test suite, one release and one download, and no public seam to keep stable for another mod. The cost is a Workshop page that also has to explain features some players never turn on.

Management is on by default, so every player gets the full system, and players who want the simple version turn it off. Logistic regrowth, the fish-down limit and the regrowth line share one "Fish stock management" switch, because any of them alone would make a broken combination. Events such as urchins and invasive predators each have their own switch, like storyteller events. Buildings and jobs (hatchery, artificial reef, habitat restoration) follow the same switch: with management off they are disabled completely (revised with the author on 2026-11-18, see below). Toggling mid-game is safe, because a body of water keeps its stock either way; only how it regrows and where divers stop change.

With Odyssey active, every recovery boost also raises Odyssey's fish population for that water, through its public `Population` property, so line fishing benefits too; otherwise a dive, which reads the more fished-down of the two stocks (ADR 0013), would never see the boost. Odyssey's own cap still bounds line fishing. For the same reason, while logistic regrowth is on, Odyssey's population for each water is moved along with ours, so the two shares stay in step even though Odyssey regrows flat.

## Revision, 2026-11-18

This ADR first said buildings and jobs have no switch, because research already gates them and a switch would strand half-built structures. The author reversed that during the fish recovery interview: with fish stock management off, the recovery buildings and jobs are disabled completely, so the simple mode really is simple. They add no research project of their own, so nothing is hidden there; instead the artificial reef and hatchery leave the architect menu and the "Restore sea floor" designator is gone. Turning management off mid-game cancels their blueprints and unfinished frames (refunding materials as vanilla cancelling does), removes restoration designations, stops restored floor spreading and artificial reefs turning to reef, and leaves a built hatchery standing but idle. Sea floor that has already become reef stays reef, like natural reef. Turning management back on resumes them.

## Revision: threat events, 2026-11-18

In the threat events interview the author settled that the events (urchins and invasive predators) need both their own switch and fish stock management: with management off they never fire, as the recovery buildings are disabled. Each event's switch still lets a player with management on turn that one threat off. Pollution cleanup, once listed among the recovery methods, is dropped.

As built (threat events tickets 01 to 03): the two switches, "Urchin events" and "Invasive predator events", sit under the management switch and are greyed out while it is off. Turning management or an event's switch off ends that kind's active outbreak on every map at once, with no letter: barren and culled cells get their reef or kelp back, and the predator count drops to zero. The same check runs whenever a map finishes loading, so a switch changed at the main menu reaches a save loaded after it. Turning a switch back on brings no outbreak back.

## Considered Options

- A separate Workshop add-on built on a seam in Spearfishing (ADR 0014): a shorter Workshop page for each, but two mods to build, test and release, and a public seam between them.
- One switch for each system: allows broken combinations, such as a fish-down limit with flat regrowth.
- Buildings and jobs without a switch, gated only by research (this ADR's first version): no stranded structures, but with management off a reef would still be buildable while doing nothing for regrowth.
- Management off by default: a simpler start, but most players would never see the system.
- A core mod required by both: a third download and another load-order rule, with only one mod using it.
