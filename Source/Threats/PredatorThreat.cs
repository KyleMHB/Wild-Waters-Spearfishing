using RimWorld;
using Verse;

namespace Spearfishing;

// Invasive predators (spec stories 17-25, ADR 0017): any body of fishing water. Start gives the body a predator count in the
// fish stock model (FishStockModel, PredatorRules), which grows toward its maximum and cuts the body's regrowth; End clears it.
// Spearfishing culls them: a share of successful catches in that water are predators (Notify_Caught). Odyssey's line fishing
// never calls it, so only spearfishing culls.
public sealed class PredatorThreat : ThreatEvent
{
    public override ThreatKind Kind => ThreatKind.InvasivePredators;

    public override bool SwitchOn => SpearfishingMod.Settings == null || SpearfishingMod.Settings.invasivePredatorEvents;

    // A random cell of fishing water, so a body is picked in proportion to its size.
    public override bool TryFindTarget(Map map, out IntVec3 cell)
    {
        cell = IntVec3.Invalid;
        MapComponent_FishStock fishStock = MapComponent_FishStock.Of(map);
        if (fishStock == null || fishStock.Stock.BodyCount == 0) return false;
        int seen = 0;
        int count = map.cellIndices.NumGridCells;
        for (int i = 0; i < count; i++)
        {
            if (fishStock.Stock.BodyAt(i) < 0) continue;
            seen++;
            if (Rand.Range(0, seen) == 0) cell = map.cellIndices.IndexToCell(i);
        }
        return seen > 0;
    }

    // The body at the outbreak's cell gets about a tenth of its maximum.
    public override bool Start(Map map, Outbreak outbreak)
    {
        MapComponent_FishStock fishStock = MapComponent_FishStock.Of(map);
        int body = fishStock?.BodyAt(outbreak.Cell) ?? -1;
        if (body < 0) return false;
        float maximum = PredatorRules.Maximum(fishStock.Stock.Capacity(body));
        fishStock.Stock.SetPredators(map.cellIndices.CellToIndex(outbreak.Cell), PredatorRules.StartCount(maximum), maximum);
        return true;
    }

    // Culled out or switched off: no predators are left anywhere on the map.
    public override void End(Map map, Outbreak outbreak) => MapComponent_FishStock.Of(map)?.Stock.ClearPredators();

    // A diver's successful catch at `at`: in water with predators it is a predator with chance count / maximum, which lowers
    // the count by one (the fish still lands as raw fish and came out of the stock like any catch). Culling the last one ends
    // the outbreak with a letter.
    public static void Notify_Caught(Map map, IntVec3 at)
    {
        MapComponent_FishStock fishStock = MapComponent_FishStock.Of(map);
        if (fishStock == null || !fishStock.Stock.HasPredators) return;
        int body = fishStock.BodyAt(at);
        if (!Rand.Chance(fishStock.Stock.PredatorCatchShare(body))) return;
        if (!fishStock.Stock.CullPredator(body)) return;
        ThreatEvents.Of(map).End(ThreatKind.InvasivePredators);
        Find.LetterStack.ReceiveLetter("Spearfishing_PredatorsCulledLabel".Translate(PredatorName(map, at).Named("PREDATOR")),
            "Spearfishing_PredatorsCulled".Translate(PredatorName(map, at).Named("PREDATOR"), FryRelease.WaterLabel(map, at).Named("WATER")),
            LetterDefOf.PositiveEvent, new LookTargets(at, map));
    }

    // The zone inspect line for a body with predators, such as "Invasive lionfish: 40, cutting regrowth by 20%", with its
    // leading newline; empty for a body without.
    public static string InspectLine(Map map, int body)
    {
        FishStockModel model = MapComponent_FishStock.For(map);
        float count = model.Predators(body);
        if (count <= 0f) return "";
        return "\n" + "Spearfishing_ZonePredators".Translate(PredatorName(map, map.cellIndices.IndexToCell(model.PredatorCell)),
            PredatorRules.Shown(count), model.PredatorCut(body).ToStringPercent()).Resolve();
    }

    // The regrowth tooltip's line on the cut, with its leading blank line; empty for a body without predators.
    public static string RegrowthTipLine(Map map, int body)
    {
        FishStockModel model = MapComponent_FishStock.For(map);
        if (model.Predators(body) <= 0f) return "";
        return "\n\n" + "Spearfishing_ZonePredatorsTip".Translate(PredatorName(map, map.cellIndices.IndexToCell(model.PredatorCell)),
            model.PredatorCut(body).ToStringPercent()).Resolve();
    }

    // "lionfish" at sea, "snakeheads" in lakes and rivers (spec story 18).
    public static string PredatorName(Map map, IntVec3 cell)
    {
        TerrainDef terrain = cell.IsValid && cell.InBounds(map) ? cell.GetTerrain(map) : null;
        return WavesBridge.IsSea(terrain) ? "Spearfishing_PredatorLionfish".Translate() : "Spearfishing_PredatorSnakehead".Translate();
    }

    public override NamedArgument[] LetterArgs(Map map, Outbreak outbreak) => new[]
    {
        FryRelease.WaterLabel(map, outbreak.Cell).Named("WATER"), PredatorName(map, outbreak.Cell).Named("PREDATOR"),
    };
}
