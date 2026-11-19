using System.Collections.Generic;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace Spearfishing;

// What a player sees of a dive (ticket 12): the diver, or a freediving snorkeler (ticket 17), hidden while under the water,
// drawn face down while floating at the surface at the spot (ticket 18: the back of the head with its headgear and no body,
// with sunk shoulders and a waterline ring, art/face-down/APPROVAL.md), a pawn-shaped shadow under the water while they
// dive (ticket 26), a ripple as the head goes under and as it comes up, bubbles while down (ticket 20), shoals of fish around the
// swimmer while they are in the water (ticket 23, FishShoals), and on a catch the nearest fish darting in to the spear with a
// small burst. Cosmetic only (ADR 0002): the catch is rolled from the fish stock, and nothing here is saved, ticked or a
// Thing. Drawn on the frame clock with Graphics.DrawMesh, as Waves draws its sea life, but with our own textures and code.
//
// Cost: trips register here when their toils are built, and every frame hook returns at once while the list is empty, so
// with nobody diving the only work is one count test per hook. Otherwise the work is a few shoals per swimmer on the map
// and a few draws per fish in view.
public static class DiveVisuals
{
    // Our own approved art (art/dive-visuals/APPROVAL.md): a white shape that the materials below tint and fade.
    private const string BurstTexPath = "Spearfishing/Dive/SpearBurst";

    // On a catch the burst grows and fades.
    private const float BurstSeconds = 0.6f;
    // Zoomed out past this camera root size the fish are too small to read and are not drawn; they keep swimming.
    private const float FishHideZoom = 40f;
    // The shoals run at the game speed up to this many times real time, so they keep up with a fast-forwarded swimmer.
    private const float MaxShoalSpeedUp = 3f;
    // A swimmer whose shoals were updated within this many frames can stalk them.
    private const int StalkFreshFrames = 30;
    private const float BurstMinSize = 0.5f, BurstMaxSize = 1.6f;
    private const int FadeSteps = 5;
    private static readonly Color ShadowColor = new(0.03f, 0.08f, 0.10f);
    private static readonly Color BurstColor = new(0.85f, 0.95f, 1f);

    // Face down, look C (ticket 18, chosen again in ticket 20; art/face-down/APPROVAL.md): around the head the pawn draws,
    // the shoulders sunk under the water and a ring where the head meets it. Sizes and offsets in cells; offsets run south
    // of the head's centre. The game sinks a swimmer's head 0.5 cells.
    private const string ShouldersTexPath = "Spearfishing/Dive/Shoulders";
    private const string WaterlineTexPath = "Spearfishing/Dive/Waterline";
    private const float SwimHeadSink = 0.5f;
    private const float ShouldersSize = 0.95f, ShouldersOffset = 0.38f, ShouldersAlpha = 0.5f;
    private const float WaterlineSize = 1f, WaterlineOffset = 0.1f, WaterlineAlpha = 0.45f;
    private static readonly Color WaterlineColor = new(0.84f, 0.94f, 1f);

    // Ticket 20 (art/dive-anim/APPROVAL.md): while under the water a head-and-shoulders shadow shrinks and fades as the pawn
    // goes down, holds at the bottom and grows back on the way up. One pale ripple spreads out as the head goes under and
    // another as it comes up, and while they are down a small cluster of bubbles rises and pops every so often. No glow, so
    // none of it reads as Waves' night plankton.
    // Ticket 22 turns the shadow to the way the diver travels. Ticket 26 (art/dive-anim/APPROVAL.md): the shape is a pawn
    // seen from behind, head leading, and its edge softens with the water's depth. Each blur level is its own prebuilt
    // texture (art/depth_blur.py), crisp, medium and soft, so nothing is blurred while drawing.
    private const string DiveShadowTexPath = "Spearfishing/Dive/DiveShadowPawn_";
    private static readonly string[] DiveShadowBlurLevels = { "Crisp", "Medium", "Soft" };
    private const string RippleTexPath = "Spearfishing/Dive/Ripple";
    private const string BubbleTexPath = "Spearfishing/Dive/Bubble";
    private const float DiveShadowOffset = 0.3f;
    // The silhouette fills 0.84 of its texture's height, so at 1.35 it is about a pawn's 1.14 cells tall at the surface.
    private const float DiveShadowSurfaceSize = 1.35f, DiveShadowSurfaceAlpha = 0.55f;
    // Ticket 22: the bottom of the dive follows the water under the diver (MapComponent_FishStock.SwimDepthAt): over the
    // shallowest water the shadow stays large and dark, over the deepest it shrinks and fades as ticket 20 drew it. The
    // bottom eases to a new depth over about half a second, so crossing water does not snap it.
    private const float ShallowBottomSize = 0.85f, DeepBottomSize = 0.55f;
    private const float ShallowBottomAlpha = 0.50f, DeepBottomAlpha = 0.22f;
    private const float DepthEaseSeconds = 0.5f;
    // The heading follows the smoothed travel direction, turning at most this fast, in degrees per second. Travel slower than
    // the minimum speed (cells per second) holds the last heading.
    private const float TurnSpeed = 270f, VelocitySmoothSeconds = 0.15f, MinTravelSpeed = 0.3f;
    // Share of a dive spent going down, and coming up.
    private const float DescentShare = 0.35f, AscentShare = 0.35f;
    private const int DiveShadowSteps = 16;
    // The ripple grows from its start to its end size in cells, easing out, and fades as it goes.
    private const float RippleSeconds = 0.8f, RippleAlpha = 0.8f, RippleStartSize = 0.5f, RippleEndSize = 1.7f, RippleOffset = 0.05f;
    // A cluster of three bubbles every period, a moment apart, the first as the going-under ripple ends. Each rises, growing
    // and brightening, then pops as a tiny ring. Offsets in cells from the head, south positive.
    private const float BubblePeriod = 1.4f, BubbleStagger = 0.12f, BubbleRiseSeconds = 0.7f, BubblePopSeconds = 0.2f;
    private const float BubbleRise = 0.15f, PopAlpha = 0.7f;
    private static readonly Vector2[] BubbleSpots = { new(0f, 0.1f), new(-0.12f, 0.2f), new(0.1f, 0.25f) };

    private sealed class Diver
    {
        public JobDriver_SeaTrip Driver;
        public Pawn Pawn;
        public Game Game;
        public FishShoals Shoals;
        public bool WasSubmerged;
        // Clock time of the last catch, or below zero for none.
        public float SpearedAt = -1f;
        public Vector3 SpearedAt3;
        // Clock times the head last went under and came up, or below zero for none playing.
        public float UnderAt = -1f, UpAt = -1f;
        // Clock time this dive's bubble cycle starts from.
        public float BubblesFrom;
        // Ticket 22: the eased water depth under the diver (0 to 1), the heading in degrees clockwise from north, and the
        // draw position and smoothed velocity the heading comes from. Started on the first frame the diver is seen.
        public bool Started;
        public float WaterDepth, Heading;
        public Vector3 LastPos, Velocity;
        // Ticket 33, the swim posture, worked out on the game tick: face down or not, the tick the current look ends, the
        // ticks it had left when the pawn went under (it waits out the dive), and whether the pawn has reached the spot.
        public bool FaceDown, Under, ReachedSpot;
        public int PostureEndsAt, PostureLeftUnder;
        // Whether the pather was stepping on the last surface tick, so the heading can start from the way a pawn sets off.
        public bool Travelling;
        public System.Random PostureRng;
        // Ticket 34 diagnostics: the last frame the dive shadow, and at least one of this swimmer's shoal fish, was drawn.
        public int ShadowFrame = -1, FishFrame = -1;
        // Ticket 34: whether the fishing water under the pawn was a lake or river, not the sea, so its art goes under that water.
        public bool Freshwater;
        // Gear tiers ticket 11: the shark's game tick of arrival (-1 for none), the tick it was called off before striking
        // (-1 if not), whether it bites, and where it starts round the diver and which way it circles.
        public int SharkFrom = -1, SharkCalledOff = -1;
        public bool SharkBites;
        public float SharkAngle, SharkTurn;
    }

