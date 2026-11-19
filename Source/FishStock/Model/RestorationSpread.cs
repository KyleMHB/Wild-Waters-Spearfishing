using System;
using System.Collections.Generic;

namespace Spearfishing;

// Habitat restoration's spread (fish recovery ticket 03, ADR 0015 revised): each restored cell spreads to one orthogonal
// neighbour the player has marked for restoration about every 15 days. Natural and artificial reef are never in this set, so
// they never spread. Each restored cell counts its own hours down, and only the hours the caller advances count, so while
// fish stock management is off the caller stops advancing and every count waits where it was; turning it back on resumes
// them without a burst of overdue spreads. The cost is one pass over the restored cells per hour, never a scan of the map.
// Plain C#, cells are grid indices; tested under dotnet test.
public sealed class RestorationSpread
{
    public const int HoursPerDay = 24;

    public const int IntervalDays = 15;

    public const int IntervalHours = IntervalDays * HoursPerDay;

    // Restored cell -> hours until it next spreads.
    private readonly Dictionary<int, int> hoursLeft = new();

    // The restored cells of one pass, reused, so a spread during the pass doesn't change the collection being read.
    private readonly List<int> pass = new();

    private readonly List<int> targets = new(4);

    public int Count => hoursLeft.Count;

    public IEnumerable<int> Cells => hoursLeft.Keys;

    public bool IsRestored(int cell) => hoursLeft.ContainsKey(cell);

    // Hours until the cell next spreads; -1 if it is not restored.
    public int HoursLeft(int cell) => hoursLeft.TryGetValue(cell, out int left) ? left : -1;

    // A newly restored cell starts a full interval.
    public void Add(int cell) => hoursLeft[cell] = IntervalHours;

    public void Remove(int cell) => hoursLeft.Remove(cell);

    // Advances every restored cell by `hours`. A cell that comes due spreads to one orthogonal neighbour `canTake` accepts,
    // picked by `pick(count)` (an index below count), through `spread(from, to)`, and the neighbour joins with a full interval.
    // A due cell with no neighbour to take, or that `canSpreadFrom` refuses (its floor hidden under landfill), waits a full
    // interval again, so no cell ever spreads faster than once per interval. Returns the number of spreads.
    public int Advance(int hours, int width, int height, Func<int, bool> canSpreadFrom, Func<int, bool> canTake, Func<int, int> pick,
        Action<int, int> spread)
    {
        if (hours <= 0 || hoursLeft.Count == 0) return 0;
        pass.Clear();
        pass.AddRange(hoursLeft.Keys);
        int spreads = 0;
        foreach (int cell in pass)
        {
            int left = hoursLeft[cell] - hours;
            while (left <= 0)
            {
                left += IntervalHours;
                if (!canSpreadFrom(cell)) continue;
                int to = PickTarget(cell, width, height, canTake, pick);
                if (to < 0) continue;
                spread(cell, to);
                Add(to);
                spreads++;
            }
            hoursLeft[cell] = left;
        }
        return spreads;
    }

    // One orthogonal neighbour of `cell` that `canTake` accepts, chosen by `pick`, or -1. Cells are row-major indices of a
    // width x height grid; the grid's edges don't wrap.
    public int PickTarget(int cell, int width, int height, Func<int, bool> canTake, Func<int, int> pick)
    {
        targets.Clear();
        int x = cell % width, z = cell / width;
        if (z + 1 < height) Consider(cell + width);
        if (x + 1 < width) Consider(cell + 1);
        if (z > 0) Consider(cell - width);
        if (x > 0) Consider(cell - 1);
        if (targets.Count == 0) return -1;
        int i = pick(targets.Count);
        return targets[i < 0 || i >= targets.Count ? 0 : i];

        void Consider(int n)
        {
            if (canTake(n)) targets.Add(n);
        }
    }

    // Saved as two parallel lists; null for none, so a map with no restored floor saves nothing.
    public void Save(out List<int> cells, out List<int> hours)
    {
        cells = hours = null;
        if (hoursLeft.Count == 0) return;
        cells = new List<int>(hoursLeft.Keys);
        hours = cells.ConvertAll(c => hoursLeft[c]);
    }

    public void Load(List<int> cells, List<int> hours)
    {
        hoursLeft.Clear();
        if (cells == null || hours == null) return;
        for (int i = 0; i < cells.Count && i < hours.Count; i++) hoursLeft[cells[i]] = Math.Max(1, Math.Min(IntervalHours, hours[i]));
    }
}
