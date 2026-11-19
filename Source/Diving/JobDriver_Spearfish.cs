using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace Spearfishing;

// A spearfishing work trip: the shared dive loop with its default exits and spot choice. Every catch roll adds a little recreation
// of the spearfishing type, so tolerance applies, and recreation doesn't fall while the diver is in the water, so every
// work trip ends a little up (ADR 0006). Snorkeling (JobDriver_Snorkel) is the recreation activity and gains its own way.
public class JobDriver_Spearfish : JobDriver_DiveTrip
{
    // Need_Joy skips its fall while it gained within the last few ticks. Holding its private last-gain tick at now keeps
    // recreation level in the water without adding any or raising tolerance. Null, with one warning, if RimWorld renames it.
    private static readonly AccessTools.FieldRef<Need_Joy, int> lastGainTick = ResolveLastGainTick();

    private static AccessTools.FieldRef<Need_Joy, int> ResolveLastGainTick()
    {
        try
        {
            return AccessTools.FieldRefAccess<Need_Joy, int>("lastGainTick");
        }
        catch (Exception e)
        {
            Log.Warning($"[Spearfishing] Recreation: work trips no longer hold recreation in the water because {e.GetType().Name}: {e.Message}. RimWorld may have changed; please report it."); // not translated
            return null;
        }
    }

    // Every toil of the trip, the swims there and home included, but only while the diver stands in water.
    protected override IEnumerable<Toil> MakeNewToils()
    {
        foreach (Toil toil in base.MakeNewToils())
        {
            toil.AddPreTickAction(HoldRecreationInWater);
            yield return toil;
        }
    }

    private void HoldRecreationInWater()
    {
        Need_Joy joy = pawn.needs?.joy;
        if (joy == null || lastGainTick == null || !pawn.Spawned || !pawn.Position.GetTerrain(Map).IsWater) return;
        lastGainTick(joy) = Find.TickManager.TicksGame;
    }

    protected override void OnCatchRoll(bool caught) =>
        pawn.needs?.joy?.GainJoy(DiveRules.WorkRecreationPerRoll, SpearfishingDefOf.Spearfishing_Swimming);
}
