using RimWorld;
using Verse;

namespace Spearfishing;

// Multiplies Move Speed by the pawn's swim speed while they stand in swimmable water, sea, lake or river (ADR 0005, 0010). Nothing in pathfinding is
// touched: Waves' fixed deep-water path cost still applies on top, so fins shorten only the walking part of each step.
//
// Move Speed is not cached: Pawn.TicksPerMove reads it through GetStatValue with no cache window, once per step, when the
// pawn sets up its move into the next cell. That read happens on the cell being left, so the step from land into the sea
// is still a land step and the step back out is still a swimming step; there is no stale value to refresh.
public class StatPart_SwimSpeed : StatPart
{
    public override void TransformValue(StatRequest req, ref float val)
    {
        if (TryGetFactor(req, out float factor)) val *= factor;
    }

    public override string ExplanationPart(StatRequest req) =>
        TryGetFactor(req, out float factor) ? "Spearfishing_StatsReport_Swimming".Translate() + ": x" + factor.ToStringPercent() : null; // the vanilla stat-line shape

    private static bool TryGetFactor(StatRequest req, out float factor)
    {
        factor = 1f;
        // Cheap tests first: Move Speed is read every step by every pawn on the map.
        if (req.Thing is not Pawn { Spawned: true } pawn || !WavesBridge.IsSwimmableFishingWater(pawn.Map, pawn.Position)) return false;
        factor = pawn.GetStatValue(SwimStatDefOf.Spearfishing_SwimSpeed);
        return true;
    }
}
