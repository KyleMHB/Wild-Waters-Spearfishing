# Spearfishing zones are saved outside the zone manager

During play, spearfishing zones are ordinary vanilla zones in the map's `ZoneManager`. When the game saves, they are taken out of the zone manager's list and saved in `MapComponent_FishStock` instead. On load the component puts them back into the list, links them to the zone manager and adds their cells to the zone grid.

We chose this so that a player can remove the mod from a save (story 50). RimWorld 1.6 and 1.7 can't load a zone whose class is missing: they put null in the zone list, then the zone manager's own load throws on it and the map loses its whole zone manager, stockpiles and growing zones included. No code of ours runs once the mod is gone, so the fix has to be in what gets saved. Without the mod, the component is one missing class that the map drops, and the zone manager holds only vanilla zones.

## Consequences

- A Harmony prefix and finalizer on `ZoneManager.ExposeData` do the split. The finalizer restores the list in its original order even if saving throws. Re-adding cells uses `ZoneManager`'s internal `AddZoneGridCell`, called by reflection.
- If either target is missing after a game update, the mod logs one warning and leaves vanilla saving alone. Zones still save and load with the mod, but removing it is no longer safe.
- After a reload, spearfishing zones come after vanilla zones in the zone list.
- Saves made before this change keep the zone in the zone manager's list and load as before. The next save moves it.
- A dive trip finds its zone through the zone grid, so it still resolves after a reload.
- The same reasoning covers a pawn on one of the mod's jobs. RimWorld cleans up a job whose driver class is missing, but not one whose def is missing too: the pawn fails to spawn and throws every tick. So Pawn_JobTracker.ExposeData writes such a job with the vanilla Wait def and keeps the real def in an extra element that only the mod reads back. Without the mod the job loads as Wait with no driver and is cleaned up.
- Queued jobs of the mod's defs are left to vanilla (2026-11-18, checked against the decompiled 1.7 `JobQueue`, `QueuedJob`, `Job` and `Pawn_JobTracker`). The restoration and fry release work can be shift-queued or prioritized, and so can the urchin cull. Without the mod, such a job loads with one "Could not load reference to JobDef" error, and a scanner job adds a second error for its missing `WorkGiverDef`, because `Job.ExposeData` saves `workGiverDef` too. `JobQueue.ExposeData` then removes every queued job with a null def in PostLoadInit, and the pawn is unharmed.
  - We don't write queued jobs as Wait the way the current job is written. A queued job has no driver, so the invalid-job cleanup never reaches it, and it would load as a real Wait job. `JobDriver_Wait` never completes on its own, and the job has no expiry and is often player-forced, so the colonist would stand still until ordered off.
  - We also rejected writing their def as "null", which loads silently, and restoring the real defs from an extra element. That would remove only the JobDef error, while the WorkGiverDef error stays, so it isn't worth the code.

## Considered Options

- Keep spearfishing zones out of `ZoneManager` entirely, as our own map store with our own designator, drawing, selection and inspect panel. Nothing of ours would be in a vanilla list and no vanilla method would be patched, but it means rebuilding most of tickets 01 and 02.
- A "prepare for removal" button that deletes spearfishing zones. It's small, but removal is only safe if the player remembers to press it, the same reason ADR 0008 rejected this approach for reef.
