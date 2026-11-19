using System;
using System.Collections.Generic;
using Verse;

namespace Spearfishing;

// Whether a pawn's current job keeps it in the water. Every 90 ticks, Waves sends any pawn standing still and undrafted in deep
// water ashore unless a registered check says otherwise. WavesBridge registers one check, which answers yes for a sea trip
// (spearfishing or snorkeling) or a job registered here. A job of the mod's own whose pawn stands still in deep water while it
// works, such as restoring sea floor, joins by adding its JobDef with Register at startup. Work that runs on vanilla job defs,
// such as building an artificial reef (ticket 02), can't list those defs without keeping every builder in the water, so it
// registers a check on the pawn's job instead. Every check is cheap and free of side effects, as Waves' API requires.
public static class StaysInWater
{
    private static readonly HashSet<JobDef> jobs = new();
    private static readonly List<Func<Pawn, bool>> checks = new();

    public static void Register(JobDef job)
    {
        if (job != null) jobs.Add(job);
    }

    public static void Register(Func<Pawn, bool> check)
    {
        if (check != null && !checks.Contains(check)) checks.Add(check);
    }

    public static bool Keeps(Pawn pawn)
    {
        JobDef def = pawn.CurJobDef;
        if (def == null) return false;
        if (jobs.Contains(def)) return true;
        for (int i = 0; i < checks.Count; i++)
            if (checks[i](pawn)) return true;
        return false;
    }
}
