using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace Spearfishing;

// Spearfishing work (fish recovery ticket 03): a diver swims to a cell marked "Restore sea floor" that has reef or kelp beside
// it. Marked cells with none wait until restoration reaches them. Like a trip, it needs Waves' swimming, enough Rest and warm
// enough water, and only spots the diver can swim to and back from (DiveSafety). No spear: it is gardening. Spearfishing work
// is Violent, so a pawn who can't do violence can't restore either.
public class WorkGiver_RestoreSeaFloor : WorkGiver_Scanner
{
    public override PathEndMode PathEndMode => PathEndMode.OnCell;

    public override bool ShouldSkip(Pawn pawn, bool forced = false) =>
        !FishStockManagement.On || !WavesBridge.SwimmingOn || !pawn.Map.designationManager.AnySpawnedDesignationOfDef(RestorationDefOf.Spearfishing_RestoreSeaFloor) ||
        !SpearfishingUtility.RestedForATrip(pawn) || DiveSafety.TooColdToStart(pawn);

    public override IEnumerable<IntVec3> PotentialWorkCellsGlobal(Pawn pawn)
    {
        foreach (Designation mark in pawn.Map.designationManager.SpawnedDesignationsOfDef(RestorationDefOf.Spearfishing_RestoreSeaFloor))
            yield return mark.target.Cell;
    }

    public override bool HasJobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
    {
        Map map = pawn.Map;
        if (!HabitatRestoration.CanTake(map, c) || !HabitatRestoration.HasSource(map, c)) return false;
        if (c.IsForbidden(pawn) || !pawn.CanReserve(c, 1, -1, null, forced)) return false;
        if (!pawn.CanReach(c, PathEndMode.OnCell, Danger.Some)) return false;
        return DiveSafety.FitToSetOut(pawn, c, JobDriver_RestoreSeaFloor.WorkTicks(pawn));
    }

    public override Job JobOnCell(Pawn pawn, IntVec3 c, bool forced = false) => JobMaker.MakeJob(RestorationDefOf.Spearfishing_RestoreSeaFloorJob, c);
}
