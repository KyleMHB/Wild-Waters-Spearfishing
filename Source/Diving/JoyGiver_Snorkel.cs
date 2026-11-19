using RimWorld;
using Verse;
using Verse.AI;

namespace Spearfishing;

// Offers snorkeling (ticket 17, ADR 0007) to a pawn who can start a sea trip: Waves' swimming on, rested enough, and sea warm
// enough for their gear, with swimmable sea near dry land in reach. No spear, zone, work type or research: pacifists snorkel
// too, and nothing is killed, so no ideoligion check either.
public class JoyGiver_Snorkel : JoyGiver
{
    public override Job TryGiveJob(Pawn pawn)
    {
        if (!WavesBridge.SwimmingOn || !SpearfishingUtility.RestedForATrip(pawn) || DiveSafety.TooColdToStart(pawn)) return null;
        // A map with no fishing water has nowhere to snorkel; skip the flood fill (up to ~11k cells) on every attempt.
        MapComponent_FishStock fishStock = MapComponent_FishStock.Of(pawn.Map);
        if (fishStock != null && fishStock.Stock.BodyCount == 0) return null;
        IntVec3 spot = SpearfishingUtility.SnorkelSpot(pawn);
        return spot.IsValid && DiveSafety.FitToSetOut(pawn, spot, SpearfishingUtility.FreediveCycleTicks(pawn)) ? JobMaker.MakeJob(def.jobDef, spot) : null;
    }
}
