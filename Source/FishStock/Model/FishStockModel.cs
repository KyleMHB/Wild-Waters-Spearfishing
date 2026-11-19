using System;
using System.Collections.Generic;

namespace Spearfishing;

// The fish stock of one map (ADR 0013): every body of fishing water (the sea, each lake, each river) has one stock that all
// spearfishing zones on it share. Bodies are connected fishing water, found by a flood fill over the map's cells (indexed
// z * width + x like RimWorld's CellIndices) through the four cardinal neighbours, since a swimmer can't slip diagonally
// between two corners of land. The bodies are built on the first question and rebuilt on the first question after the
// water changes; they are never saved, only each body's stock fraction is. Each body also counts its reef and kelp cells,
// which speed its logistic regrowth (ADR 0016).
public sealed class FishStockModel
{
    private readonly int width, height;
    private readonly Func<int, bool> isFishingWater;
    private readonly Func<int, bool> isReefOrKelp;

    // The body each cell belongs to, -1 for no fishing water. Null until first built.
    private int[] bodyAt;
    private readonly List<Body> bodies = new List<Body>();
    private bool stale = true;
    private int version;

    // Fractions waiting for the next build from a save. Null when there are none, so every body starts full.
    private List<SavedBody> pending;

    // The bodies before a terrain change, kept until the next build carries their fractions over. carryPending is false
    // when there is nothing to carry because every old body was full; the array is then a spare for the next swap.
    private int[] priorBodyAt;
    private readonly List<Body> priorBodies = new List<Body>();
    private bool carryPending;

    private sealed class Body
    {
        // The body's lowest cell index: the flood fill starts there, so it is the same cell however often the body is found.
        public int FirstCell;
        public int Cells;
        // Cells of the body with reef or kelp on their floor.
        public int ReefCells;
        public float Capacity;
        public float Stock;
    }

    // isFishingWater says whether a cell index is fishing water. saved holds the fractions to restore; bodies it doesn't
    // name start full. isReefOrKelp says whether a cell's floor is reef or kelp; null for none anywhere.
    public FishStockModel(int width, int height, Func<int, bool> isFishingWater, IEnumerable<SavedBody> saved = null,
        Func<int, bool> isReefOrKelp = null)
    {
        this.width = width;
        this.height = height;
        this.isFishingWater = isFishingWater;
        this.isReefOrKelp = isReefOrKelp;
        if (saved != null) pending = new List<SavedBody>(saved);
    }

    // Rises with every build, so a zone knows to find its body again.
    public int Version
    {
        get
        {
            EnsureBuilt();
            return version;
        }
    }

    // Times the bodies were found, for the developer tests.
    public int Builds { get; private set; }

    public int BodyCount
    {
        get
        {
            EnsureBuilt();
            return bodies.Count;
        }
    }

    // Whether any body is fished below capacity, without building the bodies when nothing has been fished.
    public bool AnyBelowCapacity
    {
        get
        {
            if (stale) return carryPending || (pending != null && pending.Exists(s => s.Fraction < 1f));
            foreach (Body b in bodies)
                if (b.Stock < b.Capacity) return true;
            return false;
        }
    }

    public int BodiesBelowCapacity
    {
        get
        {
            EnsureBuilt();
            int n = 0;
            foreach (Body b in bodies)
                if (b.Stock < b.Capacity) n++;
            return n;
        }
    }

    // The body of fishing water at a cell, or -1 for none.
    public int BodyAt(int cell)
    {
        EnsureBuilt();
        return cell >= 0 && cell < bodyAt.Length ? bodyAt[cell] : -1;
    }

    public int CellCount(int body) => Get(body)?.Cells ?? 0;

    public float Capacity(int body) => Get(body)?.Capacity ?? 0f;

    public int ReefCellCount(int body) => Get(body)?.ReefCells ?? 0;

    // The share of a body's cells with reef or kelp on their floor, 0 to 1; 0 for no body.
    public float ReefShare(int body)
    {
        Body b = Get(body);
        return b == null || b.Cells <= 0 ? 0f : (float)b.ReefCells / b.Cells;
    }

    // One cell's floor changed between bare and reef or kelp. Updates its body's count in place; while the bodies wait to be
    // found again this does nothing, since the next build counts every cell afresh.
    public void Notify_FloorChanged(int cell, bool wasReefOrKelp, bool isReefOrKelp)
    {
        if (stale || wasReefOrKelp == isReefOrKelp || cell < 0 || cell >= bodyAt.Length) return;
        int body = bodyAt[cell];
        if (body < 0) return;
        bodies[body].ReefCells += isReefOrKelp ? 1 : -1;
    }

