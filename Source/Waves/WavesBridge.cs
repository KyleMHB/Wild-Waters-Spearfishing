using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace Spearfishing;

// The only place that touches RimWorld: Waves and RimWorld: Living Waters. Since Waves 1.3.0 both mods have a public API
// (RimWorldWaves.WavesApi, RimWorldRivers.LivingWatersApi; see each mod's docs/API.md), and the bridge calls it by
// reflection: each member is resolved once into a delegate, with no compile-time reference to either mod's assembly, so a
// missing member turns off one feature instead of throwing mid-job (ADR 0011). The rest of the mod asks gameplay questions
// through this class and never sees a Waves type. Every lookup belongs to a BridgeFeature, which logs once and falls back
// when its member is missing. Three internals have no API equivalent and are still reached by reflection: the render queues
// just above Waves' shore veil and Living Waters' veil, and the check that Waves draws Pawn.Swimming. Harmony patches
// nothing in either mod.
public static class WavesBridge
{
    private const string WavesApiType = "RimWorldWaves.WavesApi"; // not translated
    private const string WaveMaterialsType = "RimWorldWaves.WaveMaterials"; // not translated
    // WavesApi.Version since Waves 1.3.0, and LivingWatersApi.Version since Living Waters 1.4.0.
    private const int ApiVersion = 1;

    // ---- Waves API ----------------------------------------------------------------------------------------------------------
    // Every API-backed feature requires this one, so an older Waves logs one warning, not one per feature. Without it no cell
    // is swimmable sea, so spearfishing work turns off politely (ticket 13).
    private static Type wavesApi;
    private static BridgeFeature api;

    private static Func<Map, IntVec3, bool> isSwimCell;
    private static Func<bool> swimmingOn;
    private static Func<int> underwaterQueue;
    private static BridgeFeature swimCells, swimmingSetting, reefUnderwater;

    internal static void Initialize()
    {
        api = BridgeFeature.Resolve("Waves API", () => ResolveApi(WavesApiType, out wavesApi), // not translated
            advice: "Spearfishing needs RimWorld: Waves 1.3.0 or later."); // not translated
        swimCells = ApiFeature("swimmable sea cells", () => Bind(wavesApi, "IsSwimCell", out isSwimCell)); // not translated
        swimmingSetting = ApiFeature("Waves swimming setting", () => Bind(wavesApi, "SwimmingOn", out swimmingOn)); // not translated
        // Bound now, read during play: reading it runs Waves' material setup.
        reefUnderwater = ApiFeature("reef drawn under Waves' water", () => Bind(wavesApi, "UnderwaterQueue", out underwaterQueue)); // not translated
        InitializeLimits();
        InitializeDiving();
        swimmerLook = BridgeFeature.Resolve("swimmer look", () =>
            AccessTools.TypeByName(SwimmingPatchType) == null ? SwimmingPatchType + " was not found" : null); // not translated
        overVeil = BridgeFeature.Resolve("art drawn over Waves' shore veil", ResolveOverVeil); // not translated
        // Only looked up with Living Waters loaded; without it nothing covers lakes and rivers, so there is nothing to warn about.
        if (ModsConfig.IsActive(LivingWatersId))
            freshwaterBody = BridgeFeature.Resolve("art drawn under Living Waters' water", () => ResolveFreshwaterBody(), "RimWorld: Living Waters", // not translated
                "Spearfishing needs RimWorld: Living Waters 1.4.0 or later to draw its art in lakes and rivers."); // not translated
        if (freshwaterBody != null)
            freshwaterOverVeil = BridgeFeature.Resolve("art drawn over Living Waters' veil", ResolveFreshwaterOverVeil, "RimWorld: Living Waters", requires: freshwaterBody); // not translated
    }

    private static BridgeFeature ApiFeature(string name, Func<string> resolve) => BridgeFeature.Resolve(name, resolve, requires: api);

    // Finds a public API class and checks its Version; null on success.
    private static string ResolveApi(string typeName, out Type type)
    {
        type = AccessTools.TypeByName(typeName);
        if (type == null) return typeName + " was not found"; // not translated
        string missing = Bind(type, "Version", out Func<int> version);
        if (missing != null) return missing;
        int found = version();
        return found >= ApiVersion ? null : $"{typeName}.Version is {found}, not {ApiVersion} or later"; // not translated
    }

