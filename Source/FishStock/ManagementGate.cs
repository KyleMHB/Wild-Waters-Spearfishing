using System;
using System.Collections.Generic;
using Verse;

namespace Spearfishing;

// What happens to each map when fish stock management is switched (ADR 0015, revised 2026-11-18): the recovery buildings and
// jobs exist only with it on. Each recovery feature adds one line below: what it does to a map when management goes off, and
// what it does when it is on. Both run on every map when the setting changes in a game, and again whenever a map finishes
// loading or generating, so a switch made at the main menu still reaches a save loaded after it. So each action must be
// safe to run again on a map already in that state. Features that only need to stop and resume (spreading, reef-forming,
// the hatchery's work) read FishStockManagement.On where they run instead, and need no line here.
public static class ManagementGate
{
    private static readonly List<Action<Map>> offActions = new()
    {
        // Ticket 03: restoration designations are removed. Restored floor stays and its spreading pauses (MapComponent_FishStock).
        HabitatRestoration.RemoveDesignations,
        // Ticket 04: blueprints and frames of management-only buildings (the hatchery) are cancelled with vanilla refunds. A
        // built hatchery stays and stands idle, and its architect entry hides (ManagementOnly).
        ManagementOnly.CancelBlueprintsAndFrames,
        // Threat events ticket 01: every active outbreak ends, each kind through its own End.
        ThreatEvents.EndDisallowed,
    };

    private static readonly List<Action<Map>> onActions = new()
    {
        // Threat events ticket 01: with management on, an outbreak whose own event switch is off still ends, which reaches a
        // save loaded after the switch was turned off at the main menu.
        ThreatEvents.EndDisallowed,
    };

    // Sets the setting and, if it changed, applies the switch to every map of the game in play. The settings window and
    // developer tests set it through here.
    public static void Set(bool on)
    {
        SpearfishingSettings settings = SpearfishingMod.Settings;
        if (settings == null || settings.fishStockManagement == on) return;
        settings.fishStockManagement = on;
        ApplyToAllMaps();
    }

    public static void ApplyToAllMaps()
    {
        if (Current.ProgramState != ProgramState.Playing || Find.Maps == null) return;
        foreach (Map map in Find.Maps) Apply(map);
    }

    public static void Apply(Map map)
    {
        foreach (Action<Map> action in FishStockManagement.On ? onActions : offActions) action(map);
    }
}
