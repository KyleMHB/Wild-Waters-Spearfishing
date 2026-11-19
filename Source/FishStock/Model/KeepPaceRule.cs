using System;

namespace Spearfishing;

// With fish stock management on, our water regrows logistically while a population sharing it by fraction (Odyssey's,
// ADR 0013) regrows flat. A dive reads the lower of the two fractions, so any hour ours regrows faster would be cancelled
// unless the other population is moved along with ours (ADR 0015). Plain arithmetic on shares of each population's
// maximum, with no Odyssey types.
public static class KeepPaceRule
{
    // The share of its maximum the other population gains to keep pace after one hour of our regrowth: the share our body
    // gained less the share the other population's own regrowth added, never below zero and never past our fraction. A
    // population already at or above our fraction gains nothing and is never lowered. An other regrowth below zero (a
    // condition killing fish, such as Odyssey's gill rot) added nothing, so it counts as zero: our gain is still passed on.
    public static float TopUpShare(float ourGainShare, float otherRegrowthShare, float ourFraction, float otherFraction)
    {
        float behind = ourGainShare - Math.Max(0f, otherRegrowthShare);
        float room = ourFraction - otherFraction;
        return Math.Max(0f, Math.Min(behind, room));
    }
}