    // Binds a public static method or property getter of an API class to a delegate of the expected signature; null on success.
    private static string Bind<T>(Type type, string member, out T bound) where T : Delegate
    {
        MethodInfo method = AccessTools.DeclaredMethod(type, member) ?? AccessTools.DeclaredPropertyGetter(type, member);
        bound = method is { IsStatic: true } ? Delegate.CreateDelegate(typeof(T), method, throwOnBindFailure: false) as T : null;
        return bound == null ? $"{type.FullName}.{member} was not found with the expected signature" : null; // not translated
    }

    // ---- Over the shore veil (ticket 34) ------------------------------------------------------------------------------------
    // From about 1 to 21 cells off the beach Waves draws a veil: a scrolling band texture, opaque in its bands, just above its
    // sea-life queue. Each band hid the dive shadow and the shoal fish as it swept over (the "blinking" at sea). The veil
    // pair is followed at once by the rollers and the other surf layers, so there is no free queue above it: on first use the
    // bridge moves every Waves surf layer above the veil up by one queue, keeping their order, and our under-water art takes
    // the free queue. Waves' own sea life and our reef stay under the veil. Without the lookup the art stays at Waves' sea-life
    // queue, under the veil, as before. Waves' API has no queue above the veil (its UnderwaterQueue is under it), so this one
    // stays on Waves' internal materials.
    private static BridgeFeature overVeil;
    private static FieldInfo veilTurnedField;
    private static readonly List<FieldInfo> waveMaterialFields = new();
    private static int? overVeilQueue;

    private static string ResolveOverVeil()
    {
        var type = AccessTools.TypeByName(WaveMaterialsType);
        if (type == null) return WaveMaterialsType + " was not found"; // not translated
        veilTurnedField = AccessTools.Field(type, "VeilTurned"); // not translated
        if (veilTurnedField is not { IsStatic: true } || veilTurnedField.FieldType != typeof(Material)) return WaveMaterialsType + ".VeilTurned was not found"; // not translated
        foreach (var field in type.GetFields(BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic))
            if (field.FieldType == typeof(Material)) waveMaterialFields.Add(field);
        return null;
    }

    // The render queue for the dive shadow, sunk shoulders and shoal fish at sea: just over Waves' shore veil, under its
    // rollers and foam; or Waves' sea-life queue without the lookup. Reading it runs Waves' material setup, so only read it
    // during play, from the main thread. The surf layers are moved once.
    public static int? SeaArtRenderQueue
    {
        get
        {
            if (overVeil is not { Available: true }) return UnderwaterRenderQueue;
            if (overVeilQueue != null) return overVeilQueue;
            if (veilTurnedField.GetValue(null) is not Material veil) return UnderwaterRenderQueue;
            int free = veil.renderQueue + 1;
            // Only Waves' own consecutive surf block, not its glow and shadow materials far above it.
            foreach (var field in waveMaterialFields)
                if (field.GetValue(null) is Material m && m.renderQueue >= free && m.renderQueue < free + 100) m.renderQueue++;
            overVeilQueue = free;
            return overVeilQueue;
        }
    }

    // ---- Lakes and rivers under Living Waters (ticket 34) -----------------------------------------------------------------
    // Living Waters (same author) draws its own water body over lakes and rivers, not the sea, at render queues above Waves'
    // whole range. Art drawn at Waves' sea-life queue on a lake was hidden under it. LivingWatersApi.UnderwaterQueue (Living
    // Waters 1.4.0) is over the water's body and under its sparkle, foam, rocks and ice: where the dive shadow, the sunk
    // shoulders and the shoal fish go on fresh water. Living Waters stays optional, so its class is only looked up while it is
    // active. Without the lookup the art stays at Waves' queue as before.
    private const string LivingWatersId = "patrickschwarzer.rivers"; // not translated
    private const string LivingWatersApiType = "RimWorldRivers.LivingWatersApi"; // not translated
    private static Func<int> freshwaterQueue;
    private static BridgeFeature freshwaterBody;

