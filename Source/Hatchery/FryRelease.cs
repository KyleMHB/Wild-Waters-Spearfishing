using RimWorld;
using Verse;
using Verse.AI;

namespace Spearfishing;

// Where fry go and what releasing them does (fish recovery ticket 04, ADR 0016). A hatchery's choice of water is a saved
// cell, never a body index: bodies are found again after every terrain change and renumbered, so the body is looked up from
// the cell each time. If the cell stops being fishing water (landfill, a bridge), the nearest fishing water to it is taken.
public static class FryRelease
{
    // The nearest cell of fishing water to `from`, or Invalid when the map has none.
    public static IntVec3 NearestFishingWater(Map map, IntVec3 from)
    {
        if (map == null || !from.IsValid) return IntVec3.Invalid;
        MapComponent_FishStock fishStock = MapComponent_FishStock.Of(map);
        int radial = GenRadial.RadialPattern.Length;
        for (int i = 0; i < radial; i++)
        {
            IntVec3 cell = from + GenRadial.RadialPattern[i];
            if (cell.InBounds(map) && fishStock.BodyAt(cell) >= 0) return cell;
        }
        // Past the radial pattern: one pass over the map.
        IntVec3 best = IntVec3.Invalid;
        int bestDistance = int.MaxValue;
        foreach (IntVec3 cell in map.AllCells)
        {
            int distance = (cell - from).LengthHorizontalSquared;
            if (distance < bestDistance && fishStock.BodyAt(cell) >= 0)
            {
                best = cell;
                bestDistance = distance;
            }
        }
        return best;
    }

    // `cell` while it is fishing water; otherwise the nearest fishing water to it (or to `fallbackFrom` when it was never set).
    public static IntVec3 Resolve(Map map, IntVec3 cell, IntVec3 fallbackFrom)
    {
        if (map == null) return cell;
        if (cell.IsValid && cell.InBounds(map) && MapComponent_FishStock.Of(map).BodyAt(cell) >= 0) return cell;
        return NearestFishingWater(map, cell.IsValid ? cell : fallbackFrom);
    }

    // "sea", "lake" or "river" for the water at a cell, as the release message names it.
    public static string WaterLabel(Map map, IntVec3 cell)
    {
        TerrainDef terrain = cell.IsValid && cell.InBounds(map) ? cell.GetTerrain(map) : null;
        if (WavesBridge.IsSea(terrain)) return "Spearfishing_WaterSea".Translate();
        if (terrain == TerrainDefOf.WaterMovingChestDeep) return "Spearfishing_WaterRiver".Translate();
        return "Spearfishing_WaterLake".Translate();
    }

    // A cell the pawn can stand on and reach, in the body of water at `target` or beside it on a cardinal side, nearest to
    // `target`: wading water of the sea, or the bank of a lake or river.
    public static bool TryFindReleaseCell(Pawn pawn, IntVec3 target, out IntVec3 found)
    {
        found = IntVec3.Invalid;
        Map map = pawn.Map;
        if (map == null || !target.IsValid || !target.InBounds(map)) return false;
        MapComponent_FishStock fishStock = MapComponent_FishStock.Of(map);
        int body = fishStock.BodyAt(target);
        if (body < 0) return false;
        bool Fits(IntVec3 cell)
        {
            if (!cell.InBounds(map) || !cell.Standable(map) || cell.IsForbidden(pawn)) return false;
            if (fishStock.BodyAt(cell) != body)
            {
                bool beside = false;
                foreach (IntVec3 side in GenAdj.CardinalDirections)
                    if (fishStock.BodyAt(cell + side) == body)
                    {
                        beside = true;
                        break;
                    }
                if (!beside) return false;
            }
            return pawn.CanReach(cell, PathEndMode.OnCell, Danger.Some);
        }
        int radial = GenRadial.RadialPattern.Length;
        for (int i = 0; i < radial; i++)
        {
            IntVec3 cell = target + GenRadial.RadialPattern[i];
            if (!Fits(cell)) continue;
            found = cell;
            return true;
        }
        int bestDistance = int.MaxValue;
        foreach (IntVec3 cell in map.AllCells)
        {
            int distance = (cell - target).LengthHorizontalSquared;
            if (distance >= bestDistance || !Fits(cell)) continue;
            found = cell;
            bestDistance = distance;
        }
        return found.IsValid;
    }

    // Releases a pail's fry into the body of water at its target: the stock rises by the fry, never past capacity, and with
    // Odyssey its population for that water rises by the same share. The pail is used up and a message reports the fish
    // added. Returns the fish added, or -1 when the target is no longer fishing water (the pail is kept).
    public static float Release(FryBatch pail)
    {
        Map map = pail.MapHeld;
        if (map == null) return -1f;
        IntVec3 target = pail.Target;
        MapComponent_FishStock fishStock = MapComponent_FishStock.Of(map);
        int body = fishStock.BodyAt(target);
        if (body < 0) return -1f;
        float added = fishStock.Stock.Release(body, pail.Fish);
        OdysseyFish.NotifyReleased(map, target, added);
        int shown = UnityEngine.Mathf.RoundToInt(added);
        int lost = pail.Fish - shown;
        string water = WaterLabel(map, target);
        string text = lost > 0
            ? "Spearfishing_FryReleasedCapped".Translate(shown, water, lost)
            : "Spearfishing_FryReleased".Translate(shown, water);
        Messages.Message(text, new LookTargets(target, map), MessageTypeDefOf.PositiveEvent);
        pail.Destroy();
        return added;
    }
}
