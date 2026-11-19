namespace Spearfishing;

// Tuning and the dive roll, in one place. Plain C# so the numbers are easy to find and change.
public static class DiveRules
{
    // A dive (tickets 21 and 25): time under water, growing evenly with the dive skill from DiveTicksAtSkill0 (20 seconds at
    // 1x) to DiveTicksAtSkill20 (60 seconds) and then times dive success, and time face down at the surface for breath after
    // it: SurfaceShareOfDive of the ticks actually spent under, times the diver's surface rest factor (gear tiers ticket 04;
    // 1 without gear, 0.75 in the dry snorkel).
    public const int DiveTicksAtSkill0 = 1200;
    public const int DiveTicksAtSkill20 = 3600;
    public const float SurfaceShareOfDive = 0.5f;

    // Catch rolls: one for every CatchRollCycleTicks of dive and surface together, all taken under the water, at the cell
    // the diver is swimming through. Before ticket 21 a dive and its surface took 240 ticks with one roll. Without gear the
    // surface is a fixed share of the dive, so a roll every CatchRollTicks under the water (240 / 1.5 = 160) keeps one roll
    // per 240 ticks of dive and surface at every dive length: catches, skill experience and recreation per hour stay where
    // they were. CatchRollTicks stays on the base share whatever the diver wears: gear that shortens the rest (surface rest
    // factor) fits more dives, and so more rolls, into an hour without changing the chance or the reward of a roll.
    public const int CatchRollCycleTicks = 240;
    public const float CatchRollTicks = CatchRollCycleTicks / (1f + SurfaceShareOfDive);

    // Experience in the dive skill (Melee for spears, Shooting for spearguns) for every catch roll, caught or not.
    public const float SkillXpPerRoll = 40f;

    // Moving under the water: the next waypoint is this many cells away, in a straight line over allowed water.
    public const float UnderwaterWaypointMin = 2f;
    public const float UnderwaterWaypointMax = 4.2f;

    // Rest needed to start a trip: Waves drains Rest in deep water, and an exhausted swimmer drowns. Kept well above the
    // Rest needed to swim home from a typical zone, so a trip gets some dives in before the safety exit.
    public const float MinRestToStart = 0.6f;

    // ---- Recreation (ADR 0006, ADR 0007) -------------------------------------------------------------------------------
    // Recreation from each catch roll on a work trip, before tolerance. A work trip also holds recreation level while the
    // diver is in the water (JobDriver_Spearfish), so every trip ends up by about this per roll; on land it falls as usual.
    // Snorkeling gains vanilla's 0.36 per hour, about ten times this per roll.
    public const float WorkRecreationPerRoll = 0.004f;

    // Vanilla's recreation rate for a recreation job, per tick, before the job's gain rate, tolerance and the snorkeling
    // enjoyment stat (base 1, +0.35 with a snorkel).
    public const float RecreationPerTick = 0.36f / 2500f;

    // Recreation counts as full here, as in vanilla's JoyUtility.JoyTickCheckEnd.
    public const float FullRecreation = 0.9999f;

    // ---- Snorkeling (ticket 17, ADR 0007) ------------------------------------------------------------------------------
    // The snorkeling session stat is in hours at sea (base 1 = 2,500 ticks; a snorkel adds 0.6 for 4,000).
    public const int TicksPerHour = 2500;

    // A snorkeling spot is swimmable sea at most this many cells from dry land, measured by a swim
    // (SpearfishingUtility.DistanceToShoreSquared).
    public const int SnorkelMaxCellsFromShore = 10;

    // How far from the pawn the spot search spreads, as the area of a circle of this radius. Beyond it the sea is too far
    // to walk to for recreation.
    public const float SnorkelSearchRadius = 60f;

    // The search keeps the first few swimmable cells it meets (the closest to the pawn) and picks one at random among those
    // close enough to shore, so snorkelers spread out a little.
    public const int SnorkelCandidates = 8;

    // At sea a snorkeler floats a while, then freedives, drifts to a nearby cell, or floats again. A freedive lasts this
    // share of a diver's dive at the same Melee skill, without dive success.
    public const int FloatTicks = 240;
    public const float FreediveShareOfDive = 0.5f;
    public const float FreediveChance = 0.35f;
    public const float DriftChance = 0.35f;
    public const float DriftRadius = 2.9f;

