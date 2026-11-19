using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace Spearfishing;

// Marks apparel as a buoy: its wearer stays afloat when exhausted in deep water. A def extension rather than a def check, so
// later buoys (the foam buoy) only need the marker.
public class BuoyExtension : DefModExtension
{
}

[DefOf]
public static class BuoyDefOf
{
    public static JobDef Spearfishing_FloatHome;

    static BuoyDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(BuoyDefOf));
}

// Stay-afloat (spec "Waves bridge module", story 39). The bridge registers KeepsAfloat with Waves, which then neither knocks
// out an exhausted wearer in deep water nor lets a downed one drown. Waves doesn't say when it spared someone, so every 60
// ticks CheckKeptAfloat looks for wearers exhausted in deep water. Such a pawn makes a slow swim to dry land that their own
// needs can't interrupt; drafting still can, and the next check after they are undrafted sends them home again.
public static class Buoy
{
    // How far the float-home shore search spreads through water before giving up.
    private const int ShoreSearchCells = 20000;
    // Waves knocks a swimmer out at this Rest or below, checking every 60 ticks; this check runs as often.
    private const float ExhaustedRest = 0.01f;
    private const int CheckInterval = 60;

    // Asked by Waves for each swimmer in deep water, so it stays cheap and changes nothing.
    public static bool KeepsAfloat(Pawn pawn)
    {
        var worn = pawn.apparel?.WornApparel;
        if (worn == null) return false;
        for (int i = 0; i < worn.Count; i++)
            if (worn[i].def.HasModExtension<BuoyExtension>()) return true;
        return false;
    }

    public static bool FloatingHome(Pawn pawn) => pawn.jobs?.curDriver is JobDriver_FloatHome;

    // Runs after each map tick, so outside any Waves pass: a buoy wearer whose Rest has run out on a deep-water swim cell, whom
    // Waves is now keeping afloat, starts the swim home. Off while Waves' swim limits or the stay-afloat feature are off, so
    // nothing pre-empts Waves' own knockout when it still applies.
    [HarmonyPatch(typeof(Map), nameof(Map.MapPostTick))]
    private static class CheckKeptAfloat
    {
        private static void Postfix(Map __instance)
        {
            if (Find.TickManager.TicksGame % CheckInterval != 0 || !WavesBridge.StayAfloatOn || !WavesBridge.SwimLimitsOn) return;
            var pawns = __instance.mapPawns.AllPawnsSpawned;
            for (int i = pawns.Count - 1; i >= 0; i--)
            {
                Pawn pawn = pawns[i];
                if (pawn.needs?.rest is not { CurLevel: <= ExhaustedRest } || !KeepsAfloat(pawn)) continue;
                if (WavesBridge.IsDeepSwimCell(__instance, pawn.Position)) Notify_KeptAfloat(pawn);
            }
        }
    }

    // Called for a pawn Waves is keeping afloat although exhausted. A pawn already on the way,
    // drafted or downed for another reason is left alone. With no dry land in reach there is nothing to swim to: the pawn
    // stays afloat where they are, and Waves' own idle check keeps trying to send them ashore.
    internal static void Notify_KeptAfloat(Pawn pawn)
    {
        if (!pawn.Spawned || pawn.Dead || pawn.Downed || pawn.Drafted || FloatingHome(pawn)) return;
        IntVec3 shore = DryLandNear(pawn);
        if (!shore.IsValid) return;
        Job job = JobMaker.MakeJob(BuoyDefOf.Spearfishing_FloatHome, shore);
        job.locomotionUrgency = LocomotionUrgency.Walk;
        // Ends a dive trip, whose catch goes into the inventory and comes home with them.
        pawn.jobs.StartJob(job, JobCondition.InterruptForced);
        if (FloatingHome(pawn) && PawnUtility.ShouldSendNotificationAbout(pawn))
            Messages.Message("Spearfishing_FloatingHome".Translate(pawn.Named("PAWN")), pawn, MessageTypeDefOf.NegativeEvent);
    }

    // The nearest dry land the pawn can swim to. Unlike a dive trip's shore it ignores forbidden cells and allowed areas: a
    // floating pawn must reach land even when the player's area leaves out the beach, or they would float at sea forever.
    public static IntVec3 DryLandNear(Pawn pawn)
    {
        Map map = pawn.Map;
        IntVec3 shore = IntVec3.Invalid;
        map.floodFiller.FloodFill(pawn.Position, c => c.Walkable(map), c =>
        {
            if (!SpearfishingUtility.IsDryLand(map, c)) return false;
            shore = c;
            return true;
        }, ShoreSearchCells);
        return shore;
    }

    // Only the player (drafting or a direct order) or being downed may replace the swim home. Everything else that starts a
    // job is the pawn's own: needs, think-tree overrides, Waves' idle swimmers being sent ashore.
    private static bool MayReplaceFloatHome(Pawn pawn, Job newJob) => pawn.Drafted || pawn.Downed || pawn.Dead || newJob.playerForced;

    [HarmonyPatch(typeof(Pawn_JobTracker), nameof(Pawn_JobTracker.StartJob))]
    private static class KeepSwimmingHome
    {
        // Outside a float home this is one type test per job start.
        private static bool Prefix(Pawn_JobTracker __instance, Job newJob) =>
            __instance.curDriver is not JobDriver_FloatHome driver || MayReplaceFloatHome(driver.pawn, newJob);
    }

    // Vanilla's collapse from exhaustion runs from Need_Rest on its own schedule and posts "fell asleep" even if the job it
    // starts is refused, so it is turned off at its source while the pawn swims home.
    [HarmonyPatch(typeof(Need_Rest), "CanInvoluntarilySleep")]
    private static class NoCollapseWhileFloating
    {
        private static void Postfix(Pawn pawn, ref bool __result)
        {
            if (__result && FloatingHome(pawn)) __result = false;
        }
    }
}
