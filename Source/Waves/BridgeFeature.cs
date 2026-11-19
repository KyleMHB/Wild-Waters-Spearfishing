using System;
using Verse;

namespace Spearfishing;

// One feature that depends on Waves or Living Waters. If anything it needs is missing (an older or changed mod lacks a
// member), the feature turns itself off and logs once, and every other feature keeps working.
internal sealed class BridgeFeature
{
    public string Name { get; }
    public bool Available { get; private set; }

    private BridgeFeature(string name) => Name = name;

    // `resolve` looks up everything the feature needs and returns null on success, or a description of what is missing.
    // `mod` names the mod it reads, for the warning: Waves unless told otherwise. `advice` replaces the warning's closing
    // sentence, for a feature whose failure means the player runs too old a version. A feature that `requires` another one is
    // off without a warning of its own while that one is off: its single warning already says why.
    public static BridgeFeature Resolve(string name, Func<string> resolve, string mod = "RimWorld: Waves", string advice = null, // not translated
        BridgeFeature requires = null)
    {
        var feature = new BridgeFeature(name);
        if (requires is { Available: false }) return feature;
        string missing;
        try
        {
            // A developer test can mark the feature missing before it looks anything up.
            missing = SpearfishingMod.Settings?.simulateMissingWavesFeatures?.Contains(name) == true
                ? "a developer test simulated its target as missing" // not translated
                : resolve();
        }
        catch (Exception e)
        {
            missing = e.GetType().Name + ": " + e.Message;
        }
        feature.Available = missing == null;
        if (missing != null)
            // A warning, not an error: the mod keeps running with this feature off. Not translated (developer text).
            Log.Warning($"[Spearfishing] Waves bridge: '{name}' is turned off because {missing}. {advice ?? mod + " may have changed; please report it."}"); // not translated
        return feature;
    }
}
