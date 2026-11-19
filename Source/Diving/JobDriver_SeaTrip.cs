using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace Spearfishing;

// What every trip out to sea shares, for work (JobDriver_DiveTrip) and for recreation (JobDriver_Snorkel): the swim out to a
// spot, the subclass's own loop at sea, and the swim to the nearest dry land when it is time to head home.
//
// Safe exits (ticket 05) live here, not in ShouldHeadHome, so no subclass can drop them: a pawn heads home while they still
// have the Rest and warmth to reach shore, checked at every decision and every SafetyCheckTicks while at sea. Turning off
// Waves' swimming ends the trip at once, and Waves then brings swimmers ashore itself.
//
// Target A is the current spot at sea; B is the shore, set once the trip turns for home.
public abstract class JobDriver_SeaTrip : JobDriver
{
    protected const TargetIndex SpotInd = TargetIndex.A;
    protected const TargetIndex ShoreInd = TargetIndex.B;

    // Why the pawn turned for home for their own safety, or None. Saved with the job.
    private DiveSafety.Exit safetyExit;

    // The nearest dry land, found again at every decision; the periodic safety check measures to it.
    private IntVec3 nearestShore = IntVec3.Invalid;

    public DiveSafety.Exit SafetyExit => safetyExit;

    // The shore the last decision measured to; valid after TimeToHeadHome returns false.
    protected IntVec3 NearestShore => nearestShore;

    // Swimming for shore: set once the trip turns for home, for any reason.
    public bool HeadingHome => job.GetTarget(ShoreInd).IsValid;

    public IntVec3 Spot => job.GetTarget(SpotInd).Cell;

    // The toils the dive visuals read (ticket 12): under the water, and at the surface at the spot. Set by the subclass when
    // it builds its toils, at the trip's start and again after a load; never saved.
    protected Toil diveToil, surfaceToil;

    // Under the water: a dive or a freedive. Read from the pawn draw prefix, which may run off the main thread, so only reads here.
    public bool Submerged => diveToil != null && HaveCurToil && CurToil == diveToil;

    // At the spot between swims: under the water or resting at the surface.
    public bool AtDiveSpot => Submerged || (surfaceToil != null && HaveCurToil && CurToil == surfaceToil);

    // Ticket 33: the swim posture the dive visuals worked out on the last tick, face down or not. Cosmetic and never saved;
    // written only by DiveVisuals.TickPosture on the main thread and read by DiveVisuals.LookOf from the draw threads.
    internal bool PostureFaceDown;

    // The first at-sea toil, the swim out to the spot. Set when the toils are built.
    private Toil swimToSpotToil;

    // Whether a dive follows straight after the swim to the spot (the dive trip), not a rest at the surface (snorkeling).
    protected virtual bool DivesOnArrival => false;

    // Ticket 33, cosmetic: whether the pawn may go under within this many ticks, so the visuals turn it face down in time.
    // The end of each rest at the surface counts, even when the next move turns out not to be a dive, and so does the end
    // of the swim out when a dive follows it. Main thread only; reads, never writes.
    public bool MayDiveWithin(int ticks)
    {
        if (!HaveCurToil || HeadingHome) return false;
        Toil cur = CurToil;
        if (cur == surfaceToil) return ticksLeftThisToil <= ticks;
        return cur == swimToSpotToil && DivesOnArrival && TicksToSpot() <= ticks;
    }

    // Roughly how many ticks the swim to the spot has left: the cells left on the path at the cost of the cell being crossed.
    private float TicksToSpot()
    {
        PawnPath path = pawn.pather.curPath;
        if (path == null || !path.Found)
        {
            IntVec3 d = pawn.Position - Spot;
            return Math.Max(Math.Abs(d.x), Math.Abs(d.z)) * (float)pawn.TicksPerMoveCardinal;
        }
        float perCell = Math.Max(pawn.pather.nextCellCostTotal, pawn.TicksPerMoveCardinal);
        return pawn.pather.nextCellCostLeft + Math.Max(0, path.NodesLeftCount - 1) * perCell;
    }

    // How far through the current dive or freedive, 0 to 1, or -1 when not under the water. Read off the main thread too.
    public float SubmergedFraction
    {
        get
        {
            if (!Submerged || diveToil.defaultDuration <= 0) return -1f;
            return UnityEngine.Mathf.Clamp01(1f - (float)ticksLeftThisToil / diveToil.defaultDuration);
        }
    }

    // Ticks at sea before the pawn can next turn home (tickets 21 and 25): the rest of the current dive and the surface after
    // it, or, at any other point, what the subclass holds the pawn for between dives. 0 once swimming home. The safety exits
    // keep Rest and warmth for this as well as the swim home.
    public float TicksBeforeTurningHome =>
        HeadingHome ? 0f : Submerged ? ticksLeftThisToil + SurfaceTicksAfterDive : TicksHeldBetweenDives;

