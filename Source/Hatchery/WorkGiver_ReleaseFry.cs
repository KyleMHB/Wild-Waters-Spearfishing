using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace Spearfishing;

// Hauling: a fry pail on the map, from a hatchery or dropped on the way, goes to its water's edge (fish recovery ticket 04).
// Nothing is offered while fish stock management is off.
public class WorkGiver_ReleaseFry : WorkGiver_Scanner
{
    // When no release cell fits (the bank outside a hauler's allowed area, or out of reach), the search falls back to every
    // cell on the map, so a failure is remembered for a while per pail and pawn instead of repeating that scan on every work
    // check. JobOnThing reuses the cell HasJobOnThing found in the same tick rather than searching twice.
    private const int RetryTicks = 500;
    private static readonly Dictionary<(int pail, int pawn), int> noCellUntil = new();
    private static (int pail, int pawn, int tick, IntVec3 cell) lastFound = (-1, -1, -1, IntVec3.Invalid);

    public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForDef(HatcheryDefOf.Spearfishing_FryBatch);

    public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

    public override bool ShouldSkip(Pawn pawn, bool forced = false) =>
        !FishStockManagement.On || pawn.Map.listerThings.ThingsOfDef(HatcheryDefOf.Spearfishing_FryBatch).Count == 0;

    public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false) =>
        t is FryBatch pail && FishStockManagement.On && !pail.IsForbidden(pawn) && pawn.CanReserve(pail, 1, -1, null, forced) &&
        FindCell(pawn, pail, forced, out _);

    public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
    {
        if (t is not FryBatch pail || !FindCell(pawn, pail, forced, out IntVec3 cell)) return null;
        Job job = JobMaker.MakeJob(HatcheryDefOf.Spearfishing_ReleaseFry, pail, cell);
        job.count = 1;
        return job;
    }

    private static bool FindCell(Pawn pawn, FryBatch pail, bool forced, out IntVec3 cell)
    {
        int now = Find.TickManager.TicksGame;
        var key = (pail.thingIDNumber, pawn.thingIDNumber);
        if (lastFound.pail == key.Item1 && lastFound.pawn == key.Item2 && lastFound.tick == now)
        {
            cell = lastFound.cell;
            return true;
        }
        // A player's forced order always searches afresh.
        if (!forced && noCellUntil.TryGetValue(key, out int until) && now < until)
        {
            cell = IntVec3.Invalid;
            return false;
        }
        if (FryRelease.TryFindReleaseCell(pawn, pail.Target, out cell))
        {
            noCellUntil.Remove(key);
            lastFound = (key.Item1, key.Item2, now, cell);
            return true;
        }
        if (noCellUntil.Count > 64) noCellUntil.Clear();
        noCellUntil[key] = now + RetryTicks;
        return false;
    }
}
