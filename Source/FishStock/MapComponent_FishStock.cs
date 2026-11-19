using System.Collections.Generic;
using RimWorld;
using Verse;

namespace Spearfishing;

// Owns one map's sea floor and fish stock: the reef grid (reef and kelp), the fish stock of each body of fishing water
// (ADR 0013) and its hourly regrowth. RimWorld adds a MapComponent to every map, including maps from saves made before the
// mod. Without the mod a save keeps only this component's missing class, which the map drops, so the sea and the terrain
// are untouched (ADR 0008).
public partial class MapComponent_FishStock : MapComponent
{
    private FishStockModel stock;
    private List<SavedBody> loadedBodies;

    // Reef and kelp, one FloorMark byte per cell, over plain ocean terrain. Null while the map has neither.
    private byte[] reef;
    private int reefCount, kelpCount;

    // Habitat restoration (fish recovery ticket 03): the cells divers restored or restored floor spread to, each counting the
    // hours to its next spread. Natural and artificial reef are never here, so they never spread.
    private readonly RestorationSpread restored = new();

    public MapComponent_FishStock(Map map) : base(map)
    {
        Outbreaks = new Outbreaks(map);
    }

    // Threat events (threat events ticket 01): the outbreaks active on this map, saved with the fish stock.
    public Outbreaks Outbreaks { get; }

    public FishStockModel Stock => stock ??= new FishStockModel(map.Size.x, map.Size.z, IsFishingWater, loadedBodies, IsReefOrKelp);

    public static FishStockModel For(Map map) => map.GetComponent<MapComponent_FishStock>().Stock;

    public static MapComponent_FishStock Of(Map map) => map.GetComponent<MapComponent_FishStock>();

    // The body of fishing water at a cell, or -1.
    public int BodyAt(IntVec3 cell) => cell.InBounds(map) ? Stock.BodyAt(map.cellIndices.CellToIndex(cell)) : -1;

    // The stock fraction of the body of water at a cell: the catch chance's stock term and what the shoals read. 0 off
    // fishing water.
    public float StockFractionAt(IntVec3 cell) => Stock.StockFraction(BodyAt(cell));

    // Takes a catch from the body of water at a cell; returns the fish taken.
    public float TakeCatchAt(IntVec3 cell, float fish = 1f) => Stock.TakeCatch(BodyAt(cell), fish);

    // Ticket 22: how deep each fishing water cell reads, 0 to 1, below zero off fishing water. Built on first use and after a
    // terrain change, never saved. Ticket 23's fish read it too.
    private SwimDepthGrid swimDepth;

    public static float SwimDepthAt(Map map, IntVec3 cell) => Of(map)?.SwimDepth.DepthAt(cell) ?? -1f;

    private SwimDepthGrid SwimDepth => swimDepth ??= new SwimDepthGrid(map);

    // A terrain change can reshape the bodies of fishing water, so they are found again on the next question.
    internal void Notify_TerrainChanged()
    {
        swimDepth?.Notify_TerrainChanged();
        stock?.Notify_WaterChanged();
    }

    public int ReefCellCount => reefCount;

    public int KelpCellCount => kelpCount;

    // The mark on one cell where it shows: landfill, a bridge or a floor over it hides reef and kelp, and taking that away
    // brings them back.
    public FloorMark MarkAt(int index) =>
        reef == null || reef[index] == 0 || !IsOcean(map.terrainGrid.TerrainAt(index)) ? FloorMark.Bare : (FloorMark)reef[index];

    public FloorMark MarkAt(IntVec3 cell) => MarkAt(map.cellIndices.CellToIndex(cell));

    public bool IsReef(int index) => MarkAt(index) == FloorMark.Reef;

    public bool IsReef(IntVec3 cell) => IsReef(map.cellIndices.CellToIndex(cell));

    public bool IsKelp(IntVec3 cell) => MarkAt(cell).IsKelp();

    // Reef or kelp: the floors where fish are densest, and which speed their water's regrowth (ADR 0016).
    // An urchin barren's cells, barren or recovering, keep their mark but count as neither (threat events ticket 02).
    public bool IsReefOrKelp(IntVec3 cell) => IsReefOrKelp(map.cellIndices.CellToIndex(cell));

    private bool IsReefOrKelp(int index) => MarkAt(index) != FloorMark.Bare && !urchins.IsGrazed(index);

    // The catch chance's floor factor at a cell, and how divers rank dive spots: above 1 over reef and kelp, 1 elsewhere.
    public float FloorFactorAt(int index) => FloorRules.FloorFactor(LiveMarkAt(index));

    public float FloorFactorAt(IntVec3 cell) => FloorFactorAt(map.cellIndices.CellToIndex(cell));

    // Marks or clears reef on one cell; clearing leaves kelp alone.
    public void SetReef(IntVec3 cell, bool value)
    {
        int index = map.cellIndices.CellToIndex(cell);
        FloorMark now = reef == null ? FloorMark.Bare : (FloorMark)reef[index];
        if (value) SetMark(cell, FloorMark.Reef);
        else if (now == FloorMark.Reef) SetMark(cell, FloorMark.Bare);
    }

