using RimWorld;
using UnityEngine;
using Verse;

namespace Spearfishing;

// The fish shoals around one swimmer (ticket 23), owned by DiveVisuals' entry for that trip. Up to three shoals live on
// swimmable fishing water near the pawn while the pawn is in that water, with fewer and smaller shoals where the local
// stock is fished out. Each shoal is a leader that wanders slowly and turns gently, looking ahead so it never swims onto
// land. Each follower swims on its own (ticket 32): it keeps its own position and velocity and steers toward its slot, a
// fixed offset behind the leader with a small sine wobble, at a speed capped a little above the leader's and a limited
// turn rate, facing the way it travels. So a turning shoal bends instead of sweeping round its leader like a rigid plate.
// A spearfisher who comes within about 2 cells scatters a shoal: each fish darts off on its own line away from them, then
// the shoal regroups a few cells off. A snorkeler gets circled.
//
// Cosmetic only (ADR 0002): moves on the frame clock with a System.Random seeded from the pawn, never Verse.Rand, and
// nothing here is saved. The spearfisher's waypoints read the shoal positions (DiveVisuals.TryStalkTarget), but nothing
// rolled or saved depends on them.
//
// Each outline ships at three edge blur levels (ticket 27, art/fish-shapes/APPROVAL.md): a fish's edge crossfades from
// crisp over the shallowest water to soft over the deepest, like the dive shadow's (ticket 26).
internal sealed class FishShoals
{
    internal enum Shape
    {
        Generic,
        Slim,
        Stocky,
        Large,
        Long,
    }

    internal const int MaxShoals = 3, MaxFish = 8;
    // Room for a full set of shoals plus as many again fading out, so a replacement can fade in while one fades out
    // (ticket 34: the swimmer is never left without fish while it is in the water).
    private const int Slots = MaxShoals * 2;

    // Our own art (art/fish-shapes): white shapes facing east, tinted, scaled, faded and bent here. Indexed by Shape, each
    // with a blur level suffix from BlurLevels.
    private static readonly string[] TexPaths =
    {
        "Spearfishing/Dive/FishShadow_", "Spearfishing/Dive/FishSlim_", "Spearfishing/Dive/FishStocky_",
        "Spearfishing/Dive/FishLarge_", "Spearfishing/Dive/FishLong_",
    };
    // Sharpest first. The medium level is the look the shapes were approved in.
    private static readonly string[] BlurLevels = { "Crisp", "Medium", "Soft" };
    // Drawn length in cells over the shallowest water, and the fish in a full shoal: the values the contact sheets show.
    private static readonly float[] Sizes = { 0.6f, 0.55f, 0.6f, 0.85f, 1f };
    private static readonly int[] FullCounts = { 6, 8, 5, 3, 2 };
    // Follower offsets (forward, side) from the leader in cells, leader first, as the sheets lay them out. Large and long
    // fish spread them wider.
    private static readonly Vector2[] Offsets =
    {
        new(0f, 0f), new(-0.7f, 0.45f), new(-0.7f, -0.45f), new(-1.35f, 0f), new(-1.35f, 0.85f), new(-1.35f, -0.85f),
        new(-2f, 0.4f), new(-2f, -0.4f),
    };
    private const float WideSpread = 1.3f;

    // Over the shallowest water a fish draws at full size and half alpha, over the deepest smaller and fainter.
    private const float ShallowAlpha = 0.5f, DeepAlpha = 0.28f, DeepSize = 0.72f;
    private const int AlphaSteps = 16;
    // A fish's depth, and so its size, alpha and blur, eases over this long instead of jumping at a cell edge.
    private const float DepthEaseSeconds = 0.5f;
    // Tail sway: prebuilt bent meshes, the tail tip shifting sideways by up to this share of the fish's length.
    private const float Sway = 0.09f, SwayHz = 1.6f, FastSway = 2.5f;
    private const int SwayFrames = 8, SwaySegments = 8;

    // Spawning: a few cells ahead of or beside the pawn; a shoal more than LeaveDistance behind fades out.
    private const float SpawnMin = 3f, SpawnMax = 6f, SpawnSpread = 100f, LeaveDistance = 8f;
    private const float FadeSeconds = 1f, RespawnSeconds = 1f, RecheckSeconds = 2f;
    // Cruising: cells per second, the wander turn and how often it changes, and the pull back to a pawn out past it.
    private const float CruiseSpeed = 0.6f, WanderTurn = 60f, PullDistance = 5f;
    private const float TurnSpeed = 120f, FastTurnSpeed = 360f, LookAhead = 1.5f;
    // A spearfisher scatters a shoal, which then regroups and cruises on.
    private const float ScatterRange = 2.2f, ScatterSeconds = 1.5f, ScatterSpeed = 3f, ScatterSpread = 1.8f, RegroupSeconds = 1.5f;
    // A snorkeler is circled by shoals within CircleRange, each at its own radius.
    private const float CircleRange = 5f, CircleSpeed = 0.9f, CircleRadius = 1.6f, CircleRadiusStep = 0.8f;
    // A pawn that jumps this far between frames (a teleport, a load) resets the shoals.
    private const float JumpReset = 3f;
    // Followers: the speed cap over the leader's speed (enough to catch up after a turn), how hard a fish closes on its slot
    // (per second), its turn rate and acceleration, and how fast its facing eases onto its travel. A fish slower than
    // StillSpeed holds its facing. Each scatter line is jittered by up to FleeJitter degrees; a fish whose next step would
    // leave the water stops and heads for its leader for BlockedSeconds.
    private const float CapFactor = 1.3f, CapExtra = 0.3f, FollowGain = 1.5f, FollowTurnSpeed = 180f, FollowAccel = 8f;
    private const float FaceEaseSeconds = 0.05f, StillSpeed = 0.05f, FleeJitter = 25f, BlockedSeconds = 0.5f;
    // A fleeing fish past the tether bends its line back toward the leader, so a scatter fans the shoal without breaking it up.
    private const float ScatterTether = 3f, TetherGain = 3f;
    // Developer tests: a step faster than the cap by this share is over it, and a cruising leader this far off its target
    // heading is making a wander turn.
    private const float OverCapMargin = 0.1f, TurnSampleAngle = 15f;