    // Ticks at sea, away from a dive, before the pawn can next turn home: the next dive the trip commits to and its surface.
    protected abstract int TicksHeldBetweenDives { get; }

    // Length of the rest at the surface after the current dive or freedive.
    protected abstract int SurfaceTicksAfterDive { get; }

    public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

    // Moving under the water (ticket 21), called every tick of a dive or freedive: swims on to a waypoint a few cells away
    // over cells that cellOk allows, at the pawn's own swim speed, and stops at once if the path turns onto a cell it does
    // not. The spot follows the pawn, so the pawn surfaces where the dive ends. waypointOk, if given, is a dearer test run
    // only on a waypoint. Gameplay, so Rand is fine (ADR 0002).
    //
    // stalk (ticket 23, spearfishers): with a fish shoal in sight the pawn takes, of the same random waypoints, the one
    // nearest the shoal, at a walk instead of a jog. With the dive visuals off or no shoal the waypoint is ticket 21's. The
    // dive's length and its catch do not depend on where the pawn swims, so neither changes.
    //
    // The six waypoints are drawn before the shoal is looked at (ticket 28, ADR 0002): the visuals may choose among the
    // gameplay draws, but the number of draws never depends on what is drawn on screen.
    protected void SwimUnderwater(Func<IntVec3, bool> cellOk, Func<IntVec3, bool> waypointOk = null, bool stalk = false)
    {
        if (!pawn.Spawned) return;
        job.SetTarget(SpotInd, pawn.Position);
        if (pawn.pather.Moving)
        {
            if (cellOk(pawn.pather.nextCell)) return;
            pawn.pather.StopDead();
        }
        // A pawn boxed in by disallowed water waits where it is; a few tries a second are enough.
        if (!pawn.IsHashIntervalTick(15)) return;
        IntVec3 here = pawn.Position;
        int from = GenRadial.NumCellsInRadius(DiveRules.UnderwaterWaypointMin), to = GenRadial.NumCellsInRadius(DiveRules.UnderwaterWaypointMax);
        waypoints.Clear();
        for (int i = 0; i < WaypointDraws; i++) waypoints.Add(here + GenRadial.RadialPattern[Rand.Range(from, to)]);
        waypoints.RemoveAll(c => !c.InBounds(Map) || !cellOk(c) || !LineAllowed(here, c, cellOk));
        if (stalk)
        {
            // The last stalking path is over: did it end nearer a shoal than it began? Developer diagnostics only.
            if (stalkFrom >= 0f) DiveVisuals.Notify_StalkEnded(pawn, stalkFrom);
            stalkFrom = -1f;
            job.locomotionUrgency = LocomotionUrgency.Jog;
            if (DiveVisuals.TryStalkTarget(pawn, out UnityEngine.Vector3 shoal))
            {
                // A stable sort, so equally near waypoints keep their draw order.
                waypoints.SortStable((a, b) =>
                    (a.ToVector3Shifted() - shoal).MagnitudeHorizontalSquared().CompareTo((b.ToVector3Shifted() - shoal).MagnitudeHorizontalSquared()));
                IntVec3 near = FirstGoodWaypoint(waypointOk);
                if (!near.IsValid) return;
                // A slow, quiet approach: walking costs twice a jog's ticks per cell.
                job.locomotionUrgency = LocomotionUrgency.Walk;
                pawn.pather.StartPath(near, PathEndMode.OnCell);
                stalkFrom = (pawn.DrawPos - shoal).MagnitudeHorizontal();
                DiveVisuals.Notify_StalkStarted();
                return;
            }
        }
        // Ticket 21's waypoint: the first of the draws that passes every test.
        IntVec3 next = FirstGoodWaypoint(waypointOk);
        if (next.IsValid) pawn.pather.StartPath(next, PathEndMode.OnCell);
    }

    // waypointOk and reachability are the dear tests, so they run last and only until a waypoint passes.
    private IntVec3 FirstGoodWaypoint(Func<IntVec3, bool> waypointOk)
    {
        foreach (IntVec3 c in waypoints)
            if ((waypointOk == null || waypointOk(c)) && pawn.CanReach(c, PathEndMode.OnCell, Danger.Some)) return c;
        return IntVec3.Invalid;
    }

    private const int WaypointDraws = 6;

    // Unsaved: how far the pawn was from the stalked shoal when this stalking path began, or below zero for none.
    private float stalkFrom = -1f;
    private static readonly List<IntVec3> waypoints = new();

