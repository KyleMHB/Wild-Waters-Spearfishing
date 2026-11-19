using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace Spearfishing;

// Water where divers may spearfish. The zone holds only its cells and its fish-down limit; the fish stock belongs to the body
// of water under it (ADR 0013), and the zone reads it from the map's model. The limit is saved with the zone, which itself is
// saved inside MapComponent_FishStock (ADR 0009), so removing the mod drops it along with the zone.
public class Zone_Spearfishing : Zone
{
    // With fish stock management on, the share of its water's capacity this zone leaves: its divers stop below it. Each zone
    // keeps its own, even on shared water (ticket 07).
    private float fishDownLimit = FishStockRules.DefaultFishDownLimit;

    // The zone's view of its body of water. Built on first use, because cells loaded from a save bypass AddCell.
    [Unsaved] private ZoneFishStock fishStock;

    // Used by the save loader.
    public Zone_Spearfishing()
    {
    }

    public Zone_Spearfishing(ZoneManager zoneManager) : base("Spearfishing_ZoneLabel".Translate(), zoneManager)
    {
    }

    public override bool IsMultiselectable => true;

    protected override Color NextZoneColor => ZoneColorUtility.NextFishingZoneColor();

    public float FishStock => Stock.Stock;

    public float FishCapacity => Stock.Capacity;

    public float FishStockFraction => Stock.StockFraction;

    public float FishDownLimit
    {
        get => fishDownLimit;
        set => fishDownLimit = FishStockRules.ClampFishDownLimit(value);
    }

    // Where this zone's divers stop: its fish-down limit with fish stock management on, the fixed quarter with it off.
    public float StopFraction => FishStockRules.StopFraction(FishStockManagement.On, fishDownLimit);

    // False when the zone's water is below the stop for a dive. With Odyssey, line fishing that has fished the water down
    // stops divers too (ADR 0013): Odyssey's population at the zone's water must also be above the same stop, so both stocks
    // stop divers at the same point. A diver already out finishes the dive and heads home through the trip's usual exits.
    public bool WorthADive
    {
        get
        {
            float stop = StopFraction;
            return Stock.WorthADiveAt(stop) && OdysseyWorthADive(stop);
        }
    }

    // Odyssey's population at one zone cell in the zone's body of water, against the active stop. Odyssey's bodies need not
    // match ours, so it is read at a cell, kept until the zone's cells or the bodies change.
    private bool OdysseyWorthADive(float stop)
    {
        if (!OdysseyFish.Sharing) return true;
        MapComponent_FishStock fishStock = MapComponent_FishStock.Of(Map);
        int body = Stock.Body;
        if (!odysseyCell.IsValid || Map.zoneManager.ZoneAt(odysseyCell) != this || fishStock.BodyAt(odysseyCell) != body)
            odysseyCell = cells.FirstOrFallback(c => fishStock.BodyAt(c) == body, IntVec3.Invalid);
        return !odysseyCell.IsValid || OdysseyFish.PopulationFraction(Map, odysseyCell) >= stop;
    }

    [Unsaved] private IntVec3 odysseyCell = IntVec3.Invalid;

    // Takes a catch from the body of water at the spot; returns the fish taken.
    public float TakeCatch(IntVec3 spot, float fish = 1f) => Stock.TakeCatch(Map.cellIndices.CellToIndex(spot), fish);

    // A zone cell to dive at, reef and kelp first among the samples, or IntVec3.Invalid for an empty zone.
    public IntVec3 PickDiveSpot()
    {
        int cell = Stock.PickDiveSpot(() => Rand.Value, floorFactor: FloorFactor);
        return cell < 0 ? IntVec3.Invalid : Map.cellIndices.IndexToCell(cell);
    }

    // The first of the sampled cells that fits, reef and kelp first, or IntVec3.Invalid when none does (ticket 28).
    public IntVec3 PickDiveSpot(Func<IntVec3, bool> fits)
    {
        int cell = Stock.PickDiveSpot(() => Rand.Value, i => fits(Map.cellIndices.IndexToCell(i)), floorFactor: FloorFactor);
        return cell < 0 ? IntVec3.Invalid : Map.cellIndices.IndexToCell(cell);
    }

    private float FloorFactor(int cell) => MapComponent_FishStock.Of(Map).FloorFactorAt(cell);

    // The zone's edge cells, nearest the shore first (ticket 28): where a diver goes when no sampled spot is within
    // reach, and the quick test of whether any cell is. Every cell needs a shore search, so the list is kept a while, and
    // dropped at once when the zone's cells change. Interior cells are left out: the way to shore from one crosses the edge.
    public List<IntVec3> EdgeCellsNearestShore()
    {
        if (edgeCells != null && Find.TickManager.TicksGame - edgeCellsTick < EdgeCellsKeepTicks) return edgeCells;
        Map map = Map;
        edgeCells = cells.Where(c => GenAdj.CardinalDirections.Any(d => !(c + d).InBounds(map) || map.zoneManager.ZoneAt(c + d) != this))
            .OrderBy(c => SpearfishingUtility.DistanceToShoreSquared(map, c)).ToList();
        edgeCellsTick = Find.TickManager.TicksGame;
        return edgeCells;
    }

