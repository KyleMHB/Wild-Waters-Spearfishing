using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace Spearfishing;

// Rules shared by the work giver, the sea trips (spearfishing and snorkeling) and the snorkeling joy giver.
public static class SpearfishingUtility
{
    // How far the shore search spreads through water before giving up.
    private const int ShoreSearchCells = 20000;

    // The pawn's spear: its equipped weapon, if that has dive power. Pole spears, steel-tipped ones and spearguns are all spears.
    public static ThingWithComps Spear(Pawn pawn)
    {
        ThingWithComps weapon = pawn.equipment?.Primary;
        return weapon != null && weapon.GetStatValue(SpearfishingDefOf.Spearfishing_DivePower) > 0f ? weapon : null;
    }

    // Spears train Melee and spearguns Shooting.
    public static SkillDef DiveSkill(Thing spear) => spear.def.IsRangedWeapon ? SkillDefOf.Shooting : SkillDefOf.Melee;

    // The pawn's level in the skill their spear trains, or 0 without a spear.
    public static int DiveSkillLevel(Pawn pawn)
    {
        ThingWithComps spear = Spear(pawn);
        return spear == null ? 0 : pawn.skills?.GetSkill(DiveSkill(spear))?.Level ?? 0;
    }

    // The shortest dive and the surface after it for this diver, what a trip must afford to set out (ticket 25), and one
    // freedive and float for this snorkeler (ticket 21).
    public static int ShortestDiveCycleTicks(Pawn pawn) =>
        DiveRules.DiveCycleTicks(DiveRules.ShortestDiveTicks(pawn.GetStatValue(DiveGearDefOf.Spearfishing_DiveSuccess)), SurfaceRestFactor(pawn));

    // The share of the usual rest this diver takes at the surface after a spearfishing dive: 1 without gear, less in a dry
    // snorkel (gear tiers ticket 04). Read at dive decisions and safety checks, never on the draw threads.
    public static float SurfaceRestFactor(Pawn pawn) => pawn.GetStatValue(SurfaceRestDefOf.Spearfishing_SurfaceRest);

    public static int FreediveCycleTicks(Pawn pawn) =>
        DiveRules.FreediveTicksFor(pawn.skills?.GetSkill(SkillDefOf.Melee)?.Level ?? 0) + DiveRules.FloatTicks;

    public static bool RestedForATrip(Pawn pawn) =>
        pawn.needs?.rest == null || pawn.needs.rest.CurLevelPercentage >= DiveRules.MinRestToStart;

    public static int StringerCapacity(Pawn pawn) =>
        Mathf.Max(1, Mathf.RoundToInt(pawn.GetStatValue(SpearfishingDefOf.Spearfishing_StringerCapacity)));

    // Entry conditions for a spearfishing trip: a spear, Waves' swimming on, enough Rest, a zone, a sea warm enough for the
    // pawn's gear, and an ideoligion that allows killing fish.
    public static bool CanStartTrip(Pawn pawn) => !SkipTrips(pawn) && OdysseyFish.WillingToFish(pawn);

    // The cheap part of CanStartTrip, for WorkGiver.ShouldSkip.
    public static bool SkipTrips(Pawn pawn) =>
        !WavesBridge.SwimmingOn || Spear(pawn) == null || !RestedForATrip(pawn) || !AnyZone(pawn.Map) || DiveSafety.TooColdToStart(pawn);

    // The first dive spot of a trip, in the nearest zone worth a dive with a spot the pawn can afford; IntVec3.Invalid when
    // the pawn can't start a trip. Not a cell scan: like vanilla fishing it picks a zone. outOfReach is set when no spot was
    // found because every zone with a way in was too far from shore for this pawn, so the player can be told why.
    public static IntVec3 FirstSpot(Pawn pawn, out bool outOfReach)
    {
        bool tooFar = false;
        IntVec3 spot = FirstSpot(pawn, (p, zone) =>
        {
            IntVec3 fitting = AffordableSpot(p, zone, out bool zoneTooFar);
            tooFar |= zoneTooFar;
            return fitting;
        });
        outOfReach = !spot.IsValid && tooFar;
        return spot;
    }

