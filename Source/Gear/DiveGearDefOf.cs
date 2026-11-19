using RimWorld;
using Verse;

namespace Spearfishing;

// The Spearfishing research and the medieval dive gear it unlocks (tickets 09, 10 and 17).
[DefOf]
public static class DiveGearDefOf
{
    public static StatDef Spearfishing_DiveSuccess;
    public static ResearchProjectDef Spearfishing_Spearfishing;
    public static ThingDef Spearfishing_SteelPoleSpear;
    public static ThingDef Spearfishing_GlassMask;
    public static ThingDef Spearfishing_BasicWetsuit;
    public static ThingDef Spearfishing_Snorkel;
    // The industrial low-volume mask (gear tiers ticket 03), after Spearfishing and Machining.
    public static ThingDef Spearfishing_LowVolumeMask;

    static DiveGearDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(DiveGearDefOf));
}
