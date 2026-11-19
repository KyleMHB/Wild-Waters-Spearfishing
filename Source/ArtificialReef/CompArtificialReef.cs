using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace Spearfishing;

public class CompProperties_ArtificialReef : CompProperties
{
    // About a season (spec story 9).
    public float daysToReef = 15f;

    public CompProperties_ArtificialReef() => compClass = typeof(CompArtificialReef);
}

// A built artificial reef growing into reef: it counts the ticks it has grown while fish stock management is on, and when they
// reach daysToReef it marks its cell as reef through the reef grid (so its water's reef count and regrowth follow, ADR 0016)
// and removes itself. With management off the count waits; on again it carries on (ADR 0015 revised).
//
// The frame is printed under the water, at Waves' sea-life render queue like the reef overlay, in three stages of growth
// (art/artificial-reef/APPROVAL.md): built for the first third, half way for the second, nearly reef for the last. The def's
// graphic is only the blueprint and the menu icon.
public class CompArtificialReef : ThingComp
{
    private int ticksGrown;

    public CompProperties_ArtificialReef Props => (CompProperties_ArtificialReef)props;

    public int TicksToReef => Mathf.RoundToInt(Props.daysToReef * GenDate.TicksPerDay);

    public int TicksGrown => ticksGrown;

    public float Progress => Mathf.Clamp01((float)ticksGrown / TicksToReef);

    // 0 built, 1 half way, 2 nearly reef.
    public int Stage => Progress < 1f / 3f ? 0 : Progress < 2f / 3f ? 1 : 2;

    public override void CompTickLong()
    {
        if (FishStockManagement.On) Advance(GenTicks.TickLongInterval);
    }

    // Grows the reef by `ticks`; the long tick calls this every 2000 ticks while management is on. Developer tests call it to
    // pass most of the 15 days at once.
    public void Advance(int ticks)
    {
        if (!parent.Spawned || ticks <= 0) return;
        int stageBefore = Stage;
        ticksGrown = Math.Min(ticksGrown + ticks, TicksToReef);
        if (ticksGrown >= TicksToReef)
        {
            TurnToReef();
            return;
        }
        if (Stage != stageBefore) parent.Map.mapDrawer.MapMeshDirty(parent.Position, (ulong)MapMeshFlagDefOf.Things);
    }

    // The reef grid takes the mark first, then the frame goes with nothing left behind: no steel back and no rubble. A cell that
    // has meanwhile become kelp or reef (habitat restoration) keeps its mark.
    private void TurnToReef()
    {
        Map map = parent.Map;
        IntVec3 cell = parent.Position;
        var floor = MapComponent_FishStock.Of(map);
        if (floor.MarkAt(cell) == FloorMark.Bare) floor.SetMark(cell, FloorMark.Reef);
        parent.Destroy(DestroyMode.Vanish);
    }

    public override void PostExposeData()
    {
        base.PostExposeData();
        Scribe_Values.Look(ref ticksGrown, "ticksGrown");
    }

    public override string CompInspectStringExtra()
    {
        if (!FishStockManagement.On) return "Spearfishing_ArtificialReefPaused".Translate();
        float daysLeft = (TicksToReef - ticksGrown) / (float)GenDate.TicksPerDay;
        return "Spearfishing_ArtificialReefGrowing".Translate(Progress.ToStringPercent(), daysLeft.ToString("0.#"));
    }

    // ---- Drawing ----------------------------------------------------------------------------------------------------------

    private const float ShallowStrength = 1f, DeepStrength = 0.7f;
    private static readonly Color32 SteelColor = new(105, 105, 105, 255); // vanilla Steel's stuff colour, as on the def

    private static readonly string[] StageTextures =
    {
        "Things/Spearfishing/Building/ArtificialReef/ArtificialReef",
        "Things/Spearfishing/Building/ArtificialReef/ArtificialReef_HalfWay",
        "Things/Spearfishing/Building/ArtificialReef/ArtificialReef_NearlyReef",
    };

    private static readonly Material[] stageMaterials = new Material[StageTextures.Length];

    public override bool DontDrawParent() => true;

    public override void PostPrintOnto(SectionLayer layer)
    {
        Map map = parent.Map;
        bool deep = parent.Position.GetTerrain(map) == TerrainDefOf.WaterOceanDeep;
        Color32 tint = SteelColor;
        tint.a = (byte)Mathf.RoundToInt((deep ? DeepStrength : ShallowStrength) * 255f);
        Vector3 center = parent.TrueCenter();
        center.y = AltitudeLayer.TerrainScatter.AltitudeFor();
        Printer_Plane.PrintPlane(layer, center, Vector2.one, StageMaterial(Stage), colors: new[] { tint, tint, tint, tint });
    }

    // Made on first print, during play: reading Waves' queue runs its material setup. The same shader as the reef overlay, so
    // day and night light the frame as they light the water over it.
    private static Material StageMaterial(int stage)
    {
        if (stageMaterials[stage] != null) return stageMaterials[stage];
        var material = new Material(ShaderDatabase.TransparentPostLight) { mainTexture = ContentFinder<Texture2D>.Get(StageTextures[stage]) };
        if (WavesBridge.UnderwaterRenderQueue is { } queue) material.renderQueue = queue;
        return stageMaterials[stage] = material;
    }
}
