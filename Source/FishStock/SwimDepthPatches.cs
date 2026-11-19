using HarmonyLib;
using Verse;

namespace Spearfishing;

// Every terrain change on a map (laying or removing terrain, foundations, temporary terrain such as ice) passes through
// this one method, so the swim depth grid only needs to hear about it here. Setting a flag is all it does.
[HarmonyPatch(typeof(TerrainGrid), "DoTerrainChangedEffects")]
internal static class Patch_TerrainGrid_DoTerrainChangedEffects
{
    private static void Postfix(Map ___map) => ___map?.GetComponent<MapComponent_FishStock>()?.Notify_TerrainChanged();
}