    private static readonly Color Tint = new(0.03f, 0.08f, 0.10f);
    private static readonly float[] LookTurns = { 0f, 45f, -45f, 90f, -90f, 135f, -135f, 180f };

    private enum State
    {
        Cruise,
        Scatter,
        Regroup,
        Circle,
    }

    private sealed class Shoal
    {
        // Fresh: spawned this frame, so no step to measure yet. Freshwater: over a lake or river, drawn at that queue (ticket 34).
        public bool Live, Leaving, Fresh, Freshwater;
        public Shape Shape;
        public int Count, Gone;
        public float Fade;
        // The leader: position, heading in degrees counter-clockwise from east, the heading it turns to and its speed.
        public float X, Z, Heading, Target, Speed, WanderAt;
        public State State;
        // Its place among the swimmer's shoals when it spawned, which sets its circling radius.
        public int CircleIndex;
        public float StateEnds, Spread = 1f, SwayPhase, ScatterFrom, CircleDir, CircleAngle;
        public IntVec3 LookCell = IntVec3.Invalid;
        public bool LookWet;
        // Each fish: position; travel heading (counter-clockwise from east) and speed; the smoothed facing, and Yaw, the
        // facing with its sway; its scatter line; until when it heads for the leader after meeting the shore, and the last
        // dry cell it met so it does not test that cell again every frame. Fish 0 is the leader.
        public readonly Vector3[] Pos = new Vector3[MaxFish];
        public readonly float[] Dir = new float[MaxFish];
        public readonly float[] Spd = new float[MaxFish];
        public readonly float[] Face = new float[MaxFish];
        public readonly float[] Yaw = new float[MaxFish];
        public readonly float[] Flee = new float[MaxFish];
        public readonly float[] BlockedUntil = new float[MaxFish];
        public readonly IntVec3[] DryCell = new IntVec3[MaxFish];
        public readonly IntVec3[] Cell = new IntVec3[MaxFish];
        public readonly bool[] Wet = new bool[MaxFish];
        // Depth is the swim depth under the fish's cell; Eased follows it, below 0 until the fish is first over water.
        public readonly float[] Depth = new float[MaxFish];
        public readonly float[] Eased = new float[MaxFish];
    }

    // Read-only diagnostics for the developer tests, since the game started.
    internal static int ScatterEvents, RegroupEvents, ScatterMovedAway, LeaderShoreTurns;
    internal static float CircledDegrees;
    // Follower steps measured from the drawn positions, during a scatter and during a cruising wander turn: moving steps,
    // steps faster than the cap plus OverCapMargin, and the summed degrees between a fish's facing and its step.
    internal static int ScatterSteps, ScatterOverCap, TurnSteps, TurnOverCap;
    internal static float ScatterFaceError, TurnFaceError;

    // [shape][blur level][alpha step]
    private static Material[][][] materials, freshwaterMaterials;
    private static Mesh[] swayMeshes;

    private readonly System.Random rand;
    private readonly Shoal[] shoals = new Shoal[Slots];
    private float time, nextSpawnAt;
    private bool fishedOut;
    private int lastFrame = -100;
    private Vector3 lastPawn;
    private bool pawnInWater;

    // The farthest any fish sits from its leader this frame, in cells.
    internal float LargestSpread { get; private set; }

    // The frame these shoals last moved; a stale entry is not stalked.
    internal int UpdatedFrame => lastFrame;

    internal FishShoals(Pawn pawn)
    {
        // From the pawn, not Rand: cosmetic code must not move the gameplay random stream (ADR 0002).
        rand = new System.Random(pawn.thingIDNumber * 7919 + 17);
        for (int i = 0; i < Slots; i++) shoals[i] = new Shoal();
    }

    // Developer diagnostics (ticket 34), read only: the pawn's water test and each shoal's state.
    internal string Diagnose()
    {
        var sb = new System.Text.StringBuilder(pawnInWater ? "inWater" : "notInWater"); // not translated
        for (int i = 0; i < Slots; i++)
        {
            Shoal s = shoals[i];
            int wet = 0;
            for (int f = 0; f < s.Count; f++) if (s.Wet[f] && (s.Gone & (1 << f)) == 0) wet++;
            sb.Append(s.Live ? $" [{s.State} fade {s.Fade:0.00}{(s.Leaving ? " leaving" : "")} wet {wet}/{s.Count}]" : " [none]"); // not translated
        }
        sb.Append($" next spawn in {nextSpawnAt - time:0.0}s{(fishedOut ? ", fished out" : "")}"); // not translated
        return sb.ToString();
    }

    internal static int RenderQueue(bool freshwater) => (freshwater ? freshwaterMaterials : materials)?[0][0][0].renderQueue ?? -1;

