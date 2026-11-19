using System.Collections.Generic;
using RimWorld;
using Verse;

namespace Spearfishing;

// The urchin barren of one map (threat events ticket 02, ADR 0017), kept beside the reef grid. A barren or recovering cell keeps
// its reef or kelp mark in the grid, so the mark comes back when it recovers and a save without the mod still holds the reef;
// meanwhile the cell counts as bare floor for the reef share, the catch chance and the overlays (LiveMarkAt). Barren cells draw
// the approved barren look (SectionLayer_UrchinBarren); recovering cells draw nothing, as bare sea floor.
//
// Schedule: the hourly tick advances the barren while fish stock management is on (UrchinBarren: one counter, and one pass over
// the barren cells every 3 days or over the recovering cells each hour). Nothing scans the map per tick.
public partial class MapComponent_FishStock
{
    private readonly UrchinBarren urchins = new();

    // The floor that grows on a cell now: its mark, or Bare while urchins have grazed it (barren or recovering).
    public FloorMark LiveMarkAt(int index) => urchins.IsGrazed(index) ? FloorMark.Bare : MarkAt(index);

    public FloorMark LiveMarkAt(IntVec3 cell) => LiveMarkAt(map.cellIndices.CellToIndex(cell));

    public int BarrenCellCount => urchins.BarrenCount;

    public int RecoveringCellCount => urchins.RecoveringCount;

    public bool IsBarren(IntVec3 cell) => cell.InBounds(map) && urchins.IsBarren(map.cellIndices.CellToIndex(cell));

    public bool IsBarren(int index) => urchins.IsBarren(index);

    public bool IsRecovering(IntVec3 cell) => cell.InBounds(map) && urchins.IsRecovering(map.cellIndices.CellToIndex(cell));

    public IEnumerable<IntVec3> BarrenCells
    {
        get
        {
            foreach (int index in urchins.BarrenCells) yield return map.cellIndices.IndexToCell(index);
        }
    }

    // Hours until the barren next spreads.
    public int HoursToUrchinSpread => urchins.HoursToSpread;

    // Hours until a culled cell's reef or kelp returns; -1 if it is not recovering.
    public int HoursToRecover(IntVec3 cell) => urchins.HoursToRecover(map.cellIndices.CellToIndex(cell));

    // An urchin outbreak strikes: a connected patch of about 10 to 20 reef or kelp cells around `start` turns barren. Returns
    // the number of cells grazed; 0 when `start` holds no reef or kelp that shows.
    public int StartBarren(IntVec3 start)
    {
        if (!start.InBounds(map)) return 0;
        int size = Rand.RangeInclusive(UrchinBarren.MinPatch, UrchinBarren.MaxPatch);
        List<int> patch = UrchinBarren.PickPatch(map.cellIndices.CellToIndex(start), size, map.Size.x, map.Size.z, IsReefOrKelp,
            count => Rand.Range(0, count));
        foreach (int index in patch) Graze(index);
        return patch.Count;
    }

    // Makes one reef or kelp cell barren (the outbreak's patch, its spread, developer tools). Returns whether it changed.
    public bool Graze(IntVec3 cell) => cell.InBounds(map) && IsReefOrKelp(cell) && Graze(map.cellIndices.CellToIndex(cell));

    // A diver culls the urchins on a barren cell: it starts recovering, and culling the last barren cell that shows ends the
    // outbreak with a letter. A barren cell under landfill or a bridge can't be culled (nor spread), so it would otherwise hold
    // the outbreak open for good; ending gives it back with the rest. Returns whether the cell was barren.
    public bool CullUrchins(IntVec3 cell)
    {
        if (!cell.InBounds(map) || !urchins.Cull(map.cellIndices.CellToIndex(cell))) return false;
        // Its look goes from barren to bare floor; it still counts as neither reef nor kelp.
        map.mapDrawer.MapMeshDirty(cell, (ulong)MapMeshFlagDefOf.Terrain, regenAdjacentCells: true, regenAdjacentSections: false);
        if (urchins.AnyBarren(Shows) || ThreatEvents.Of(map)?.End(ThreatKind.Urchins) != true) return true;
        // Only a cull ends an outbreak this way; a switch going off ends it through ThreatEvents with no letter.
        Find.LetterStack.ReceiveLetter("Spearfishing_UrchinsCulledLabel".Translate(), "Spearfishing_UrchinsCulled".Translate(),
            LetterDefOf.PositiveEvent, new LookTargets(cell, map));
        return true;
    }

    // A cell whose mark shows: ocean terrain, not under landfill, a bridge or a floor.
    private bool Shows(int index) => MarkAt(index) != FloorMark.Bare;

    // The outbreak ended: every barren cell gets its reef or kelp back at once, and so do the recovering cells when
    // `andRecovering` (a switch went off). Culled out, the recovering cells keep their own 5 days.
    public void EndBarren(bool andRecovering)
    {
        foreach (int index in urchins.Clear(andRecovering)) Regrown(index);
    }

    // Runs `hours` of the barren's spread and the culled cells' recovery. The hourly tick calls this with 1 while fish stock
    // management is on. Returns the number of spreads.
    public int AdvanceUrchins(int hours)
    {
        if (urchins.IsEmpty) return 0;
        return urchins.Advance(hours, map.Size.x, map.Size.z, Shows, IsReefOrKelp, count => Rand.Range(0, count), GrazeChanged, Regrown);
    }

    private bool Graze(int index)
    {
        if (!urchins.Add(index)) return false;
        GrazeChanged(index);
        return true;
    }

    // A cell turned barren: it leaves its water's reef count, and its look changes.
    private void GrazeChanged(int index)
    {
        stock?.Notify_FloorChanged(index, MarkAt(index) != FloorMark.Bare, IsReefOrKelp(index));
        RedrawCell(index);
    }

    // A grazed cell let go: its reef or kelp, if it still shows, counts again and draws again.
    private void Regrown(int index)
    {
        stock?.Notify_FloorChanged(index, false, IsReefOrKelp(index));
        RedrawCell(index);
    }

    // The edge fade reaches one cell past the patch, which can sit in the next section.
    private void RedrawCell(int index) =>
        map.mapDrawer.MapMeshDirty(map.cellIndices.IndexToCell(index), (ulong)MapMeshFlagDefOf.Terrain, regenAdjacentCells: true, regenAdjacentSections: false);

    // Saved as cell lists, written only while some cell is grazed. The reef grid keeps every grazed cell's mark, so a save
    // loaded without the mod drops this with the component and the reef is whole.
    private void ExposeUrchins()
    {
        bool saving = Scribe.mode == LoadSaveMode.Saving;
        List<int> barrenCells = null, recoveringCells = null, recoveringHours = null;
        int spreadHours = UrchinBarren.SpreadIntervalHours;
        if (saving) urchins.Save(out barrenCells, out recoveringCells, out recoveringHours, out spreadHours);
        if (saving && barrenCells == null && recoveringCells == null) return;
        Scribe_Collections.Look(ref barrenCells, "urchinBarrenCells", LookMode.Value);
        Scribe_Collections.Look(ref recoveringCells, "urchinRecoveringCells", LookMode.Value);
        Scribe_Collections.Look(ref recoveringHours, "urchinRecoveringHours", LookMode.Value);
        Scribe_Values.Look(ref spreadHours, "urchinHoursToSpread", UrchinBarren.SpreadIntervalHours);
        if (Scribe.mode == LoadSaveMode.LoadingVars) urchins.Load(barrenCells, recoveringCells, recoveringHours, spreadHours);
    }
}
