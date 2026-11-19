using System;
using System.Collections.Generic;

namespace Spearfishing;

// A zone's view of the fish stock: the body of fishing water under most of its cells (ADR 0013). The zone holds no fish of
// its own, so painting more cells adds none, and every zone on the same water reads the same stock. The body is found
// again only after the zone's cells change or the bodies are rebuilt, so reading it every frame costs nothing.
public sealed class ZoneFishStock
{
    private readonly FishStockModel model;
    private readonly HashSet<int> cells = new HashSet<int>();
    private readonly List<int> cellList = new List<int>();
    private readonly Dictionary<int, int> cellsPerBody = new Dictionary<int, int>();
    private readonly List<int> ranked = new List<int>();
    private readonly List<float> rankedFactors = new List<float>();
    private bool cellListStale, bodyStale = true;
    private int bodyVersion, body = -1;

    public ZoneFishStock(FishStockModel model) => this.model = model;

    public int CellCount => cells.Count;

    // The body under most of the zone's cells (the lowest-numbered on a tie), or -1 when none is fishing water.
    public int Body
    {
        get
        {
            int now = model.Version;
            if (bodyStale || bodyVersion != now) FindBody(now);
            return body;
        }
    }

    public float Stock => model.Stock(Body);

    public float Capacity => model.Capacity(Body);

    public float StockFraction => model.StockFraction(Body);

    // Whether the zone's water holds enough fish to be worth a dive: with fish stock management off, a fixed quarter.
    public bool WorthADive => WorthADiveAt(FishStockRules.FixedStopFraction);

    // Whether the zone's water is at or above a stop fraction: the active stop (FishStockRules.StopFraction), which with fish
    // stock management on is the zone's own fish-down limit, so two zones on one water can stop at different points.
    public bool WorthADiveAt(float stopFraction) => Capacity > 0f && !model.IsBelow(Body, stopFraction);

    public void Add(int cell)
    {
        if (!cells.Add(cell)) return;
        cellListStale = bodyStale = true;
    }

    public void Remove(int cell)
    {
        if (!cells.Remove(cell)) return;
        cellListStale = bodyStale = true;
    }

    public bool Contains(int cell) => cells.Contains(cell);

    // Takes a catch from the body under the dive spot, not the zone's: a zone over two bodies fishes the one the diver is
    // in. Returns the fish taken.
    public float TakeCatch(int spot, float fish = 1f) => model.TakeCatch(model.BodyAt(spot), fish);

    // A cell of the zone to dive at, or -1 for an empty zone. random returns a value in [0, 1). Samples a few cells, ranks
    // them by floorFactor (reef and kelp first, keeping the sample order among equals) and returns the first that fits
    // (ticket 28): fits is the caller's test, such as whether a diver can afford the swim, so a reef spot out of reach gives
    // way to bare floor in reach. -1 when none fits. The same samples are drawn whether or not fits or floorFactor is given.
    public int PickDiveSpot(Func<float> random, Func<int, bool> fits = null, int samples = 8, Func<int, float> floorFactor = null)
    {
        if (cells.Count == 0) return -1;
        if (cellListStale)
        {
            cellList.Clear();
            cellList.AddRange(cells);
            cellList.Sort();
            cellListStale = false;
        }
        ranked.Clear();
        rankedFactors.Clear();
        for (int i = 0; i < samples; i++)
        {
            int cell = cellList[Math.Min((int)(random() * cellList.Count), cellList.Count - 1)];
            float factor = floorFactor?.Invoke(cell) ?? FloorRules.BareFloorFactor;
            // After every sample with at least this factor: a stable rank, highest first.
            int at = ranked.Count;
            while (at > 0 && rankedFactors[at - 1] < factor) at--;
            ranked.Insert(at, cell);
            rankedFactors.Insert(at, factor);
        }
        foreach (int cell in ranked)
            if (fits == null || fits(cell)) return cell;
        return -1;
    }

    private void FindBody(int now)
    {
        cellsPerBody.Clear();
        foreach (int cell in cells)
        {
            int b = model.BodyAt(cell);
            if (b < 0) continue;
            cellsPerBody.TryGetValue(b, out int n);
            cellsPerBody[b] = n + 1;
        }
        body = -1;
        int most = 0;
        foreach (KeyValuePair<int, int> kv in cellsPerBody)
            if (kv.Value > most || (kv.Value == most && kv.Key < body))
            {
                body = kv.Key;
                most = kv.Value;
            }
        bodyVersion = now;
        bodyStale = false;
    }
}