    public float Stock(int body) => Get(body)?.Stock ?? 0f;

    // Stock as a fraction of capacity; 0 for no body.
    public float StockFraction(int body)
    {
        Body b = Get(body);
        return b == null || b.Capacity <= 0f ? 0f : b.Stock / b.Capacity;
    }

    // The stock fraction a dive reads when another population shares this water by fraction (Odyssey's, ADR 0013): the
    // lower of the body's fraction and `otherFraction`, so whichever is more fished down limits the dive. An other fraction
    // of 1 leaves the body's own. 0 for no body.
    public float SharedStockFraction(int body, float otherFraction) =>
        Math.Min(StockFraction(body), Math.Max(0f, Math.Min(1f, otherFraction)));

    // The share of a body's capacity that `fish` makes up: what a catch lowers a population sharing the water by. 0 for no
    // body.
    public float ShareOfCapacity(int body, float fish)
    {
        Body b = Get(body);
        return b == null || b.Capacity <= 0f || fish <= 0f ? 0f : Math.Min(1f, fish / b.Capacity);
    }

    // Whether the body's stock is below a fraction of its capacity: where divers stop. No body counts as below.
    public bool IsBelow(int body, float stopFraction)
    {
        Body b = Get(body);
        return b == null || b.Capacity <= 0f || b.Stock < stopFraction * b.Capacity;
    }

    // Takes up to `fish` from one body. Returns the fish taken: less than asked only when the body holds less.
    public float TakeCatch(int body, float fish)
    {
        Body b = Get(body);
        if (b == null || fish <= 0f || b.Stock <= 0f) return 0f;
        float taken = Math.Min(fish, b.Stock);
        b.Stock -= taken;
        return taken;
    }

    // Adds up to `fish` released fry to one body (the hatchery, ADR 0016): never past capacity, and fry that don't fit are
    // lost. Returns the fish added.
    public float Release(int body, float fish)
    {
        Body b = Get(body);
        if (b == null || fish <= 0f) return 0f;
        float added = Math.Max(0f, Math.Min(fish, b.Capacity - b.Stock));
        b.Stock += added;
        return added;
    }

    // Sets a body's stock to a fraction of its capacity, clamped to 0..1. Restoring a save uses it, as do developer tools.
    public void SetStockFraction(int body, float fraction)
    {
        Body b = Get(body);
        if (b == null) return;
        b.Stock = b.Capacity * Math.Max(0f, Math.Min(1f, fraction));
    }

    // Every body back to full (developer tools).
    public void RefillAll()
    {
        if (stale)
        {
            pending = null;
            carryPending = false;
            return;
        }
        foreach (Body b in bodies) b.Stock = b.Capacity;
    }

    // Fish the body would regrow in a day at its current stock under the rule, reef boost included, never past capacity.
    public float RegrowthPerDay(int body, RegrowthRule rule)
    {
        Body b = Get(body);
        if (b == null) return 0f;
        return Math.Max(0f, Math.Min(PerDay(b, rule), b.Capacity - b.Stock));
    }

    // RegrowthPerDay without the reef boost: the base the zone's tooltip shows the boost against.
    public float BaseRegrowthPerDay(int body, RegrowthRule rule)
    {
        Body b = Get(body);
        if (b == null) return 0f;
        return Math.Max(0f, Math.Min(rule.PerDay(b.Stock, b.Capacity), b.Capacity - b.Stock));
    }

    // One in-game hour of regrowth for every body below capacity, zoned or not. Builds nothing while every body is full.
    public void RegrowOneHour(RegrowthRule rule)
    {
        if (!AnyBelowCapacity) return;
        EnsureBuilt();
        foreach (Body b in bodies)
        {
            if (b.Stock >= b.Capacity) continue;
            float gain = Math.Max(0f, PerDay(b, rule)) / FishStockRules.HoursPerDay;
            b.Stock = Math.Min(b.Capacity, b.Stock + gain);
        }
    }

