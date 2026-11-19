using RimWorld;
using Verse;

namespace Spearfishing;

// The hatchery and its fry (fish recovery ticket 04).
[DefOf]
public static class HatcheryDefOf
{
    public static ThingDef Spearfishing_Hatchery;
    public static ThingDef Spearfishing_FryBatch;
    public static JobDef Spearfishing_ReleaseFry;

    static HatcheryDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(HatcheryDefOf));
}
