using System;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace Spearfishing;

// Keeps a pawn on one of the mod's jobs loadable without the mod (ADR 0009). RimWorld clears a job whose driver class is
// missing ("Cleaning up invalid job state"), but only if the job's def still exists: with the def missing too, ending the job
// throws, and the pawn keeps a job with no def, so it fails to spawn and throws every tick. So while a job tracker saves, a
// current job of ours is written with the vanilla Wait def, and its real def goes in an extra element of the tracker that only
// this patch reads back. Without the mod the job loads as Wait with no driver and is cleaned up as usual.
// If the target moves after a game update, this logs once and leaves vanilla saving alone.
public static class JobSaveSplit
{
    private const string RealDefLabel = "spearfishingJobDef";

    public static bool On { get; private set; }

    internal static void Initialize(Harmony harmony, string packageId)
    {
        ourPackageId = packageId;
        string missing;
        try
        {
            var expose = AccessTools.Method(typeof(Pawn_JobTracker), nameof(Pawn_JobTracker.ExposeData));
            missing = expose == null ? "Pawn_JobTracker.ExposeData was not found" : null; // not translated
            if (missing == null)
                harmony.Patch(expose, prefix: new HarmonyMethod(typeof(JobSaveSplit), nameof(BeforeExpose)),
                    finalizer: new HarmonyMethod(typeof(JobSaveSplit), nameof(AfterExpose)));
        }
        catch (Exception e)
        {
            missing = e.GetType().Name + ": " + e.Message;
        }
        On = missing == null;
        if (missing != null)
            Log.Warning($"[Spearfishing] Spearfishing jobs are saved as usual because {missing}. The mod still works, but removing it from a save could break a colonist who was on a spearfishing job."); // not translated
    }

    private static string ourPackageId;

    private static bool Ours(JobDef def) => def?.modContentPack != null && def.modContentPack.PackageId == ourPackageId;

    private static void BeforeExpose(Pawn_JobTracker __instance, out JobDef __state)
    {
        __state = null;
        var job = __instance.curJob;
        if (Scribe.mode != LoadSaveMode.Saving || job == null || !Ours(job.def)) return;
        __state = job.def;
        job.def = JobDefOf.Wait;
    }

    // A finalizer, so the job gets its def back even if saving throws.
    private static Exception AfterExpose(Pawn_JobTracker __instance, JobDef __state, Exception __exception)
    {
        if (Scribe.mode == LoadSaveMode.Saving && __state != null)
        {
            __instance.curJob.def = __state;
            if (__exception == null)
            {
                JobDef real = __state;
                Scribe_Defs.Look(ref real, RealDefLabel);
            }
        }
        else if (Scribe.mode == LoadSaveMode.LoadingVars && __exception == null)
        {
            JobDef real = null;
            Scribe_Defs.Look(ref real, RealDefLabel);
            if (real != null && __instance.curJob != null) __instance.curJob.def = real;
        }
        return __exception;
    }
}
