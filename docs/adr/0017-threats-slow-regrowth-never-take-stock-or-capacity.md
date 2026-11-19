# Threats slow regrowth, never take stock or capacity

Decided with the author on 2026-11-18, in the threat events interview.

The threat events of fish stock management (ADR 0015), urchins and invasive predators, mirror the recovery levers of ADR 0016 in reverse: they only slow regrowth. An urchin barren stops its reef and kelp cells counting toward their water's reef share, so that water's regrowth boost falls. Invasive predators are a count kept with a body of fishing water, not animals on the map; they cut that water's regrowth by up to half as the count rises. Neither takes fish already in the stock, and neither lowers capacity.

A threat therefore never empties a body of water or changes the food cap of ADR 0013; it makes a fished-down water slow to recover, which is the pressure culling answers. The stock a colony sees only falls when someone catches fish, so a player is never surprised by fish vanishing from a full sea. Predators are culled by ordinary spearfishing in their water (a share of catches are predators and still land like any catch), urchins by a diving job; GLOSSARY's "Urchin barren" and "Invasive predators" describe both as built.

As built (threat events tickets 02 and 03): barren cells keep their reef or kelp mark in the reef grid but count as bare floor for the reef share, the catch chance and the overlays, so `FishStockModel` needed no barren state. The predator cut multiplies regrowth by 1 − 0.5 × count ÷ maximum after the reef boost, with a maximum of a 24th of capacity. A predator catch still lowers the stock like any catch, since the predator came out of that water's fish; the count is a share of the stock, not extra fish. With Odyssey, the keep-pace rule (ADR 0015) carries the slower regrowth to Odyssey's population, and line fishing never touches the count.

## Considered Options

- Predators eat fish from the stock each day: closer to life, but a full sea could drain with no one fishing, and the stock line would fall for reasons the player cannot see.
- Threats lower capacity: undoes ADR 0016's rule that capacity is the one fixed number for food.
- Predators as animals on the map that can be hunted: visible, but needs art, AI and swimming behaviour, all for a number that already does the job.