    private static readonly List<Diver> divers = new();
    private static Material[] burstMaterials, rippleMaterials, bubbleMaterials;
    // Per blur level, its alpha steps.
    private static Material[][] diveShadowMaterials, freshwaterDiveShadowMaterials;
    private static Material shouldersMaterial, freshwaterShouldersMaterial, waterlineMaterial;
    private static float clock, frameDelta;
    private static int lastFrame = -1, lastTick = -1;

    // Read-only diagnostics for the developer tests: trips the renderer knows about, frames it did work in, shadows drawn
    // and speared-shadow effects started since the game started.
    public static int ActiveDivers => divers.Count;
    public static int FramesWorked { get; private set; }
    public static int ShadowsDrawn { get; private set; }
    public static int SpearEffects { get; private set; }
    // Ticket 20: face-down shoulders-and-ring draws, dive-shadow draws, going-under and coming-up animations started, and
    // bubble and bubble-pop draws.
    public static int FaceDownShapesDrawn { get; private set; }
    public static int DiveShadowsDrawn { get; private set; }
    public static int GoingUnderEffects { get; private set; }
    public static int ComingUpEffects { get; private set; }
    public static int BubblesDrawn { get; private set; }
    // Fish draws left out because the fish was over a cell that is not swimmable sea (a shore, a small pond).
    public static int ShadowsOffWaterSkipped { get; private set; }
    // Developer tests only: called with each shoal fish's position as it is drawn. Null in play, so one null test per draw.
    public static System.Action<Vector3> ShadowDrawnHook;

    // Ticket 23 diagnostics, since the game started: shoals a spearfisher scattered, shoals that regrouped after it, scatters
    // that ended farther from the pawn than they began, look-ahead turns that kept a leader off the shore, and degrees of
    // circling round snorkelers; stalking paths begun, and those that ended nearer a shoal than they began.
    public static int ShoalScatters => FishShoals.ScatterEvents;
    public static int ShoalRegroups => FishShoals.RegroupEvents;
    public static int ShoalScattersMovedAway => FishShoals.ScatterMovedAway;
    public static int ShoalShoreTurns => FishShoals.LeaderShoreTurns;
    public static float ShoalCircledDegrees => FishShoals.CircledDegrees;
    // Ticket 32 diagnostics, since the game started: fish steps measured during scatters and during cruising wander turns,
    // those faster than the fish's speed cap plus a small margin, and the summed degrees between facing and travel.
    public static int ShoalScatterSteps => FishShoals.ScatterSteps;
    public static int ShoalScatterOverCap => FishShoals.ScatterOverCap;
    public static float ShoalScatterFaceError => FishShoals.ScatterFaceError;
    public static int ShoalTurnSteps => FishShoals.TurnSteps;
    public static int ShoalTurnOverCap => FishShoals.TurnOverCap;
    public static float ShoalTurnFaceError => FishShoals.TurnFaceError;
    public static int StalkPathsStarted { get; private set; }
    public static int StalkPathsEndedNearer { get; private set; }

    // Live shoals over every swimmer.
    public static int ShoalCount
    {
        get
        {
            int total = 0;
            for (int i = 0; i < divers.Count; i++)
            {
                divers[i].Shoals.Stats(out int n, out _, out _, out _);
                total += n;
            }
            return total;
        }
    }

    // The farthest any fish sits from its shoal's leader this frame, in cells.
    public static float LargestShoalSpread
    {
        get
        {
            float widest = 0f;
            for (int i = 0; i < divers.Count; i++) widest = Mathf.Max(widest, divers[i].Shoals.LargestSpread);
            return widest;
        }
    }

    // One swimmer's shoals: how many, their fish in all, and the fewest and most in one shoal. All 0 with none.
    public static void ShoalStats(Pawn pawn, out int shoals, out int fish, out int minFish, out int maxFish)
    {
        shoals = fish = minFish = maxFish = 0;
        DiverOf(pawn)?.Shoals.Stats(out shoals, out fish, out minFish, out maxFish);
    }

    // One swimmer's shoal fish settled at their depth: the summed blur level (0 crisp, 2 soft) and count over shallow water
    // (swim depth under 0.1) and over deep water (over 0.3). Reads shoal state only, so the camera does not matter.
    public static void FishBlurSample(Pawn pawn, ref float shallowSum, ref int shallowN, ref float deepSum, ref int deepN) =>
        DiverOf(pawn)?.Shoals.BlurSample(ref shallowSum, ref shallowN, ref deepSum, ref deepN);

    // Cells from the pawn to their nearest shoal's leader, or NaN with none.
    public static float NearestShoalDistance(Pawn pawn)
    {
        Diver diver = DiverOf(pawn);
        if (diver == null || !diver.Shoals.Nearest(pawn.DrawPos, false, out Vector3 at)) return float.NaN;
        at.y = pawn.DrawPos.y;
        return (at - pawn.DrawPos).magnitude;
    }

    // The shoal a spearfisher stalks: the nearest one not scattering or fading out, while the shoals are being updated.
    // False with the visuals off, the map not shown or no such shoal, and the dive then takes ticket 21's waypoints.
    public static bool TryStalkTarget(Pawn pawn, out Vector3 at)
    {
        at = Vector3.zero;
        Diver diver = DiverOf(pawn);
        if (diver == null || Time.frameCount - diver.Shoals.UpdatedFrame > StalkFreshFrames) return false;
        return diver.Shoals.Nearest(pawn.DrawPos, true, out at);
    }

    internal static void Notify_StalkStarted() => StalkPathsStarted++;

    internal static void Notify_StalkEnded(Pawn pawn, float startDistance)
    {
        float now = NearestShoalDistance(pawn);
        if (!float.IsNaN(now) && now < startDistance) StalkPathsEndedNearer++;
    }

    // Pawn draws the face-down patch has turned to the back of the head since the game started. Counted from the parallel
    // draw phase, so with Interlocked.
    public static int FaceDownDraws => faceDownDraws;
    private static int faceDownDraws;

    public static bool On => SpearfishingMod.Settings == null || SpearfishingMod.Settings.diveVisuals;

    // How a pawn is drawn this frame.
    public enum Look
    {
        // As the game and Waves draw it ("face up"): ashore, wading, looking up while swimming, or the visuals are off.
        Normal,
        // Under the water: not drawn at all.
        Hidden,
        // Face down in the water (tickets 18 and 33): the back of the head with its headgear, the body under the water.
        FaceDown,
    }

