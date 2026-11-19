using System.Collections.Generic;
using RimWorld;
using Verse;

namespace Spearfishing;

[DefOf]
public static class RestorationDefOf
{
    public static DesignationDef Spearfishing_RestoreSeaFloor;
    public static JobDef Spearfishing_RestoreSeaFloorJob;

    static RestorationDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(RestorationDefOf));
}

// The restoring diver stands still in deep water while it works, so Waves must not send it ashore (StaysInWater).
[StaticConstructorOnStartup]
public static class RestorationStartup
{
    static RestorationStartup() => StaysInWater.Register(RestorationDefOf.Spearfishing_RestoreSeaFloorJob);
}

// Habitat restoration (fish recovery ticket 03): the player marks bare sea floor, and a diver restores a marked cell next to
// reef or kelp by moving cuttings onto it, giving it that neighbour's kind. Restored cells then spread on their own
// (RestorationSpread, run by MapComponent_FishStock). Only with fish stock management on (ADR 0015 revised).
//
// The marks are vanilla cell designations, saved by the designation manager. Without the mod their def is missing, so each
// one logs a one-time "Could not load reference" error on load and the designation manager drops it (RimWorld 1.7.5013,
// DesignationManager.ExposeData), like the gear and fish the review checklist already lists.
public static class HabitatRestoration
{
    // Bare sea floor: ocean terrain whose reef grid shows neither reef nor kelp. Lakes and rivers never hold reef (ADR 0008).
    public static bool IsBareSeaFloor(Map map, IntVec3 cell) =>
        cell.InBounds(map) && WavesBridge.IsSea(cell.GetTerrain(map)) && MapComponent_FishStock.Of(map).MarkAt(cell) == FloorMark.Bare;

    public static bool IsMarked(Map map, IntVec3 cell) =>
        map.designationManager.DesignationAt(cell, RestorationDefOf.Spearfishing_RestoreSeaFloor) != null;

    // A marked cell a diver or a spread can restore now: still bare sea floor.
    public static bool CanTake(Map map, IntVec3 cell) => IsBareSeaFloor(map, cell) && IsMarked(map, cell);

    // The kind a diver gives this cell: that of a reef or kelp cell beside it (orthogonally), picked at random when it has
    // more than one; Bare when it has none, and the cell waits. A map with no kelp has only reef to copy.
    public static FloorMark SourceKind(Map map, IntVec3 cell)
    {
        var floor = MapComponent_FishStock.Of(map);
        var kinds = new List<FloorMark>(4);
        foreach (IntVec3 offset in GenAdj.CardinalDirections)
        {
            IntVec3 n = cell + offset;
            if (!n.InBounds(map)) continue;
            FloorMark mark = floor.LiveMarkAt(n);
            if (mark != FloorMark.Bare) kinds.Add(mark);
        }
        return kinds.Count == 0 ? FloorMark.Bare : kinds.RandomElement();
    }

    public static bool HasSource(Map map, IntVec3 cell)
    {
        var floor = MapComponent_FishStock.Of(map);
        foreach (IntVec3 offset in GenAdj.CardinalDirections)
        {
            IntVec3 n = cell + offset;
            if (n.InBounds(map) && floor.LiveMarkAt(n) != FloorMark.Bare) return true;
        }
        return false;
    }

    // The management gate's off action: every restoration mark goes. Restored floor stays.
    public static void RemoveDesignations(Map map) => map.designationManager?.RemoveAllDesignationsOfDef(RestorationDefOf.Spearfishing_RestoreSeaFloor);
}