    internal void Clear()
    {
        for (int i = 0; i < Slots; i++) shoals[i].Live = false;
        time = nextSpawnAt = 0f;
        fishedOut = false;
        LargestSpread = 0f;
    }

    // Live shoals not fading out and their fish (not counting speared ones), and the fewest and most fish in one shoal.
    internal void Stats(out int count, out int fish, out int minFish, out int maxFish)
    {
        count = fish = maxFish = 0;
        minFish = int.MaxValue;
        for (int i = 0; i < Slots; i++)
        {
            Shoal s = shoals[i];
            if (!s.Live || s.Leaving) continue;
            int n = s.Count - CountBits(s.Gone);
            count++;
            fish += n;
            minFish = Mathf.Min(minFish, n);
            maxFish = Mathf.Max(maxFish, n);
        }
        if (count == 0) minFish = 0;
    }

    // The nearest live shoal's leader that is not fading out; for stalking also not scattering. False with none.
    internal bool Nearest(Vector3 from, bool forStalk, out Vector3 at)
    {
        at = Vector3.zero;
        float best = float.MaxValue;
        for (int i = 0; i < Slots; i++)
        {
            Shoal s = shoals[i];
            if (!s.Live || s.Leaving || (forStalk && s.State == State.Scatter)) continue;
            float d = Sq(s.X - from.x, s.Z - from.z);
            if (d >= best) continue;
            best = d;
            at = new Vector3(s.X, from.y, s.Z);
        }
        return best < float.MaxValue;
    }

    // One frame: dt is the shoals' own time step (0 while paused), heading the pawn's way of travel in degrees clockwise
    // from north, spearfisher whether the pawn scatters shoals (else they circle it).
    internal void Update(Map map, Vector3 pawnPos, float heading, float dt, bool spearfisher, Zone_Spearfishing zone)
    {
        int frame = Time.frameCount;
        // Not drawn for a few frames (another map in view, the world map, the visuals off) or a jump: start afresh.
        if (frame - lastFrame > 2 || Sq(pawnPos.x - lastPawn.x, pawnPos.z - lastPawn.z) > JumpReset * JumpReset) Clear();
        lastFrame = frame;
        lastPawn = pawnPos;
        time += dt;
        pawnInWater = WavesBridge.IsSwimmableFishingWater(map, pawnPos.ToIntVec3());
        if (pawnInWater) Replenish(map, pawnPos, heading, zone);
        float spread = 0f;
        for (int i = 0; i < Slots; i++)
        {
            Shoal s = shoals[i];
            if (!s.Live) continue;
            float dx = s.X - pawnPos.x, dz = s.Z - pawnPos.z;
            float dist = Mathf.Sqrt(dx * dx + dz * dz);
            if (!pawnInWater || dist > LeaveDistance) s.Leaving = true;
            s.Fade = Mathf.MoveTowards(s.Fade, s.Leaving ? 0f : 1f, dt / FadeSeconds);
            if (s.Leaving && s.Fade <= 0f)
            {
                s.Live = false;
                continue;
            }
            Steer(s, map, pawnPos, dx, dz, dist, dt, spearfisher);
            spread = Mathf.Max(spread, MoveFish(s, map, dt));
        }
        LargestSpread = spread;
    }

    // Keeps the swimmer's shoals topped up while they are in the water: one at a time, a second apart, up to the number the
    // local stock allows. With none left that is not fading out (on entering the water, or after every shoal swam off or
    // was left behind), the next spawns at once, so a swimmer is never without fish (ticket 34) unless the water is fished
    // out. Spawning is the only place the stock is read; a fished-out patch is read again every RecheckSeconds.
    private void Replenish(Map map, Vector3 pawnPos, float heading, Zone_Spearfishing zone)
    {
        int active = 0, free = -1;
        for (int i = 0; i < Slots; i++)
        {
            if (!shoals[i].Live) { if (free < 0) free = i; }
            else if (!shoals[i].Leaving) active++;
        }
        if (free < 0 || active >= MaxShoals) return;
        if (time < nextSpawnAt && (active > 0 || fishedOut)) return;
        // The stock of the body of water at the pawn's cell decides how many shoals and how many fish: fished-out water
        // shows few or none. Off fishing water (a wading strip) the shoals read as full.
        IntVec3 at = pawnPos.ToIntVec3();
        MapComponent_FishStock fishStock = MapComponent_FishStock.Of(map);
        float stock = fishStock != null && fishStock.BodyAt(at) >= 0 ? fishStock.StockFractionAt(at) : 1f;
        int wanted = stock >= 0.66f ? 3 : stock >= 0.33f ? 2 : stock > 0.05f ? 1 : 0;
        fishedOut = wanted == 0;
        if (active >= wanted)
        {
            nextSpawnAt = time + RecheckSeconds;
            return;
        }
        nextSpawnAt = time + (TrySpawn(shoals[free], active, map, pawnPos, heading, stock) ? RespawnSeconds : 0f);
    }