    private static string ResolveFreshwaterBody() =>
        ResolveApi(LivingWatersApiType, out Type type) ?? Bind(type, "UnderwaterQueue", out freshwaterQueue);

    // The render queue for art under the water of a lake or river, or null when Living Waters is not loaded or the lookup
    // failed (the art then uses Waves' queue, as on the sea). Only read it during play.
    public static int? FreshwaterUnderwaterRenderQueue => freshwaterBody is { Available: true } ? freshwaterQueue() : null;

    // ---- Over Living Waters' veil ---------------------------------------------------------------------------------------------
    // Past the shallows Living Waters draws a veil over lakes and rivers: a water-coloured layer up to 80% opaque whose texture
    // is half clear and half solid patches, scrolling with the flow, just above its UnderwaterQueue. The patches drifting over
    // the dive shadow made it come and go (filmed on a river, 2026-11-18). As at sea, on first use the bridge moves every Living
    // Waters water layer above the veil up by one queue, keeping their order, and the dive art takes the free queue: still under
    // the whitewater, rocks, ice and lilies. Living Waters' API has no queue above the veil, so this reads its internal
    // RiverMaterials; without the lookup the art stays at UnderwaterQueue, under the veil.
    private const string RiverMaterialsType = "RimWorldRivers.RiverMaterials"; // not translated
    private static BridgeFeature freshwaterOverVeil;
    private static FieldInfo freshwaterVeilField;
    private static readonly List<FieldInfo> riverMaterialFields = new();
    private static int? freshwaterOverVeilQueue;

    private static string ResolveFreshwaterOverVeil()
    {
        var type = AccessTools.TypeByName(RiverMaterialsType);
        if (type == null) return RiverMaterialsType + " was not found"; // not translated
        freshwaterVeilField = AccessTools.Field(type, "Veil"); // not translated
        if (freshwaterVeilField is not { IsStatic: true } || freshwaterVeilField.FieldType != typeof(Material)) return RiverMaterialsType + ".Veil was not found"; // not translated
        foreach (var field in type.GetFields(BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic))
            if (field.FieldType == typeof(Material) || field.FieldType == typeof(Material[])) riverMaterialFields.Add(field);
        return null;
    }

    // The render queue for the dive shadow, sunk shoulders, spear and shoal fish in a lake or river: just over Living Waters'
    // veil, else its UnderwaterQueue, else null (as FreshwaterUnderwaterRenderQueue). Only read it during play, from the main
    // thread. The layers are moved once.
    public static int? FreshwaterArtRenderQueue
    {
        get
        {
            if (freshwaterOverVeil is not { Available: true }) return FreshwaterUnderwaterRenderQueue;
            if (freshwaterOverVeilQueue != null) return freshwaterOverVeilQueue;
            if (freshwaterVeilField.GetValue(null) is not Material veil) return FreshwaterUnderwaterRenderQueue;
            int free = veil.renderQueue + 1;
            // Only its own water layers just above the veil; a material held in two fields moves once.
            var moved = new HashSet<Material>();
            void Move(Material m)
            {
                if (m != null && m.renderQueue >= free && m.renderQueue < free + 100 && moved.Add(m)) m.renderQueue++;
            }
            foreach (var field in riverMaterialFields)
                switch (field.GetValue(null))
                {
                    case Material m: Move(m); break;
                    case Material[] set: foreach (var m in set) Move(m); break;
                }
            freshwaterOverVeilQueue = free;
            return freshwaterOverVeilQueue;
        }
    }

    // ---- Swimming or wading (ticket 33) ---------------------------------------------------------------------------------
    // Waves draws a pawn swimming where its patch on Pawn.Swimming says so (a spawned, standing pawn on one of its swim cells),
    // and wading everywhere else in the water. The vanilla property is the answer; the feature only confirms Waves still
    // drives it through that patch. Checked by type, not by Harmony's patch list, so the order mods patch in doesn't matter.
    // Waves' API says nothing about how it draws swimmers, so this stays a check on its internal patch class.
    private const string SwimmingPatchType = "RimWorldWaves.Patch_Pawn_Swimming"; // not translated
    private static BridgeFeature swimmerLook;