    // Writes one cell's mark, whatever its terrain is now. Map generation, developer tools and a later artificial reef write
    // here; nothing writes reef or kelp terrain. The overlays refresh. The fish stock and capacity don't change (ADR 0013),
    // but the body's reef count does, which speeds its regrowth (ADR 0016); only a mark that shows counts.
    public void SetMark(IntVec3 cell, FloorMark mark)
    {
        int index = map.cellIndices.CellToIndex(cell);
        FloorMark now = reef == null ? FloorMark.Bare : (FloorMark)reef[index];
        if (now == mark) return;
        // Cleared floor is no longer restored floor.
        if (mark == FloorMark.Bare) restored.Remove(index);
        reef ??= new byte[map.cellIndices.NumGridCells];
        Count(now, -1);
        Count(mark, 1);
        bool wasShown = IsReefOrKelp(index);
        reef[index] = (byte)mark;
        stock?.Notify_FloorChanged(index, wasShown, IsReefOrKelp(index));
        // Cleared floor is no longer grazed either: only reef and kelp can be barren (threat events ticket 02).
        if (mark == FloorMark.Bare) urchins.Remove(index);
        // The edge fade reaches one cell past the patch, which can sit in the next section.
        map.mapDrawer.MapMeshDirty(cell, (ulong)MapMeshFlagDefOf.Terrain, regenAdjacentCells: true, regenAdjacentSections: false);
    }

    public bool IsRestored(IntVec3 cell) => restored.IsRestored(map.cellIndices.CellToIndex(cell));

    public int RestoredCellCount => restored.Count;

    // Hours until a restored cell next spreads; -1 if it is not restored.
    public int HoursToSpread(IntVec3 cell) => restored.HoursLeft(map.cellIndices.CellToIndex(cell));

    // Restores one cell (habitat restoration): it takes `kind`, joins the restored floor that spreads, and loses its mark.
    public void Restore(IntVec3 cell, FloorMark kind)
    {
        if (kind == FloorMark.Bare) return;
        SetMark(cell, kind);
        restored.Add(map.cellIndices.CellToIndex(cell));
        Designation mark = map.designationManager.DesignationAt(cell, RestorationDefOf.Spearfishing_RestoreSeaFloor);
        if (mark != null) map.designationManager.RemoveDesignation(mark);
    }

    // Runs `hours` of restored floor's spread: each restored cell that comes due copies its own kind onto one marked bare
    // neighbour. The hourly tick calls this with 1 while fish stock management is on; the count waits while it is off.
    // Returns the number of spreads.
    public int AdvanceRestoration(int hours)
    {
        if (restored.Count == 0) return 0;
        return restored.Advance(hours, map.Size.x, map.Size.z, IsReefOrKelp,
            to => HabitatRestoration.CanTake(map, map.cellIndices.IndexToCell(to)), count => Rand.Range(0, count),
            (from, to) => Restore(map.cellIndices.IndexToCell(to), (FloorMark)reef[from]));
    }

    // A map that finishes loading or generating takes the current fish stock management setting (ManagementGate), so a
    // switch made at the main menu reaches it.
    public override void FinalizeInit() => ManagementGate.Apply(map);

    private void Count(FloorMark mark, int by)
    {
        if (mark == FloorMark.Reef) reefCount += by;
        else if (mark.IsKelp()) kelpCount += by;
    }

    // Regrowth is hourly; on other ticks this is one integer compare. The rule follows the fish stock management setting:
    // logistic when on, flat when off. With management on and Odyssey sharing the fish, Odyssey's population then keeps pace
    // with what each body gained (ticket 08, ADR 0015), so the logistic regrowth reaches the dives that read the lower fraction.
    public override void MapComponentTick()
    {
        if (Find.TickManager.TicksGame % GenDate.TicksPerHour != 0) return;
        if (FishStockManagement.On) AdvanceRestoration(1);
        if (FishStockManagement.On) AdvanceUrchins(1);
        if (stock == null && loadedBodies == null) return;
        // Invasive predators grow whether or not the water is fished (threat events ticket 03).
        stock?.GrowPredatorsOneHour();
        bool keepPace = FishStockManagement.On && OdysseyFish.Sharing && Stock.AnyBelowCapacity;
        if (keepPace) SnapshotFractions();
        Stock.RegrowOneHour(FishStockManagement.Rule);
        if (keepPace) OdysseyFish.KeepPace(map, fractionsBefore);
    }

    // Each body's stock fraction before the hour's regrowth, by body; reused hour to hour.
    private float[] fractionsBefore;

    private void SnapshotFractions()
    {
        int count = Stock.BodyCount;
        if (fractionsBefore == null || fractionsBefore.Length != count) fractionsBefore = new float[count];
        for (int b = 0; b < count; b++) fractionsBefore[b] = Stock.StockFraction(b);
    }

