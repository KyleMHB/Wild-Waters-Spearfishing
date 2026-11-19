using System;
using System.Collections.Generic;

namespace Spearfishing;

// An urchin barren (threat events ticket 02, ADR 0017): reef and kelp cells of the sea that urchins have grazed bare, and the
// culled cells waiting to regrow. A grazed cell (barren or recovering) keeps its floor mark in the reef grid, but its owner
// stops counting it as reef or kelp: it leaves its water's reef share and loses the floor catch bonus until it recovers.
//
// The barren spreads as a whole, to one reef or kelp cell beside it about every 3 days, so a barren left alone grows by one
// cell per interval rather than doubling. A culled cell leaves the barren and recovers about 5 days later. Only the hours the
// caller advances count, so while fish stock management is off every count waits. The cost is one counter per hour, plus one
// pass over the barren cells when a spread comes due, and one pass over the recovering cells per hour: never a scan of the map.
// Plain C#, cells are row-major grid indices; tested under dotnet test.
public sealed class UrchinBarren
{
    public const int HoursPerDay = 24;

    public const int SpreadIntervalDays = 3;

    public const int SpreadIntervalHours = SpreadIntervalDays * HoursPerDay;

    public const int RecoveryDays = 5;

    public const int RecoveryHours = RecoveryDays * HoursPerDay;

    // An outbreak's starting patch: about 10 to 20 connected reef or kelp cells.
    public const int MinPatch = 10, MaxPatch = 20;

    private readonly HashSet<int> barren = new();

    // Culled cell -> hours until its reef or kelp returns.
    private readonly Dictionary<int, int> recovering = new();

    private readonly List<int> pass = new();
    private readonly List<int> targets = new();
    private readonly HashSet<int> seen = new();

    private int hoursToSpread = SpreadIntervalHours;

    public int BarrenCount => barren.Count;

    public int RecoveringCount => recovering.Count;

    // Whether nothing is grazed at all: the owner's fast path.
    public bool IsEmpty => barren.Count == 0 && recovering.Count == 0;

    public IEnumerable<int> BarrenCells => barren;

    public IEnumerable<int> RecoveringCells => recovering.Keys;

    public bool IsBarren(int cell) => barren.Contains(cell);

    public bool IsRecovering(int cell) => recovering.ContainsKey(cell);

    // Barren or recovering: the cell's reef or kelp doesn't count.
    public bool IsGrazed(int cell) => !IsEmpty && (barren.Contains(cell) || recovering.ContainsKey(cell));

    // Hours until the barren next spreads.
    public int HoursToSpread => hoursToSpread;

    // Hours until a culled cell recovers; -1 if it is not recovering.
    public int HoursToRecover(int cell) => recovering.TryGetValue(cell, out int left) ? left : -1;

    // Makes a cell barren. A recovering cell grazed again starts over. Returns whether it was not barren before.
    public bool Add(int cell)
    {
        recovering.Remove(cell);
        return barren.Add(cell);
    }

    // A diver culls a barren cell: it leaves the barren and starts recovering. Returns false for a cell that is not barren.
    public bool Cull(int cell)
    {
        if (!barren.Remove(cell)) return false;
        recovering[cell] = RecoveryHours;
        return true;
    }

    // Whether any barren cell is one `shows` accepts: a cell hidden under landfill or a bridge can't be culled, so the barren is
    // culled out once no barren cell shows.
    public bool AnyBarren(Func<int, bool> shows)
    {
        foreach (int cell in barren)
            if (shows(cell)) return true;
        return false;
    }

    // Forgets a cell altogether (its floor was cleared). Returns whether it was grazed.
    public bool Remove(int cell) => barren.Remove(cell) | recovering.Remove(cell);

    // Empties the barren, and the recovering cells too when `andRecovering`. Returns every cell let go, so the owner can give
    // their reef or kelp back at once.
    public List<int> Clear(bool andRecovering)
    {
        var freed = new List<int>(barren);
        barren.Clear();
        if (andRecovering)
        {
            freed.AddRange(recovering.Keys);
            recovering.Clear();
        }
        hoursToSpread = SpreadIntervalHours;
        return freed;
    }