    // The one decision both pawn draw patches use. Runs for every drawn pawn, every frame, and on worker threads during the
    // parallel draw phase: the empty-list test comes first, and nothing here writes. The swim posture's timers run on the
    // tick (TickPosture); this only reads the result. Without the bridge's swimming question it keeps ticket 18's rule:
    // face down at the spot, normal elsewhere.
    public static Look LookOf(Pawn pawn)
    {
        if (divers.Count == 0 || !On || pawn?.jobs?.curDriver is not JobDriver_SeaTrip driver) return Look.Normal;
        if (driver.Submerged) return Look.Hidden;
        // The posture flag is only as fresh as the last posture tick, which runs before the pather moves the pawn and not
        // at all on the trip's land toils, so the swimming question is asked again here: until Waves has the pawn swimming,
        // walking ashore, entering the water and wading draw exactly as the game and Waves draw them (ticket 33 fix-ups).
        if (WavesBridge.KnowsSwimming) return driver.PostureFaceDown && WavesBridge.IsSwimming(pawn) ? Look.FaceDown : Look.Normal;
        return driver.AtDiveSpot && OnWater(pawn) ? Look.FaceDown : Look.Normal;
    }

    // Read only, so safe from the draw threads.
    private static bool OnWater(Pawn pawn)
    {
        Map map = pawn.MapHeld;
        return pawn.Spawned && map != null && pawn.Position.InBounds(map) && pawn.Position.GetTerrain(map).IsWater;
    }

    // Ticket 33's swim posture, in ticks at 1x: swimming out or home, face down 4 to 8 seconds then normal 2 to 4; at the
    // spot, face down 10 to 20 seconds and a look-up of 2 to 4. Face down for at least the last DiveFaceDownTicks before a
    // possible dive, cutting a look-up short; no look-up starts within NoLookUpTicks of one, so a cut look-up still lasts
    // over a second. A pawn that is not swimming keeps the normal look, even wading into a dive (the user dropped the
    // wading duck on 2026-11-16: the look must not change until the pawn swims).
    private const int SwimFaceDownMin = 240, SwimFaceDownMax = 480, SpotFaceDownMin = 600, SpotFaceDownMax = 1200;
    private const int LookUpMin = 120, LookUpMax = 240, NoLookUpTicks = 150;
    public const int DiveFaceDownTicks = 75;

    // Called every tick of the trip at sea and on the swim home. Cosmetic only (ADR 0002): its own System.Random, nothing
    // saved, nothing read back by gameplay. Does nothing with the visuals off or without the bridge's swimming question.
    internal static void TickPosture(JobDriver_SeaTrip driver)
    {
        Diver diver = DiverFor(driver);
        if (diver == null || !WavesBridge.KnowsSwimming)
        {
            driver.PostureFaceDown = false;
            return;
        }
        int now = Find.TickManager.TicksGame;
        // The look waits out a dive: the time it had left carries on at the surface.
        if (driver.Submerged)
        {
            if (!diver.Under) diver.PostureLeftUnder = Mathf.Max(0, diver.PostureEndsAt - now);
            diver.Under = true;
            diver.Travelling = false;
            return;
        }
        if (diver.Under)
        {
            diver.Under = false;
            diver.PostureEndsAt = now + diver.PostureLeftUnder;
        }
        // A pawn comes up standing still and holds whatever heading it had; eased from there it would spin on the spot as it
        // swims off (the third review). So a pawn setting off, or going face down while moving, starts facing its next step.
        // Done on the tick, not the frame, as several ticks can pass in one frame at speed.
        bool wasFaceDown = diver.FaceDown;
        bool travelling = TravelAngle(driver.pawn, out float travel);
        if (travelling && !diver.Travelling) SeedHeading(diver, travel);
        diver.Travelling = travelling;
        if (driver.AtDiveSpot) diver.ReachedSpot = true;
        diver.PostureRng ??= new System.Random(driver.pawn.thingIDNumber * 104729 + 31);
        // Wading or ashore: the normal look, and the next swim starts with it.
        if (!WavesBridge.IsSwimming(driver.pawn))
        {
            diver.FaceDown = false;
            diver.PostureEndsAt = now + diver.PostureRng.Next(LookUpMin, LookUpMax + 1);
            driver.PostureFaceDown = false;
            return;
        }
        bool atSpot = diver.ReachedSpot && !driver.HeadingHome;
        if (driver.MayDiveWithin(DiveFaceDownTicks))
        {
            if (!diver.FaceDown) StartFaceDown(diver, now, atSpot);
        }
        else if (now >= diver.PostureEndsAt)
        {
            if (!diver.FaceDown) StartFaceDown(diver, now, atSpot);
            // A look-up that is due waits until no dive can come before it would be cut short.
            else if (!driver.MayDiveWithin(NoLookUpTicks))
            {
                diver.FaceDown = false;
                diver.PostureEndsAt = now + diver.PostureRng.Next(LookUpMin, LookUpMax + 1);
            }
        }
        if (travelling && diver.FaceDown && !wasFaceDown) SeedHeading(diver, travel);
        driver.PostureFaceDown = diver.FaceDown;
    }

    // The way the pawn is stepping, in degrees clockwise from north like the heading, or false while it is not moving.
    private static bool TravelAngle(Pawn pawn, out float angle)
    {
        angle = 0f;
        if (pawn.pather == null || !pawn.pather.Moving || pawn.pather.nextCell == pawn.Position) return false;
        IntVec3 step = pawn.pather.nextCell - pawn.Position;
        angle = Mathf.Repeat(Mathf.Atan2(step.x, step.z) * Mathf.Rad2Deg, 360f);
        return true;
    }

    // The smoothed velocity starts again too, so the old motion does not ease the heading back round.
    private static void SeedHeading(Diver diver, float angle)
    {
        diver.Heading = angle;
        diver.Velocity = Vector3.zero;
    }

    private static void StartFaceDown(Diver diver, int now, bool atSpot)
    {
        diver.FaceDown = true;
        diver.PostureEndsAt = now + (atSpot
            ? diver.PostureRng.Next(SpotFaceDownMin, SpotFaceDownMax + 1)
            : diver.PostureRng.Next(SwimFaceDownMin, SwimFaceDownMax + 1));
    }

    public static bool Hides(Pawn pawn) => LookOf(pawn) == Look.Hidden;

    internal static void Notify_FaceDownDraw() => System.Threading.Interlocked.Increment(ref faceDownDraws);

    // Ticket 35: a swimmer holds the spear at their right side, parallel to the heading with the tip forward, the front half
    // out of the water and the back half under it. Offsets in cells from the body's centre in the heading's frame (right,
    // forward). The side offset clears the sunk head in both postures: the head sits at most about 0.2 cells to either side
    // of the centre, so the shaft stays about 0.3 from it. The spear is placed from the centre, not the head, so it does not
    // jump when the head moves at a posture switch. The art points right (east) along its length.
    private const float SpearSideOffset = 0.5f, SpearForwardOffset = 0f;
    // The back half: the spear's own texture tinted toward the water and faded, drawn under the water's surface layers like
    // ticket 18's shoulders. No shadow or outline.
    private const float SpearUnderAlpha = 0.55f;
    private static readonly Color SpearUnderTint = new(0.45f, 0.68f, 0.76f);
    private static Mesh spearFrontMesh, spearBackMesh;
    private static readonly Dictionary<Material, Material> spearUnderSea = new(), spearUnderFreshwater = new();