    // Whether the bridge can tell a swimming pawn from a wading one. Without it the dive visuals keep the old rule.
    public static bool KnowsSwimming => swimmerLook is { Available: true };

    // Whether Waves draws this pawn swimming (true) or, in the water, wading (false). False without the feature.
    public static bool IsSwimming(Pawn pawn) => KnowsSwimming && pawn.Swimming;

    // Sea water: the bridge alone decides which terrain counts as sea, so every caller agrees on it. Both vanilla ocean
    // terrains, which Waves classifies as sea by defName. Reef is a grid over this ocean (ADR 0008), so it needs no Waves hook.
    public static bool IsSea(TerrainDef terrain) =>
        terrain != null && (terrain == TerrainDefOf.WaterOceanDeep || terrain == TerrainDefOf.WaterOceanShallow);

    // The render queue Waves draws sea life at: above its opaque water body, below its foam, so art drawn there shows through
    // the water. Null without the lookup. Reading it runs Waves' material setup, so only read it during play.
    public static int? UnderwaterRenderQueue => reefUnderwater is { Available: true } ? underwaterQueue() : null;

    // A sea cell that Waves lets colonists swim in. Waves counts deep ocean, and shallow ocean far enough from the beach,
    // as swim water; wading water near the shore, lakes and rivers are not swimmable sea. Gameplay asks
    // IsSwimmableFishingWater instead (ticket 24); this sea-only question is kept for reef and developer checks.
    // Without the Waves lookup no cell qualifies.
    public static bool IsSwimmableSea(Map map, IntVec3 cell)
    {
        if (map == null || !cell.InBounds(map) || !IsSea(map.terrainGrid.TerrainAt(cell))) return false;
        return swimCells is { Available: true } && isSwimCell(map, cell);
    }

    // Water spearfishing can use (ticket 24, ADR 0010): both ocean terrains, the vanilla deep lake and the chest-deep river.
    // Defs are compared by reference, not by name, so a mod's look-alike terrain (Odyssey's toxic water, a marsh, a modded
    // shallow) is never picked up by accident. Shallow freshwater is left out: colonists wade it, they don't swim.
    public static bool IsFishingWater(TerrainDef terrain) =>
        terrain != null && (IsSea(terrain) || terrain == TerrainDefOf.WaterDeep || terrain == TerrainDefOf.WaterMovingChestDeep);

    // Fishing water that Waves lets colonists swim in, out in the open: the cell every zone, dive, snorkel, fin and fish
    // shadow check asks about. Waves decides which cells are swim water, so a lake or river counts wherever Waves lets pawns
    // swim, and the sea only far enough from the beach. Water under a natural rock roof is cave water and never counts, in the
    // sea too. Frozen water reads as ice, so it is never fishing water. Without the Waves lookup no cell qualifies.
    public static bool IsSwimmableFishingWater(Map map, IntVec3 cell)
    {
        if (map == null || !cell.InBounds(map) || !IsFishingWater(map.terrainGrid.TerrainAt(cell))) return false;
        if (UnderNaturalRoof(map, cell)) return false;
        return swimCells is { Available: true } && isSwimCell(map, cell);
    }

    // Why a cell is not swimmable fishing water, for the zone tool's message; None when it is.
    public static FishingWaterRefusal RefusalAt(Map map, IntVec3 cell)
    {
        if (map == null || !cell.InBounds(map)) return FishingWaterRefusal.Land;
        if (IsSwimmableFishingWater(map, cell)) return FishingWaterRefusal.None;
        TerrainGrid grid = map.terrainGrid;
        TerrainDef terrain = grid.TerrainAt(cell);
        // Ice or another temporary terrain laid over water (vanilla freezing, Living Waters' ice).
        TerrainDef under = grid.TerrainAtIgnoreTemp(map.cellIndices.CellToIndex(cell));
        if (grid.TempTerrainAt(cell) != null && terrain is not { IsWater: true } && under is { IsWater: true })
            return FishingWaterRefusal.Frozen;
        if (terrain is { IsWater: true } && terrain.toxicBuildupFactor > 0f) return FishingWaterRefusal.Toxic;
        if (terrain == TerrainDefOf.Marsh) return FishingWaterRefusal.Marsh;
        if (terrain is not { IsWater: true }) return FishingWaterRefusal.Land;
        if (swimCells is not { Available: true }) return FishingWaterRefusal.NotSwimmable;
        if (UnderNaturalRoof(map, cell)) return FishingWaterRefusal.Cave;
        if (terrain == TerrainDefOf.WaterShallow || terrain == TerrainDefOf.WaterMovingShallow || IsFishingWater(terrain))
            return FishingWaterRefusal.Shallow;
        return FishingWaterRefusal.NotSwimmable;
    }

