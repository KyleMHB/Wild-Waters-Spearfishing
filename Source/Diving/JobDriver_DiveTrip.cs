using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace Spearfishing;

// The dive loop of a spearfishing trip (ADR 0006): swim to a spot in the zone, dive, surface, and repeat. Under the water (ticket 21) the diver swims on through
// the zone's water, with a catch roll every so often at the cell they are in, and surfaces where the dive ends. The swim out and home and the safe exits are
// the shared sea trip's (JobDriver_SeaTrip). Ashore the diver leaves the catch for haulers. A trip that ends any other way
// (drafted, interrupted, failed) keeps the catch: dropped if the diver is on dry land, otherwise carried in their inventory
// until they unload it ashore.
//
// A work trip (JobDriver_Spearfish) is the subclass; spearing is only ever work (ADR 0007). Target A is the current dive
// spot, inside a spearfishing zone.
public abstract class JobDriver_DiveTrip : JobDriver_SeaTrip
{
    // Fish on the stringer this trip. Saved with the job.
    private int stringer;

    // Ticks under the water toward the next catch roll, carried from one dive to the next, and the rolls this trip. Saved.
    private float rollProgress;
    private int catchRolls;

    // Ticks under the water on the current or last dive, for the rest at the surface after it. Saved.
    private int ticksUnder;

    public int FishOnStringer => stringer;

    public int CatchRolls => catchRolls;

    // The length of the current dive, or of the last one; read by the developer tests.
    public int DiveTicks => diveToil?.defaultDuration ?? 0;

    // The zone around the current spot; null once it is deleted or shrunk away from the spot.
    public Zone_Spearfishing Zone => Map.zoneManager.ZoneAt(Spot) as Zone_Spearfishing;

    public override void ExposeData()
    {
        base.ExposeData();
        Scribe_Values.Look(ref stringer, "stringer");
        Scribe_Values.Look(ref rollProgress, "rollProgress");
        Scribe_Values.Look(ref catchRolls, "catchRolls");
        Scribe_Values.Look(ref ticksUnder, "ticksUnder");
    }

    // When the diver stops diving and heads home, besides the safety exits. Subclasses add their own reasons and keep these.
    protected override bool ShouldHeadHome()
    {
        if (stringer >= SpearfishingUtility.StringerCapacity(pawn)) return true;
        Zone_Spearfishing zone = Zone;
        return zone == null || !zone.WorthADive;
    }

    // Multiplier on the catch chance from the diver's gear, and on each dive's length: the dive success stat the mask raises.
    protected virtual float DiveSuccess() => pawn.GetStatValue(DiveGearDefOf.Spearfishing_DiveSuccess);

    // Called after every catch roll, caught or not. A work trip's recreation from diving goes here.
    protected virtual void OnCatchRoll(bool caught)
    {
    }

    // A whole dive at the diver's skill and gear.
    private int FullDiveTicks() => DiveRules.DiveTicksFor(SpearfishingUtility.DiveSkillLevel(pawn), DiveSuccess());

    // Between dives a diver is committed only to the shortest dive and its surface (ticket 25): a longer dive is cut to the
    // Rest left when it starts, so skill never asks for more Rest than a novice needs.
    // The dive begins as the swim out ends, so the dive visuals turn the pawn face down before it arrives (ticket 33).
    protected override bool DivesOnArrival => true;

    protected override int TicksHeldBetweenDives => DiveRules.DiveCycleTicks(DiveRules.ShortestDiveTicks(DiveSuccess()), SurfaceRestFactor());

    protected override int SurfaceTicksAfterDive => DiveRules.SurfaceTicksAfter(diveToil?.defaultDuration ?? 0, SurfaceRestFactor());

    // The diver's own surface rest factor (gear tiers ticket 04): the dry snorkel shortens the rest after each dive.
    private float SurfaceRestFactor() => SpearfishingUtility.SurfaceRestFactor(pawn);

    protected override IEnumerable<Toil> MakeNewToils()
    {
        this.FailOn(() => SpearfishingUtility.Spear(pawn) == null);
        // Drafted, interrupted or failed: the catch is not lost.
        AddFinishAction(_ => ReleaseStringer());
        foreach (Toil toil in base.MakeNewToils()) yield return toil;
    }

    protected override IEnumerable<Toil> AtSeaToils(Toil headHome)
    {
        Toil swimToSpot = Toils_Goto.GotoCell(SpotInd, PathEndMode.OnCell);
        Toil dive = Dive(headHome);
        Toil surface = Surface();
        diveToil = dive;
        surfaceToil = surface;
        yield return swimToSpot;
        yield return dive;
        yield return Surfaced();
        yield return surface;
        yield return NextMove(dive, headHome);
    }