    // The fishing water changed (landfill, a bridge, digging, ice). The bodies are found again once, on the next question,
    // however many changes come first. Each new body takes the capacity-weighted stock fraction of the old bodies it
    // overlaps, and cells new to fishing water count as full, so no change refills fished water.
    public void Notify_WaterChanged()
    {
        if (stale) return;
        stale = true;
        // Full water carries nothing over: every new body starts full anyway. Ice coming and going costs no snapshot.
        carryPending = bodies.Exists(b => b.Stock < b.Capacity);
        // Predators keep the old bodies too, to move their anchor if its cell stops being water.
        reanchorPending = predatorCount > 0;
        if (!carryPending && !reanchorPending) return;
        // Keep the old bodies; the next build writes into the spare array.
        (priorBodyAt, bodyAt) = (bodyAt, priorBodyAt);
        priorBodies.Clear();
        priorBodies.AddRange(bodies);
    }

    // The state to save: one cell and the stock fraction of every body below capacity. Bodies left out load full.
    public List<SavedBody> SaveState()
    {
        // A change waiting to be carried over is carried now, so a save made before the next read keeps every fraction.
        if (stale && carryPending) EnsureBuilt();
        if (stale) return pending == null ? new List<SavedBody>() : new List<SavedBody>(pending);
        var saved = new List<SavedBody>();
        foreach (Body b in bodies)
            if (b.Stock < b.Capacity) saved.Add(new SavedBody(b.FirstCell, b.Capacity > 0f ? b.Stock / b.Capacity : 1f));
        return saved;
    }

    // A day's regrowth under the rule, times (1 + reef share) for a rule the reef boosts (ADR 0016): at most double. Invasive
    // predators then cut it (ADR 0017).
    private float PerDay(Body b, RegrowthRule rule)
    {
        float perDay = rule.PerDay(b.Stock, b.Capacity);
        perDay = rule.ReefBoosts && b.Cells > 0 ? perDay * (1f + (float)b.ReefCells / b.Cells) : perDay;
        return perDay * (1f - PredatorCutOf(b));
    }

    private Body Get(int body)
    {
        EnsureBuilt();
        return body >= 0 && body < bodies.Count ? bodies[body] : null;
    }

    private void EnsureBuilt()
    {
        if (!stale) return;
        Build();
        stale = false;
        version++;
        if (reanchorPending) ReanchorPredators();
        if (carryPending) CarryOver();
        if (pending == null) return;
        foreach (SavedBody s in pending)
        {
            int body = s.Cell >= 0 && s.Cell < bodyAt.Length ? bodyAt[s.Cell] : -1;
            if (body >= 0) SetStockFraction(body, s.Fraction);
        }
        pending = null;
    }

    // Flood fill in cell order, so each body's first cell is its lowest index. Every body starts full.
    private void Build()
    {
        int count = width * height;
        bodyAt ??= new int[count];
        bodies.Clear();
        for (int i = 0; i < count; i++) bodyAt[i] = isFishingWater(i) ? Unvisited : -1;
        var stack = new Stack<int>();
        for (int start = 0; start < count; start++)
        {
            if (bodyAt[start] != Unvisited) continue;
            int id = bodies.Count;
            int cells = 0, reefCells = 0;
            bodyAt[start] = id;
            stack.Push(start);
            while (stack.Count > 0)
            {
                int cell = stack.Pop();
                cells++;
                if (isReefOrKelp != null && isReefOrKelp(cell)) reefCells++;
                int x = cell % width;
                if (x > 0) Visit(cell - 1, id, stack);
                if (x < width - 1) Visit(cell + 1, id, stack);
                if (cell >= width) Visit(cell - width, id, stack);
                if (cell + width < count) Visit(cell + width, id, stack);
            }
            float capacity = FishStockRules.Capacity(cells);
            bodies.Add(new Body { FirstCell = start, Cells = cells, ReefCells = reefCells, Capacity = capacity, Stock = capacity });
        }
        Builds++;
    }

    private const int Unvisited = -2;

    // Each new body's fraction is the capacity-weighted mean over its cells: a cell that was fishing water carries its old
    // body's fraction, weighted by that body's capacity per cell; a cell new to fishing water is full, weighted by
    // FishPerCell. A mean never exceeds the fractions it is made of, so only new water can raise a body's fraction.
    private void CarryOver()
    {
        carryPending = false;
        var weight = new double[bodies.Count];
        var fish = new double[bodies.Count];
        for (int i = 0; i < bodyAt.Length; i++)
        {
            int now = bodyAt[i];
            if (now < 0) continue;
            int was = priorBodyAt[i];
            if (was < 0)
            {
                weight[now] += FishStockRules.FishPerCell;
                fish[now] += FishStockRules.FishPerCell;
                continue;
            }
            Body old = priorBodies[was];
            double perCell = (double)old.Capacity / old.Cells;
            weight[now] += perCell;
            fish[now] += perCell * old.Stock / old.Capacity;
        }
        for (int b = 0; b < bodies.Count; b++)
            if (weight[b] > 0d) SetStockFraction(b, (float)(fish[b] / weight[b]));
        priorBodies.Clear();
    }

