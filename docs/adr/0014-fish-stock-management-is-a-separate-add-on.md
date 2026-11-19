# Fish stock management is a separate add-on, built on a seam in Spearfishing

Decided with the author on 2026-11-17, after ADR 0013. Superseded the same day by ADR 0015: the management systems stay in Spearfishing as optional settings.

Spearfishing itself stays simple: one capped fish stock per body of fishing water, a flat regrowth like Odyssey's, and a fixed point below which divers stop. Everything that asks the player to manage a stock goes into a separate Workshop add-on: logistic regrowth, the fish-down limit and the regrowth line in the zone's inspect panel, the artificial reef, and ways to speed recovery. Logistic regrowth only matters when the player has tools to manage it, and a fish-down limit only matters when regrowth is logistic, so they ship together or not at all. Keeping them out of Spearfishing keeps its Workshop page and its learning curve short, and gives the management features their own audience.

Spearfishing exposes a small public seam for the add-on: the regrowth rule, the rule for when divers stop, and adding fish to a body of water's stock. The add-on is built only once it has at least two recovery methods besides logistic regrowth.

With Odyssey active, every recovery boost from the add-on also raises Odyssey's fish population for that water, through its public `Population` property, so line fishing benefits too. Otherwise the boosts would be wasted: our stock would refill faster, but a dive reads the more fished-down of the two (ADR 0013). Odyssey's own cap still bounds line fishing; the boosts only make it refill sooner.

There is no separate core mod: Spearfishing owns the fish stock, the bodies of water and the Odyssey link, and the add-on requires Spearfishing. A core is split out only when a second mod needs the stock without spearfishing (such as fish traps or nets); moving code into a core later is easier than folding one back.

## Considered Options

- Keep everything in Spearfishing, as ADR 0013 first had it: one mod to maintain, but a harder mod to learn, and the management parts would be present for every player.
- One mod with the management features behind a setting, off by default: one build and one test suite, but the Workshop page has to explain features most players never turn on.
- A core mod now, required by both Spearfishing and the add-on: a third download, another load-order rule and another release to keep in step, with only one mod using it.
