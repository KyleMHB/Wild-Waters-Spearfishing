using RimWorld;
using Verse;

namespace Spearfishing;

[DefOf]
public static class ReefDefOf
{
    // Its genStep holds the reef and kelp tuning from Defs/MapGeneration/GenStep_Reef.xml.
    public static GenStepDef Spearfishing_Reef;

    static ReefDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(ReefDefOf));
}