    // Ticket 35 diagnostics: side-spear draws since the game started, and, for the developer tests only, each one's pawn,
    // butt and tip as drawn. Null in play.
    public static int SwimSpearsDrawn { get; private set; }
    public static System.Action<Pawn, Vector3, Vector3> SwimSpearDrawnHook;

    // Called from the game's carried-weapon draw, on the main thread. True when the spear was drawn here and the game's
    // carry pose must be skipped: a registered swimmer (which also means the visuals are on) at the surface, swimming as Waves
    // answers it. Without the bridge's swimming question, wading, ashore and under the water the game draws as before.
    internal static bool TryDrawSwimSpear(Pawn pawn, ThingWithComps weapon, Vector3 drawPos)
    {
        Diver diver = DiverOf(pawn);
        if (diver == null || diver.Driver.Submerged || !WavesBridge.KnowsSwimming || !WavesBridge.IsSwimming(pawn)) return false;
        EnsureMaterials();
        Graphic graphic = weapon.Graphic;
        Material material = graphic.MatSingleFor(weapon);
        Quaternion turn = Quaternion.AngleAxis(diver.Heading, Vector3.up);
        Vector3 centre = drawPos + turn * new Vector3(SpearSideOffset, 0f, SpearForwardOffset);
        Quaternion spin = Quaternion.AngleAxis(diver.Heading - 90f, Vector3.up);
        var scale = new Vector3(graphic.drawSize.x, 1f, graphic.drawSize.y);
        Matrix4x4 front = Matrix4x4.TRS(centre, spin, scale);
        Graphics.DrawMesh(spearFrontMesh, front, material, 0);
        var under = new Vector3(centre.x, AltitudeLayer.TerrainScatter.AltitudeFor(), centre.z);
        Graphics.DrawMesh(spearBackMesh, Matrix4x4.TRS(under, spin, scale), UnderwaterSpear(material, diver.Freshwater), 0);
        SwimSpearsDrawn++;
        // The butt and tip as drawn: the ends of the texture's length through the draw matrix.
        SwimSpearDrawnHook?.Invoke(pawn, front.MultiplyPoint3x4(new Vector3(-0.5f, 0f, 0f)), front.MultiplyPoint3x4(new Vector3(0.5f, 0f, 0f)));
        return true;
    }

    private static Material UnderwaterSpear(Material spear, bool freshwater)
    {
        var cache = freshwater ? spearUnderFreshwater : spearUnderSea;
        if (cache.TryGetValue(spear, out Material under)) return under;
        int? queue = freshwater ? WavesBridge.FreshwaterArtRenderQueue ?? WavesBridge.SeaArtRenderQueue : WavesBridge.SeaArtRenderQueue;
        Color c = spear.color * SpearUnderTint;
        under = Tinted((Texture2D)spear.mainTexture, c, SpearUnderAlpha, queue);
        cache[spear] = under;
        return under;
    }

    // Half of a 1-cell plane split across its length: the front half (x 0 to 0.5) shows the right half of the texture, the
    // back half the left, so the two together draw the whole texture where plane10 would.
    private static Mesh HalfPlane(bool front)
    {
        float x0 = front ? 0f : -0.5f, x1 = x0 + 0.5f, u0 = x0 + 0.5f, u1 = u0 + 0.5f;
        var mesh = new Mesh
        {
            name = front ? "SpearfishingSpearFront" : "SpearfishingSpearBack", // not translated
            vertices = new[] { new Vector3(x0, 0f, -0.5f), new Vector3(x0, 0f, 0.5f), new Vector3(x1, 0f, 0.5f), new Vector3(x1, 0f, -0.5f) },
            uv = new[] { new Vector2(u0, 0f), new Vector2(u0, 1f), new Vector2(u1, 1f), new Vector2(u1, 0f) },
        };
        mesh.SetTriangles(new[] { 0, 1, 2, 0, 2, 3 }, 0);
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
        return mesh;
    }

    internal static void Register(JobDriver_SeaTrip driver)
    {
        // Only the previous game's entries go here: during a load, divers built earlier are not spawned yet. The frame hook
        // prunes the rest.
        divers.RemoveAll(d => d.Game != Current.Game);
        for (int i = 0; i < divers.Count; i++)
            if (divers[i].Driver == driver) return;
        divers.Add(new Diver { Driver = driver, Pawn = driver.pawn, Game = Current.Game, Shoals = new FishShoals(driver.pawn) });
    }

    // The dive shadow's size for a pawn this frame, as a share of its size just under the surface, or 0 when they are not
    // under the water or the visuals are off. Pure: the draw and the developer tests both read it.
    public static float DiveShadowScaleOf(Pawn pawn)
    {
        Diver diver = DiverOf(pawn);
        if (diver == null) return 0f;
        float t = diver.Driver.SubmergedFraction;
        if (t < 0f) return 0f;
        return Mathf.Lerp(DiveShadowSurfaceSize, BottomSize(diver), Depth(t)) / DiveShadowSurfaceSize;
    }

    // Ticket 22 diagnostics: the size the shadow would hold at the bottom of the dive over the water the diver is in now
    // (eased), and the heading the shadow is turned to, in degrees clockwise from north. NaN with no diver or with the
    // visuals off. Read only.
    public static float DiveShadowBottomSizeOf(Pawn pawn) => DiverOf(pawn) is { } diver ? BottomSize(diver) : float.NaN;

    public static float DiveShadowHeadingOf(Pawn pawn) => DiverOf(pawn) is { } diver ? diver.Heading : float.NaN;

    // Ticket 33: the angle the face-down look is turned to, in degrees clockwise from north: the diver's eased heading, the
    // way it travels. 0 with no diver. Read only, so safe from the draw threads.
    public static float FaceDownHeadingOf(Pawn pawn) => DiverOf(pawn) is { } diver ? diver.Heading : 0f;

    // Ticket 26 diagnostic: the shadow's blur level over the water the diver is in now (eased), from 0 (crisp) through 1
    // (medium) to 2 (soft). NaN with no diver or with the visuals off. Read only.
    public static float DiveShadowBlurOf(Pawn pawn) => DiverOf(pawn) is { } diver ? BlurLevel(diver) : float.NaN;

    private static float BlurLevel(Diver diver) => diver.WaterDepth * (DiveShadowBlurLevels.Length - 1);

    private static float BottomSize(Diver diver) => Mathf.Lerp(ShallowBottomSize, DeepBottomSize, diver.WaterDepth);

    private static float BottomAlpha(Diver diver) => Mathf.Lerp(ShallowBottomAlpha, DeepBottomAlpha, diver.WaterDepth);

    private static Diver DiverOf(Pawn pawn) =>
        divers.Count == 0 || pawn?.jobs?.curDriver is not JobDriver_SeaTrip driver ? null : DiverFor(driver);

    // 0 just under the surface, 1 at the bottom: down over the first share of the dive, held, back up over the last.
    private static float Depth(float t) =>
        t < DescentShare ? t / DescentShare : t > 1f - AscentShare ? (1f - t) / AscentShare : 1f;

    internal static void Notify_WentUnder(JobDriver_SeaTrip driver)
    {
        Diver diver = DiverFor(driver);
        if (diver == null) return;
        diver.UnderAt = clock;
        diver.UpAt = -1f;
        GoingUnderEffects++;
        DiveSounds.Notify_WentUnder(driver.pawn);
    }

