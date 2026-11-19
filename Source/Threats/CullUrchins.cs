using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace Spearfishing;

[DefOf]
public static class UrchinDefOf
{
    public static JobDef Spearfishing_CullUrchinsJob;

    static UrchinDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(UrchinDefOf));
}

// The culling diver stands still in deep water while it works, so Waves must not send it ashore (StaysInWater).
[StaticConstructorOnStartup]
public static class CullUrchinsStartup
{
    static CullUrchinsStartup() => StaysInWater.Register(UrchinDefOf.Spearfishing_CullUrchinsJob);
}

// Spearfishing work (threat events ticket 02, spec stories 12-13): a diver swims to a barren cell and culls its urchins, with
// no order needed: every barren cell of the map's sea is a target. Like a trip, it needs Waves' swimming, enough Rest and warm
// enough water, and only cells the diver can swim to and back from (DiveSafety). Spearfishing work is Violent, so a pawn who
// can't do violence can't cull either.
public class WorkGiver_CullUrchins : WorkGiver_Scanner
{
    public override PathEndMode PathEndMode => PathEndMode.OnCell;

    public override bool ShouldSkip(Pawn pawn, bool forced = false) =>
        !FishStockManagement.On || !WavesBridge.SwimmingOn || (MapComponent_FishStock.Of(pawn.Map)?.BarrenCellCount ?? 0) == 0 ||
        !SpearfishingUtility.RestedForATrip(pawn) || DiveSafety.TooColdToStart(pawn);

    // A copy, so a cull finishing elsewhere while the scan runs doesn't change the set being read.
    public override IEnumerable<IntVec3> PotentialWorkCellsGlobal(Pawn pawn) =>
        new List<IntVec3>(MapComponent_FishStock.Of(pawn.Map).BarrenCells);

    public override bool HasJobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
    {
        Map map = pawn.Map;
        if (!MapComponent_FishStock.Of(map).IsBarren(c) || !WavesBridge.IsSea(c.GetTerrain(map))) return false;
        if (c.IsForbidden(pawn) || !pawn.CanReserve(c, 1, -1, null, forced)) return false;
        if (!pawn.CanReach(c, PathEndMode.OnCell, Danger.Some)) return false;
        return DiveSafety.FitToSetOut(pawn, c, JobDriver_CullUrchins.WorkTicks);
    }

    public override Job JobOnCell(Pawn pawn, IntVec3 c, bool forced = false) => JobMaker.MakeJob(UrchinDefOf.Spearfishing_CullUrchinsJob, c);
}

// A diver swims to a barren cell, works through the urchins with a spear or knife for a short while, using and training Melee,
// then the cell starts recovering its reef or kelp (spec story 13). No item: the cull gives only Melee experience.
public class JobDriver_CullUrchins : JobDriver
{
    // Seven seconds at normal speed.
    public const int WorkTicks = 420;

    // Melee experience per tick of work: 42 a cull.
    private const float XpPerTick = 0.1f;

    private IntVec3 Cell => job.targetA.Cell;

    public override bool TryMakePreToilReservations(bool errorOnFailed) => pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);

    protected override IEnumerable<Toil> MakeNewToils()
    {
        // Management or the urchin switch off ends the barren, which ends the job; so does another diver culling the cell.
        this.FailOn(() => !FishStockManagement.On || !MapComponent_FishStock.Of(Map).IsBarren(Cell));
        yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);

        Toil work = ToilMaker.MakeToil("CullUrchins");
        work.defaultCompleteMode = ToilCompleteMode.Delay;
        work.defaultDuration = WorkTicks;
        work.tickAction = () => pawn.skills?.Learn(SkillDefOf.Melee, XpPerTick);
        work.WithProgressBarToilDelay(TargetIndex.A);
        yield return work;

        Toil cull = ToilMaker.MakeToil("UrchinsCulled");
        cull.defaultCompleteMode = ToilCompleteMode.Instant;
        cull.initAction = () => MapComponent_FishStock.Of(Map).CullUrchins(Cell);
        yield return cull;
    }
}
