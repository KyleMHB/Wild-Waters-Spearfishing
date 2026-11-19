using System;

namespace Spearfishing;

// Invasive predators (threat events ticket 03, ADR 0017): a count kept with one body of fishing water that grows toward a
// maximum and cuts that water's regrowth. Plain C# like the rest of this folder.
//
// The numbers, and why (2026-11-18):
// - Maximum: a 24th of the water's capacity, so a full 2400-fish sea holds at most 100 (the spec's "Invasive lionfish: 40,
//   cutting regrowth by 20%" is that sea at 40 of 100). It scales with capacity because culling is paced by catches, and a
//   water's catches are paced by its regrowth: a fixed maximum would leave a small lake, which regrows a few fish a day, unable
//   ever to clear it.
// - Growth: logistic at 0.3 a day, so the count climbs from a tenth of its maximum to nine tenths in about 15 days, one season
//   (ln 81 / 0.3 = 14.6 days).
// - Catch chance: count / maximum, as the spec says, with no extra factor. Divers keeping a water at its fish-down limit
//   catch about its peak regrowth, about 2% (lake) to 2.5% (sea with typical reef) of capacity a day. Against a maximum of
//   capacity / 24 that culls each predator at 0.47 (lake) to 0.6 (sea) a day, above growth's 0.3, so steady fishing clears
//   the water in one to two weeks, faster while there is a backlog of stock to fish down; light fishing only holds the count
//   below the maximum.
public static class PredatorRules
{
    public const float CapacityPerPredator = 24f;
    public const float GrowthPerDay = 0.3f;
    public const float StartShare = 0.1f;
    // The most a full count cuts its water's regrowth by.
    public const float MaxRegrowthCut = 0.5f;
    // A count below this after a cull is none left: the count grows as a fraction but predators are culled one by one.
    public const float ClearedBelow = 0.5f;

    // The maximum for a water of this capacity: at least one.
    public static float Maximum(float capacity) => Math.Max(1f, (float)Math.Round(capacity / CapacityPerPredator));

    // An outbreak's first count: about a tenth of the maximum, at least one.
    public static float StartCount(float maximum) => Math.Max(1f, (float)Math.Round(maximum * StartShare));

    // The share of regrowth a count cuts: 0 with none, MaxRegrowthCut at the maximum.
    public static float RegrowthCut(float count, float maximum) =>
        maximum <= 0f || count <= 0f ? 0f : MaxRegrowthCut * Math.Min(1f, count / maximum);

    // The chance that a successful catch in the water is a predator.
    public static float CatchShare(float count, float maximum) => maximum <= 0f || count <= 0f ? 0f : Math.Min(1f, count / maximum);

    // One in-game hour of logistic growth toward the maximum.
    public static float GrowOneHour(float count, float maximum)
    {
        if (count <= 0f || maximum <= 0f) return count;
        float gain = GrowthPerDay * count * (1f - count / maximum) / FishStockRules.HoursPerDay;
        return Math.Min(maximum, count + Math.Max(0f, gain));
    }

    // The count as the player sees it: whole predators, at least one while any are left.
    public static int Shown(float count) => count <= 0f ? 0 : Math.Max(1, (int)Math.Round(count));
}
