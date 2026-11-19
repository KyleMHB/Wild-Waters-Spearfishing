using System.Collections.Generic;
using HarmonyLib;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace Spearfishing;

// What a swimmer sounds like (ticket 30): a quiet stroke now and then while swimming at the surface, a splash going under, a
// splash coming up and a soft burst of bubbles with each bubble cluster DiveVisuals draws. Like the visuals they play only
// for pawns in view on the map being looked at, and only with the dive visuals setting on. Cosmetic only (ADR 0002): nothing
// is saved, and every play runs inside its own Rand state so the gameplay random stream never moves.
public static class DiveSounds
{
    // DiveVisuals' bubble timing: the first cluster leaves as the going-under ripple ends, then one cluster every period.
    private const float BubbleDelay = 0.8f, BubblePeriod = 1.4f;
    // Strokes: at most one a second per swimmer, with jitter so a group does not stroke in step. Floating still at the spot
    // is a slow, occasional paddle.
    private const float StrokeMin = 1.0f, StrokeMax = 1.6f, PaddleMin = 2.5f, PaddleMax = 4.0f;

    private sealed class State
    {
        public bool WasSubmerged;
        public float BubblesFrom;
        public int LastBubble = -1;
        public float NextStrokeAt;
        public int SeenFrame;
    }

    private static readonly Dictionary<Pawn, State> states = new();
    private static readonly List<Pawn> stale = new();
    private static readonly System.Random rng = new(30);
    private static float clock;
    private static int lastFrame = -1, lastTick = -1;
    private static Game game;

    // Read-only diagnostics for the developer tests: each counts the decision to play, made just before the sound starts.
    public static int StrokesPlayed { get; private set; }
    public static int DivesPlayed { get; private set; }
    public static int SurfacesPlayed { get; private set; }
    public static int BubblesPlayed { get; private set; }
    // The sound clock, in seconds; it moves only on frames this class works in.
    public static float Clock => clock;

    // From the dive toil's start, through DiveVisuals, which has already checked the setting.
    internal static void Notify_WentUnder(Pawn pawn)
    {
        if (!Audible(pawn)) return;
        DivesPlayed++;
        Play(DiveSoundDefOf.Spearfishing_DiveDown, pawn);
    }

    // From the dive toil's end, through DiveVisuals.
    internal static void Notify_CameUp(Pawn pawn)
    {
        if (!Audible(pawn)) return;
        SurfacesPlayed++;
        Play(DiveSoundDefOf.Spearfishing_Surface, pawn);
    }

    // Every frame for the map being drawn. Returns at once while nobody is at sea, as DiveVisuals does.
    internal static void MapUpdate(Map map)
    {
        if (DiveVisuals.ActiveDivers == 0 || !DiveVisuals.On || !WorldRendererUtility.DrawingMap || Find.CurrentMap != map) return;
        if (lastFrame == Time.frameCount) return;
        lastFrame = Time.frameCount;
        if (game != Current.Game)
        {
            game = Current.Game;
            states.Clear();
        }
        // The same clock as the bubbles: real time, still while paused.
        int tick = Find.TickManager.TicksGame;
        bool running = !Find.TickManager.Paused || tick != lastTick;
        lastTick = tick;
        if (running) clock += Mathf.Min(Time.unscaledDeltaTime, 0.1f);

        CellRect view = Find.CameraDriver.CurrentViewRect.ExpandedBy(3);
        IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
        for (int i = 0; i < pawns.Count; i++)
        {
            Pawn pawn = pawns[i];
            if (pawn.jobs?.curDriver is not JobDriver_SeaTrip driver) continue;
            if (!states.TryGetValue(pawn, out State state)) states[pawn] = state = new State();
            state.SeenFrame = lastFrame;
            Update(pawn, driver, state, map, view.Contains(pawn.Position));
        }
        if (states.Count > 0 && lastFrame % 120 == 0) Prune();
    }

    private static void Update(Pawn pawn, JobDriver_SeaTrip driver, State state, Map map, bool inView)
    {
        bool submerged = driver.Submerged;
        if (submerged && !state.WasSubmerged)
        {
            state.BubblesFrom = clock + BubbleDelay;
            state.LastBubble = -1;
        }
        state.WasSubmerged = submerged;

        if (submerged)
        {
            if (clock < state.BubblesFrom) return;
            // One sound as each cluster leaves the diver.
            int cluster = (int)((clock - state.BubblesFrom) / BubblePeriod);
            if (cluster == state.LastBubble) return;
            state.LastBubble = cluster;
            if (!inView) return;
            BubblesPlayed++;
            Play(DiveSoundDefOf.Spearfishing_Bubbles, pawn);
            return;
        }

        if (clock < state.NextStrokeAt || !pawn.Position.GetTerrain(map).IsWater) return;
        bool swimming = pawn.pather.Moving;
        bool floating = !swimming && driver.AtDiveSpot;
        if (!swimming && !floating) return;
        float min = swimming ? StrokeMin : PaddleMin, max = swimming ? StrokeMax : PaddleMax;
        state.NextStrokeAt = clock + min + (float)rng.NextDouble() * (max - min);
        if (!inView) return;
        StrokesPlayed++;
        Play(DiveSoundDefOf.Spearfishing_SwimStroke, pawn);
    }

    private static bool Audible(Pawn pawn) =>
        pawn.Spawned && pawn.Map == Find.CurrentMap && WorldRendererUtility.DrawingMap &&
        Find.CameraDriver.CurrentViewRect.ExpandedBy(3).Contains(pawn.Position);

    // PlayOneShot rolls the clip, volume and pitch with Verse.Rand: run it on its own seed so cosmetic code never moves the
    // gameplay random stream (ADR 0002).
    private static void Play(SoundDef def, Pawn pawn)
    {
        Rand.PushState(rng.Next());
        try
        {
            def.PlayOneShot(new TargetInfo(pawn.Position, pawn.Map));
        }
        finally
        {
            Rand.PopState();
        }
    }

    // Swimmers not seen this frame have finished their trip, left the map or belong to an old game.
    private static void Prune()
    {
        stale.Clear();
        foreach (var pair in states)
            if (pair.Value.SeenFrame != lastFrame) stale.Add(pair.Key);
        for (int i = 0; i < stale.Count; i++) states.Remove(stale[i]);
    }
}

// The frame hook for the swim sounds. Returns at once while nobody is at sea.
[HarmonyPatch(typeof(Map), nameof(Map.MapUpdate))]
internal static class Patch_Map_MapUpdate_DiveSounds
{
    private static void Postfix(Map __instance) => DiveSounds.MapUpdate(__instance);
}