    // Long enough that a busy diver doesn't search again every work check, short enough to notice new land or a new wall.
    private const int EdgeCellsKeepTicks = 2500;

    [Unsaved] private List<IntVec3> edgeCells;
    [Unsaved] private int edgeCellsTick;

    private ZoneFishStock Stock
    {
        get
        {
            if (fishStock == null)
            {
                fishStock = new ZoneFishStock(MapComponent_FishStock.For(Map));
                foreach (IntVec3 cell in cells) fishStock.Add(Map.cellIndices.CellToIndex(cell));
            }
            return fishStock;
        }
    }

    public override void AddCell(IntVec3 c)
    {
        int before = cells.Count;
        base.AddCell(c);
        edgeCells = null;
        if (fishStock != null && cells.Count > before) fishStock.Add(Map.cellIndices.CellToIndex(c));
    }

    public override void RemoveCell(IntVec3 c)
    {
        int before = cells.Count;
        base.RemoveCell(c);
        edgeCells = null;
        if (fishStock != null && cells.Count < before) fishStock.Remove(Map.cellIndices.CellToIndex(c));
    }

    public override string GetInspectString()
    {
        string text = base.GetInspectString() + "\n" + "Spearfishing_ZoneFishStock".Translate(
            FishStockFraction.ToStringPercent(), FishStock.ToString("0"), FishCapacity.ToString("0"));
        // RegrowthTooltip's own null test, without building the whole tooltip every frame the inspect pane is open.
        if (FishStockManagement.On && FishCapacity > 0f) text += "\n" + "Spearfishing_ZoneFishRegrowth".Translate(FishRegrowthPerDay.ToString("0.#"));
        if (FishStockManagement.On) text += PredatorThreat.InspectLine(Map, Stock.Body);
        bool management = FishStockManagement.On;
        if (management && FishCapacity > 0f) text += "\n" + "Spearfishing_ZoneFishDownLimit".Translate(fishDownLimit.ToStringPercent());
        if (FishCapacity > 0f && !WorthADive)
            text += "\n" + (management ? "Spearfishing_ZoneBelowFishDownLimit".Translate() : "Spearfishing_ZoneNotWorthADive".Translate());
        return text;
    }

    public override void ExposeData()
    {
        base.ExposeData();
        Scribe_Values.Look(ref fishDownLimit, "fishDownLimit", FishStockRules.DefaultFishDownLimit);
        if (Scribe.mode == LoadSaveMode.PostLoadInit) fishDownLimit = FishStockRules.ClampFishDownLimit(fishDownLimit);
    }

    // With fish stock management on, buttons to step this zone's fish-down limit down (a burst of fish in a famine) or up
    // (rest the water). With several zones selected, each steps its own limit.
    public override IEnumerable<Gizmo> GetGizmos()
    {
        foreach (Gizmo gizmo in base.GetGizmos()) yield return gizmo;
        if (!FishStockManagement.On) yield break;
        string current = fishDownLimit.ToStringPercent();
        yield return new Command_Action
        {
            defaultLabel = "Spearfishing_LowerFishDownLimit".Translate(),
            defaultDesc = "Spearfishing_LowerFishDownLimitDesc".Translate(current),
            icon = TexButton.Minus,
            action = () => FishDownLimit = fishDownLimit - FishStockRules.FishDownLimitStep,
            Disabled = fishDownLimit <= FishStockRules.MinFishDownLimit + 0.001f,
        };
        yield return new Command_Action
        {
            defaultLabel = "Spearfishing_RaiseFishDownLimit".Translate(),
            defaultDesc = "Spearfishing_RaiseFishDownLimitDesc".Translate(current),
            icon = TexButton.Plus,
            action = () => FishDownLimit = fishDownLimit + FishStockRules.FishDownLimitStep,
            Disabled = fishDownLimit >= FishStockRules.MaxFishDownLimit - 0.001f,
        };
    }

    // Fish the zone's water regrows a day at its current stock, under the rule the fish stock management setting picks.
    public float FishRegrowthPerDay => MapComponent_FishStock.For(Map).RegrowthPerDay(Stock.Body, FishStockManagement.Rule);

    // With fish stock management on, the inspect panel's tooltip (drawn by InspectTooltipPatch) explaining why the regrowth
    // line moves with the stock, then the base rate before the reef boost and the reef and kelp share behind it (ADR 0016),
    // then any invasive predators' cut (ADR 0017).
    // Null when management is off or the zone has no fishing water, and then no regrowth line shows.
    public string RegrowthTooltip
    {
        get
        {
            if (!FishStockManagement.On || FishCapacity <= 0f) return null;
            FishStockModel model = MapComponent_FishStock.For(Map);
            int body = Stock.Body;
            string share = model.ReefShare(body).ToStringPercent();
            return "Spearfishing_ZoneFishRegrowthTip".Translate().Resolve() + "\n\n" + "Spearfishing_ZoneFishRegrowthReefTip".Translate(
                model.BaseRegrowthPerDay(body, FishStockManagement.Rule).ToString("0.#"), share).Resolve() + PredatorThreat.RegrowthTipLine(Map, body);
        }
    }

    public override IEnumerable<Gizmo> GetZoneAddGizmos()
    {
        yield return DesignatorUtility.FindAllowedDesignator<Designator_ZoneAdd_Spearfishing_Expand>();
    }
}