    protected override IEnumerable<Toil> AshoreToils()
    {
        yield return LeaveCatch();
    }

    private Toil Dive(Toil headHome)
    {
        Toil toil = ToilMaker.MakeToil("Dive");
        toil.defaultCompleteMode = ToilCompleteMode.Delay;
        // Set when the toils are built too, so a load mid-dive times the dive shadow over about the right length.
        toil.defaultDuration = FullDiveTicks();
        // The length from the skill and gear now, cut short to the Rest and warmth left (ticket 25). The driver set the
        // countdown from defaultDuration before this ran.
        toil.initAction = () =>
        {
            pawn.pather.StopDead();
            ticksUnder = 0;
            // Checked as the shortest dive first: a diver without the Rest or warmth even for that heads home instead.
            int shortest = DiveRules.ShortestDiveTicks(DiveSuccess());
            toil.defaultDuration = shortest;
            ticksLeftThisToil = shortest;
            if (TimeToHeadHome())
            {
                JumpToToil(headHome);
                return;
            }
            toil.defaultDuration = DiveSafety.DiveTicksToFit(pawn, NearestShore, shortest, FullDiveTicks());
            ticksLeftThisToil = toil.defaultDuration;
        };
        toil.tickAction = () =>
        {
            SwimUnderwater(InDiveWater, stalk: true);
            ticksUnder++;
            if (SharkTick(headHome)) return;
            rollProgress += 1f;
            // A fixed interval under the water: without gear the surface is a fixed share of the time under, so this keeps
            // one roll per CatchRollCycleTicks of dive and surface however long the dive is. A diver whose gear shortens the
            // rest keeps the same interval and so rolls more often per hour (DiveRules.CatchRollTicks).
            if (rollProgress < DiveRules.CatchRollTicks) return;
            rollProgress -= DiveRules.CatchRollTicks;
            CatchRoll();
            // A full stringer ends the dive early: the diver surfaces where they are and heads home from there. A shark on
            // its way strikes first (SharkTick).
            if (stringer >= SpearfishingUtility.StringerCapacity(pawn) && sharkStrikeIn < 0) ReadyForNextToil();
        };
        toil.AddFinishAction(() =>
        {
            CallOffShark();
            if (pawn.Spawned) pawn.pather.StopDead();
            // Stalking walks; the swim on, and the swim home, jog again.
            EndStalk();
        });
        toil.WithProgressBarToilDelay(SpotInd);
        return toil;
    }

    // Gear tiers ticket 11: the trip's shark roll, made on a deep-ocean dive with time left for the strike once the stringer
    // holds the trip's seeded number of fish (SharkEncounter.FishBeforeShark), and a strike on its way. Never saved (ADR
    // 0002): after a load the roll is made again, and being seeded by the job it gives the same answer at the same stringer,
    // so a shark driven off before the save can show up and be driven off once more.
    private bool sharkRolled;
    private SharkEncounter.Outcome sharkComing;
    private int sharkStrikeIn = -1;
    private int fishBeforeShark = -1;

    // Whether this trip has made its shark roll; read by the developer tests.
    public bool SharkRolled => sharkRolled;

    // Called every tick under the water. True when the strike ended the dive this tick.
    private bool SharkTick(Toil headHome)
    {
        if (sharkStrikeIn < 0)
        {
            if (sharkRolled || ticksLeftThisToil <= DiveRules.SharkStrikeTicks || !SharkEncounter.IsSharkWater(Map, pawn.Position)) return false;
            if (fishBeforeShark < 0) fishBeforeShark = SharkEncounter.FishBeforeShark(pawn, job);
            if (stringer < fishBeforeShark) return false;
            sharkRolled = true;
            sharkComing = SharkEncounter.Roll(pawn, job);
            if (sharkComing == SharkEncounter.Outcome.None) return false;
            sharkStrikeIn = DiveRules.SharkStrikeTicks;
            DiveVisuals.Notify_Shark(this, sharkComing == SharkEncounter.Outcome.Bite);
            return false;
        }
        if (--sharkStrikeIn > 0) return false;
        sharkStrikeIn = -1;
        if (sharkComing == SharkEncounter.Outcome.DrivenOff)
        {
            SharkEncounter.DriveOff(pawn);
            if (stringer < SpearfishingUtility.StringerCapacity(pawn)) return false;
            ReadyForNextToil();
            return true;
        }
        // The catch is gone with the shark, not dropped. The diver heads home first, so a job the bite may start (tending,
        // bed rest) finds the trip already on its way out.
        stringer = 0;
        JumpToToil(headHome);
        SharkEncounter.Bite(pawn);
        return true;
    }

