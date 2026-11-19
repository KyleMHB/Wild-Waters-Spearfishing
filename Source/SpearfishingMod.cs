using HarmonyLib;
using UnityEngine;
using Verse;

namespace Spearfishing;

public class SpearfishingMod : Mod
{
    public const string HarmonyId = "kylemhb.wildwaters.spearfishing";

    public static SpearfishingSettings Settings { get; private set; }

    public SpearfishingMod(ModContentPack content) : base(content)
    {
        Settings = GetSettings<SpearfishingSettings>();
        var harmony = new Harmony(HarmonyId);
        // Waves loads first (About.xml loadAfter), so its assembly is present when the bridge resolves its members.
        WavesBridge.Initialize();
        ZoneSaveSplit.Initialize(harmony);
        JobSaveSplit.Initialize(harmony, content.PackageId);
        harmony.PatchAll(typeof(SpearfishingMod).Assembly);
    }

    public override string SettingsCategory() => Content.Name;

    public override void DoSettingsWindowContents(Rect inRect) => Settings.Draw(inRect);
}
