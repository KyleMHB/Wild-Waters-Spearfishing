using System;
using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace Spearfishing;

// Keeps spearfishing zones out of the zone manager's saved list (ADR 0009). Without the mod, RimWorld can't load a zone whose
// class is missing: it puts null in the zone list, and the zone manager's own load then throws and the map loses its whole
// zone manager, stockpiles included. So while the zone manager saves, spearfishing zones are taken out of its list, and
// MapComponent_FishStock saves them instead and puts them back on load. During play they are ordinary zones.
// If a game update moves either target, this logs once and leaves vanilla saving alone: the zones still save and load with
// the mod, but removing the mod is no longer safe.
public static class ZoneSaveSplit
{
    private static Action<ZoneManager, Zone, IntVec3> addZoneGridCell;

    public static bool On { get; private set; }

    internal static void Initialize(Harmony harmony)
    {
        string missing;
        try
        {
            var expose = AccessTools.Method(typeof(ZoneManager), nameof(ZoneManager.ExposeData));
            var add = AccessTools.Method(typeof(ZoneManager), "AddZoneGridCell", new[] { typeof(Zone), typeof(IntVec3) });
            missing = expose == null ? "ZoneManager.ExposeData was not found" // not translated
                : add == null ? "ZoneManager.AddZoneGridCell(Zone, IntVec3) was not found" // not translated
                : null;
            if (missing == null)
            {
                addZoneGridCell = AccessTools.MethodDelegate<Action<ZoneManager, Zone, IntVec3>>(add);
                harmony.Patch(expose, prefix: new HarmonyMethod(typeof(ZoneSaveSplit), nameof(BeforeExpose)),
                    finalizer: new HarmonyMethod(typeof(ZoneSaveSplit), nameof(AfterExpose)));
            }
        }
        catch (Exception e)
        {
            missing = e.GetType().Name + ": " + e.Message;
        }
        On = missing == null;
        if (missing != null)
            Log.Warning($"[Spearfishing] Spearfishing zones are saved in the zone manager as usual because {missing}. The mod still works, but removing it from a save would lose that map's zones."); // not translated
    }

    // While saving, the list holds no spearfishing zones; the whole list is kept to put back in its own order.
    private static void BeforeExpose(ZoneManager __instance, out List<Zone> __state)
    {
        __state = null;
        if (Scribe.mode != LoadSaveMode.Saving) return;
        var zones = __instance.AllZones;
        if (!zones.Exists(z => z is Zone_Spearfishing)) return;
        __state = new List<Zone>(zones);
        zones.RemoveAll(z => z is Zone_Spearfishing);
    }

    // A finalizer, so a save that throws still gets its zones back.
    private static Exception AfterExpose(ZoneManager __instance, List<Zone> __state, Exception __exception)
    {
        if (__state != null)
        {
            __instance.AllZones.Clear();
            __instance.AllZones.AddRange(__state);
        }
        return __exception;
    }

    // The zones this map saves itself; none while the split is off, as they are then in the zone manager's list.
    public static List<Zone_Spearfishing> ToSave(Map map) =>
        On && map.zoneManager != null ? map.zoneManager.AllZones.FindAll(z => z is Zone_Spearfishing).ConvertAll(z => (Zone_Spearfishing)z) : null;

    // Puts zones loaded by MapComponent_FishStock back into the zone manager, as its own load does for vanilla zones: listed,
    // linked and in the zone grid. The zone manager loads before map components, so it is ready here.
    public static void Restore(Map map, List<Zone_Spearfishing> zones)
    {
        if (zones == null || map.zoneManager == null || addZoneGridCell == null) return;
        var manager = map.zoneManager;
        foreach (var zone in zones)
        {
            if (zone == null || manager.AllZones.Contains(zone)) continue;
            manager.AllZones.Add(zone);
            zone.zoneManager = manager;
            foreach (IntVec3 cell in zone.Cells) addZoneGridCell(manager, zone, cell);
        }
    }
}