    // The reef grid is saved like vanilla's per-cell grids: LookByteArray deflates it, and a reefless sea saves nothing.
    // The fish stock saves one cell and the stock fraction of each body below capacity; on load the bodies are found again
    // from the terrain and each takes the fraction saved for the body holding its cell, or starts full. The per-cell
    // depletion grid of saves before ADR 0013 ("fishDepletion") is never read, so those maps start every body full.
    public override void ExposeData()
    {
        bool saving = Scribe.mode == LoadSaveMode.Saving;
        List<int> bodyCells = null;
        List<float> bodyFractions = null;
        if (saving)
        {
            List<SavedBody> bodies = stock?.SaveState() ?? loadedBodies;
            if (bodies != null && bodies.Count > 0)
            {
                bodyCells = bodies.ConvertAll(b => b.Cell);
                bodyFractions = bodies.ConvertAll(b => b.Fraction);
            }
        }
        // Written only while some water is fished, so a full sea saves nothing at all.
        if (!saving || bodyCells != null)
        {
            Scribe_Collections.Look(ref bodyCells, "fishBodyCells", LookMode.Value);
            Scribe_Collections.Look(ref bodyFractions, "fishBodyFractions", LookMode.Value);
        }
        // Kelp shares the reef grid (ticket 38), so saves gain no field and old saves load unchanged.
        byte[] reefSaved = saving && reefCount + kelpCount > 0 ? reef : null;
        DataExposeUtility.LookByteArray(ref reefSaved, "reef");
        // Restored floor and its spread counts (ticket 03), written only while there is some.
        List<int> restoredCells = null, restoredHours = null;
        if (saving) restored.Save(out restoredCells, out restoredHours);
        if (!saving || restoredCells != null)
        {
            Scribe_Collections.Look(ref restoredCells, "restoredCells", LookMode.Value);
            Scribe_Collections.Look(ref restoredHours, "restoredHours", LookMode.Value);
        }
        if (Scribe.mode == LoadSaveMode.LoadingVars) restored.Load(restoredCells, restoredHours);
        // An urchin barren and its recovering cells (threat events ticket 02), written only while there are some.
        ExposeUrchins();
        // Active threat outbreaks, written only while there is one.
        Outbreaks.ExposeData();
        ExposePredators(saving);
        // Spearfishing zones are saved here, not in the zone manager, so a save without the mod keeps its other zones (ADR 0009).
        List<Zone_Spearfishing> zones = saving ? ZoneSaveSplit.ToSave(map) : null;
        Scribe_Collections.Look(ref zones, "spearfishingZones", LookMode.Deep);
        if (Scribe.mode == LoadSaveMode.LoadingVars)
        {
            ZoneSaveSplit.Restore(map, zones);
            loadedBodies = null;
            if (bodyCells != null && bodyFractions != null)
            {
                loadedBodies = new List<SavedBody>();
                for (int i = 0; i < bodyCells.Count && i < bodyFractions.Count; i++) loadedBodies.Add(new SavedBody(bodyCells[i], bodyFractions[i]));
            }
            stock = null;
            reef = reefSaved != null && reefSaved.Length == map.cellIndices.NumGridCells ? reefSaved : null;
            reefCount = kelpCount = 0;
            if (reef != null)
                foreach (byte b in reef)
                    Count((FloorMark)b, 1);
        }
    }

    // Invasive predators (threat events ticket 03): the anchor cell, count and maximum, written only while there are some. The
    // model is made at PostLoadInit to take them, after the stock fractions have loaded.
    private void ExposePredators(bool saving)
    {
        bool any = saving && stock != null && stock.HasPredators;
        if (saving && !any) return;
        int cell = any ? stock.PredatorCell : -1;
        float count = any ? stock.PredatorCount : 0f, maximum = any ? stock.PredatorMaximum : 0f;
        Scribe_Values.Look(ref cell, "predatorCell", -1);
        Scribe_Values.Look(ref count, "predatorCount");
        Scribe_Values.Look(ref maximum, "predatorMax");
        if (Scribe.mode == LoadSaveMode.LoadingVars && count > 0f) loadedPredators = (cell, count, maximum);
        if (Scribe.mode != LoadSaveMode.PostLoadInit || loadedPredators == null) return;
        (int c, float n, float max) = loadedPredators.Value;
        loadedPredators = null;
        Stock.SetPredators(c, n, max);
    }

    private (int cell, float count, float maximum)? loadedPredators;

    private static bool IsOcean(TerrainDef terrain) => terrain == TerrainDefOf.WaterOceanShallow || terrain == TerrainDefOf.WaterOceanDeep;

    // Bodies of fishing water follow the terrain alone (ADR 0010's terrain list), not Waves' swim cells, so they don't move
    // with Waves' settings. Frozen water reads as ice, so it is no fishing water while frozen.
    private bool IsFishingWater(int index) => WavesBridge.IsFishingWater(map.terrainGrid.TerrainAt(index));
}
