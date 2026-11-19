using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace Spearfishing;

// The mod's options. Later options join as one field, one Scribe line and one row in Draw, with their text in the Keyed file.
public class SpearfishingSettings : ModSettings
{
    // Hide divers under the water and draw fish shadows and the speared-shadow burst around them (ticket 12).
    public bool diveVisuals = true;

    // Fish stock management (ADR 0015): logistic regrowth and the regrowth line on the zone; off is flat regrowth.
    public bool fishStockManagement = true;

    // Threat events (ADR 0015, revised): each fires only while its switch and fishStockManagement are both on. Set them
    // through ThreatEvents.Set, which ends that kind's outbreaks when one goes off.
    public bool urchinEvents = true;
    public bool invasivePredatorEvents = true;

    // Gear tiers ticket 11: the chance per spearfishing trip of a shark in deep ocean, 0 for none.
    public float sharkChance = DiveRules.DefaultSharkChance;

    // Developer only, never drawn: names of Waves bridge features to treat as missing at load, so the failure path can be
    // tested without changing Waves (ticket 13). Only the developer test harness writes it, through its own settings file;
    // a player's settings never contain it, so it is always empty in play.
    public List<string> simulateMissingWavesFeatures = new();

    public override void ExposeData()
    {
        base.ExposeData();
        Scribe_Values.Look(ref diveVisuals, "diveVisuals", true);
        Scribe_Values.Look(ref fishStockManagement, "fishStockManagement", true);
        Scribe_Values.Look(ref urchinEvents, "urchinEvents", true);
        Scribe_Values.Look(ref invasivePredatorEvents, "invasivePredatorEvents", true);
        Scribe_Values.Look(ref sharkChance, "sharkChance", DiveRules.DefaultSharkChance);
        // Written only while non-empty, so a player's settings file never gains the entry.
        if (Scribe.mode != LoadSaveMode.Saving || simulateMissingWavesFeatures.Count > 0)
            Scribe_Collections.Look(ref simulateMissingWavesFeatures, "simulateMissingWavesFeatures", LookMode.Value);
        simulateMissingWavesFeatures ??= new List<string>();
    }

    public void Draw(Rect inRect)
    {
        var list = new Listing_Standard();
        list.Begin(inRect);
        list.CheckboxLabeled("Spearfishing_SettingDiveVisuals".Translate(), ref diveVisuals, "Spearfishing_SettingDiveVisualsDesc".Translate());
        bool management = fishStockManagement;
        list.CheckboxLabeled("Spearfishing_SettingFishStockManagement".Translate(), ref management, "Spearfishing_SettingFishStockManagementDesc".Translate());
        // Switched in a game, the recovery features react at once (ManagementGate).
        ManagementGate.Set(management);
        // The event switches sit under it, greyed while it is off, since an event never fires without it.
        list.Indent();
        EventSwitch(list, ThreatKind.Urchins, urchinEvents, "Spearfishing_SettingUrchinEvents", "Spearfishing_SettingUrchinEventsDesc");
        EventSwitch(list, ThreatKind.InvasivePredators, invasivePredatorEvents, "Spearfishing_SettingInvasivePredatorEvents",
            "Spearfishing_SettingInvasivePredatorEventsDesc");
        list.Outdent();
        list.Gap();
        list.Label("Spearfishing_SettingSharkChance".Translate(sharkChance.ToStringPercent("0.#")), tooltip: "Spearfishing_SettingSharkChanceDesc".Translate());
        // Steps of half a percent, so the 1% default is easy to find again.
        sharkChance = Mathf.Round(list.Slider(sharkChance, 0f, DiveRules.MaxSharkChance) * 200f) / 200f;
        list.End();
    }

    // Listing_Standard's checkbox has no disabled state, so the row is drawn with Widgets directly.
    private void EventSwitch(Listing_Standard list, ThreatKind kind, bool value, string labelKey, string tooltipKey)
    {
        Rect row = list.GetRect(Text.LineHeight);
        if (Mouse.IsOver(row)) Widgets.DrawHighlight(row);
        TooltipHandler.TipRegion(row, tooltipKey.Translate());
        Widgets.CheckboxLabeled(row, labelKey.Translate(), ref value, disabled: !fishStockManagement);
        list.Gap(list.verticalSpacing);
        // Switched off in a game, that kind's outbreaks end at once (ThreatEvents).
        ThreatEvents.Set(kind, value);
    }
}
