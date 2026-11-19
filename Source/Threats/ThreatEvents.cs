using Verse;

namespace Spearfishing;

// The threat events and their switches (ADR 0015, revised for threat events). Each kind has one ThreatEvent; a new kind adds
// a ThreatKind value, a subclass and a line in For.
public static class ThreatEvents
{
    public static readonly ThreatEvent Urchins = new UrchinThreat();
    public static readonly ThreatEvent InvasivePredators = new PredatorThreat();

    public static readonly ThreatEvent[] All = { Urchins, InvasivePredators };

    public static ThreatEvent For(ThreatKind kind) => kind == ThreatKind.Urchins ? Urchins : InvasivePredators;

    public static Outbreaks Of(Map map) => MapComponent_FishStock.Of(map)?.Outbreaks;

    // Whether an outbreak of `kind` may start on the map now, and where: its switch and fish stock management on, none of
    // that kind active there, and water it can strike. The incident worker and the developer tests both ask this.
    public static bool CanStart(ThreatKind kind, Map map, out IntVec3 cell)
    {
        cell = IntVec3.Invalid;
        ThreatEvent threat = For(kind);
        Outbreaks outbreaks = map == null ? null : Of(map);
        return outbreaks != null && threat.Allowed && !outbreaks.IsActive(kind) && threat.TryFindTarget(map, out cell);
    }

    // Ends every outbreak whose kind is no longer allowed: its switch or fish stock management is off. Turning either back on
    // brings nothing back. ManagementGate runs this on every map when management is switched and whenever a map finishes
    // loading, so a switch made at the main menu reaches a save loaded after it; a kind's own switch runs it through Set.
    // Safe to run again.
    public static void EndDisallowed(Map map)
    {
        Outbreaks outbreaks = Of(map);
        if (outbreaks == null || outbreaks.Count == 0) return;
        foreach (ThreatEvent threat in All)
            if (!threat.Allowed)
                outbreaks.End(threat.Kind);
    }

    // Sets a kind's switch and, if it changed, ends that kind's outbreaks on every map of the game in play. The settings
    // window and developer tests set it through here.
    public static void Set(ThreatKind kind, bool on)
    {
        SpearfishingSettings settings = SpearfishingMod.Settings;
        if (settings == null || For(kind).SwitchOn == on) return;
        if (kind == ThreatKind.Urchins) settings.urchinEvents = on;
        else settings.invasivePredatorEvents = on;
        if (Current.ProgramState != ProgramState.Playing || Find.Maps == null) return;
        foreach (Map map in Find.Maps) EndDisallowed(map);
    }
}
