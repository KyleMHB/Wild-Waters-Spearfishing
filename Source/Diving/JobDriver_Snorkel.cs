using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace Spearfishing;

// Snorkeling, the recreation activity (ticket 17, ADR 0007): swim out to sea near shore, float, drift now and then, freedive
// from time to time, and swim home. A freedive (ticket 21) lasts half a diver's dive at the same Melee skill and drifts under
// the water the way a dive does, surfacing where it ends. No spear, no dive roll, no catch, no fish stock and no skill experience. The swim out and
// home and the safe exits are the shared sea trip's.
//
// Recreation comes only while the pawn is in the water, at vanilla's rate times the snorkeling enjoyment stat. The trip turns
// home when recreation is full, recreation time is over, the session limit (time in the water) is reached, or a safety exit
// fires. Vanilla's JoyTickCheckEnd is never called, so it can't end the job while the pawn is at sea.
public class JobDriver_Snorkel : JobDriver_SeaTrip
{
    // Ticks in the water this session. Saved with the job.
    private int ticksInWater;

    // The snorkeler's stats, read when the toils are built (at the trip's start and again on load), not every tick.
    private float enjoyment = 1f;
    private int sessionTicks = DiveRules.TicksPerHour;

    public int TicksInWater => ticksInWater;

    public int SessionTicks => sessionTicks;

    private int NextDiveTicks() => DiveRules.FreediveTicksFor(pawn.skills?.GetSkill(SkillDefOf.Melee)?.Level ?? 0);

    protected override int TicksHeldBetweenDives => NextDiveTicks() + DiveRules.FloatTicks;

    protected override int SurfaceTicksAfterDive => DiveRules.FloatTicks;

    public override void ExposeData()
    {
        base.ExposeData();
        Scribe_Values.Look(ref ticksInWater, "ticksInWater");
    }

    protected override bool ShouldHeadHome()
    {
        Need_Joy joy = pawn.needs?.joy;
        return joy == null || joy.CurLevel > DiveRules.FullRecreation || ticksInWater >= sessionTicks ||
               (!job.ignoreJoyTimeAssignment && !TimetableUtility.GetTimeAssignment(pawn).allowJoy);
    }

    protected override void TickAtSea()
    {
        if (!pawn.Spawned || !pawn.Position.GetTerrain(Map).IsWater) return;
        ticksInWater++;
        pawn.needs?.joy?.GainJoy(job.def.joyGainRate * DiveRules.RecreationPerTick * enjoyment, job.def.joyKind);
    }

    protected override IEnumerable<Toil> AtSeaToils(Toil headHome)
    {
        enjoyment = pawn.GetStatValue(SnorkelDefOf.Spearfishing_SnorkelingEnjoyment);
        sessionTicks = (int)(pawn.GetStatValue(SnorkelDefOf.Spearfishing_SnorkelingSession) * DiveRules.TicksPerHour);

        Toil swimToSpot = Toils_Goto.GotoCell(SpotInd, PathEndMode.OnCell);
        Toil floating = Toils_General.Wait(DiveRules.FloatTicks);
        Toil freedive = Freedive();
        surfaceToil = floating;
        diveToil = freedive;
        yield return swimToSpot;
        yield return floating;
        yield return NextMove(swimToSpot, floating, freedive, headHome);
        yield return freedive;
        // After a freedive, back to the surface to float.
        yield return Toils_Jump.Jump(floating);
    }

    private Toil Freedive()
    {
        Toil toil = ToilMaker.MakeToil("Freedive");
        toil.defaultCompleteMode = ToilCompleteMode.Delay;
        toil.defaultDuration = NextDiveTicks();
        // The driver set the countdown from defaultDuration before this ran.
        toil.initAction = () =>
        {
            pawn.pather.StopDead();
            toil.defaultDuration = NextDiveTicks();
            ticksLeftThisToil = toil.defaultDuration;
        };
        toil.tickAction = () => SwimUnderwater(InSnorkelWater, NearShore);
        toil.AddFinishAction(() =>
        {
            if (pawn.Spawned) pawn.pather.StopDead();
        });
        return toil;
    }

    // Under the water a snorkeler drifts over the same water a drift at the surface may reach (SnorkelDriftCell).
    private bool InSnorkelWater(IntVec3 c) => WavesBridge.IsSwimmableFishingWater(Map, c) && !c.IsForbidden(pawn);

    private bool NearShore(IntVec3 c) =>
        SpearfishingUtility.DistanceToShoreSquared(Map, c) <= DiveRules.SnorkelMaxCellsFromShore * DiveRules.SnorkelMaxCellsFromShore;

    // Head home, freedive, drift to a nearby cell, or float again here.
    private Toil NextMove(Toil swimToSpot, Toil floating, Toil freedive, Toil headHome)
    {
        Toil toil = ToilMaker.MakeToil("SnorkelNextMove");
        toil.initAction = () =>
        {
            if (TimeToHeadHome())
            {
                JumpToToil(headHome);
                return;
            }
            float roll = Rand.Value;
            if (roll < DiveRules.FreediveChance)
            {
                JumpToToil(freedive);
                return;
            }
            if (roll < DiveRules.FreediveChance + DiveRules.DriftChance)
            {
                IntVec3 next = SpearfishingUtility.SnorkelDriftCell(pawn, Spot);
                if (next.IsValid)
                {
                    job.SetTarget(SpotInd, next);
                    JumpToToil(swimToSpot);
                    return;
                }
            }
            JumpToToil(floating);
        };
        toil.defaultCompleteMode = ToilCompleteMode.Instant;
        return toil;
    }
}