    internal static void Notify_CameUp(JobDriver_SeaTrip driver)
    {
        Diver diver = DiverFor(driver);
        if (diver == null) return;
        diver.UpAt = clock;
        diver.UnderAt = -1f;
        ComingUpEffects++;
        DiveSounds.Notify_CameUp(driver.pawn);
    }

    private static Diver DiverFor(JobDriver_SeaTrip driver)
    {
        if (divers.Count == 0 || !On) return null;
        for (int i = 0; i < divers.Count; i++)
            if (divers[i].Driver == driver) return divers[i];
        return null;
    }

    // ---- Shark shadow (gear tiers ticket 11, art/shark/APPROVAL.md) -----------------------------------------------------
    // Our own top-down shark, 256 px a side, at its depth blur levels like the dive shadow. It is drawn SharkLength cells
    // over deep ocean (a body of about 2.2 cells, a 2 to 3 m shark beside the diver), scaled from there by the dive shadow's
    // bottom size. Its alpha is 0.70 in deep water and up to 0.85 as it rises for the bite, well above the deep fish's 0.28
    // and the diver's 0.22, so it reads as one large dark shape among the fish (the first look, about 1 cell at 0.30, was
    // lost in a shoal). Its tail beats with the fish's bent mesh at a stiffer sway. It circles, turns in and strikes at
    // DiveRules.SharkStrikeTicks, then swings away and sinks. Timed by game ticks from its arrival, like the dive shadow, so
    // the strike lands with the bite at any speed; nothing in it uses a gameplay random draw.
    private const string SharkTexPath = "Spearfishing/Dive/SharkShadow_";
    private const float SharkLength = 2.35f, SharkSway = 0.06f, SharkSwayHz = 1.2f;
    // SharkShallowAlpha is also the top of the material ladder, so it must stay the larger.
    private const float SharkShallowAlpha = 0.85f, SharkDeepAlpha = 0.70f;
    private const int SharkSteps = 16, SharkSwayFrames = 8;
    // Seconds at 1x: circling, the lunge (the bite comes SharkStrikeTicks after arrival), and the swing away.
    private const float SharkPassSeconds = 2.4f, SharkStrikeSeconds = 0.7f, SharkLeaveSeconds = 1.8f;
    private const float SharkPassDegrees = 150f, SharkFadeInSeconds = 1.6f;
    private static Material[][] sharkMaterials;
    private static Mesh[] sharkMeshes;

    // Diagnostics since the game started: shark encounters shown, shark shadow draws, and bite ripple draws.
    public static int SharkEncountersShown { get; private set; }
    public static int SharkShadowsDrawn { get; private set; }
    public static int SharkBiteRipplesDrawn { get; private set; }

    // Whether a shark shadow is playing round this pawn. Read only.
    public static bool SharkShowing(Pawn pawn) => DiverOf(pawn) is { SharkFrom: >= 0 };

    internal static void Notify_Shark(JobDriver_DiveTrip driver, bool bites)
    {
        Diver diver = DiverFor(driver);
        if (diver == null) return;
        int now = Find.TickManager.TicksGame;
        diver.SharkFrom = now;
        diver.SharkCalledOff = -1;
        diver.SharkBites = bites;
        // Cosmetic only: placed from the pawn and the tick, never from the game's random stream.
        int hash = Gen.HashCombineInt(driver.pawn.thingIDNumber, now);
        diver.SharkAngle = (hash & 0x7fffffff) % 360;
        diver.SharkTurn = (hash & 0x100) == 0 ? 1f : -1f;
        SharkEncountersShown++;
    }

    internal static void Notify_SharkCalledOff(JobDriver_DiveTrip driver)
    {
        Diver diver = DiverFor(driver);
        if (diver == null || diver.SharkFrom < 0) return;
        diver.SharkCalledOff = Find.TickManager.TicksGame;
    }

    private struct SharkPose
    {
        public float X, Z, Heading, Size, Alpha, Lift;
    }

    // Where the shark is s seconds after it came, relative to the diver's centre: x east, z north, heading in degrees
    // counter-clockwise from east as the fish turn, its size and alpha as shares of its depth's, and how far it has risen
    // toward the diver (0 to 1). False once it has gone.
    private static bool SharkAt(Diver diver, float s, out SharkPose pose)
    {
        float leaveFrom = SharkPassSeconds + SharkStrikeSeconds;
        if (diver.SharkCalledOff >= 0) leaveFrom = Mathf.Min(leaveFrom, (diver.SharkCalledOff - diver.SharkFrom) / 60f);
        if (s < leaveFrom)
        {
            pose = SharkBefore(diver, s);
            return true;
        }
        float k = (s - leaveFrom) / SharkLeaveSeconds;
        pose = SharkBefore(diver, leaveFrom);
        if (k >= 1f) return false;
        // Swings further round and away, sinking: smaller and fading out at its depth.
        float h = (pose.Heading + diver.SharkTurn * 20f * k) * Mathf.Deg2Rad;
        pose.X += Mathf.Cos(h) * 2.1f * k;
        pose.Z += Mathf.Sin(h) * 2.1f * k;
        pose.Heading += diver.SharkTurn * 40f * k;
        pose.Size = Mathf.Lerp(1f, 0.8f, k);
        pose.Alpha = 1f - 0.88f * k;
        pose.Lift = 0f;
        return true;
    }

    // Circling, then the lunge.
    private static SharkPose SharkBefore(Diver diver, float s)
    {
        var pose = new SharkPose { Size = 1f, Alpha = 1f };
        float pass = Mathf.Min(s, SharkPassSeconds) / SharkPassSeconds;
        float a = (diver.SharkAngle + diver.SharkTurn * SharkPassDegrees * pass) * Mathf.Deg2Rad, r = 1.35f - 0.15f * pass;
        pose.X = r * Mathf.Cos(a);
        pose.Z = r * Mathf.Sin(a);
        pose.Heading = a * Mathf.Rad2Deg + diver.SharkTurn * 90f;
        pose.Alpha = Mathf.Lerp(0.35f, 1f, Mathf.Clamp01(s / SharkFadeInSeconds));
        if (s <= SharkPassSeconds) return pose;
        // Turns in at the diver: a bite goes through them, a shark that is driven off veers past.
        float k = Mathf.Clamp01((s - SharkPassSeconds) / SharkStrikeSeconds);
        float inX = -pose.X / r, inZ = -pose.Z / r;
        float endX = diver.SharkBites ? inX * 0.4f : -inZ * diver.SharkTurn * 0.9f;
        float endZ = diver.SharkBites ? inZ * 0.4f : inX * diver.SharkTurn * 0.9f;
        float lunge = Mathf.Atan2(endZ - pose.Z, endX - pose.X) * Mathf.Rad2Deg;
        pose.Heading = Mathf.LerpAngle(pose.Heading, lunge, Mathf.Clamp01(k / 0.3f));
        pose.X = Mathf.Lerp(pose.X, endX, k);
        pose.Z = Mathf.Lerp(pose.Z, endZ, k);
        // It comes up to the diver for the bite: larger, darker and sharper, easing back after.
        float bite = (DiveRules.SharkStrikeTicks / 60f - SharkPassSeconds) / SharkStrikeSeconds;
        float lift = k < bite ? k / bite : 1f - 0.33f * (k - bite) / (1f - bite);
        pose.Lift = diver.SharkBites ? lift : lift * 0.5f;
        pose.Size = 1f + 0.12f * pose.Lift;
        return pose;
    }

