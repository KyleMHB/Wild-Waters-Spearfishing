using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace Spearfishing;

// The hatchery's tuning (fish recovery ticket 04); the numbers and why are in Buildings_Hatchery.xml.
public class CompProperties_Hatchery : CompProperties
{
    // In-game days to fill one batch while powered and fed.
    public float cycleDays = 3f;
    // Fry in a full batch: the fish the stock gains on release, before the cap at capacity.
    public int batchFish = 30;
    // Feed units (CompRefuelable fuel, 0.05 nutrition each) one batch uses up.
    public float feedPerBatch = 240f;

    public CompProperties_Hatchery() => compClass = typeof(CompHatchery);
}

// Fills a batch of fry while powered, fed and fish stock management is on, and puts each full batch out as a pail at the
// interaction cell for a hauler. The next batch waits until the last pail is released or lost. Feed is used in step with
// the batch, so partial feed gives partial progress. With management off the hatchery stands idle: nothing advances and no
// pail is released, and turning management on resumes it where it was (ADR 0015 revised). Saves its progress, its water
// and its waiting pail; CompRefuelable saves the feed.
[StaticConstructorOnStartup]
public class CompHatchery : ThingComp
{
    private static readonly Texture2D ChooseWaterIcon = ContentFinder<Texture2D>.Get("Things/Spearfishing/Item/FryBatch");

    private float progress;
    private IntVec3 targetCell = IntVec3.Invalid;
    private Thing pail;

    // The fish stock version at which no fishing water was found, so a map with none isn't searched again until its water
    // changes.
    private int noWaterAtVersion = -1;

    public CompProperties_Hatchery Props => (CompProperties_Hatchery)props;

    private CompPowerTrader Power => parent.GetComp<CompPowerTrader>();

    private CompRefuelable Feed => parent.GetComp<CompRefuelable>();

    // How full the batch in the tank is, 0 to 1.
    public float Progress
    {
        get => progress;
        set => progress = Mathf.Clamp01(value);
    }

    // The last pail, until a hauler releases it or it is lost.
    public Thing WaitingPail => pail is { Destroyed: false } ? pail : null;

    public bool PowerOn => Power is not { PowerOn: false };

    // Whether the batch fills now.
    public bool Working => FishStockManagement.On && PowerOn && Feed is { HasFuel: true } && WaitingPail == null;

    // The chosen water: a cell of a body of fishing water, defaulting to the nearest to the hatchery. Invalid while the map
    // has none.
    public IntVec3 TargetCell
    {
        get
        {
            Map map = parent.MapHeld;
            if (map == null) return targetCell;
            MapComponent_FishStock fishStock = MapComponent_FishStock.Of(map);
            if (targetCell.IsValid && targetCell.InBounds(map) && fishStock.BodyAt(targetCell) >= 0) return targetCell;
            int version = fishStock.Stock.Version;
            if (noWaterAtVersion == version) return IntVec3.Invalid;
            IntVec3 found = FryRelease.Resolve(map, targetCell, parent.Position);
            if (found.IsValid) targetCell = found;
            else noWaterAtVersion = version;
            return found;
        }
    }

    public void SetTarget(IntVec3 cell)
    {
        targetCell = cell;
        noWaterAtVersion = -1;
    }

    public override void PostSpawnSetup(bool respawningAfterLoad)
    {
        base.PostSpawnSetup(respawningAfterLoad);
        if (!targetCell.IsValid) _ = TargetCell;
        UpdatePowerDraw();
    }

    public override void CompTickRare()
    {
        base.CompTickRare();
        UpdatePowerDraw();
        Advance(GenTicks.TickRareInterval);
    }

    // Draws its full power only while it has something to fill: none while fish stock management is off, the tank is out
    // of feed or a pail waits for a hauler, as vanilla machines idle. Not Working itself, which needs power on and so would
    // never turn the draw back on.
    private void UpdatePowerDraw()
    {
        CompPowerTrader power = Power;
        if (power == null) return;
        bool busy = FishStockManagement.On && Feed is { HasFuel: true } && WaitingPail == null;
        power.PowerOutput = busy ? -power.Props.PowerConsumption : 0f;
    }

    // Runs `ticks` of filling: the batch gains its share of a cycle and uses its share of a batch's feed, less when the feed
    // runs short. A full batch becomes a pail.
    public void Advance(int ticks)
    {
        if (!Working) return;
        CompRefuelable feed = Feed;
        float step = Mathf.Min(ticks / (Props.cycleDays * GenDate.TicksPerDay), 1f - progress);
        float need = step * Props.feedPerBatch;
        if (feed.Fuel < need)
        {
            step *= feed.Fuel / need;
            need = feed.Fuel;
        }
        feed.ConsumeFuel(need);
        progress += step;
        if (progress >= 1f - 0.0001f) FillPail();
    }

    private void FillPail()
    {
        progress = 0f;
        var made = (FryBatch)ThingMaker.MakeThing(HatcheryDefOf.Spearfishing_FryBatch);
        made.Init(Props.batchFish, parent, TargetCell);
        if (GenPlace.TryPlaceThing(made, parent.InteractionCell, parent.Map, ThingPlaceMode.Near)) pail = made;
    }

    public override IEnumerable<Gizmo> CompGetGizmosExtra()
    {
        foreach (Gizmo gizmo in base.CompGetGizmosExtra()) yield return gizmo;
        if (parent.Faction != Faction.OfPlayer) yield break;
        yield return new Command_Action
        {
            defaultLabel = "Spearfishing_HatcheryChooseWater".Translate(),
            defaultDesc = "Spearfishing_HatcheryChooseWaterDesc".Translate(),
            icon = ChooseWaterIcon,
            action = () =>
            {
                Map map = parent.Map;
                var parms = new TargetingParameters
                {
                    canTargetLocations = true,
                    canTargetPawns = false,
                    canTargetBuildings = false,
                    canTargetItems = false,
                    validator = t => t.Cell.InBounds(map) && MapComponent_FishStock.Of(map).BodyAt(t.Cell) >= 0,
                };
                Find.Targeter.BeginTargeting(parms, t => SetTarget(t.Cell));
            },
        };
    }

    public override void PostDrawExtraSelectionOverlays()
    {
        base.PostDrawExtraSelectionOverlays();
        IntVec3 target = TargetCell;
        if (!target.IsValid) return;
        GenDraw.DrawLineBetween(parent.TrueCenter(), target.ToVector3Shifted());
        GenDraw.DrawTargetHighlight(target);
    }

    public override string CompInspectStringExtra()
    {
        var lines = new List<string>();
        if (!FishStockManagement.On) lines.Add("Spearfishing_HatcheryIdle".Translate());
        if (WaitingPail != null) lines.Add("Spearfishing_HatcheryPailWaiting".Translate(Props.batchFish));
        else lines.Add("Spearfishing_HatcheryProgress".Translate(progress.ToStringPercent(), Props.batchFish));
        IntVec3 target = TargetCell;
        lines.Add(target.IsValid
            ? "Spearfishing_HatcheryTarget".Translate(FryRelease.WaterLabel(parent.Map, target))
            : "Spearfishing_HatcheryNoWater".Translate());
        return string.Join("\n", lines);
    }

    public override void PostExposeData()
    {
        base.PostExposeData();
        if (Scribe.mode == LoadSaveMode.Saving && pail is { Destroyed: true }) pail = null;
        Scribe_Values.Look(ref progress, "fryProgress");
        Scribe_Values.Look(ref targetCell, "fryTargetCell", IntVec3.Invalid);
        Scribe_References.Look(ref pail, "fryPail");
    }
}