    // As above with the zone's spot chosen by pickSpot, and taken only if the pawn can afford it (tickets 21 and 25).
    public static IntVec3 FirstSpot(Pawn pawn, Func<Pawn, Zone_Spearfishing, IntVec3> pickSpot)
    {
        if (!CanStartTrip(pawn)) return IntVec3.Invalid;
        IntVec3 best = IntVec3.Invalid;
        float bestDistance = float.MaxValue;
        int cycleTicks = ShortestDiveCycleTicks(pawn);
        foreach (Zone zone in pawn.Map.zoneManager.AllZones)
        {
            if (zone is not Zone_Spearfishing fishing || !fishing.WorthADive) continue;
            float distance = pawn.Position.DistanceToSquared(fishing.Cells[0]);
            if (distance >= bestDistance) continue;
            IntVec3 spot = pickSpot(pawn, fishing);
            if (!spot.IsValid || !DiveSafety.FitToSetOut(pawn, spot, cycleTicks)) continue;
            best = spot;
            bestDistance = distance;
        }
        return best;
    }

    // A spot in the zone the pawn can reach, make the shortest dive at and swim home from (ticket 28): the first
    // sampled spot that fits, or else the edge cell nearest the shore. Rest and warmth only limit how far from shore a spot
    // may be, so if that edge cell doesn't fit no cell does: tooFar is set and the dearer sampling is skipped.
    private static IntVec3 AffordableSpot(Pawn pawn, Zone_Spearfishing zone, out bool tooFar)
    {
        tooFar = false;
        int cycleTicks = ShortestDiveCycleTicks(pawn);
        IntVec3 nearest = zone.EdgeCellsNearestShore().FirstOrFallback(c => CanSwimTo(pawn, c), IntVec3.Invalid);
        if (!nearest.IsValid) return IntVec3.Invalid;
        if (!DiveSafety.FitToSetOut(pawn, nearest, cycleTicks))
        {
            tooFar = true;
            return IntVec3.Invalid;
        }
        IntVec3 spot = zone.PickDiveSpot(c => CanSwimTo(pawn, c) && DiveSafety.FitToSetOut(pawn, c, cycleTicks));
        return spot.IsValid ? spot : nearest;
    }

    private static bool CanSwimTo(Pawn pawn, IntVec3 c) => !c.IsForbidden(pawn) && pawn.CanReach(c, PathEndMode.OnCell, Danger.Some);

    // Where to snorkel (ticket 17): swimmable water (sea, lake or river, ticket 24) within a short swim of dry land, close to
    // the pawn. Any such water will do; zones
    // neither attract nor block snorkelers. A capped flood fill from the pawn keeps the first few swimmable cells it meets,
    // then one of those near enough to shore and reachable is picked at random. The shore distance is a flood fill of its
    // own, so it runs after the search, never inside it. IntVec3.Invalid when there is none.
    public static IntVec3 SnorkelSpot(Pawn pawn)
    {
        Map map = pawn.Map;
        var found = new List<IntVec3>(DiveRules.SnorkelCandidates);
        map.floodFiller.FloodFill(pawn.Position, c => c.Walkable(map), c =>
        {
            if (WavesBridge.IsSwimmableFishingWater(map, c) && !c.IsForbidden(pawn)) found.Add(c);
            return found.Count >= DiveRules.SnorkelCandidates;
        }, GenRadial.NumCellsInRadius(DiveRules.SnorkelSearchRadius));
        found.RemoveAll(c => DistanceToShoreSquared(map, c) > DiveRules.SnorkelMaxCellsFromShore * DiveRules.SnorkelMaxCellsFromShore);
        found.Shuffle();
        foreach (IntVec3 spot in found)
            if (pawn.CanReach(spot, PathEndMode.OnCell, Danger.Some)) return spot;
        return IntVec3.Invalid;
    }

    // A nearby cell for a snorkeler to drift to: swimmable, still near shore, and reachable. IntVec3.Invalid for none.
    public static IntVec3 SnorkelDriftCell(Pawn pawn, IntVec3 from)
    {
        Map map = pawn.Map;
        int maxSquared = DiveRules.SnorkelMaxCellsFromShore * DiveRules.SnorkelMaxCellsFromShore;
        for (int i = 0; i < 4; i++)
        {
            IntVec3 c = from + GenRadial.RadialPattern[Rand.Range(1, GenRadial.NumCellsInRadius(DiveRules.DriftRadius))];
            if (!WavesBridge.IsSwimmableFishingWater(map, c) || c.IsForbidden(pawn)) continue;
            if (DistanceToShoreSquared(map, c) > maxSquared || !pawn.CanReach(c, PathEndMode.OnCell, Danger.Some)) continue;
            return c;
        }
        return IntVec3.Invalid;
    }

