using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace Spearfishing;

public class Designator_ZoneAdd_Spearfishing : Designator_ZoneAdd
{
    protected override string NewZoneLabel => "Spearfishing_ZoneLabel".Translate();

    public Designator_ZoneAdd_Spearfishing()
    {
        zoneTypeToPlace = typeof(Zone_Spearfishing);
        defaultLabel = "Spearfishing_ZoneLabel".Translate();
        defaultDesc = "Spearfishing_DesignatorZoneDesc".Translate();
        // Placeholder until the mod has its own icon (no Waves or DLC art).
        icon = ContentFinder<Texture2D>.Get("UI/Designators/ZoneCreate_Growing");
    }

    // The reason the last refused cell gave, posted when a whole paint is refused.
    private string lastRefusal;

    public override AcceptanceReport CanDesignateCell(IntVec3 c)
    {
        if (!c.InBounds(Map)) return false;
        FishingWaterRefusal refusal = WavesBridge.RefusalAt(Map, c);
        if (refusal != FishingWaterRefusal.None)
        {
            lastRefusal = RefusalText(refusal);
            return lastRefusal;
        }
        return base.CanDesignateCell(c);
    }

    // Each refusal has its own translated reason (ticket 24), so the player learns what to look for.
    public static string RefusalText(FishingWaterRefusal refusal) => refusal switch
    {
        FishingWaterRefusal.Land => "Spearfishing_ZoneRefused_Land".Translate(),
        FishingWaterRefusal.Shallow => "Spearfishing_ZoneRefused_Shallow".Translate(),
        FishingWaterRefusal.Frozen => "Spearfishing_ZoneRefused_Frozen".Translate(),
        FishingWaterRefusal.Toxic => "Spearfishing_ZoneRefused_Toxic".Translate(),
        FishingWaterRefusal.Marsh => "Spearfishing_ZoneRefused_Marsh".Translate(),
        FishingWaterRefusal.Cave => "Spearfishing_ZoneRefused_Cave".Translate(),
        _ => "Spearfishing_ZoneRefused_NotSwimmable".Translate(),
    };

    // The drag tool filters cells before calling this, but vanilla's base adds whatever it is given. Filter here too, so no
    // caller (other mods, dev tools) can put land or water nobody swims in into a spearfishing zone.
    public override void DesignateMultiCell(IEnumerable<IntVec3> cells)
    {
        var accepted = cells.Where(c => CanDesignateCell(c).Accepted).ToList();
        if (accepted.Count == 0)
        {
            Finalize(somethingSucceeded: false);
            return;
        }
        base.DesignateMultiCell(accepted);
    }

    protected override void FinalizeDesignationFailed()
    {
        base.FinalizeDesignationFailed();
        Messages.Message(lastRefusal ?? RefusalText(FishingWaterRefusal.NotSwimmable), MessageTypeDefOf.RejectInput, historical: false);
    }

    protected override Zone MakeNewZone() => new Zone_Spearfishing(Find.CurrentMap.zoneManager);
}

public class Designator_ZoneAdd_Spearfishing_Expand : Designator_ZoneAdd_Spearfishing
{
    public Designator_ZoneAdd_Spearfishing_Expand()
    {
        defaultLabel = "DesignatorZoneExpand".Translate();
        hotKey = KeyBindingDefOf.Misc6;
    }
}
