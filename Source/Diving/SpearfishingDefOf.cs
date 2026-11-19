using RimWorld;
using Verse;

namespace Spearfishing;

[DefOf]
public static class SpearfishingDefOf
{
    public static StatDef Spearfishing_DivePower;
    public static StatDef Spearfishing_StringerCapacity;
    public static ThingDef Spearfishing_RawFish;
    public static ThingDef Spearfishing_PoleSpear;
    public static WorkTypeDef Spearfishing;
    public static JobDef Spearfishing_Spearfish;
    public static JoyKindDef Spearfishing_Swimming;

    static SpearfishingDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(SpearfishingDefOf));
}