    // A new shoal ahead of or beside the pawn on swimmable fishing water; index is its place among the live ones, for its
    // circling radius. Six random places first; on narrow water (a river) where all miss, any such cell in reach.
    private bool TrySpawn(Shoal s, int index, Map map, Vector3 pawnPos, float heading, float stock)
    {
        // Ahead of or beside the pawn: the heading turned from clockwise-from-north to counter-clockwise-from-east.
        float ahead = 90f - heading;
        for (int t = 0; t < 7; t++)
        {
            float x, z;
            if (t < 6)
            {
                float a = (ahead + Range(-SpawnSpread, SpawnSpread)) * Mathf.Deg2Rad, r = Range(SpawnMin, SpawnMax);
                x = pawnPos.x + Mathf.Cos(a) * r;
                z = pawnPos.z + Mathf.Sin(a) * r;
            }
            else if (!AnyWaterNear(map, pawnPos, out x, out z)) break;
            var cell = new IntVec3(Mathf.FloorToInt(x), 0, Mathf.FloorToInt(z));
            if (!WavesBridge.IsSwimmableFishingWater(map, cell)) continue;
            s.Freshwater = !WavesBridge.IsSea(map.terrainGrid.TerrainAt(cell));
            s.Shape = ShapeOf(OdysseyFish.ShoalSpecies(map, cell, rand));
            int full = FullCounts[(int)s.Shape], least = s.Shape == Shape.Long ? 1 : 3;
            s.Count = Mathf.Clamp(least + Mathf.RoundToInt((full - least) * stock), 1, Mathf.Min(full, MaxFish));
            s.Live = true;
            s.Leaving = false;
            s.Gone = 0;
            s.Fade = 0f;
            s.X = x;
            s.Z = z;
            s.Heading = s.Target = Range(0f, 360f);
            s.Speed = CruiseSpeed;
            s.WanderAt = time + Range(2f, 4f);
            s.State = State.Cruise;
            s.Spread = 1f;
            s.SwayPhase = Range(0f, Mathf.PI * 2f);
            s.CircleDir = index % 2 == 0 ? 1f : -1f;
            s.CircleIndex = index;
            s.LookCell = IntVec3.Invalid;
            s.Fresh = true;
            for (int f = 0; f < MaxFish; f++)
            {
                // Spawned in its slot, swimming with the leader; a slot over land starts on the leader instead.
                Slot(s, f, out float fx, out float fz);
                if (f > 0 && f < s.Count && !WavesBridge.IsSwimmableFishingWater(map, new IntVec3(Mathf.FloorToInt(fx), 0, Mathf.FloorToInt(fz))))
                {
                    fx = x;
                    fz = z;
                }
                s.Pos[f] = new Vector3(fx, 0f, fz);
                s.Dir[f] = s.Face[f] = s.Yaw[f] = s.Flee[f] = s.Heading;
                s.Spd[f] = s.Speed;
                s.BlockedUntil[f] = 0f;
                s.DryCell[f] = IntVec3.Invalid;
                s.Cell[f] = IntVec3.Invalid;
                s.Eased[f] = -1f;
            }
            return true;
        }
        return false;
    }

    // A random swimmable fishing water cell within SpawnMax of the pawn, as a point in it, preferring cells at least SpawnMin
    // away. The pawn's own cell counts too, so it never fails while the pawn is on such water.
    private bool AnyWaterNear(Map map, Vector3 pawnPos, out float x, out float z)
    {
        IntVec3 centre = pawnPos.ToIntVec3();
        int cells = GenRadial.NumCellsInRadius(SpawnMax), far = 0, near = 0;
        IntVec3 pickFar = IntVec3.Invalid, pickNear = IntVec3.Invalid;
        for (int i = 0; i < cells; i++)
        {
            IntVec3 c = centre + GenRadial.RadialPattern[i];
            if (!WavesBridge.IsSwimmableFishingWater(map, c)) continue;
            // Reservoir picks, so every qualifying cell is as likely.
            if ((c - centre).LengthHorizontalSquared >= SpawnMin * SpawnMin) { if (rand.Next(++far) == 0) pickFar = c; }
            else if (rand.Next(++near) == 0) pickNear = c;
        }
        IntVec3 pick = pickFar.IsValid ? pickFar : pickNear;
        x = pick.x + Range(0.2f, 0.8f);
        z = pick.z + Range(0.2f, 0.8f);
        return pick.IsValid;
    }

    private void Steer(Shoal s, Map map, Vector3 pawnPos, float dx, float dz, float dist, float dt, bool spearfisher)
    {
        float awayAngle = Mathf.Atan2(dz, dx) * Mathf.Rad2Deg;
        switch (s.State)
        {
            case State.Cruise:
                if (!s.Leaving && spearfisher && dist < ScatterRange)
                {
                    StartScatter(s, awayAngle, dist, pawnPos.x, pawnPos.z);
                    break;
                }
                if (!s.Leaving && !spearfisher && dist < CircleRange)
                {
                    s.State = State.Circle;
                    s.CircleAngle = awayAngle;
                    break;
                }
                if (time >= s.WanderAt)
                {
                    s.Target = s.Heading + Range(-WanderTurn, WanderTurn);
                    s.WanderAt = time + Range(2f, 4f);
                }
                // A shoal drifting off from its swimmer turns back toward them.
                if (dist > PullDistance) s.Target = awayAngle + 180f;
                s.Speed = CruiseSpeed;
                s.Spread = Mathf.MoveTowards(s.Spread, 1f, dt);
                break;
            case State.Scatter:
                if (time >= s.StateEnds)
                {
                    if (dist > s.ScatterFrom) ScatterMovedAway++;
                    s.State = State.Regroup;
                    s.StateEnds = time + RegroupSeconds;
                }
                break;
            case State.Regroup:
                s.Speed = Mathf.MoveTowards(s.Speed, CruiseSpeed, ScatterSpeed * dt);
                s.Spread = Mathf.MoveTowards(s.Spread, 1f, (ScatterSpread - 1f) * dt / RegroupSeconds);
                if (time >= s.StateEnds)
                {
                    s.State = State.Cruise;
                    s.Spread = 1f;
                    s.WanderAt = time + Range(2f, 4f);
                    RegroupEvents++;
                }
                break;
            case State.Circle:
                if (spearfisher || dist > CircleRange + 1f)
                {
                    s.State = State.Cruise;
                    break;
                }
                // Along the circle round the pawn, steering in or out toward this shoal's own radius.
                float rx = dist > 0.01f ? dx / dist : 1f, rz = dist > 0.01f ? dz / dist : 0f;
                float pull = (CircleRadius + CircleRadiusStep * s.CircleIndex - dist) * 0.8f;
                float wx = -rz * s.CircleDir + rx * pull, wz = rx * s.CircleDir + rz * pull;
                s.Target = Mathf.Atan2(wz, wx) * Mathf.Rad2Deg;
                s.Speed = CircleSpeed;
                s.Spread = Mathf.MoveTowards(s.Spread, 1f, dt);
                CircledDegrees += Mathf.Abs(Mathf.DeltaAngle(s.CircleAngle, awayAngle));
                s.CircleAngle = awayAngle;
                break;
        }
        Swim(s, map, dt);
    }

