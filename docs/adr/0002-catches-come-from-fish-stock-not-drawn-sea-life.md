# Catches come from fish stock, not from drawn sea life

A diver's catch is rolled from the fish stock of the water they work, weighted by gear, reefs, kelp and depth. Waves' drawn sea life stays scenery: at most a shadow is shown being speared. Making each drawn fish a real, saved target would look the same at normal zoom, but it would tie gameplay to Waves' internal, unsaved render layer and cost per-fish work every tick.

## Consequences

- Performance is a requirement, not a nice-to-have: fish stock is updated rarely, per area and not per fish, and anything that runs every frame stays at the visual layer.
- The look of the sea life never has to match what was caught.
- Visuals may choose among gameplay random draws, but must never change how many draws are made (ticket 28). A diver stalking a drawn shoal picks from the same six waypoint draws as one who sees none, so turning the visuals off, or a shoal appearing, leaves the game's random sequence where it was.
