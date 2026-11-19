using RimWorld;
using Verse;

namespace Spearfishing;

// The industrial dry snorkel (gear tiers ticket 04).
[DefOf]
public static class DrySnorkelDefOf
{
    public static ThingDef Spearfishing_DrySnorkel;

    static DrySnorkelDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(DrySnorkelDefOf));
}