    private static void DrawShark(Diver diver, Vector3 centre)
    {
        if (diver.SharkFrom < 0) return;
        float s = (Find.TickManager.TicksGame - diver.SharkFrom) / 60f;
        if (!SharkAt(diver, s, out SharkPose pose))
        {
            diver.SharkFrom = -1;
            return;
        }
        float depth = Mathf.Clamp01(diver.WaterDepth - 0.5f * pose.Lift);
        float alpha = Mathf.Lerp(SharkShallowAlpha, SharkDeepAlpha, depth) * pose.Alpha;
        float level = depth * (DiveShadowBlurLevels.Length - 1);
        int lower = Mathf.Min((int)level, DiveShadowBlurLevels.Length - 2);
        float soft = level - lower;
        float a1 = alpha * (1f - soft), a2 = (alpha - a1) / (1f - a1);
        Material m1 = Step(sharkMaterials[lower], a1 / SharkShallowAlpha), m2 = Step(sharkMaterials[lower + 1], a2 / SharkShallowAlpha);
        if (m1 != null || m2 != null)
        {
            float size = SharkLength * BottomSize(diver) / DeepBottomSize * pose.Size;
            int frame = (int)(Mathf.Repeat(s * SharkSwayHz, 1f) * SharkSwayFrames) % SharkSwayFrames;
            var at = new Vector3(centre.x + pose.X, AltitudeLayer.TerrainScatter.AltitudeFor(), centre.z + pose.Z);
            var matrix = Matrix4x4.TRS(at, Quaternion.AngleAxis(-pose.Heading, Vector3.up), new Vector3(size, 1f, size));
            if (m1 != null) Graphics.DrawMesh(sharkMeshes[frame], matrix, m1, 0);
            if (m2 != null) Graphics.DrawMesh(sharkMeshes[frame], matrix, m2, 0);
            SharkShadowsDrawn++;
        }
        // The bite: the approved ripple at the diver.
        float sinceBite = s - DiveRules.SharkStrikeTicks / 60f;
        if (diver.SharkBites && diver.SharkCalledOff < 0 && sinceBite >= 0f && sinceBite < RippleSeconds)
        {
            DrawRipple(centre, AltitudeLayer.Item.AltitudeFor(), sinceBite / RippleSeconds);
            SharkBiteRipplesDrawn++;
        }
    }

    internal static void Notify_Speared(JobDriver_DiveTrip driver)
    {
        if (!On) return;
        for (int i = 0; i < divers.Count; i++)
        {
            var diver = divers[i];
            if (diver.Driver != driver) continue;
            Vector3 centre = diver.Pawn.DrawPos;
            // The nearest fish of the nearest shoal is taken and the rest scatter (the user dropped the fish darting in to
            // the spear: it read as the fish flying at the pawn).
            diver.Shoals.Spear(centre);
            diver.SpearedAt3 = centre;
            diver.SpearedAt = clock;
            SpearEffects++;
            return;
        }
    }

    // Developer tests only (ticket 34): called at the end of every map's frame hook, whether or not anything was drawn, so
    // a test can count the frames a shadow or fish should have been drawn against the frames they were. Null in play.
    public static System.Action<Map> FrameHook;

    // Ticket 34 diagnostics, read only: whether the dive shadow, and at least one shoal fish, was drawn for this pawn in the
    // current frame.
    public static bool DiveShadowDrawnThisFrame(Pawn pawn) => DiverOf(pawn) is { } diver && diver.ShadowFrame == Time.frameCount;
    public static bool FishDrawnThisFrame(Pawn pawn) => DiverOf(pawn) is { } diver && diver.FishFrame == Time.frameCount;

    // Developer diagnostics (ticket 34), read only: this swimmer's shoal states, and the render queues of the dive shadow and
    // of the fish (-1 before anything was drawn).
    public static string ShoalDiagnosis(Pawn pawn) => DiverOf(pawn)?.Shoals.Diagnose() ?? "no diver"; // not translated
    public static int DiveShadowRenderQueue(bool freshwater) => (freshwater ? freshwaterDiveShadowMaterials : diveShadowMaterials)?[0][0].renderQueue ?? -1;
    public static int FishRenderQueue(bool freshwater) => FishShoals.RenderQueue(freshwater);

    // Called once per map per frame (Map.MapUpdate postfix).
    internal static void MapUpdate(Map map)
    {
        if (divers.Count > 0) DrawFrame(map);
        FrameHook?.Invoke(map);
    }

    private static void DrawFrame(Map map)
    {
        Prune();
        if (divers.Count == 0 || !On || !WorldRendererUtility.DrawingMap || Find.CurrentMap != map) return;

        if (lastFrame != Time.frameCount)
        {
            lastFrame = Time.frameCount;
            // Real time, as Waves' sea life moves, frozen while the game is paused. Ticks run by hand while paused
            // (developer tools) count as running.
            int tick = Find.TickManager.TicksGame;
            bool running = !Find.TickManager.Paused || tick != lastTick;
            lastTick = tick;
            frameDelta = running ? Mathf.Min(Time.unscaledDeltaTime, 0.1f) : 0f;
            clock += frameDelta;
        }
        FramesWorked++;
        EnsureMaterials();
        CellRect view = Find.CameraDriver.CurrentViewRect.ExpandedBy(3);
        bool drawFish = Find.CameraDriver.ZoomRootSize <= FishHideZoom;
        float shoalDelta = frameDelta * Mathf.Clamp(Find.TickManager.TickRateMultiplier, 1f, MaxShoalSpeedUp);
        float fishY = AltitudeLayer.TerrainScatter.AltitudeFor();
        int drawn = 0, skipped = 0;
        for (int i = 0; i < divers.Count; i++)
        {
            var diver = divers[i];
            if (diver.Pawn.Map != map) continue;
            Update(diver);
            Vector3 centre = diver.Pawn.DrawPos;
            // Shoals move for every swimmer on the map, in view or not, so a spearfisher off screen still stalks them.
            var zone = map.zoneManager.ZoneAt(centre.ToIntVec3()) as Zone_Spearfishing;
            diver.Shoals.Update(map, centre, diver.Heading, shoalDelta, diver.Driver is JobDriver_DiveTrip, zone);
            if (drawFish)
            {
                int before = drawn;
                diver.Shoals.Draw(view, fishY, ref drawn, ref skipped);
                if (drawn > before) diver.FishFrame = Time.frameCount;
            }
            if (!view.Contains(centre.ToIntVec3())) continue;
            Draw(diver);
            DrawAtHead(diver, centre);
            DrawShark(diver, centre);
        }
        ShadowsDrawn += drawn;
        ShadowsOffWaterSkipped += skipped;
    }