    // At the end of a dive: back to a jog, and no stalking path left open.
    protected void EndStalk()
    {
        job.locomotionUrgency = LocomotionUrgency.Jog;
        stalkFrom = -1f;
    }

    private bool LineAllowed(IntVec3 a, IntVec3 b, Func<IntVec3, bool> cellOk)
    {
        foreach (IntVec3 c in GenSight.PointsOnLineOfSight(a, b))
            if (!c.InBounds(Map) || !cellOk(c)) return false;
        return true;
    }

    // A failed path under the water only means another waypoint; anywhere else it ends the trip as usual.
    public override void Notify_PatherFailed()
    {
        if (Submerged) return;
        base.Notify_PatherFailed();
    }

    public override void ExposeData()
    {
        base.ExposeData();
        Scribe_Values.Look(ref safetyExit, "safetyExit");
    }

    // When the pawn stops and heads home, besides the safety exits.
    protected abstract bool ShouldHeadHome();

    // The toils at sea, after the swim out begins and before the swim home: the swim to the spot first. Every toil returned
    // gets the at-sea tick. headHome is the toil to jump to when the trip is over.
    protected abstract IEnumerable<Toil> AtSeaToils(Toil headHome);

    // Toils once the pawn stands on dry land at the end of the trip.
    protected virtual IEnumerable<Toil> AshoreToils()
    {
        yield break;
    }

    // Called every tick while at sea, before the safety check.
    protected virtual void TickAtSea()
    {
    }

    // The safety exits, then the subclass's reasons. Finds the nearest shore again first.
    protected bool TimeToHeadHome()
    {
        nearestShore = SpearfishingUtility.ShoreCellNear(pawn);
        return UnsafeToStay() || ShouldHeadHome();
    }

    // No reachable shore means no safe swim to plan, so the trip ends (and Waves brings the pawn ashore).
    private bool UnsafeToStay()
    {
        if (!nearestShore.IsValid) nearestShore = SpearfishingUtility.ShoreCellNear(pawn);
        if (!nearestShore.IsValid) return true;
        DiveSafety.Exit exit = DiveSafety.MustHeadHome(pawn, nearestShore);
        if (exit == DiveSafety.Exit.None) return false;
        safetyExit = exit;
        return true;
    }

    protected override IEnumerable<Toil> MakeNewToils()
    {
        this.FailOn(() => !WavesBridge.SwimmingOn);

        Toil headHome = HeadHome();
        var atSea = new List<Toil>(AtSeaToils(headHome));
        swimToSpotToil = atSea.Count > 0 ? atSea[0] : null;
        // Runs when the toils are built: at the trip's start and again after a load. Cosmetic only (ADR 0002).
        DiveVisuals.Register(this);
        // From the toil, not the frame clock, so no dive is missed at high speed and a load mid-dive plays nothing.
        if (diveToil != null)
        {
            diveToil.AddPreInitAction(() => DiveVisuals.Notify_WentUnder(this));
            diveToil.AddFinishAction(() => DiveVisuals.Notify_CameUp(this));
        }
        foreach (Toil toil in atSea)
            toil.AddPreTickAction(() =>
            {
                // Dubs Bad Hygiene: time in the water counts as a wash. Does nothing without DBH.
                if (BadHygieneCompat.Active && pawn.Position.GetTerrain(Map).IsWater) BadHygieneCompat.WashTick(pawn);
                TickAtSea();
                DiveVisuals.TickPosture(this);
                if (pawn.IsHashIntervalTick(DiveRules.SafetyCheckTicks) && UnsafeToStay()) JumpToToil(headHome);
            });

        yield return Toils_Jump.JumpIf(headHome, TimeToHeadHome);
        foreach (Toil toil in atSea) yield return toil;
        yield return headHome;
        Toil swimHome = Toils_Goto.GotoCell(ShoreInd, PathEndMode.OnCell);
        swimHome.AddPreTickAction(() => DiveVisuals.TickPosture(this));
        // Ashore the posture no longer ticks, so the last look in the water must not carry up the beach.
        swimHome.AddFinishAction(() => PostureFaceDown = false);
        yield return swimHome;
        foreach (Toil toil in AshoreToils()) yield return toil;
    }

    private Toil HeadHome()
    {
        Toil toil = ToilMaker.MakeToil("HeadHome");
        toil.initAction = () =>
        {
            IntVec3 shore = SpearfishingUtility.ShoreCellNear(pawn);
            if (!shore.IsValid)
            {
                EndJobWith(JobCondition.Incompletable);
                return;
            }
            job.SetTarget(ShoreInd, shore);
        };
        toil.defaultCompleteMode = ToilCompleteMode.Instant;
        return toil;
    }
}