    private static bool UnderNaturalRoof(Map map, IntVec3 cell) => map.roofGrid.RoofAt(cell) is { isNatural: true };

    // Whether spearfishing can go ahead: Waves' swimming setting is on and the bridge can read it and Waves' swimmable cells.
    // Without either lookup this reports off, so spearfishing work stops politely instead of sending divers into water the
    // bridge can't judge (ticket 13). The work giver and the dive trip both gate on it.
    public static bool SwimmingOn => swimCells is { Available: true } && swimmingSetting is { Available: true } && swimmingOn();

    // ---- Divers stay out at sea ----------------------------------------------------------------------------------------
    // Every 90 ticks Waves sends idle pawns in deep water ashore. A diver or snorkeler holding still looks idle to it, so the
    // bridge registers a check through WavesApi.AddStaysInWater that keeps anyone on a sea trip out there; they head ashore by
    // their own job instead. Registered from here rather than as Waves' WavesWaterJob extension on the job defs, so no Waves
    // type is named outside the bridge (ADR 0011). Without this feature divers are still sent ashore mid-trip, so trips end
    // early but nothing breaks.
    private static BridgeFeature diversStayAtSea;

    // ---- Stay afloat ----------------------------------------------------------------------------------------------------
    // Waves asks WavesApi.KeepsAfloat in its limits pass: a pawn kept afloat is not knocked out when their Rest runs out in
    // deep water, and does not drown while downed there. The bridge registers Buoy.KeepsAfloat, which has no side effects.
    // Waves no longer says when it spared someone, so Buoy starts the swim home on its own check (Buoy.CheckKeptAfloat), which
    // asks IsDeepSwimCell below. Without this feature buoys still add stringer capacity, but an exhausted wearer drowns like
    // anyone else.
    private static BridgeFeature stayAfloat;
    private static Func<TerrainDef, bool> isDeepWater;

    private static void InitializeDiving()
    {
        diversStayAtSea = ApiFeature("divers stay out at sea", () => // not translated
        {
            string missing = Bind(wavesApi, "AddStaysInWater", out Action<Func<Pawn, bool>> addStaysInWater);
            if (missing == null) addStaysInWater(OnSeaTrip);
            return missing;
        });
        stayAfloat = ApiFeature("stay afloat", () => // not translated
        {
            string missing = Bind(wavesApi, "IsDeepWater", out isDeepWater);
            if (missing != null) return missing;
            missing = Bind(wavesApi, "AddKeepsAfloat", out Action<Func<Pawn, bool>> addKeepsAfloat);
            if (missing == null) addKeepsAfloat(Buoy.KeepsAfloat);
            return missing;
        });
    }

    // Asked by Waves for each idle pawn in deep water; cheap and free of side effects, as the API requires.
    // A sea trip, or a job StaysInWater lists (restoring sea floor).
    private static bool OnSeaTrip(Pawn pawn) => pawn.jobs?.curDriver is JobDriver_SeaTrip || StaysInWater.Keeps(pawn);

    // Whether exhausted buoy wearers are kept afloat.
    public static bool StayAfloatOn => stayAfloat is { Available: true };

    // A swim cell in deep water, where Waves exhausts and drowns swimmers. False without the stay-afloat feature.
    public static bool IsDeepSwimCell(Map map, IntVec3 cell) =>
        StayAfloatOn && swimCells is { Available: true } && isSwimCell(map, cell) && isDeepWater(map.terrainGrid.TerrainAt(cell));