    // ---- Safe exits (ticket 05) ----------------------------------------------------------------------------------------
    // How often, in ticks, a diver checks Rest and cold between dives and while swimming to a spot.
    public const int SafetyCheckTicks = 60;

    // A swim home is assumed this much longer than the straight line to shore.
    public const float ShoreDetourFactor = 1.3f;

    // Rest and chill a diver must keep for the swim home are worked out for this much longer than the swim should take,
    // plus the time at sea before they can next turn home: the rest of the current dive and the surface after it, or
    // between dives one more shortest dive and its surface (ticket 25). That time is known, so the factor is on the swim only.
    public const float SwimHomeSafetyFactor = 1.5f;

    // A dive cut short to the Rest or warmth left is planned as if the swim home started this many cells farther out, since
    // the diver moves under the water (ticket 21). Without it a cut dive starts right at the safety exits' limit and the
    // first stroke away from shore ends it.
    public const float DiveDriftCells = 8f;

    // Rest kept above Waves' knockout level (0.01) on arrival.
    public const float RestReserve = 0.05f;

    // A diver works water down to this many degrees below the temperature at which Waves starts chilling them. Clothing
    // keeps rewarming a diver against Waves' chill, so mildly cold water is safe; the hypothermia limits below catch the rest.
    public const float WaterColdMargin = 5f;

    // Hypothermia severity a diver turns home at, counting the chill still to come on the way. Below vanilla's "minor" stage
    // (0.2) and well short of "serious" (0.35).
    public const float HeadHomeHypothermia = 0.15f;

    // No trip starts while a pawn is still more chilled than this.
    public const float MaxHypothermiaToStart = 0.05f;

    // Ticks to swim home from cells away, at ticksPerCell per cell.
    public static float TicksToShore(float cells, float ticksPerCell) => cells * ShoreDetourFactor * ticksPerCell;

    // The Rest a diver needs now: the loss over ticksBeforeTurning more at sea and a cautious swim home, plus the reserve.
    public static float RestToReachShore(float restLossPerTick, float ticksToShore, float ticksBeforeTurning) =>
        restLossPerTick * (ticksToShore * SwimHomeSafetyFactor + ticksBeforeTurning) + RestReserve;

    // The hypothermia severity a diver would reach after ticksBeforeTurning more at sea and a cautious swim home.
    public static float HypothermiaAtShore(float severity, float chillPerTick, float ticksToShore, float ticksBeforeTurning) =>
        severity + chillPerTick * (ticksToShore * SwimHomeSafetyFactor + ticksBeforeTurning);

    // ---- Shark encounters (gear tiers ticket 11) ------------------------------------------------------------------------
    // The chance per spearfishing trip, rolled once on a deep-ocean dive (SharkEncounter.FishBeforeShark): a mod setting from 0 (off) up to
    // MaxSharkChance, one trip in five, for players who want a dangerous sea.
    public const float DefaultSharkChance = 0.01f;
    public const float MaxSharkChance = 0.2f;

    // The shark circles for 2.4 seconds at 1x, turns in and strikes this many ticks after it appears, as the dive visuals
    // draw it (art/shark/APPROVAL.md). A roll is only made while the dive has more ticks left than this.
    public const int SharkStrikeTicks = 174;

    // One vanilla bite: about a third of a grizzly or polar bear's 23-damage bite, so it hurts without crippling a diver.
    public const float SharkBiteDamage = 8f;

    // A speargun diver's chance to drive the shark off: their Shooting's skill factor times the speargun's dive power, so
    // 30% at Shooting 0 with the band speargun, 65% at 10 and certain at 20 (the pneumatic reaches it sooner).
    public static float DriveOffChance(int shootingLevel, float divePower)
    {
        float chance = SkillFactor(shootingLevel) * divePower;
        return chance < 0f ? 0f : chance > 1f ? 1f : chance;
    }

    // No dive is a sure thing.
    public const float MaxChance = 0.95f;

