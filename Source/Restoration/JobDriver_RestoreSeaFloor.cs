using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace Spearfishing;

// A diver swims to a marked cell, works cuttings from the reef or kelp beside it into the floor for a short while, using and
// training Plants, then the cell takes that neighbour's kind and joins the restored floor that spreads (fish recovery ticket 03).
public class JobDriver_RestoreSeaFloor : JobDriver
{
    // Ten seconds at normal speed for a pawn with average plant work speed.
    public const int BaseWorkTicks = 600;

    // Plants experience per tick of work, as vanilla sowing gives.
    private const float XpPerTick = 0.085f;

    public static int WorkTicks(Pawn pawn) => Mathf.CeilToInt(BaseWorkTicks / Mathf.Max(0.1f, pawn.GetStatValue(StatDefOf.PlantWorkSpeed)));

    private IntVec3 Cell => job.targetA.Cell;

    public override bool TryMakePreToilReservations(bool errorOnFailed) => pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);

    protected override IEnumerable<Toil> MakeNewToils()
    {
        // Management switched off removes the marks, which ends the job; a mark cancelled by the player does too.
        this.FailOn(() => !FishStockManagement.On || !HabitatRestoration.IsMarked(Map, Cell));
        yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);

        Toil work = ToilMaker.MakeToil("RestoreSeaFloor");
        work.defaultCompleteMode = ToilCompleteMode.Delay;
        work.defaultDuration = WorkTicks(pawn);
        work.tickAction = () => pawn.skills?.Learn(SkillDefOf.Plants, XpPerTick);
        work.WithProgressBarToilDelay(TargetIndex.A);
        yield return work;

        Toil restore = ToilMaker.MakeToil("SeaFloorRestored");
        restore.defaultCompleteMode = ToilCompleteMode.Instant;
        restore.initAction = () =>
        {
            // The floor may have changed while the diver worked: a neighbour cleared, the cell filled in.
            if (!HabitatRestoration.CanTake(Map, Cell)) return;
            FloorMark kind = HabitatRestoration.SourceKind(Map, Cell);
            if (kind != FloorMark.Bare) MapComponent_FishStock.Of(Map).Restore(Cell, kind);
        };
        yield return restore;
    }
}