    // The leader flees away from (fromX, fromZ), the diver or the spear; each follower picks its own line away from that
    // point as seen from where it is, jittered, and bursts along it.
    private void StartScatter(Shoal s, float awayAngle, float dist, float fromX, float fromZ)
    {
        s.State = State.Scatter;
        s.StateEnds = time + ScatterSeconds;
        s.Target = awayAngle + Range(-30f, 30f);
        s.Speed = ScatterSpeed;
        s.Spread = ScatterSpread;
        s.ScatterFrom = dist;
        for (int f = 1; f < s.Count; f++)
        {
            float fx = s.Pos[f].x - fromX, fz = s.Pos[f].z - fromZ;
            float away = fx * fx + fz * fz > 0.0001f ? Mathf.Atan2(fz, fx) * Mathf.Rad2Deg : awayAngle;
            s.Flee[f] = away + Range(-FleeJitter, FleeJitter);
        }
        ScatterEvents++;
    }

    // Turns toward the target heading, or the nearest heading off it that keeps a look-ahead cell on water, then moves on
    // unless the next step would leave the water.
    private void Swim(Shoal s, Map map, float dt)
    {
        float chosen = s.Target;
        for (int k = 0; k < LookTurns.Length; k++)
        {
            float h = s.Target + LookTurns[k];
            float a = h * Mathf.Deg2Rad;
            var cell = new IntVec3(Mathf.FloorToInt(s.X + Mathf.Cos(a) * LookAhead), 0, Mathf.FloorToInt(s.Z + Mathf.Sin(a) * LookAhead));
            bool wet;
            if (k == 0 && cell == s.LookCell) wet = s.LookWet;
            else
            {
                wet = WavesBridge.IsSwimmableFishingWater(map, cell);
                if (k == 0)
                {
                    s.LookCell = cell;
                    s.LookWet = wet;
                }
            }
            if (!wet) continue;
            if (k > 0)
            {
                // Turn the target itself, so the shoal keeps its new way instead of turning back to the shore.
                s.Target = h;
                LeaderShoreTurns++;
            }
            chosen = h;
            break;
        }
        float turn = s.State == State.Scatter ? FastTurnSpeed : TurnSpeed;
        s.Heading = Mathf.Repeat(Mathf.MoveTowardsAngle(s.Heading, chosen, turn * dt), 360f);
        float rad = s.Heading * Mathf.Deg2Rad, step = s.Speed * dt;
        float nx = s.X + Mathf.Cos(rad) * step, nz = s.Z + Mathf.Sin(rad) * step;
        if (WavesBridge.IsSwimmableFishingWater(map, new IntVec3(Mathf.FloorToInt(nx), 0, Mathf.FloorToInt(nz))))
        {
            s.X = nx;
            s.Z = nz;
        }
        bool fast = s.State == State.Scatter;
        s.SwayPhase = Mathf.Repeat(s.SwayPhase + Mathf.PI * 2f * SwayHz * (fast ? FastSway : 1f) * dt, Mathf.PI * 2f);
    }

    // A fish's slot: its offset behind the leader, turned to the leader's heading and scaled by the shoal's spread, with
    // its own small wobble.
    private void Slot(Shoal s, int f, out float x, out float z)
    {
        float rad = s.Heading * Mathf.Deg2Rad, cos = Mathf.Cos(rad), sin = Mathf.Sin(rad);
        float wide = s.Shape is Shape.Large or Shape.Long ? WideSpread : 1f;
        Vector2 o = Offsets[f];
        float fwd = o.x * wide * s.Spread, side = o.y * wide * s.Spread;
        if (f > 0)
        {
            fwd += 0.08f * Mathf.Sin(time * 1.3f + f * 2.3f);
            side += 0.12f * Mathf.Sin(time * 1.7f + f * 1.9f);
        }
        x = s.X + fwd * cos - side * sin;
        z = s.Z + fwd * sin + side * cos;
    }

