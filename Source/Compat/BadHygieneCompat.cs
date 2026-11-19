using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace Spearfishing;

// Every contact with Dubs Bad Hygiene lives here. With DBH loaded (full, or Lite, which runs on the full mod's assembly), a
// diver in the water on a spearfishing trip gets washed at about the rate DBH washes a pawn in open water, so a day in the
// sea counts as a wash. Without DBH nothing here does anything, and Spearfishing never requires it.
//
// DBH is reached only by def name and reflection, never a compile-time reference. As with a Waves bridge feature, if DBH's
// need or members are missing (a DBH update renamed them), this logs one warning and turns off; trips carry on unchanged.
public static class BadHygieneCompat
{
    private const string FullPackageId = "Dubwise.DubsBadHygiene", LitePackageId = "Dubwise.DubsBadHygiene.Lite";

    // DBH's open-water wash (its washAtCell job) raises Hygiene by 0.001 every tick, in 1.6 and 1.7 alike.
    private const float WashPerTick = 0.001f;

    private static bool resolved, available;
    private static NeedDef hygiene;
    private static MethodInfo clean;
    private static readonly object[] cleanArgs = { WashPerTick };

    // Whether DBH is loaded and its Hygiene need was found; false without DBH or once the feature turned off.
    public static bool Active
    {
        get
        {
            if (!resolved) Resolve();
            return available;
        }
    }

    // One tick of washing for a diver in the water. Called every tick; does nothing without DBH, or for a pawn with no
    // Hygiene need (DBH exempts some bodies and non-humanlikes).
    public static void WashTick(Pawn pawn)
    {
        if (!Active) return;
        Need need = pawn.needs?.TryGetNeed(hygiene);
        if (need == null) return;
        try
        {
            // DBH's own clean(float), not CurLevel: it also pauses the need's fall and shows the rising arrow, as a wash does.
            clean.Invoke(need, cleanArgs);
        }
        catch (Exception e)
        {
            TurnOff((e as TargetInvocationException)?.InnerException ?? e);
        }
    }

    private static void Resolve()
    {
        resolved = true;
        if (!ModsConfig.IsActive(FullPackageId) && !ModsConfig.IsActive(LitePackageId)) return;
        string missing;
        try
        {
            missing = Lookup();
        }
        catch (Exception e)
        {
            missing = e.GetType().Name + ": " + e.Message;
        }
        available = missing == null;
        // A warning, not an error: trips keep working without the wash. Not translated (developer text).
        if (missing != null)
            Log.Warning($"[Spearfishing] Dubs Bad Hygiene: washing on dives is turned off because {missing}. Dubs Bad Hygiene may have changed; please report it."); // not translated
    }

    // Returns null when everything was found, or what is missing.
    private static string Lookup()
    {
        hygiene = DefDatabase<NeedDef>.GetNamedSilentFail("Hygiene");
        if (hygiene == null) return "the Hygiene need def is missing"; // not translated
        Type needClass = hygiene.needClass;
        if (needClass == null || !typeof(Need).IsAssignableFrom(needClass)) return "the Hygiene need has no need class"; // not translated
        clean = AccessTools.Method(needClass, "clean", new[] { typeof(float) });
        if (clean == null || clean.IsStatic) return $"{needClass.FullName}.clean(float) is missing"; // not translated
        return null;
    }

    private static void TurnOff(Exception e)
    {
        available = false;
        Log.Warning($"[Spearfishing] Dubs Bad Hygiene: washing on dives is turned off because {e.GetType().Name}: {e.Message}. Dubs Bad Hygiene may have changed; please report it."); // not translated
    }
}