    // Advances the barren by `hours`. Each recovering cell that comes due leaves through `recovered(cell)`. Each time the spread
    // comes due, one cell `canTake` accepts beside a barren cell `canSpreadFrom` accepts (orthogonally; never a barren or
    // recovering cell) is picked by `pick(count)` and joins through `spread(cell)`; with nothing to take, the spread waits a full
    // interval. canSpreadFrom refuses barren cells hidden under landfill or a bridge. An empty barren keeps its spread count where
    // it is. Returns the number of spreads.
    public int Advance(int hours, int width, int height, Func<int, bool> canSpreadFrom, Func<int, bool> canTake, Func<int, int> pick,
        Action<int> spread, Action<int> recovered)
    {
        if (hours <= 0 || IsEmpty) return 0;
        if (recovering.Count > 0)
        {
            pass.Clear();
            pass.AddRange(recovering.Keys);
            foreach (int cell in pass)
            {
                int left = recovering[cell] - hours;
                if (left > 0)
                {
                    recovering[cell] = left;
                    continue;
                }
                recovering.Remove(cell);
                recovered(cell);
            }
        }
        if (barren.Count == 0) return 0;
        int spreads = 0;
        hoursToSpread -= hours;
        while (hoursToSpread <= 0)
        {
            hoursToSpread += SpreadIntervalHours;
            int to = PickSpread(width, height, canSpreadFrom, canTake, pick);
            if (to < 0) continue;
            barren.Add(to);
            spread(to);
            spreads++;
        }
        return spreads;
    }

    // One cell beside a barren cell `canSpreadFrom` accepts (orthogonally) that `canTake` accepts and that is not already grazed,
    // chosen by `pick`, or -1. Each candidate counts once however many barren cells it touches. Candidates are listed in cell order, so a pick is the
    // same for the same barren.
    public int PickSpread(int width, int height, Func<int, bool> canSpreadFrom, Func<int, bool> canTake, Func<int, int> pick)
    {
        targets.Clear();
        seen.Clear();
        foreach (int cell in barren)
            if (canSpreadFrom(cell))
                Neighbours(cell, width, height, Consider);
        if (targets.Count == 0) return -1;
        targets.Sort();
        int i = pick(targets.Count);
        return targets[i < 0 || i >= targets.Count ? 0 : i];

        void Consider(int n)
        {
            if (!IsGrazed(n) && seen.Add(n) && canTake(n)) targets.Add(n);
        }
    }

    // A connected patch of up to `size` cells `canTake` accepts, grown from `start` one orthogonal neighbour at a time, each
    // picked by `pick(count)` among the patch's open edge. Empty when `start` itself is refused. A small reef gives a smaller
    // patch.
    public static List<int> PickPatch(int start, int size, int width, int height, Func<int, bool> canTake, Func<int, int> pick)
    {
        var patch = new List<int>();
        if (size <= 0 || !canTake(start)) return patch;
        var inPatch = new HashSet<int> { start };
        var edge = new List<int>();
        var onEdge = new HashSet<int>();
        patch.Add(start);
        AddEdge(start);
        while (patch.Count < size && edge.Count > 0)
        {
            int i = pick(edge.Count);
            if (i < 0 || i >= edge.Count) i = 0;
            int next = edge[i];
            edge[i] = edge[edge.Count - 1];
            edge.RemoveAt(edge.Count - 1);
            inPatch.Add(next);
            patch.Add(next);
            AddEdge(next);
        }
        return patch;

        void AddEdge(int cell) => Neighbours(cell, width, height, n =>
        {
            if (!inPatch.Contains(n) && onEdge.Add(n) && canTake(n)) edge.Add(n);
        });
    }

    private static void Neighbours(int cell, int width, int height, Action<int> visit)
    {
        int x = cell % width, z = cell / width;
        if (z + 1 < height) visit(cell + width);
        if (x + 1 < width) visit(cell + 1);
        if (z > 0) visit(cell - width);
        if (x > 0) visit(cell - 1);
    }

    // Saved as lists; null for none, so a map with no barren saves nothing.
    public void Save(out List<int> barrenCells, out List<int> recoveringCells, out List<int> recoveringHours, out int spreadHours)
    {
        barrenCells = barren.Count == 0 ? null : new List<int>(barren);
        barrenCells?.Sort();
        recoveringCells = recoveringHours = null;
        if (recovering.Count > 0)
        {
            recoveringCells = new List<int>(recovering.Keys);
            recoveringCells.Sort();
            recoveringHours = recoveringCells.ConvertAll(c => recovering[c]);
        }
        spreadHours = hoursToSpread;
    }

    public void Load(List<int> barrenCells, List<int> recoveringCells, List<int> recoveringHours, int spreadHours)
    {
        barren.Clear();
        recovering.Clear();
        if (barrenCells != null) barren.UnionWith(barrenCells);
        if (recoveringCells != null && recoveringHours != null)
            for (int i = 0; i < recoveringCells.Count && i < recoveringHours.Count; i++)
                if (!barren.Contains(recoveringCells[i]))
                    recovering[recoveringCells[i]] = Math.Max(1, Math.Min(RecoveryHours, recoveringHours[i]));
        hoursToSpread = Math.Max(1, Math.Min(SpreadIntervalHours, spreadHours));
    }
}
