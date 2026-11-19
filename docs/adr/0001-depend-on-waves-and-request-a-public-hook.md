---
status: accepted; the hook request and internal patches are superseded by ADR 0011
---

# Depend on Waves and ask for a public swimming hook

Spearfishing requires RimWorld: Waves for swimming instead of implementing its own, because Waves already handles deep-water pathing, reachability, drowning and cold. Waves exposes no public API (`Swimming`, `SeaLife` and `ShoreField` are internal), so we ask its author for a small stat-based hook that Waves reads for swim endurance and water cold limits. Until that exists, every patch on Waves internals lives in one isolated file, so a Waves update breaks one place.

## Consequences

Gear needs two seams in Waves: swim endurance (Waves drains the Rest need while in deep water) and the water cold limit (Waves deliberately strips clothing warmth from it, so a wetsuit cannot work through ordinary apparel stats). The hook request covers both, plus a way to keep an exhausted pawn with a buoy afloat instead of downed. Swim speed needs no seam: it acts through Move Speed (ADR 0005).

## Considered Options

- Patch Waves internals permanently: fastest, but breaks on any Waves rename.
- Own swimming system with Waves optional: no fragility, but duplicates Waves' pathing and region patches.