    private void Visit(int cell, int id, Stack<int> stack)
    {
        if (bodyAt[cell] != Unvisited) return;
        bodyAt[cell] = id;
        stack.Push(cell);
    }

    // Invasive predators (threat events ticket 03, ADR 0017). A map has at most one predator outbreak, so the model keeps one
    // count and maximum, anchored to a cell rather than a body index: bodies are renumbered on every rebuild, and the body
    // holding the anchor is the one with predators. While no body holds the anchor (its water frozen over, say) the count waits
    // with no effect. Growth, the regrowth cut and culling follow PredatorRules.
    private int predatorCell = -1;
    private float predatorCount, predatorMax;
    private bool reanchorPending;

    public bool HasPredators => predatorCount > 0f;

    public float PredatorCount => predatorCount;

    public float PredatorMaximum => predatorMax;

    // The anchor cell, or -1 with no predators.
    public int PredatorCell => predatorCount > 0f ? predatorCell : -1;

    // The body the predators are in, or -1.
    public int PredatorBody => predatorCount > 0f ? BodyAt(predatorCell) : -1;

    // The count in one body: the predators' count in theirs, 0 elsewhere.
    public float Predators(int body) => body >= 0 && body == PredatorBody ? predatorCount : 0f;

    // The share of one body's regrowth the predators cut, 0 to PredatorRules.MaxRegrowthCut.
    public float PredatorCut(int body) => body >= 0 && body == PredatorBody ? PredatorRules.RegrowthCut(predatorCount, predatorMax) : 0f;

    // The chance that a successful catch in one body is a predator.
    public float PredatorCatchShare(int body) => body >= 0 && body == PredatorBody ? PredatorRules.CatchShare(predatorCount, predatorMax) : 0f;

    // Puts predators in the body at `cell`, replacing any. Restoring a save uses it too.
    public void SetPredators(int cell, float count, float maximum)
    {
        if (count <= 0f || maximum <= 0f || cell < 0)
        {
            ClearPredators();
            return;
        }
        predatorCell = cell;
        predatorMax = maximum;
        predatorCount = Math.Min(count, maximum);
    }

    public void ClearPredators()
    {
        predatorCell = -1;
        predatorCount = predatorMax = 0f;
    }

    // One predator caught in `body`: the count falls by one, and a remainder below PredatorRules.ClearedBelow is none. Returns
    // whether this cleared the last of them. Does nothing in a body without predators.
    public bool CullPredator(int body)
    {
        if (body < 0 || body != PredatorBody) return false;
        predatorCount -= 1f;
        if (predatorCount >= PredatorRules.ClearedBelow) return false;
        ClearPredators();
        return true;
    }

    // One in-game hour of the predators' growth toward their maximum. Builds nothing.
    public void GrowPredatorsOneHour()
    {
        if (predatorCount > 0f) predatorCount = PredatorRules.GrowOneHour(predatorCount, predatorMax);
    }

    private float PredatorCutOf(Body b)
    {
        if (predatorCount <= 0f || predatorCell < 0 || predatorCell >= bodyAt.Length) return 0f;
        int body = bodyAt[predatorCell];
        return body >= 0 && bodies[body] == b ? PredatorRules.RegrowthCut(predatorCount, predatorMax) : 0f;
    }

    // After a rebuild: if the anchor's cell is no longer fishing water, move it to a cell of the same old body that still is.
    // If none is left (the whole water froze or was filled), the anchor stays, and the predators come back with its water.
    private void ReanchorPredators()
    {
        reanchorPending = false;
        if (!carryPending) priorBodies.Clear();
        if (predatorCount <= 0f || predatorCell < 0 || predatorCell >= bodyAt.Length || bodyAt[predatorCell] >= 0) return;
        int was = priorBodyAt[predatorCell];
        if (was < 0) return;
        for (int i = 0; i < bodyAt.Length; i++)
            if (priorBodyAt[i] == was && bodyAt[i] >= 0)
            {
                predatorCell = i;
                return;
            }
    }
}
