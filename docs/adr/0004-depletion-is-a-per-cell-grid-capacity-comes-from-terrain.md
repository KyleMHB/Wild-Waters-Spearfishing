# Depletion lives in the water as a per-cell grid; capacity comes from terrain

Superseded by ADR 0013: each body of fishing water keeps one capped fish stock shared by its zones; the per-cell depletion grid is dropped.

Amended by ADR 0008: reef is read from its own per-cell grid, not from terrain.

Fish stock belongs to the sea, not to spearfishing zones. Each map keeps one grid with a depletion byte per cell, and each cell's capacity is worked out from its terrain (reef, kelp, depth) whenever it is needed and is never saved. A cell's stock is its capacity times what remains after depletion, and a zone's stock is the total over its cells, cached and refreshed only on a catch, after recovery or when the zone changes. A catch depletes the cells around the dive spot, so overfishing one spot is local. Recovery runs once per in-game hour over depleted cells only, rather than per tick.

Because zones hold no fish of their own, deleting, repainting, shrinking, extending, splitting and merging zones need no rules: the same water always has the same stock. The grid costs about one byte per map cell in memory (about 62 KB on a 250×250 map) and is saved like vanilla's own per-cell grids, so a mostly full sea compresses to very little. Nothing runs per frame.

## Considered Options

- Save a fish count per zone: deleting and repainting a zone would give a full stock.
- One depletion number per zone: tiny saves, but deleting a zone loses its depletion, and every merge, split and resize needs a rule to share it out. Fishing one corner of a big zone lowers the whole zone evenly.
- One number per zone plus remembered cells (cells that leave a zone still depleted keep their depletion until recovered): closes the refill exploit with sparse saves, but keeps two stores that every zone edit must convert between, and averaging blurs depletion when zones grow.
- Depletion per block of cells (for example 8×8): even less data, but block edges don't follow zone edges, and a catch depletes water outside the zone.
- Start every new zone depleted: no extra data, but a zone on untouched sea would also start poor.