    // Moves each follower one step on its own and faces it along its travel; the water test and depth only when a fish
    // enters a new cell, and the eased depth every frame. Returns the farthest fish from the leader.
    private float MoveFish(Shoal s, Map map, float dt)
    {
        float cap = s.Speed * CapFactor + CapExtra;
        bool scatter = s.State == State.Scatter;
        // Sampled for the developer tests: a scatter, or a cruising leader turning onto a new wander heading.
        bool turning = s.State == State.Cruise && Mathf.Abs(Mathf.DeltaAngle(s.Heading, s.Target)) > TurnSampleAngle;
        bool sample = dt > 0f && !s.Fresh && (scatter || turning);
        s.Fresh = false;
        float leadRad = s.Heading * Mathf.Deg2Rad;
        float leadVX = Mathf.Cos(leadRad) * s.Speed, leadVZ = Mathf.Sin(leadRad) * s.Speed;
        float widest = 0f;
        for (int f = 0; f < s.Count; f++)
        {
            if ((s.Gone & (1 << f)) != 0) continue;
            float oldX = s.Pos[f].x, oldZ = s.Pos[f].z, x, z;
            if (f == 0)
            {
                // The leader has already swum (Swim).
                x = s.X;
                z = s.Z;
                s.Dir[0] = s.Face[0] = s.Heading;
            }
            else
            {
                float want, wantSpeed, turn = scatter ? FastTurnSpeed : FollowTurnSpeed;
                if (scatter)
                {
                    want = s.Flee[f];
                    wantSpeed = ScatterSpeed;
                    float dx = s.X - oldX, dz = s.Z - oldZ, d = Mathf.Sqrt(dx * dx + dz * dz);
                    if (d > ScatterTether)
                    {
                        float pull = (d - ScatterTether) * TetherGain / d, fleeRad = want * Mathf.Deg2Rad;
                        want = Mathf.Atan2(Mathf.Sin(fleeRad) + dz * pull, Mathf.Cos(fleeRad) + dx * pull) * Mathf.Rad2Deg;
                    }
                }
                else
                {
                    // Swim with the leader and close on the slot; just after meeting the shore, head for the leader.
                    float tx, tz;
                    if (time < s.BlockedUntil[f])
                    {
                        tx = s.X;
                        tz = s.Z;
                    }
                    else Slot(s, f, out tx, out tz);
                    float vx = leadVX + FollowGain * (tx - oldX), vz = leadVZ + FollowGain * (tz - oldZ);
                    wantSpeed = Mathf.Sqrt(vx * vx + vz * vz);
                    want = wantSpeed > 0.001f ? Mathf.Atan2(vz, vx) * Mathf.Rad2Deg : s.Dir[f];
                }
                s.Dir[f] = Mathf.Repeat(Mathf.MoveTowardsAngle(s.Dir[f], want, turn * dt), 360f);
                // Slow while the way it wants is still well round from where it swims, so it curves instead of looping wide.
                float facing = Mathf.Cos(Mathf.DeltaAngle(s.Dir[f], want) * Mathf.Deg2Rad);
                wantSpeed = Mathf.Min(wantSpeed * Mathf.Clamp01(0.5f + 0.5f * facing), cap);
                s.Spd[f] = Mathf.Min(Mathf.MoveTowards(s.Spd[f], wantSpeed, FollowAccel * dt), cap);
                float rad = s.Dir[f] * Mathf.Deg2Rad, step = s.Spd[f] * dt;
                x = oldX + Mathf.Cos(rad) * step;
                z = oldZ + Mathf.Sin(rad) * step;
                // A step from water onto land is refused: the fish slows and turns for the leader, or in a scatter takes the
                // leader's shore-safe line instead.
                var next = new IntVec3(Mathf.FloorToInt(x), 0, Mathf.FloorToInt(z));
                if (s.Wet[f] && next != s.Cell[f])
                {
                    bool dry = next == s.DryCell[f];
                    if (!dry && !WavesBridge.IsSwimmableFishingWater(map, next))
                    {
                        s.DryCell[f] = next;
                        dry = true;
                    }
                    if (dry)
                    {
                        x = oldX;
                        z = oldZ;
                        s.Spd[f] *= 0.5f;
                        s.BlockedUntil[f] = time + BlockedSeconds;
                        if (scatter) s.Flee[f] = s.Heading + Range(-FleeJitter, FleeJitter);
                    }
                }
                // Facing eases onto the travel; a near-still fish holds it.
                if (s.Spd[f] > StillSpeed) s.Face[f] = Mathf.LerpAngle(s.Face[f], s.Dir[f], 1f - Mathf.Exp(-dt / FaceEaseSeconds));
            }
            s.Pos[f] = new Vector3(x, 0f, z);
            s.Yaw[f] = s.Face[f] + 6f * Mathf.Sin(time * 2f + f);
            widest = Mathf.Max(widest, Mathf.Sqrt(Sq(x - s.X, z - s.Z)));
            if (sample)
            {
                float mx = x - oldX, mz = z - oldZ, moved = Mathf.Sqrt(mx * mx + mz * mz) / dt;
                if (moved > StillSpeed)
                {
                    float error = Mathf.Abs(Mathf.DeltaAngle(s.Yaw[f], Mathf.Atan2(mz, mx) * Mathf.Rad2Deg));
                    bool over = moved > cap * (1f + OverCapMargin);
                    if (scatter)
                    {
                        ScatterSteps++;
                        if (over) ScatterOverCap++;
                        ScatterFaceError += error;
                    }
                    else
                    {
                        TurnSteps++;
                        if (over) TurnOverCap++;
                        TurnFaceError += error;
                    }
                }
            }
            var cell = new IntVec3(Mathf.FloorToInt(x), 0, Mathf.FloorToInt(z));
            if (cell != s.Cell[f])
            {
                s.Cell[f] = cell;
                s.Wet[f] = WavesBridge.IsSwimmableFishingWater(map, cell);
                // Over land the last depth holds, so a fish skirting the shore does not ease toward crisp.
                if (s.Wet[f]) s.Depth[f] = Mathf.Clamp01(MapComponent_FishStock.SwimDepthAt(map, cell));
                // The first time over water a fish takes its depth at once: the shoal is fading in, so nothing pops.
                if (s.Wet[f] && s.Eased[f] < 0f) s.Eased[f] = s.Depth[f];
            }
            if (s.Eased[f] >= 0f) s.Eased[f] = Mathf.MoveTowards(s.Eased[f], s.Depth[f], dt / DepthEaseSeconds);
        }
        return widest;
    }