    // How far out a cell is: the squared distance to the first dry land a swim from it reaches, so land behind a wall (a
    // seawall, the colony's outer wall) does not make the water beside it look close to shore. int.MaxValue - 1 when the
    // search finds none, so such cells still beat no spot at all. Not a district match: in game the sea and the land
    // beside it are separate districts, so that found no shore for any cell and the pick fell to the first sample.
    public static int DistanceToShoreSquared(Map map, IntVec3 cell)
    {
        IntVec3 shore = IntVec3.Invalid;
        map.floodFiller.FloodFill(cell, c => c.Walkable(map), c =>
        {
            if (!IsDryLand(map, c)) return false;
            shore = c;
            return true;
        }, GenRadial.NumCellsInRadius(ShoreRadius));
        return shore.IsValid ? (shore - cell).LengthHorizontalSquared : int.MaxValue - 1;
    }

    // How far DistanceToShoreSquared looks for land around a cell, as the area of a circle of this radius.
    private const float ShoreRadius = 20f;

    // The nearest dry land the pawn can walk or swim to: not water, so the catch is not left in the surf.
    public static IntVec3 ShoreCellNear(Pawn pawn)
    {
        Map map = pawn.Map;
        IntVec3 shore = IntVec3.Invalid;
        map.floodFiller.FloodFill(pawn.Position, c => c.Walkable(map), c =>
        {
            if (!IsDryLand(map, c) || c.IsForbidden(pawn)) return false;
            shore = c;
            return true;
        }, ShoreSearchCells);
        return shore;
    }

    // Leaves the catch on dry land near the cell, unforbidden, where haulers will pick it up. `water` is a cell of the water
    // it was caught in, which sets each fish's species with Odyssey (OdysseyFish); without it every fish is our raw fish.
    public static void DropCatch(Pawn pawn, IntVec3 near, int fish, IntVec3 water)
    {
        Map map = pawn.Map;
        foreach (IGrouping<ThingDef, ThingDef> species in Enumerable.Range(0, fish).Select(_ => OdysseyFish.CatchDef(map, water)).GroupBy(d => d))
            DropStacks(map, near, species.Key, species.Count());
    }

    private static void DropStacks(Map map, IntVec3 near, ThingDef def, int fish)
    {
        while (fish > 0)
        {
            Thing stack = ThingMaker.MakeThing(def);
            stack.stackCount = Mathf.Min(fish, stack.def.stackLimit);
            fish -= stack.stackCount;
            if (!GenPlace.TryPlaceThing(stack, near, map, ThingPlaceMode.Near, out Thing placed, extraValidator: c => IsDryLand(map, c)) &&
                !GenPlace.TryPlaceThing(stack, near, map, ThingPlaceMode.Near, out placed))
                continue;
            placed.SetForbidden(false, warnOnFail: false);
        }
    }

    // Puts the catch in the pawn's inventory, for a diver whose trip ended away from dry land (drafted or interrupted). The
    // player can drop it from the gear tab, and once the pawn is free vanilla's unload-your-inventory job takes it to
    // storage. That flag unloads the rest of the inventory too, such as packed meals, which the pawn packs again later.
    public static void CarryCatch(Pawn pawn, int fish, IntVec3 water)
    {
        Map map = pawn.MapHeld;
        foreach (IGrouping<ThingDef, ThingDef> species in Enumerable.Range(0, fish).Select(_ => map == null ? SpearfishingDefOf.Spearfishing_RawFish : OdysseyFish.CatchDef(map, water)).GroupBy(d => d))
            CarryStacks(pawn, species.Key, species.Count());
        pawn.inventory.UnloadEverything = true;
    }

    private static void CarryStacks(Pawn pawn, ThingDef def, int fish)
    {
        while (fish > 0)
        {
            Thing stack = ThingMaker.MakeThing(def);
            stack.stackCount = Mathf.Min(fish, stack.def.stackLimit);
            fish -= stack.stackCount;
            int count = stack.stackCount;
            if (pawn.inventory.innerContainer.TryAdd(stack, count) < count && pawn.Spawned)
                GenPlace.TryPlaceThing(stack, pawn.Position, pawn.Map, ThingPlaceMode.Near);
        }
    }

    public static bool AnyZone(Map map) => map.zoneManager.AllZones.Any(z => z is Zone_Spearfishing);

    public static bool IsDryLand(Map map, IntVec3 c) => c.Standable(map) && !c.GetTerrain(map).IsWater && !c.Fogged(map);
}
