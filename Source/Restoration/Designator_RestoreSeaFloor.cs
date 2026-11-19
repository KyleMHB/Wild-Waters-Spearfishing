using RimWorld;
using UnityEngine;
using Verse;

namespace Spearfishing;

// "Restore sea floor" in the orders menu (fish recovery ticket 03): marks bare sea floor for divers to restore. Shown after
// the Spearfishing research, and only with fish stock management on (ADR 0015 revised).
public class Designator_RestoreSeaFloor : Designator_Cells
{
    public Designator_RestoreSeaFloor()
    {
        defaultLabel = "Spearfishing_DesignatorRestoreSeaFloor".Translate();
        defaultDesc = "Spearfishing_DesignatorRestoreSeaFloorDesc".Translate();
        icon = ContentFinder<Texture2D>.Get("UI/Designators/Spearfishing_RestoreSeaFloor");
        useMouseIcon = true;
        soundDragSustain = SoundDefOf.Designate_DragStandard;
        soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
        soundSucceeded = SoundDefOf.Designate_ExtractTree;
    }

    protected override DesignationDef Designation => RestorationDefOf.Spearfishing_RestoreSeaFloor;

    public override DrawStyleCategoryDef DrawStyleCategory => DrawStyleCategoryDefOf.Orders;

    public override bool DragDrawMeasurements => true;

    public override bool Visible =>
        FishStockManagement.On && (DiveGearDefOf.Spearfishing_Spearfishing.IsFinished || DebugSettings.godMode);

    public override AcceptanceReport CanDesignateCell(IntVec3 c)
    {
        if (!c.InBounds(Map) || c.Fogged(Map)) return false;
        if (!FishStockManagement.On) return false;
        if (HabitatRestoration.IsMarked(Map, c)) return false;
        if (!WavesBridge.IsSea(c.GetTerrain(Map))) return "Spearfishing_RestoreRefused_NotSea".Translate();
        // A culled urchin cell looks bare but keeps its reef or kelp mark, and grows it back on its own.
        if (MapComponent_FishStock.Of(Map).IsRecovering(c)) return "Spearfishing_RestoreRefused_Recovering".Translate();
        if (MapComponent_FishStock.Of(Map).MarkAt(c) != FloorMark.Bare) return "Spearfishing_RestoreRefused_NotBare".Translate();
        return AcceptanceReport.WasAccepted;
    }

    public override void DesignateSingleCell(IntVec3 c) => Map.designationManager.AddDesignation(new Designation(c, Designation));

    public override void SelectedUpdate() => GenUI.RenderMouseoverBracket();
}