    // On a catch: the nearest fish of the nearest shoal is taken out of it, and the rest scatter.
    internal void Spear(Vector3 at)
    {
        Shoal nearest = null;
        if (!Nearest(at, false, out Vector3 leader)) return;
        for (int i = 0; i < Slots && nearest == null; i++)
            if (shoals[i].Live && !shoals[i].Leaving && shoals[i].X == leader.x && shoals[i].Z == leader.z) nearest = shoals[i];
        if (nearest == null) return;
        int pick = -1;
        float best = float.MaxValue;
        for (int f = 0; f < nearest.Count; f++)
        {
            if ((nearest.Gone & (1 << f)) != 0 || !nearest.Wet[f]) continue;
            float d = Sq(nearest.Pos[f].x - at.x, nearest.Pos[f].z - at.z);
            if (d >= best) continue;
            best = d;
            pick = f;
        }
        if (pick < 0) return;
        nearest.Gone |= 1 << pick;
        float dx = nearest.X - at.x, dz = nearest.Z - at.z;
        StartScatter(nearest, Mathf.Atan2(dz, dx) * Mathf.Rad2Deg, Mathf.Sqrt(dx * dx + dz * dz), at.x, at.z);
    }

    // Draws the fish over swimmable water in view. A follower over land is left out and counted in skipped.
    internal void Draw(CellRect view, float y, ref int drawn, ref int skipped)
    {
        for (int i = 0; i < Slots; i++)
        {
            Shoal s = shoals[i];
            if (!s.Live || s.Fade <= 0f) continue;
            for (int f = 0; f < s.Count; f++)
            {
                if ((s.Gone & (1 << f)) != 0) continue;
                if (!s.Wet[f])
                {
                    skipped++;
                    continue;
                }
                if (!view.Contains(s.Cell[f])) continue;
                Vector3 at = s.Pos[f];
                at.y = y;
                float depth = Mathf.Max(0f, s.Eased[f]);
                float alpha = Mathf.Lerp(ShallowAlpha, DeepAlpha, depth) * s.Fade;
                if (!DrawFish(at, s.Yaw[f], s.Shape, Mathf.Lerp(1f, DeepSize, depth), alpha, BlurLevelAt(depth), s.SwayPhase + f * 1.3f, s.Freshwater))
                    continue;
                DiveVisuals.ShadowDrawnHook?.Invoke(at);
                drawn++;
            }
        }
    }

    // 0 crisp over the shallowest water, 1 medium, 2 soft over the deepest.
    private static float BlurLevelAt(float depth) => depth * (BlurLevels.Length - 1);

    // One fish at its depth's size factor, alpha and blur level, heading counter-clockwise from east, with the sway frame
    // for phase. The blur level crossfades its two neighbouring textures: the sharper layer at a1 and the softer one topping
    // it up so the core stays at alpha (a1 + a2 * (1 - a1) = alpha) and only the edge blends.
    internal static bool DrawFish(Vector3 at, float heading, Shape shape, float sizeFactor, float alpha, float blurLevel, float phase, bool freshwater)
    {
        Material[][] levels = (freshwater ? freshwaterMaterials : materials)[(int)shape];
        float level = Mathf.Clamp(blurLevel, 0f, BlurLevels.Length - 1);
        int lower = Mathf.Min((int)level, BlurLevels.Length - 2);
        float soft = level - lower;
        float a1 = alpha * (1f - soft), a2 = (alpha - a1) / (1f - a1);
        Material m1 = Step(levels[lower], a1), m2 = Step(levels[lower + 1], a2);
        if (m1 == null && m2 == null) return false;
        int frame = (int)(Mathf.Repeat(phase, Mathf.PI * 2f) / (Mathf.PI * 2f) * SwayFrames) % SwayFrames;
        float size = Sizes[(int)shape] * sizeFactor;
        var matrix = Matrix4x4.TRS(at, Quaternion.AngleAxis(-heading, Vector3.up), new Vector3(size, 1f, size));
        if (m1 != null) Graphics.DrawMesh(swayMeshes[frame], matrix, m1, 0);
        if (m2 != null) Graphics.DrawMesh(swayMeshes[frame], matrix, m2, 0);
        return true;
    }

    // The step for an alpha, as a share of ShallowAlpha; null when it rounds to nothing.
    private static Material Step(Material[] steps, float alpha)
    {
        int index = Mathf.CeilToInt(Mathf.Clamp01(alpha / ShallowAlpha) * AlphaSteps) - 1;
        return index < 0 ? null : steps[index];
    }

