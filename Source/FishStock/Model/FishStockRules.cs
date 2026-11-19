using System;

namespace Spearfishing;

// The fish stock model (this folder) is plain C# with no RimWorld references, so its rules are tested without the game.
// It also compiles for the 1.6 build (net472): keep to APIs that exist there.

public static class FishStockRules
{
    // Capacity (ADR 0013): one fish per cell of fishing water, up to the same cap for any body of water, so a small lake
    // holds fewer fish than the sea and a huge ocean is not bottomless. The floor (reef, kelp, bare) and the depth never
    // change it. The cap was 1600 (40 fish a day) until 2026-11-17, when the author raised it so that one best-gear diver
    // (about 45 fish a day) no longer takes a whole sea's regrowth.
    public const float FishPerCell = 1f;
    public const float CapacityCap = 2400f;

    // With fish stock management off: a flat 2.5% of capacity a day, the same share Odyssey's water regrows, so a full
    // 2400-fish sea regrows 60 a day.
    public const float FlatRegrowthShare = 0.025f;

    // With fish stock management on: logistic regrowth of LogisticGrowthRate * stock * (1 - stock / capacity) a day, never
    // below the floor share so fished-out water still recovers, all times (1 + reef share), where reef share is the body's
    // reef and kelp cells over all its cells (ADR 0016). It peaks at half full, at a quarter of the rate times the boost. Near
    // empty or full it is slow.
    // The rate is set so a sea with the typical natural reef and kelp share peaks at 2.5% of capacity, the flat share: a full
    // 2400-fish coastal sea still regrows at most about 60 a day, as before reef sped regrowth, and the player's own reef adds
    // on top. TypicalReefShare is the median share measured on four new coastal maps (fish recovery ticket 01), which makes
    // the rate about 0.078; before the boost it was 0.1.
    public const float TypicalReefShare = 0.28f;
    public const float LogisticGrowthRate = 4f * FlatRegrowthShare / (1f + TypicalReefShare);
    public const float LogisticFloorShare = 0.0025f;

    // With fish stock management off, a zone whose water is below this fraction of its capacity is not worth a dive.
    public const float FixedStopFraction = 0.25f;

    // With fish stock management on, each zone's fish-down limit replaces the fixed stop (ticket 07): half by default, where
    // logistic regrowth is fastest, and set on the zone in steps between the bounds. The lowest bound still leaves some fish,
    // so a famine burst never strips the water bare.
    public const float DefaultFishDownLimit = 0.5f;
    public const float FishDownLimitStep = 0.1f;
    public const float MinFishDownLimit = 0.1f;
    public const float MaxFishDownLimit = 0.9f;

    // The fraction below which a zone's divers stop: its own fish-down limit with fish stock management on, the fixed quarter
    // with it off.
    public static float StopFraction(bool management, float fishDownLimit) => management ? ClampFishDownLimit(fishDownLimit) : FixedStopFraction;

    // A fish-down limit on the nearest step and within the bounds, so steps up and down never drift from round percentages.
    public static float ClampFishDownLimit(float limit)
    {
        float stepped = (float)Math.Round(limit / FishDownLimitStep) * FishDownLimitStep;
        return Math.Max(MinFishDownLimit, Math.Min(MaxFishDownLimit, stepped));
    }

    public const int HoursPerDay = 24;

    public static float Capacity(int cells) => Math.Min(cells * FishPerCell, CapacityCap);
}

// How a body of water regrows each day at a given stock. Run once an in-game hour, a twenty-fourth at a time. Flat is fish
// stock management off, Logistic is management on (ADR 0015).
public abstract class RegrowthRule
{
    public static readonly RegrowthRule Flat = new FlatRegrowth();
    public static readonly RegrowthRule Logistic = new LogisticRegrowth();

    // Fish gained in one day at this stock, before the reef boost and the cap at capacity.
    public abstract float PerDay(float stock, float capacity);

    // Whether reef and kelp speed this rule (ADR 0016): only with fish stock management on.
    public virtual bool ReefBoosts => false;

    private sealed class FlatRegrowth : RegrowthRule
    {
        public override float PerDay(float stock, float capacity) => capacity * FishStockRules.FlatRegrowthShare;
    }

    private sealed class LogisticRegrowth : RegrowthRule
    {
        public override bool ReefBoosts => true;

        public override float PerDay(float stock, float capacity)
        {
            if (capacity <= 0f) return 0f;
            float growth = FishStockRules.LogisticGrowthRate * stock * (1f - stock / capacity);
            return Math.Max(growth, capacity * FishStockRules.LogisticFloorShare);
        }
    }
}

// One body's saved state: a cell inside it and its stock as a fraction of capacity. The cell finds the body again after
// the bodies are rebuilt from the terrain on load.
public readonly struct SavedBody
{
    public readonly int Cell;
    public readonly float Fraction;

    public SavedBody(int cell, float fraction)
    {
        Cell = cell;
        Fraction = fraction;
    }
}
