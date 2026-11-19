using System;
using System.Linq;
using RimWorld;
using Verse;

namespace Spearfishing;

// Every contact with Odyssey's fishing lives here (ADR 0003). With Odyssey active a catch is one of Odyssey's own fish
// species for the water, picked the way line fishing picks them, and line fishing and spearfishing share the fish by
// fraction (ADR 0013): a dive reads the lower of our body's stock fraction and Odyssey's population fraction for the water
// body at the dive cell, and each catch lowers Odyssey's population by the same share of its maximum that it took from our
// body. Nothing patches Odyssey's fishing: its line catches lower its population, which dives then read. Our bodies of
// water stay our own flood fill; Odyssey's are only looked up at a cell, since the two need not match. With fish stock
// management on, Odyssey's population is also moved along with our hourly regrowth (KeepPace, ADR 0015).
//
// Odyssey's fishing types are in Core's assembly, so nothing here needs reflection. Nothing reaches them unless
// ModsConfig.OdysseyActive, and signatures outside this class carry no Odyssey types. Like a Waves bridge feature, if a
// game update breaks a call here the feature logs once and turns off, and catches fall back to our raw fish.
public static class OdysseyFish
{
    private static bool broken;

    private static bool Active => !broken && ModsConfig.OdysseyActive;

    // The fish item for one catch from the water at `water`: an Odyssey species, or our raw fish without Odyssey or when that
    // water has no Odyssey fish (a water body too small for fish, or a biome with none).
    public static ThingDef CatchDef(Map map, IntVec3 water)
    {
        if (Active && water.IsValid)
        {
            try
            {
                ThingDef species = PickSpecies(map, water);
                if (species != null) return species;
            }
            catch (Exception e)
            {
                TurnOff(e);
            }
        }
        return SpearfishingDefOf.Spearfishing_RawFish;
    }

    // Whether the pawn's ideoligion lets them fish, asked the way line fishing asks before offering work: a pawn whose
    // ideoligion prohibits slaughtering fish takes no spearfishing work either. Always true without Odyssey, which owns the
    // fish precepts and their history event.
    public static bool WillingToFish(Pawn pawn)
    {
        if (!Active || pawn.Ideo == null) return true;
        try
        {
            return new HistoryEvent(HistoryEventDefOf.SlaughteredFish, pawn.Named(HistoryEventArgsNames.Doer)).Notify_PawnAboutToDo_Job();
        }
        catch (Exception e)
        {
            TurnOff(e);
            return true;
        }
    }

    // Whether Odyssey shares the fish on this game: false without the DLC, or after a call here broke.
    public static bool Sharing => Active;

    // Odyssey's population as a fraction of its maximum for the water body at `water`: 1 (no limit) without Odyssey, off its
    // water bodies, or for a body where Odyssey placed no fish species (too small, or none rolled), so such a lake never
    // blocks a dive. A body whose fish line fishing has caught out still has its species and reads empty.
    public static float PopulationFraction(Map map, IntVec3 water)
    {
        if (!Active || !water.IsValid || !water.InBounds(map)) return 1f;
        try
        {
            WaterBody body = map.waterBodyTracker?.WaterBodyAt(water);
            if (!HasSpecies(body)) return 1f;
            float max = body.MaxPopulation;
            return max > 0f ? Math.Max(0f, Math.Min(1f, body.Population / max)) : 1f;
        }
        catch (Exception e)
        {
            TurnOff(e);
            return 1f;
        }
    }

    // The stock fraction a dive at `water` reads: our body's fraction, or with Odyssey the lower of it and Odyssey's
    // population fraction there.
    public static float DiveStockFraction(Map map, IntVec3 water)
    {
        MapComponent_FishStock fishStock = MapComponent_FishStock.Of(map);
        return fishStock.Stock.SharedStockFraction(fishStock.BodyAt(water), PopulationFraction(map, water));
    }