    // Developer tests, read only: the eased blur level of the live fish over water that have settled at their depth, summed
    // for fish over shallow water (swim depth under 0.1) and deep water (over 0.3).
    internal void BlurSample(ref float shallowSum, ref int shallowN, ref float deepSum, ref int deepN)
    {
        for (int i = 0; i < Slots; i++)
        {
            Shoal s = shoals[i];
            if (!s.Live) continue;
            for (int f = 0; f < s.Count; f++)
            {
                if ((s.Gone & (1 << f)) != 0 || !s.Wet[f] || s.Eased[f] < 0f || Mathf.Abs(s.Eased[f] - s.Depth[f]) > 0.05f) continue;
                float level = BlurLevelAt(s.Eased[f]);
                if (s.Depth[f] < 0.1f) { shallowSum += level; shallowN++; }
                else if (s.Depth[f] > 0.3f) { deepSum += level; deepN++; }
            }
        }
    }

    internal static float SizeOf(Shape shape) => Sizes[(int)shape];

    // The outline for a species, by its def name; anything else, toxfish included, is generic.
    internal static Shape ShapeOf(ThingDef species)
    {
        switch (species?.defName)
        {
            case "Fish_Bluefish":
            case "Fish_Salmon":
            case "Fish_Frostfish":
            case "Fish_Guppy":
                return Shape.Slim;
            case "Fish_Tilapia":
            case "Fish_Piranha":
            case "Fish_Bass":
            case "Fish_Flounder":
                return Shape.Stocky;
            case "Fish_Tuna":
            case "Fish_Cod":
            case "Fish_Catfish":
                return Shape.Large;
            case "Fish_Dogfish":
            case "Fish_Marlin":
                return Shape.Long;
            default:
                return Shape.Generic;
        }
    }

    // Built once, on the main thread, the first frame anything is drawn. Sea fish at Waves' sea-life queue, like the reef:
    // over its opaque water body, under its foam. Lake and river fish at the freshwater queue (just over Living Waters'
    // veil), the same set when there is no separate one.
    internal static void EnsureMaterials(int? seaQueue, int? freshwaterQueue)
    {
        if (materials != null) return;
        materials = BuildMaterials(seaQueue);
        freshwaterMaterials = freshwaterQueue is { } q && q != seaQueue ? BuildMaterials(q) : materials;
        swayMeshes = new Mesh[SwayFrames];
        for (int k = 0; k < SwayFrames; k++) swayMeshes[k] = BentPlane(k * Mathf.PI * 2f / SwayFrames, Sway);
    }

    private static Material[][][] BuildMaterials(int? renderQueue)
    {
        var set = new Material[TexPaths.Length][][];
        for (int s = 0; s < TexPaths.Length; s++)
        {
            set[s] = new Material[BlurLevels.Length][];
            for (int l = 0; l < BlurLevels.Length; l++)
            {
                var tex = ContentFinder<Texture2D>.Get(TexPaths[s] + BlurLevels[l]);
                set[s][l] = new Material[AlphaSteps];
                for (int i = 0; i < AlphaSteps; i++)
                {
                    var m = new Material(ShaderDatabase.Transparent)
                    {
                        mainTexture = tex,
                        color = new Color(Tint.r, Tint.g, Tint.b, ShallowAlpha * (i + 1f) / AlphaSteps),
                    };
                    if (renderQueue is { } queue) m.renderQueue = queue;
                    set[s][l][i] = m;
                }
            }
        }
        return set;
    }

    // A unit plane like MeshPool.plane10, cut into columns along its length, the tail half shifted sideways by a travelling
    // wave; the head (x = +0.5) stays put. Texture coordinates are not bent, so the outline bends with the mesh. The shark
    // shadow (DiveVisuals) uses it with a smaller sway.
    internal static Mesh BentPlane(float phase, float sway)
    {
        var verts = new Vector3[(SwaySegments + 1) * 2];
        var uvs = new Vector2[verts.Length];
        var normals = new Vector3[verts.Length];
        var tris = new int[SwaySegments * 6];
        for (int c = 0; c <= SwaySegments; c++)
        {
            float u = (float)c / SwaySegments, x = u - 0.5f, t = 1f - u;
            float off = sway * t * t * Mathf.Sin(phase + 2.4f * t);
            verts[c * 2] = new Vector3(x, 0f, -0.5f + off);
            verts[c * 2 + 1] = new Vector3(x, 0f, 0.5f + off);
            uvs[c * 2] = new Vector2(u, 0f);
            uvs[c * 2 + 1] = new Vector2(u, 1f);
            normals[c * 2] = normals[c * 2 + 1] = Vector3.up;
            if (c == SwaySegments) continue;
            int a = c * 2, b = c * 2 + 1, cc = c * 2 + 3, d = c * 2 + 2, o = c * 6;
            tris[o] = a;
            tris[o + 1] = b;
            tris[o + 2] = cc;
            tris[o + 3] = a;
            tris[o + 4] = cc;
            tris[o + 5] = d;
        }
        var mesh = new Mesh { name = "SpearfishingFishSway" }; // not translated
        mesh.vertices = verts;
        mesh.uv = uvs;
        mesh.normals = normals;
        mesh.triangles = tris;
        mesh.RecalculateBounds();
        return mesh;
    }

    private float Range(float min, float max) => min + (float)rand.NextDouble() * (max - min);

    private static float Sq(float x, float z) => x * x + z * z;

    private static int CountBits(int v)
    {
        int n = 0;
        for (; v != 0; v &= v - 1) n++;
        return n;
    }
}
