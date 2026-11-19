using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace Spearfishing;

// Marks a building that exists only with fish stock management on (ADR 0015 revised): the hatchery, and the artificial reef
// when it comes. With management off such a building leaves the architect menu, can't be placed (copy included), and its
// blueprints and frames are cancelled; a built one stays and reads FishStockManagement.On itself.
public class ManagementOnly : DefModExtension
{
    public static bool Applies(BuildableDef def) => def != null && def.HasModExtension<ManagementOnly>();

    // Cancels every blueprint and unfinished frame of a management-only building on the map, refunding a frame's materials
    // as vanilla's cancel order does. Safe to run again: a second run finds nothing.
    public static void CancelBlueprintsAndFrames(Map map)
    {
        var doomed = new List<Thing>();
        foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Blueprint))
            if (Applies(t.def.entityDefToBuild)) doomed.Add(t);
        foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingFrame))
            if (Applies(t.def.entityDefToBuild)) doomed.Add(t);
        foreach (Thing t in doomed)
            if (!t.Destroyed) t.Destroy(DestroyMode.Cancel);
    }
}

// Refuses to place a management-only building while fish stock management is off; this also covers the copy gizmo.
public class PlaceWorker_ManagementOn : PlaceWorker
{
    public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null) =>
        FishStockManagement.On ? AcceptanceReport.WasAccepted : new AcceptanceReport("Spearfishing_NeedsFishStockManagement".Translate());
}

// Hides a management-only building's architect entry while fish stock management is off.
[HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.Visible), MethodType.Getter)]
public static class Patch_DesignatorBuild_Visible
{
    public static void Postfix(Designator_Build __instance, ref bool __result)
    {
        if (__result && !FishStockManagement.On && ManagementOnly.Applies(__instance.PlacingDef)) __result = false;
    }
}
