using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace Spearfishing;

// Gear tiers ticket 11: a rare shark in deep ocean. Once per spearfishing trip, on a deep-ocean dive once the stringer holds
// the trip's seeded number of fish (FishBeforeShark), the shark chance is rolled. On a hit a diver holding a speargun may drive it off on a Shooting check and keep the catch;
// otherwise it bites once and takes the catch, and the diver heads home (JobDriver_DiveTrip). Snorkelers never meet one:
// only the dive trip rolls. The shark is a shadow the dive visuals draw, never a pawn or thing (ADR 0002), and nothing about
// it is saved. Both rolls are seeded by the job, so they never move the game's random sequence and a reload mid-trip gives
// the same answer.
public static class SharkEncounter
{
    public enum Outcome { None, Bite, DrivenOff }

    private const int SeedSalt = 0x5A4B11;

    // Developer diagnostics since the game started: rolls made, sharks that came, bites and sharks driven off.
    public static int Rolls { get; private set; }
    public static int Encounters { get; private set; }
    public static int Bites { get; private set; }
    public static int DrivenOff { get; private set; }

    // Developer tests only: a chance that replaces the setting, past its maximum too. The harness holds it at 0 so no other
    // batch meets a shark, and the shark batch sets 1. Null in play.
    public static float? ForcedChance;

    // The setting, clamped, so a hand-edited settings file can't go past the slider.
    public static float Chance => ForcedChance ??
        Mathf.Clamp(SpearfishingMod.Settings?.sharkChance ?? DiveRules.DefaultSharkChance, 0f, DiveRules.MaxSharkChance);

    // Deep ocean only: never shallow ocean, lakes or rivers.
    public static bool IsSharkWater(Map map, IntVec3 cell) =>
        map != null && cell.InBounds(map) && map.terrainGrid.TerrainAt(cell) == TerrainDefOf.WaterOceanDeep;

    private static int Seed(Job job) => Gen.HashCombineInt(job.loadID, SeedSalt);

    // How many fish the stringer holds before the trip's roll: from none up to one short of full, seeded by the job. So the
    // shark can come on any deep dive of the trip, a bite can cost a fuller stringer, and a full stringer, which ends the trip,
    // never comes first. The stringer is saved, so after a load the roll comes at the same point. A forced chance (developer
    // tests) forces the first deep dive, and so does a chance of 0, which can never bring a shark: the roll is still made, as
    // the chance-zero case checks, on the first deep dive as before.
    public static int FishBeforeShark(Pawn pawn, Job job)
    {
        if (ForcedChance.HasValue || Chance <= 0f) return 0;
        int capacity = SpearfishingUtility.StringerCapacity(pawn);
        return Mathf.Min(capacity - 1, (int)(Rand.ValueSeeded(Seed(job) + 2) * capacity));
    }

    // The trip's one roll, and, on a hit, whether a speargun drives the shark off.
    public static Outcome Roll(Pawn pawn, Job job)
    {
        Rolls++;
        int seed = Seed(job);
        if (!Rand.ChanceSeeded(Chance, seed)) return Outcome.None;
        Encounters++;
        ThingWithComps spear = SpearfishingUtility.Spear(pawn);
        if (spear == null || !spear.def.IsRangedWeapon) return Outcome.Bite;
        int shooting = pawn.skills?.GetSkill(SkillDefOf.Shooting)?.Level ?? 0;
        float chance = DiveRules.DriveOffChance(shooting, spear.GetStatValue(SpearfishingDefOf.Spearfishing_DivePower));
        return Rand.ChanceSeeded(chance, seed + 1) ? Outcome.DrivenOff : Outcome.Bite;
    }

    public static void DriveOff(Pawn pawn)
    {
        DrivenOff++;
        Messages.Message("Spearfishing_SharkDrivenOff".Translate(pawn.Named("PAWN")), pawn, MessageTypeDefOf.PositiveEvent);
    }

    // One vanilla bite on a random outside part. The caller has already emptied the stringer and sent the diver home.
    public static void Bite(Pawn pawn)
    {
        Bites++;
        Messages.Message("Spearfishing_SharkBite".Translate(pawn.Named("PAWN")), pawn, MessageTypeDefOf.NegativeHealthEvent);
        BodyPartRecord part = pawn.health.hediffSet.GetRandomNotMissingPart(DamageDefOf.Bite, BodyPartHeight.Undefined, BodyPartDepth.Outside);
        pawn.TakeDamage(new DamageInfo(DamageDefOf.Bite, DiveRules.SharkBiteDamage, 0f, -1f, null, part));
    }
}
