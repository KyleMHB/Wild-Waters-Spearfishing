using RimWorld;
using Verse;
using Verse.AI;

namespace Spearfishing;

// Offers a spearfishing trip to a pawn who meets the entry conditions every trip shares (SpearfishingUtility.CanStartTrip),
// to the nearest zone whose stock is worth a dive and that has a spot the pawn can reach.
public class WorkGiver_Spearfish : WorkGiver_Scanner
{
    public override bool ShouldSkip(Pawn pawn, bool forced = false) => SpearfishingUtility.SkipTrips(pawn);

    public override Job NonScanJob(Pawn pawn)
    {
        IntVec3 spot = SpearfishingUtility.FirstSpot(pawn, out bool outOfReach);
        if (spot.IsValid) return JobMaker.MakeJob(SpearfishingDefOf.Spearfishing_Spearfish, spot);
        // Otherwise a diver with a zone and nothing else to do would stand idle with no word why (ticket 28).
        if (outOfReach) JobFailReason.Is("Spearfishing_ZoneTooFarToDive".Translate());
        return null;
    }
}