    // ---- Swim limits: Rest drain, water cost and cold ----------------------------------------------------------------------
    // What a diver's safe exits (ticket 05) need to know about Waves' limits in deep water. Every read falls back to Waves'
    // own value as of Waves 1.7, so a missing member makes the exits use the known numbers rather than none. The fins and the
    // wetsuit raise Waves' own stats (Waves_SwimStamina, Waves_WaterInsulation), which the API's answers already include.
    private const float KnownRestDrainPer60 = 0.008571428f;
    private const int KnownWaterMoveCost = 38;
    private const float KnownColdLimit = 15f;
    // Waves chills a swimmer only below this water temperature, by this much severity per 60 ticks per degree below their
    // cold limit. Constants in Waves' limits pass that the API does not expose, so they are kept here as known values.
    private const float ChillsBelow = 15f, ChillPer60PerDegree = 0.0005f;

    private static BridgeFeature restDrain, waterMoveCost, coldLimit, waterTemperature, swimLimitsSetting;
    private static Func<bool> swimLimitsOn;
    private static Func<Pawn, float> restDrainPerTickFor;
    private static Func<int> moveCost;
    private static Func<Pawn, float> wavesColdLimit;
    private static Func<Map, float> wavesWaterTemperature;

    private static void InitializeLimits()
    {
        swimLimitsSetting = ApiFeature("Waves swim limits setting", () => Bind(wavesApi, "SwimLimitsOn", out swimLimitsOn)); // not translated
        restDrain = ApiFeature("deep-water Rest drain", () => Bind(wavesApi, "RestDrainPerTickFor", out restDrainPerTickFor)); // not translated
        waterMoveCost = ApiFeature("deep-water move cost", () => Bind(wavesApi, "DeepWaterMoveCost", out moveCost)); // not translated
        coldLimit = ApiFeature("water cold limit", () => Bind(wavesApi, "ColdLimit", out wavesColdLimit)); // not translated
        waterTemperature = ApiFeature("water temperature", () => Bind(wavesApi, "WaterTemperature", out wavesWaterTemperature)); // not translated
    }

    // Whether Waves' swim limits (deep-water exhaustion and cold) are on. Without the lookup this reports Waves' default (on),
    // so divers stay careful.
    public static bool SwimLimitsOn => swimLimitsSetting is not { Available: true } || swimLimitsOn();

    // Rest a pawn loses per tick to Waves while in deep water, after their swim stamina. Zero with Waves' limits off. Without
    // the lookup, Waves' known rate, unscaled.
    public static float DeepWaterRestDrainPerTick(Pawn pawn)
    {
        if (!SwimLimitsOn) return 0f;
        return restDrain is { Available: true } ? restDrainPerTickFor(pawn) : KnownRestDrainPer60 / 60f;
    }

    // Path cost Waves adds to every step through deep water, on top of the pawn's own ticks per move.
    public static int DeepWaterMoveCost => waterMoveCost is { Available: true } ? moveCost() : KnownWaterMoveCost;

    // The water temperature below which Waves starts chilling this pawn in deep water. Waves takes it from the pawn's
    // comfortable minimum without clothing, so ordinary clothes don't help, less their water insulation (the wetsuit's).
    public static float WaterColdLimit(Pawn pawn) => coldLimit is { Available: true } ? wavesColdLimit(pawn) : KnownColdLimit;

    // The sea temperature Waves uses: the outdoor temperature, unless Waves' developer test temperature overrides it.
    public static float WaterTemperature(Map map) =>
        waterTemperature is { Available: true } ? wavesWaterTemperature(map) : map.mapTemperature.OutdoorTemp;

    // Hypothermia severity Waves adds per tick to this pawn in deep water at the map's current sea temperature.
    public static float WaterChillPerTick(Pawn pawn)
    {
        if (!SwimLimitsOn) return 0f;
        float water = WaterTemperature(pawn.Map), limit = WaterColdLimit(pawn);
        return water < ChillsBelow && water < limit ? ChillPer60PerDegree * (limit - water) / 60f : 0f;
    }
}

// Why the zone tool refuses a cell (ticket 24). Carries no Waves type, so callers outside the bridge can switch on it.
public enum FishingWaterRefusal
{
    None,
    Land,
    Shallow,
    Frozen,
    Toxic,
    Marsh,
    Cave,
    NotSwimmable,
}
