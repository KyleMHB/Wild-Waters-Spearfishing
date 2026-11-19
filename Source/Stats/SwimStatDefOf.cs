using RimWorld;

namespace Spearfishing;

[DefOf]
public static class SwimStatDefOf
{
    public static StatDef Spearfishing_SwimSpeed;

    static SwimStatDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(SwimStatDefOf));
}
