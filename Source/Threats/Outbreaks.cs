using System.Collections.Generic;
using Verse;

namespace Spearfishing;

// One active outbreak on a map: its kind, a cell in the water it struck and when it started. The water is a saved cell, never
// a body index, because bodies are found again and renumbered after every terrain change (see FryRelease).
public sealed class Outbreak : IExposable
{
    public ThreatKind Kind;
    public IntVec3 Cell = IntVec3.Invalid;
    public int StartTick;

    public void ExposeData()
    {
        Scribe_Values.Look(ref Kind, "kind");
        Scribe_Values.Look(ref Cell, "cell", IntVec3.Invalid);
        Scribe_Values.Look(ref StartTick, "startTick");
    }
}

// A map's outbreak registry: at most one active outbreak of each kind (an event never fires while its kind is active there).
// Owned and saved by MapComponent_FishStock, so a save without the mod drops it with that component and gains no second
// missing class. Start and End call the kind's ThreatEvent, which holds what the outbreak does to the water.
public sealed class Outbreaks
{
    private readonly Map map;
    private List<Outbreak> active = new();

    public Outbreaks(Map map) => this.map = map;

    public int Count => active.Count;

    public bool IsActive(ThreatKind kind) => Get(kind) != null;

    public Outbreak Get(ThreatKind kind)
    {
        foreach (Outbreak o in active)
            if (o.Kind == kind)
                return o;
        return null;
    }

    // Starts an outbreak of `kind` in the water at `cell`. Refused while one of that kind is active, or when the kind's own
    // Start declines (it found nothing to strike after all). Returns the outbreak, or null.
    public Outbreak Start(ThreatKind kind, IntVec3 cell)
    {
        if (IsActive(kind)) return null;
        var outbreak = new Outbreak { Kind = kind, Cell = cell, StartTick = Find.TickManager.TicksGame };
        if (!ThreatEvents.For(kind).Start(map, outbreak)) return null;
        active.Add(outbreak);
        return outbreak;
    }

    // Ends the active outbreak of `kind`, if any: it leaves the registry first, then the kind undoes its effect. Safe to call
    // when none is active. Returns whether one ended.
    public bool End(ThreatKind kind)
    {
        Outbreak outbreak = Get(kind);
        if (outbreak == null) return false;
        active.Remove(outbreak);
        ThreatEvents.For(kind).End(map, outbreak);
        return true;
    }

    // Written only while some outbreak is active, so a quiet map saves nothing.
    public void ExposeData()
    {
        if (Scribe.mode == LoadSaveMode.Saving && active.Count == 0) return;
        Scribe_Collections.Look(ref active, "threatOutbreaks", LookMode.Deep);
        // A save with no outbreaks has no entry, which loads as null.
        active ??= new List<Outbreak>();
        if (Scribe.mode == LoadSaveMode.PostLoadInit) active.RemoveAll(o => o == null);
    }
}