    // Look C, the dive shadow and the going-under and coming-up animations, all placed from where the game draws a
    // swimmer's head.
    private static void DrawAtHead(Diver diver, Vector3 centre)
    {
        Pawn pawn = diver.Pawn;
        Look look = LookOf(pawn);
        // Face down, the drawn head is turned to the heading about the pawn's centre (FaceDownHeadingOf), so the planes
        // placed from it turn with it.
        Vector3 headOffset = pawn.Drawer.renderer.BaseHeadOffsetAt(Rot4.North) - new Vector3(0f, 0f, SwimHeadSink);
        if (look == Look.FaceDown) headOffset = Quaternion.AngleAxis(diver.Heading, Vector3.up) * headOffset;
        Vector3 head = centre + headOffset;
        float under = AltitudeLayer.TerrainScatter.AltitudeFor(), over = AltitudeLayer.Item.AltitudeFor();
        float upT = diver.UpAt >= 0f ? clock - diver.UpAt : -1f, underT = diver.UnderAt >= 0f ? clock - diver.UnderAt : -1f;

        if (look == Look.FaceDown)
        {
            // The shoulders and waterline sit behind the head along the heading and turn with it (the third review).
            Quaternion turn = Quaternion.AngleAxis(diver.Heading, Vector3.up);
            Vector3 shoulders = head + turn * new Vector3(0f, 0f, -ShouldersOffset), waterline = head + turn * new Vector3(0f, 0f, -WaterlineOffset);
            DrawPlane(new Vector3(shoulders.x, under, shoulders.z), turn, ShouldersSize, diver.Freshwater ? freshwaterShouldersMaterial : shouldersMaterial);
            DrawPlane(new Vector3(waterline.x, over, waterline.z), turn, WaterlineSize, waterlineMaterial);
            FaceDownShapesDrawn++;
        }

        float t = diver.Driver.SubmergedFraction;
        if (t >= 0f)
        {
            float k = Depth(t);
            float size = Mathf.Lerp(DiveShadowSurfaceSize, BottomSize(diver), k);
            float alpha = Mathf.Lerp(DiveShadowSurfaceAlpha, BottomAlpha(diver), k) / DiveShadowSurfaceAlpha;
            // Crossfade the two blur levels either side of the water's depth. Two blended layers do not add up: the sharper
            // one takes its share of the alpha and the softer one tops the core up to the full alpha, so the middle of the
            // shadow is as dark as either level alone and only the edge blends.
            float level = BlurLevel(diver);
            int lower = Mathf.Min((int)level, DiveShadowBlurLevels.Length - 2);
            float soft = level - lower;
            float a = alpha * DiveShadowSurfaceAlpha, a1 = a * (1f - soft), a2 = (a - a1) / (1f - a1);
            Material[][] shadowSet = diver.Freshwater ? freshwaterDiveShadowMaterials : diveShadowMaterials;
            Material m1 = Step(shadowSet[lower], a1 / DiveShadowSurfaceAlpha);
            Material m2 = Step(shadowSet[lower + 1], a2 / DiveShadowSurfaceAlpha);
            if (m1 != null || m2 != null)
            {
                // The head leads, so the shadow's centre trails it, opposite the way of travel.
                float h = diver.Heading * Mathf.Deg2Rad;
                var at = new Vector3(head.x - DiveShadowOffset * Mathf.Sin(h), under, head.z - DiveShadowOffset * Mathf.Cos(h));
                var turn = Quaternion.AngleAxis(diver.Heading, Vector3.up);
                if (m1 != null) DrawPlane(at, turn, size, m1);
                if (m2 != null) DrawPlane(at, turn, size, m2);
                DiveShadowsDrawn++;
                diver.ShadowFrame = Time.frameCount;
            }
        }

        // The same ripple as the head goes under and as it comes up.
        if (underT >= 0f && underT < RippleSeconds) DrawRipple(head, over, underT / RippleSeconds);
        if (upT >= 0f && upT < RippleSeconds) DrawRipple(head, over, upT / RippleSeconds);

        if (look == Look.Hidden && clock >= diver.BubblesFrom)
        {
            float cycle = (clock - diver.BubblesFrom) % BubblePeriod;
            for (int i = 0; i < BubbleSpots.Length; i++)
                DrawBubble(head, over, cycle - BubbleStagger * i, BubbleSpots[i]);
        }
    }

    private static void DrawRipple(Vector3 head, float y, float k)
    {
        Material m = Step(rippleMaterials, 1f - k);
        if (m != null)
            DrawPlane(new Vector3(head.x, y, head.z - RippleOffset), Mathf.Lerp(RippleStartSize, RippleEndSize, EaseOut(k)), m);
    }

    // Seen from above: small and faint as it leaves the diver, larger and paler near the surface, then a tiny ring.
    private static void DrawBubble(Vector3 head, float y, float age, Vector2 spot)
    {
        if (age < 0f) return;
        float x = head.x + spot.x;
        if (age < BubbleRiseSeconds)
        {
            float k = age / BubbleRiseSeconds;
            Material m = Step(bubbleMaterials, 0.35f + 0.55f * k);
            if (m == null) return;
            DrawPlane(new Vector3(x, y, head.z - spot.y + BubbleRise * k), 0.08f + 0.12f * k, m);
            BubblesDrawn++;
            return;
        }
        float p = (age - BubbleRiseSeconds) / BubblePopSeconds;
        if (p >= 1f) return;
        Material pop = Step(rippleMaterials, PopAlpha * (1f - p) / RippleAlpha);
        if (pop == null) return;
        DrawPlane(new Vector3(x, y, head.z - spot.y + BubbleRise), 0.2f + 0.2f * p, pop);
        BubblesDrawn++;
    }

    private static float EaseOut(float k) => 1f - (1f - k) * (1f - k);

    private static void DrawPlane(Vector3 at, float size, Material material) => DrawPlane(at, Quaternion.identity, size, material);

