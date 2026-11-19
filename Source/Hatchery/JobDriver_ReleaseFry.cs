using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace Spearfishing;

// Picks up a fry pail (A), carries it to a cell at its water's edge (B), and releases the fry (fish recovery ticket 04). If
// the job ends early the pawn drops the pail, which keeps its water, and the work giver offers it again. It stops while fish
// stock management is off.
public class JobDriver_ReleaseFry : JobDriver
{
    private const TargetIndex PailIndex = TargetIndex.A;
    private const TargetIndex EdgeIndex = TargetIndex.B;
    private const int ReleaseTicks = 120;

    public override bool TryMakePreToilReservations(bool errorOnFailed) =>
        pawn.Reserve(job.GetTarget(PailIndex), job, 1, -1, null, errorOnFailed);

    protected override IEnumerable<Toil> MakeNewToils()
    {
        this.FailOn(() => !FishStockManagement.On);
        yield return Toils_Goto.GotoThing(PailIndex, PathEndMode.ClosestTouch).FailOnDespawnedNullOrForbidden(PailIndex)
            .FailOnSomeonePhysicallyInteracting(PailIndex);
        yield return Toils_Haul.StartCarryThing(PailIndex);
        yield return Toils_Goto.GotoCell(EdgeIndex, PathEndMode.OnCell);
        yield return Toils_General.Wait(ReleaseTicks).WithProgressBarToilDelay(EdgeIndex);
        var release = ToilMaker.MakeToil("ReleaseFry");
        release.initAction = () =>
        {
            if (pawn.carryTracker.CarriedThing is not FryBatch pail || FryRelease.Release(pail) < 0f)
                EndJobWith(JobCondition.Incompletable);
        };
        release.defaultCompleteMode = ToilCompleteMode.Instant;
        yield return release;
    }
}
