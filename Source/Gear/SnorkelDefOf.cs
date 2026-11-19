using RimWorld;
using Verse;

namespace Spearfishing;

// Snorkeling (ticket 17): its job and the two stats the snorkel raises. The snorkel itself is in DiveGearDefOf.
[DefOf]
public static class SnorkelDefOf
{
    public static JobDef Spearfishing_Snorkeling;
    public static StatDef Spearfishing_SnorkelingEnjoyment;
    public static StatDef Spearfishing_SnorkelingSession;

    static SnorkelDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(SnorkelDefOf));
}
