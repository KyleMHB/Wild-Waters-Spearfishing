using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace Spearfishing;

// An exhausted buoy wearer's swim to dry land (target A), at walking pace (the job's urgency, set in Buoy). Not a dive trip:
// the dive visuals never hide the pawn, and Waves' idle check is refused by Buoy's job guard rather than the trip's. Any catch
// from the trip this ended is already in the inventory and is unloaded ashore like a drafted diver's.
public class JobDriver_FloatHome : JobDriver
{
    public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

    protected override IEnumerable<Toil> MakeNewToils()
    {
        yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);
    }
}
