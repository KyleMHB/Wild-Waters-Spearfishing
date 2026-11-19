using RimWorld;

namespace Spearfishing;

// The surface rest factor (gear tiers ticket 04): the share of the usual rest a diver takes at the surface after each dive.
[DefOf]
public static class SurfaceRestDefOf
{
    public static StatDef Spearfishing_SurfaceRest;

    static SurfaceRestDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(SurfaceRestDefOf));
}
