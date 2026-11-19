using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace Spearfishing;

// A zone's inspect string is plain text with no tooltips, so the regrowth line's explanation (fish stock management, ticket
// 06) is laid over the inspect string's area after the pane draws it.
[HarmonyPatch(typeof(InspectPaneFiller), nameof(InspectPaneFiller.DrawInspectStringFor))]
public static class InspectTooltipPatch
{
    public static void Postfix(ISelectable __0, Rect __1)
    {
        if (__0 is not Zone_Spearfishing zone) return;
        string tip = zone.RegrowthTooltip;
        if (tip != null) TooltipHandler.TipRegion(__1, tip);
    }
}
