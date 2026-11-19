using RimWorld;
using Verse;

namespace Spearfishing;

// When a diver must head home, or must not set out, for their own safety: Rest for the swim home and the cold. Shared by
// every sea trip (spearfishing and snorkeling), the work giver and the snorkeling joy giver. The numbers are in DiveRules; Waves' limits come from the bridge,
// so better gear (fins, wetsuit) changes the margins without changing these rules.
public static class DiveSafety
{
    public enum Exit { None, Tired, Cold }

    // Ticks the pawn takes to swim one cell of deep water at their current speed: their own ticks per move (which carries
    // swim speed while they are in the sea) plus Waves' deep-water cost.
    public static float TicksPerSwimCell(Pawn pawn) => pawn.TicksPerMoveCardinal + WavesBridge.DeepWaterMoveCost;

    public static float TicksToShore(Pawn pawn, IntVec3 shore) =>
        DiveRules.TicksToShore(pawn.Position.DistanceTo(shore), TicksPerSwimCell(pawn));

    // Ticks the pawn is held at sea before they can next turn home, from their sea trip; 0 on any other job.
    public static float TicksBeforeTurning(Pawn pawn) => pawn.jobs?.curDriver is JobDriver_SeaTrip trip ? trip.TicksBeforeTurningHome : 0f;

    // Rest the pawn needs right now to reach that shore safely; 0 for a pawn without Rest.
    public static float RestToReachShore(Pawn pawn, IntVec3 shore)
    {
        Need_Rest rest = pawn.needs?.rest;
        if (rest == null) return 0f;
        float lossPerTick = WavesBridge.DeepWaterRestDrainPerTick(pawn) + rest.RestFallPerTick;
        return DiveRules.RestToReachShore(lossPerTick, TicksToShore(pawn, shore), TicksBeforeTurning(pawn));
    }

    // Why a diver at sea must head for that shore now, or Exit.None.
    public static Exit MustHeadHome(Pawn pawn, IntVec3 shore)
    {
        Need_Rest rest = pawn.needs?.rest;
        // Waves tests CurLevel, not the percentage.
        if (rest != null && rest.CurLevel < RestToReachShore(pawn, shore)) return Exit.Tired;
        if (WaterTooCold(pawn)) return Exit.Cold;
        float chill = DiveRules.HypothermiaAtShore(Hypothermia(pawn), WavesBridge.WaterChillPerTick(pawn), TicksToShore(pawn, shore),
            TicksBeforeTurning(pawn));
        return chill >= DiveRules.HeadHomeHypothermia ? Exit.Cold : Exit.None;
    }

    // The longest dive, from shortest to full ticks, after which the pawn still has the Rest and warmth to reach that shore
    // safely once its surface is over (ticket 25): the safety exits' sums, solved for the dive, with room to drift
    // DiveDriftCells farther out. A diver who can't afford even
    // the shortest dive has already turned home, so this never goes below it.
    public static int DiveTicksToFit(Pawn pawn, IntVec3 shore, int shortest, int full)
    {
        if (full <= shortest || !shore.IsValid) return full;
        float swim = DiveRules.TicksToShore(pawn.Position.DistanceTo(shore) + DiveRules.DiveDriftCells, TicksPerSwimCell(pawn));
        float longest = float.MaxValue;
        // The diver's own rest after the dive (gear tiers ticket 04).
        float restFactor = SpearfishingUtility.SurfaceRestFactor(pawn);
        Need_Rest rest = pawn.needs?.rest;
        if (rest != null)
            longest = DiveRules.LongestDiveTicks(rest.CurLevel - DiveRules.RestReserve,
                WavesBridge.DeepWaterRestDrainPerTick(pawn) + rest.RestFallPerTick, swim, restFactor);
        longest = UnityEngine.Mathf.Min(longest,
            DiveRules.LongestDiveTicks(DiveRules.HeadHomeHypothermia - Hypothermia(pawn), WavesBridge.WaterChillPerTick(pawn), swim, restFactor));
        return longest >= full ? full : UnityEngine.Mathf.Max(shortest, (int)longest);
    }

    // Whether the pawn has the Rest and warmth to set out for spot (ticket 21): to swim out, stay one shortest dive and its
    // surface (cycleTicks; ticket 25), and still meet the safety exits' margin for the swim home. The same sum the exits make
    // at the spot between dives, so a pawn who sets out does not turn straight home on arrival. The swim out is timed at
    // swim speed from the spot's shore.
    public static bool FitToSetOut(Pawn pawn, IntVec3 spot, float cycleTicks)
    {
        float cells = UnityEngine.Mathf.Sqrt(SpearfishingUtility.DistanceToShoreSquared(pawn.Map, spot));
        float swim = DiveRules.TicksToShore(cells, TicksPerSwimCell(pawn));
        Need_Rest rest = pawn.needs?.rest;
        if (rest != null &&
            rest.CurLevel < DiveRules.RestToReachShore(WavesBridge.DeepWaterRestDrainPerTick(pawn) + rest.RestFallPerTick, swim, swim + cycleTicks))
            return false;
        return DiveRules.HypothermiaAtShore(Hypothermia(pawn), WavesBridge.WaterChillPerTick(pawn), swim, swim + cycleTicks) <
               DiveRules.HeadHomeHypothermia;
    }

    // Whether the sea is too cold for this pawn to set out, with their gear.
    public static bool TooColdToStart(Pawn pawn) => WaterTooCold(pawn) || Hypothermia(pawn) > DiveRules.MaxHypothermiaToStart;

    // Colder than the margin below the pawn's water cold limit. Waves chills nobody with its swim limits off.
    public static bool WaterTooCold(Pawn pawn) =>
        WavesBridge.SwimLimitsOn && WavesBridge.WaterTemperature(pawn.Map) < WavesBridge.WaterColdLimit(pawn) - DiveRules.WaterColdMargin;

    private static float Hypothermia(Pawn pawn) => pawn.health?.hediffSet?.GetFirstHediffOfDef(HediffDefOf.Hypothermia)?.Severity ?? 0f;
}