    // Fish balance ticket 04: every catch roll's chance is scaled by this, so a Melee 10 diver with a normal pole spear and
    // no mask lands about 15 fish per 8 hours of trips on full water (before, about 24; 35 per 8 hours at the spot). Only
    // the chance moves: dive length, surface rests, rolls per hour, experience and recreation per roll stay as they were.
    // The ticket's Comments hold the arithmetic.
    public const float BaseChanceScale = 0.56f;

    // Skill sets how much of the spear's power a diver uses: 30% at level 0 up to 100% at level 20.
    public static float SkillFactor(int skillLevel)
    {
        int level = skillLevel < 0 ? 0 : skillLevel > 20 ? 20 : skillLevel;
        return 0.3f + 0.7f * level / 20f;
    }

    // A dive's length from the dive skill alone: DiveTicksAtSkill0 at level 0, growing evenly to DiveTicksAtSkill20.
    public static int DiveTicksAtSkill(int skillLevel)
    {
        int level = skillLevel < 0 ? 0 : skillLevel > 20 ? 20 : skillLevel;
        return DiveTicksAtSkill0 + (DiveTicksAtSkill20 - DiveTicksAtSkill0) * level / 20;
    }

    // Dive success also lengthens each dive: a masked diver stays down longer, so a trip has fewer surface breaks per dive time.
    public static int DiveTicksFor(int skillLevel, float diveSuccess) => (int)(DiveTicksAtSkill(skillLevel) * diveSuccess + 0.5f);

    // A snorkeler's freedive at their Melee skill.
    public static int FreediveTicksFor(int meleeLevel) => (int)(DiveTicksAtSkill(meleeLevel) * FreediveShareOfDive + 0.5f);

    // The shortest dive at this dive success, the skill-0 length (ticket 25): what a trip must have the Rest for to set out,
    // and to dive again.
    public static int ShortestDiveTicks(float diveSuccess) => DiveTicksFor(0, diveSuccess);

    // The surface's share of the dive before it for a diver with this surface rest factor (the pawn stat, 1 without gear).
    public static float SurfaceShare(float surfaceRestFactor) => SurfaceShareOfDive * surfaceRestFactor;

    // The rest at the surface after diveTicks under the water, for a diver with this surface rest factor.
    public static int SurfaceTicksAfter(int diveTicks, float surfaceRestFactor) =>
        diveTicks <= 0 ? 1 : System.Math.Max(1, (int)(diveTicks * SurfaceShare(surfaceRestFactor) + 0.5f));

    // A dive and the surface after it.
    public static int DiveCycleTicks(int diveTicks, float surfaceRestFactor) => diveTicks + SurfaceTicksAfter(diveTicks, surfaceRestFactor);

    // The longest dive a diver can start with margin to spend (Rest above the reserve, or hypothermia below the head-home
    // level) and still have enough for a cautious swim home once the dive and its surface are over: RestToReachShore and
    // HypothermiaAtShore solved for the dive (ticket 25). Unlimited when nothing is lost. A shorter rest leaves room for a
    // longer dive.
    public static float LongestDiveTicks(float margin, float lossPerTick, float ticksToShore, float surfaceRestFactor)
    {
        if (lossPerTick <= 0f) return float.MaxValue;
        return (margin / lossPerTick - ticksToShore * SwimHomeSafetyFactor) / (1f + SurfaceShare(surfaceRestFactor));
    }

    // One catch roll. diveSuccess is a multiplier for gear that helps a diver find fish (the mask, ticket 09); 1 without.
    // stockFraction is the stock fraction of the body of water at the dive cell (ADR 0013); empty water gives no chance at all.
    // floorFactor is the sea floor's at the dive cell (FloorRules): above 1 over reef and kelp, where fish are densest.
    // yieldFactor is the difficulty's fishing yield factor (1, or 0.9 and 0.8 on the harder difficulties), as Odyssey's line
    // fishing uses it; the caller reads it, so this file stays plain C#.
    public static float CatchChance(int skillLevel, float divePower, float stockFraction, float diveSuccess = 1f, float floorFactor = 1f,
        float yieldFactor = 1f)
    {
        float chance = BaseChanceScale * SkillFactor(skillLevel) * divePower * stockFraction * diveSuccess * floorFactor * yieldFactor;
        return chance < 0f ? 0f : chance > MaxChance ? MaxChance : chance;
    }
}