    // After a catch of `taken` fish from our body of water at `water`: lowers Odyssey's population for its water body there by
    // the same share of its maximum, and records the fish slaughter for ideoligion precepts, as line fishing does for each
    // catch. A body with no fish species is left alone.
    public static void NotifyCaught(Pawn pawn, IntVec3 water, float taken)
    {
        if (!Active || !water.IsValid || taken <= 0f) return;
        try
        {
            Map map = pawn.Map;
            WaterBody body = map.waterBodyTracker?.WaterBodyAt(water);
            if (HasSpecies(body))
            {
                MapComponent_FishStock fishStock = MapComponent_FishStock.Of(map);
                float share = fishStock.Stock.ShareOfCapacity(fishStock.BodyAt(water), taken);
                map.waterBodyTracker.Notify_Fished(water, share * body.MaxPopulation);
            }
            Find.HistoryEventsManager.RecordEvent(new HistoryEvent(HistoryEventDefOf.SlaughteredFish, pawn.Named(HistoryEventArgsNames.Doer)));
        }
        catch (Exception e)
        {
            TurnOff(e);
        }
    }

    // After a hatchery released `added` fish into our body of water at `water` (fish recovery ticket 04, ADR 0015): raises
    // Odyssey's population for its water body there by the same share of its maximum, never past its maximum. A body with no
    // fish species is left alone, as for catches.
    public static void NotifyReleased(Map map, IntVec3 water, float added)
    {
        if (!Active || map == null || !water.IsValid || added <= 0f) return;
        try
        {
            WaterBody body = map.waterBodyTracker?.WaterBodyAt(water);
            if (!HasSpecies(body)) return;
            float max = body.MaxPopulation;
            if (max <= 0f) return;
            MapComponent_FishStock fishStock = MapComponent_FishStock.Of(map);
            float share = fishStock.Stock.ShareOfCapacity(fishStock.BodyAt(water), added);
            body.Population = Math.Min(max, body.Population + share * max);
        }
        catch (Exception e)
        {
            TurnOff(e);
        }
    }

    // After our hourly regrowth with fish stock management on (ticket 08, ADR 0015): each Odyssey water body with fish species
    // gains, through its Population property, the share of its maximum that our body at one of its cells gained this hour
    // (`fractionsBefore`, by our body, against the fraction now), less the share Odyssey's own hourly regrowth added, never
    // below zero and never past our fraction (KeepPaceRule). Odyssey's share is worked out from the rate its
    // WaterBodyTracker.Tick applies once an hour, not measured, so line catches within the hour don't count as regrowth.
    // Walking Odyssey's bodies, not ours, raises each one once even where it spans several of ours.
    public static void KeepPace(Map map, float[] fractionsBefore)
    {
        if (!Active || fractionsBefore == null) return;
        try
        {
            WaterBodyTracker tracker = map.waterBodyTracker;
            if (tracker == null) return;
            float odysseyShare = OdysseyRegrowthShareThisHour(map);
            MapComponent_FishStock fishStock = MapComponent_FishStock.Of(map);
            foreach (WaterBody body in tracker.Bodies)
            {
                if (!HasSpecies(body)) continue;
                float max = body.MaxPopulation;
                if (max <= 0f) continue;
                int ours = OurBodyIn(fishStock, body);
                if (ours < 0 || ours >= fractionsBefore.Length) continue;
                float now = fishStock.Stock.StockFraction(ours);
                float add = KeepPaceRule.TopUpShare(now - fractionsBefore[ours], odysseyShare, now, body.Population / max);
                if (add > 0f) body.Population += add * max;
            }
        }
        catch (Exception e)
        {
            TurnOff(e);
        }
    }

    // The share of its maximum Odyssey's own regrowth adds to each body in an hour, as WaterBodyTracker.Tick applies it: the
    // map's fish population factor a day (2.5%, or a gill rot's), a twenty-fourth at a time, and nothing on a tile with no
    // fish population. Can be below zero during gill rot.
    public static float OdysseyRegrowthShareThisHour(Map map) =>
        map.TileInfo.MaxFishPopulation > 0f ? map.gameConditionManager.FishPopulationOffsetFactorPerDay(map, out _) / GenDate.HoursPerDay : 0f;