    // A dive that ends before the strike (the Rest or cold exits, drafting) leaves the shark behind: it swims off.
    private void CallOffShark()
    {
        if (sharkStrikeIn < 0) return;
        sharkStrikeIn = -1;
        DiveVisuals.Notify_SharkCalledOff(this);
    }

    // Face down at the surface for breath: SurfaceShareOfDive of the ticks the dive just spent under, times the diver's
    // surface rest factor, so a dive cut short by Rest or a full stringer rests for less.
    private Toil Surface()
    {
        Toil toil = Toils_General.Wait(DiveRules.SurfaceTicksAfter(FullDiveTicks(), SurfaceRestFactor()));
        Action baseInit = toil.initAction;
        toil.initAction = () =>
        {
            baseInit?.Invoke();
            toil.defaultDuration = DiveRules.SurfaceTicksAfter(ticksUnder, SurfaceRestFactor());
            ticksLeftThisToil = toil.defaultDuration;
        };
        return toil;
    }

    // Water the diver may swim through under the water: swimmable water in the same zone as the spot.
    private bool InDiveWater(IntVec3 c)
    {
        Zone_Spearfishing zone = Zone;
        return zone != null && Map.zoneManager.ZoneAt(c) == zone && WavesBridge.IsSwimmableFishingWater(Map, c) && !c.IsForbidden(pawn);
    }

    // One catch roll at the cell the diver is swimming through.
    private void CatchRoll()
    {
        Zone_Spearfishing zone = Zone;
        ThingWithComps spear = SpearfishingUtility.Spear(pawn);
        if (zone == null || spear == null) return;
        IntVec3 at = pawn.Position;
        SkillDef skill = SpearfishingUtility.DiveSkill(spear);
        int level = pawn.skills?.GetSkill(skill)?.Level ?? 0;
        float floorFactor = MapComponent_FishStock.Of(Map).FloorFactorAt(at);
        float chance = DiveRules.CatchChance(level, spear.GetStatValue(SpearfishingDefOf.Spearfishing_DivePower),
            OdysseyFish.DiveStockFraction(Map, at), DiveSuccess(), floorFactor, Find.Storyteller.difficulty.fishingYieldFactor);
        float taken = Rand.Chance(chance) ? zone.TakeCatch(at, 1f) : 0f;
        bool caught = taken > 0f;
        catchRolls++;
        if (caught)
        {
            stringer++;
            OdysseyFish.NotifyCaught(pawn, at, taken);
            PredatorThreat.Notify_Caught(Map, at);
        }
        pawn.skills?.Learn(skill, DiveRules.SkillXpPerRoll);
        OnCatchRoll(caught);
        // Outside OnCatchRoll so an override that skips base still shows the speared shadow.
        if (caught) DiveVisuals.Notify_Speared(this);
    }

    // Back at the surface where the dive ended: the spot is that cell, for the rest and the next move.
    private Toil Surfaced()
    {
        Toil toil = ToilMaker.MakeToil("Surfaced");
        toil.initAction = () =>
        {
            if (pawn.Spawned) job.SetTarget(SpotInd, pawn.Position);
        };
        toil.defaultCompleteMode = ToilCompleteMode.Instant;
        return toil;
    }

    // Dive again from where the diver surfaced, or head home.
    private Toil NextMove(Toil dive, Toil headHome)
    {
        Toil toil = ToilMaker.MakeToil("NextMove");
        toil.initAction = () =>
        {
            if (TimeToHeadHome())
            {
                JumpToToil(headHome);
                return;
            }
            // The fish stock belongs to the whole body of water (ADR 0013), so no spot is better stocked than another: the
            // diver dives again from where they surfaced.
            JumpToToil(dive);
        };
        toil.defaultCompleteMode = ToilCompleteMode.Instant;
        return toil;
    }

    private Toil LeaveCatch()
    {
        Toil toil = ToilMaker.MakeToil("LeaveCatch");
        toil.initAction = ReleaseStringer;
        toil.defaultCompleteMode = ToilCompleteMode.Instant;
        return toil;
    }

    // The only place the stringer becomes items: left on dry land under the diver at the end of a trip, or carried in their
    // inventory when the trip ends at sea (drafted, interrupted or failed).
    private void ReleaseStringer()
    {
        if (stringer <= 0) return;
        int fish = stringer;
        stringer = 0;
        if (pawn.Spawned && SpearfishingUtility.IsDryLand(pawn.Map, pawn.Position))
            SpearfishingUtility.DropCatch(pawn, pawn.Position, fish, Spot);
        else if (pawn.inventory != null)
            SpearfishingUtility.CarryCatch(pawn, fish, Spot);
    }
}