    private static void DrawPlane(Vector3 at, Quaternion rotation, float size, Material material) =>
        Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(at, rotation, new Vector3(size, 1f, size)), material, 0);

    // A trip ends, is interrupted or is replaced without telling us, and a load leaves the old game's pawns looking spawned;
    // drop those entries here.
    private static void Prune()
    {
        for (int i = divers.Count - 1; i >= 0; i--)
        {
            var pawn = divers[i].Pawn;
            if (divers[i].Game != Current.Game || pawn == null || !pawn.Spawned || pawn.jobs?.curDriver != divers[i].Driver)
                divers.RemoveAt(i);
        }
    }

    private static void Update(Diver diver)
    {
        bool submerged = diver.Driver.Submerged;
        Pawn pawn = diver.Pawn;
        Vector3 pos = pawn.DrawPos;
        float cellDepth = MapComponent_FishStock.SwimDepthAt(pawn.Map, pos.ToIntVec3());
        // A new dive (or the first frame, or a load mid-dive) starts from the way the diver steps (or faces, standing) and the water under them;
        // the shadow is not drawn before the dive, so the snap is never seen.
        if (!diver.Started || (submerged && !diver.WasSubmerged))
        {
            diver.Started = true;
            diver.Heading = TravelAngle(pawn, out float travel) ? travel : pawn.Rotation.AsAngle;
            diver.Velocity = Vector3.zero;
            diver.LastPos = pos;
            if (cellDepth >= 0f) diver.WaterDepth = cellDepth;
        }
        // A new dive, or a load mid-dive, starts the bubbles: the first cluster leaves as the going-under ripple ends.
        if (submerged && !diver.WasSubmerged) diver.BubblesFrom = clock + RippleSeconds;
        // Off fishing water (a shore cell on the way out) the last depth, and the last kind of water, hold.
        if (cellDepth >= 0f)
        {
            diver.WaterDepth = Mathf.MoveTowards(diver.WaterDepth, cellDepth, frameDelta / DepthEaseSeconds);
            diver.Freshwater = !WavesBridge.IsSea(pawn.Map.terrainGrid.TerrainAt(pos.ToIntVec3()));
        }
        UpdateHeading(diver, pos);
        diver.WasSubmerged = submerged;
        if (diver.UnderAt >= 0f && clock - diver.UnderAt >= RippleSeconds) diver.UnderAt = -1f;
        if (diver.UpAt >= 0f && clock - diver.UpAt >= RippleSeconds) diver.UpAt = -1f;
        if (diver.SpearedAt >= 0f && clock - diver.SpearedAt >= BurstSeconds) diver.SpearedAt = -1f;
    }

    // The heading eases toward the smoothed direction of travel; standing still, or paused, it holds. A jump of more than a
    // cell (a teleport, a load) moves nothing.
    private static void UpdateHeading(Diver diver, Vector3 pos)
    {
        Vector3 step = pos - diver.LastPos;
        diver.LastPos = pos;
        if (frameDelta <= 0f) return;
        step.y = 0f;
        if (step.sqrMagnitude > 1f) return;
        float blend = 1f - Mathf.Exp(-frameDelta / VelocitySmoothSeconds);
        diver.Velocity = Vector3.Lerp(diver.Velocity, step / frameDelta, blend);
        if (diver.Velocity.magnitude < MinTravelSpeed) return;
        float target = Mathf.Atan2(diver.Velocity.x, diver.Velocity.z) * Mathf.Rad2Deg;
        diver.Heading = Mathf.Repeat(Mathf.MoveTowardsAngle(diver.Heading, target, TurnSpeed * frameDelta), 360f);
    }

    // The burst on a catch.
    private static void Draw(Diver diver)
    {
        if (diver.SpearedAt < 0f) return;
        float burstT = clock - diver.SpearedAt;
        if (burstT < BurstSeconds)
        {
            float k = burstT / BurstSeconds;
            Material burst = Step(burstMaterials, 1f - k);
            if (burst != null)
            {
                float size = Mathf.Lerp(BurstMinSize, BurstMaxSize, k);
                var at = new Vector3(diver.SpearedAt3.x, AltitudeLayer.MoteLow.AltitudeFor(), diver.SpearedAt3.z);
                Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(at, Quaternion.identity, new Vector3(size, 1f, size)), burst, 0);
            }
        }
    }

    // Graphics.DrawMesh draws with the material as it is at render time, so fades use a few prebuilt alpha steps.
    private static Material Step(Material[] steps, float fraction)
    {
        int index = Mathf.CeilToInt(Mathf.Clamp01(fraction) * steps.Length) - 1;
        return index < 0 ? null : steps[index];
    }

    private static void EnsureMaterials()
    {
        if (burstMaterials != null) return;
        // At sea the art goes over Waves' opaque water body and its shore veil, under its rollers and foam (ticket 34: the
        // veil's bands hid it). Under a lake or river it goes just over Living Waters' veil when that mod is loaded (its
        // drifting patches hid it too), else as at sea.
        int? underwater = WavesBridge.SeaArtRenderQueue, freshwater = WavesBridge.FreshwaterArtRenderQueue ?? underwater;
        FishShoals.EnsureMaterials(underwater, freshwater);
        var burstTex = ContentFinder<Texture2D>.Get(BurstTexPath);
        burstMaterials = new Material[FadeSteps];
        for (int i = 0; i < FadeSteps; i++)
        {
            float k = (i + 1f) / FadeSteps;
            burstMaterials[i] = new Material(ShaderDatabase.Transparent)
            {
                mainTexture = burstTex,
                color = new Color(BurstColor.r, BurstColor.g, BurstColor.b, k),
            };
        }

        var waterlineTex = ContentFinder<Texture2D>.Get(WaterlineTexPath);
        var shouldersTex = ContentFinder<Texture2D>.Get(ShouldersTexPath);
        shouldersMaterial = Tinted(shouldersTex, ShadowColor, ShouldersAlpha, underwater);
        freshwaterShouldersMaterial = freshwater != underwater ? Tinted(shouldersTex, ShadowColor, ShouldersAlpha, freshwater) : shouldersMaterial;
        waterlineMaterial = Tinted(waterlineTex, WaterlineColor, WaterlineAlpha, null);
        spearFrontMesh = HalfPlane(front: true);
        spearBackMesh = HalfPlane(front: false);
        diveShadowMaterials = DiveShadowMaterials(underwater);
        freshwaterDiveShadowMaterials = freshwater != underwater ? DiveShadowMaterials(freshwater) : diveShadowMaterials;
        // Sharks are only ever in the sea.
        sharkMaterials = new Material[DiveShadowBlurLevels.Length][];
        for (int level = 0; level < DiveShadowBlurLevels.Length; level++)
        {
            var sharkTex = ContentFinder<Texture2D>.Get(SharkTexPath + DiveShadowBlurLevels[level]);
            sharkMaterials[level] = new Material[SharkSteps];
            for (int i = 0; i < SharkSteps; i++)
                sharkMaterials[level][i] = Tinted(sharkTex, ShadowColor, SharkShallowAlpha * (i + 1f) / SharkSteps, underwater);
        }
        sharkMeshes = new Mesh[SharkSwayFrames];
        for (int k = 0; k < SharkSwayFrames; k++) sharkMeshes[k] = FishShoals.BentPlane(k * Mathf.PI * 2f / SharkSwayFrames, SharkSway);
        var rippleTex = ContentFinder<Texture2D>.Get(RippleTexPath);
        var bubbleTex = ContentFinder<Texture2D>.Get(BubbleTexPath);
        rippleMaterials = new Material[FadeSteps];
        bubbleMaterials = new Material[FadeSteps];
        for (int i = 0; i < FadeSteps; i++)
        {
            float k = (i + 1f) / FadeSteps;
            rippleMaterials[i] = Tinted(rippleTex, WaterlineColor, RippleAlpha * k, null);
            bubbleMaterials[i] = Tinted(bubbleTex, WaterlineColor, k, null);
        }
    }

    // Per blur level, its alpha steps.
    private static Material[][] DiveShadowMaterials(int? renderQueue)
    {
        var set = new Material[DiveShadowBlurLevels.Length][];
        for (int level = 0; level < DiveShadowBlurLevels.Length; level++)
        {
            var diveShadowTex = ContentFinder<Texture2D>.Get(DiveShadowTexPath + DiveShadowBlurLevels[level]);
            var steps = set[level] = new Material[DiveShadowSteps];
            for (int i = 0; i < DiveShadowSteps; i++)
                steps[i] = Tinted(diveShadowTex, ShadowColor, DiveShadowSurfaceAlpha * (i + 1f) / DiveShadowSteps, renderQueue);
        }
        return set;
    }

    private static Material Tinted(Texture2D tex, Color tint, float alpha, int? renderQueue)
    {
        var material = new Material(ShaderDatabase.Transparent) { mainTexture = tex, color = new Color(tint.r, tint.g, tint.b, alpha) };
        if (renderQueue is { } queue) material.renderQueue = queue;
        return material;
    }
}