    // Our body of water at one of the Odyssey body's cells: its root cell, or else the first of its cells in our water.
    private static int OurBodyIn(MapComponent_FishStock fishStock, WaterBody body)
    {
        int ours = fishStock.BodyAt(body.rootCell);
        if (ours >= 0 || body.cells == null) return ours;
        foreach (IntVec3 cell in body.cells)
        {
            ours = fishStock.BodyAt(cell);
            if (ours >= 0) return ours;
        }
        return -1;
    }

    // Whether Odyssey placed any fish species in the body. Not WaterBody.HasFish, which also reads false once the
    // population is caught out: an emptied body must still limit dives.
    private static bool HasSpecies(WaterBody body) =>
        body != null && body.waterBodyType != WaterBodyType.None && (body.CommonFish.Any() || body.UncommonFish.Any());

    // The species choice of FishingUtility.GetCatchesFor, without its stack sizing and rare catches: toxfish by pollution,
    // then a small chance of the water's uncommon fish, else one of its common fish.
    private static ThingDef PickSpecies(Map map, IntVec3 water)
    {
        WaterBody body = map.waterBodyTracker?.WaterBodyAt(water);
        if (body == null || body.waterBodyType == WaterBodyType.None) return null;
        if (Rand.Chance(FishingUtility.PollutionToxfishChanceCurve.Evaluate(body.PollutionPct))) return ThingDefOf.Fish_Toxfish;
        if (Rand.Chance(FishingUtility.ChanceToCatchUncommonFish) && body.UncommonFish.TryRandomElement(out ThingDef uncommon))
            return uncommon;
        return body.CommonFishIncludingExtras.TryRandomElement(out ThingDef common) ? common : null;
    }

    // The species a cosmetic shoal at `water` looks like (ticket 23): the water body's fish as PickSpecies chooses them,
    // else the biome's fish for salt or fresh water, else null for the generic outline. Draws only from `rand`, never Rand,
    // so the shoals never move the gameplay random stream (ADR 0002).
    public static ThingDef ShoalSpecies(Map map, IntVec3 water, Random rand)
    {
        if (!Active || !water.IsValid || !water.InBounds(map)) return null;
        try
        {
            WaterBody body = map.waterBodyTracker?.WaterBodyAt(water);
            if (body != null && body.waterBodyType != WaterBodyType.None)
            {
                if (rand.NextDouble() < FishingUtility.PollutionToxfishChanceCurve.Evaluate(body.PollutionPct)) return ThingDefOf.Fish_Toxfish;
                if (rand.NextDouble() < FishingUtility.ChanceToCatchUncommonFish)
                {
                    ThingDef uncommon = Pick(body.UncommonFish, rand);
                    if (uncommon != null) return uncommon;
                }
                ThingDef common = Pick(body.CommonFishIncludingExtras, rand);
                if (common != null) return common;
            }
            var types = map.Biome?.fishTypes;
            if (types == null) return null;
            bool salt = water.GetTerrain(map)?.IsOcean ?? false;
            var list = salt ? types.saltwater_Common : types.freshwater_Common;
            if (list == null || list.Count == 0) return null;
            return list[rand.Next(list.Count)].fishDef;
        }
        catch (Exception e)
        {
            TurnOff(e);
            return null;
        }
    }

    // A random item without allocating: count, then walk to the chosen index.
    private static ThingDef Pick(System.Collections.Generic.IEnumerable<ThingDef> fish, Random rand)
    {
        if (fish == null) return null;
        int n = 0;
        foreach (ThingDef _ in fish) n++;
        if (n == 0) return null;
        int pick = rand.Next(n);
        foreach (ThingDef f in fish)
            if (pick-- == 0) return f;
        return null;
    }

    private static void TurnOff(Exception e)
    {
        broken = true;
        // A warning, not an error: spearfishing keeps working with our own raw fish. Not translated (developer text).
        Log.Warning($"[Spearfishing] Odyssey fish are turned off because {e.GetType().Name}: {e.Message}. RimWorld may have changed; please report it."); // not translated
    }
}
