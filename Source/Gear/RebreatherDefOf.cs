using RimWorld;
using Verse;

namespace Spearfishing;

// The spacer rebreather (gear tiers ticket 09), in the snorkel's slot.
[DefOf]
public static class RebreatherDefOf
{
    public static ThingDef Spearfishing_Rebreather;

    static RebreatherDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(RebreatherDefOf));
}
