using RimWorld;
using Verse;
using Verse.AI;

namespace Spearfishing;

[DefOf]
public static class ArtificialReefDefOf
{
    public static ThingDef Spearfishing_ArtificialReef;

    static ArtificialReefDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(ArtificialReefDefOf));
}

// The artificial reef (fish recovery ticket 02, ADR 0015 revised, ADR 0016): a steel frame a constructor sinks on bare sea floor,
// which turns its cell to reef after about a season (CompArtificialReef) and never spreads. It exists only with fish stock
// management on: its def carries the ManagementOnly mark, which hides it from the architect menu, refuses placing and cancels
// its blueprints and frames while management is off; a built one pauses on its own (CompArtificialReef).
//
// Removal (ADR 0009 pattern): the building, its blueprints and frames are vanilla classes with this mod's defs, so a save
// without the mod logs one missing-def error for each and drops them, like the gear and raw fish; the cell it already turned
// to reef is in the reef grid, which leaves with MapComponent_FishStock.
public static class ArtificialReef
{
    public static ThingDef Def => ArtificialReefDefOf.Spearfishing_ArtificialReef;

    // Where one may go: bare sea floor (ocean terrain whose reef grid shows neither reef nor kelp). Lakes and rivers never hold
    // reef (ADR 0008). Fish stock management is checked apart, through the ManagementOnly mark on the def.
    public static AcceptanceReport CanPlaceAt(Map map, IntVec3 cell)
    {
        if (!WavesBridge.IsSea(cell.GetTerrain(map))) return "Spearfishing_ArtificialReefRefused_NotSea".Translate();
        if (MapComponent_FishStock.Of(map).MarkAt(cell) != FloorMark.Bare) return "Spearfishing_ArtificialReefRefused_NotBare".Translate();
        return AcceptanceReport.WasAccepted;
    }

    // Whether a pawn's current job is work on an artificial reef: delivering steel to it, building its frame or taking it down.
    // Waves sends any pawn standing still in deep water ashore, so a constructor at a reef out at sea must be kept there.
    public static bool KeepsBuilderInWater(Pawn pawn)
    {
        Job job = pawn.CurJob;
        return job != null && (IsReefWork(job.targetA.Thing) || IsReefWork(job.targetB.Thing));
    }

    private static bool IsReefWork(Thing thing) => thing != null && (thing.def == Def || thing.def.entityDefToBuild == Def);
}

// A constructor working on a reef out at sea stands still in deep water, so Waves must not send it ashore (StaysInWater). The
// work runs on vanilla job defs, so the reef registers a check on the job's target rather than the defs.
[StaticConstructorOnStartup]
public static class ArtificialReefStartup
{
    static ArtificialReefStartup() => StaysInWater.Register(ArtificialReef.KeepsBuilderInWater);
}

public class PlaceWorker_ArtificialReef : PlaceWorker
{
    public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null) =>
        ArtificialReef.CanPlaceAt(map, loc);
}
