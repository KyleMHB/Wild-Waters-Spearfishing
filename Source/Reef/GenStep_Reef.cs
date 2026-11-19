using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.Noise;

namespace Spearfishing;

// Places reef and kelp patches in the coastal ocean of a newly generated map, in the map's reef grid (ADR 0008); terrain stays
// vanilla ocean. It runs only during map generation, so maps from saves made before the mod start with an empty grid and fish over
// bare sea floor.
// Patches come from noise over the ocean near land: high noise becomes reef, at the depth of the ocean above it. The threshold rises with
// distance from land, so reef is common close in, thins out further out and stops at maxShoreDistance, leaving good and poor
// stretches of coast. Reef is placed the same way at every temperature. Kelp (ticket 38) comes from a second noise over the
// same band, on cells that are not reef. Its look follows the map tile's average yearly temperature: brown below
// oliveKelpFrom, olive up to noKelpFrom, and no kelp from there up. The tuning values are set in
// Defs/MapGeneration/GenStep_Reef.xml.
public class GenStep_Reef : GenStep
{
    // Ocean cells this close to land, counted in steps across water, can become reef. Within minShoreDistance the sea
    // floor stays bare, so reef does not crowd the beach.
    public int minShoreDistance = 2;
    public int maxShoreDistance = 40;
    // Noise above the threshold is reef: nearThreshold next to land, rising to farThreshold at maxShoreDistance.
    public float nearThreshold = 0.15f;
    public float farThreshold = 0.45f;
    // About one patch per 1/frequency cells across.
    public float noiseFrequency = 0.06f;
    // Kelp patches: the same band and frequency as reef, with their own noise thresholds.
    public float kelpNearThreshold = 0.15f;
    public float kelpFarThreshold = 0.45f;
    // Kelp keeps out of the knee-deep shallows: none within kelpMinShoreDistance of land, and over the next kelpFadeCells its
    // threshold falls back from kelpFadeRaise to normal, so patches thin out towards the beach instead of stopping on a line.
    public int kelpMinShoreDistance = 6;
    public int kelpFadeCells = 3;
    public float kelpFadeRaise = 0.3f;
    // Average yearly temperatures, in degrees C, where kelp turns from brown to olive and where it stops.
    public float oliveKelpFrom = 15f;
    public float noKelpFrom = 22f;

    public static GenStep_Reef Settings => (GenStep_Reef)ReefDefOf.Spearfishing_Reef.genStep;

    // The kelp a map with this average yearly temperature gets: brown, olive, or none (Bare).
    public FloorMark KelpFor(float temperature) =>
        temperature >= noKelpFrom ? FloorMark.Bare : temperature >= oliveKelpFrom ? FloorMark.KelpOlive : FloorMark.KelpBrown;

    public override int SeedPart => 482915307;

    public override void Generate(Map map, GenStepParams parms)
    {
        TerrainDef shallow = TerrainDefOf.WaterOceanShallow, deep = TerrainDefOf.WaterOceanDeep;
        CellIndices indices = map.cellIndices;
        TerrainGrid terrain = map.terrainGrid;
        int width = map.Size.x, height = map.Size.z, count = indices.NumGridCells;

        // Distance to land across ocean, by breadth-first search from ocean cells that touch land. -1: not ocean, or not
        // reached within maxShoreDistance. Only vanilla ocean is reef-able; other mods' water is left alone.
        var distance = new int[count];
        var queue = new Queue<int>();
        bool any = false;
        for (int i = 0; i < count; i++)
        {
            TerrainDef def = terrain.TerrainAt(i);
            distance[i] = -1;
            if (def != shallow && def != deep) continue;
            any = true;
            IntVec3 c = indices.IndexToCell(i);
            if (TouchesLand(c, width, height, indices, terrain, shallow, deep))
            {
                distance[i] = 1;
                queue.Enqueue(i);
            }
        }
        if (!any) return;

        while (queue.Count > 0)
        {
            int i = queue.Dequeue();
            int next = distance[i] + 1;
            if (next > maxShoreDistance) continue;
            IntVec3 c = indices.IndexToCell(i);
            for (int d = 0; d < 4; d++)
            {
                IntVec3 n = c + GenAdj.CardinalDirections[d];
                if (n.x < 0 || n.z < 0 || n.x >= width || n.z >= height) continue;
                int ni = indices.CellToIndex(n);
                if (distance[ni] != -1) continue;
                TerrainDef def = terrain.TerrainAt(ni);
                if (def != shallow && def != deep) continue;
                distance[ni] = next;
                queue.Enqueue(ni);
            }
        }

        var noise = new Perlin(noiseFrequency, 2.0, 0.5, 3, Rand.Range(0, int.MaxValue), QualityMode.Medium);
        float span = UnityEngine.Mathf.Max(1, maxShoreDistance - minShoreDistance);
        // Seeded after the reef noise, so reef lies exactly where it did before kelp.
        var kelpNoise = new Perlin(noiseFrequency, 2.0, 0.5, 3, Rand.Range(0, int.MaxValue), QualityMode.Medium);
        FloorMark kelp = KelpFor(Find.WorldGrid[map.Tile].temperature);
        var floor = MapComponent_FishStock.Of(map);
        for (int i = 0; i < count; i++)
        {
            int dist = distance[i];
            if (dist < minShoreDistance) continue;
            float along = (dist - minShoreDistance) / span;
            IntVec3 c = indices.IndexToCell(i);
            if (noise.GetValue(c.x, 0.0, c.z) > UnityEngine.Mathf.Lerp(nearThreshold, farThreshold, along))
                floor.SetMark(c, FloorMark.Reef);
            else if (kelp != FloorMark.Bare && dist >= kelpMinShoreDistance && kelpNoise.GetValue(c.x, 0.0, c.z) > KelpThreshold(dist, along))
                floor.SetMark(c, kelp);
        }
    }

    private float KelpThreshold(int dist, float along)
    {
        float fade = kelpFadeCells > 0 ? 1f - UnityEngine.Mathf.Clamp01((dist - kelpMinShoreDistance) / (float)kelpFadeCells) : 0f;
        return UnityEngine.Mathf.Lerp(kelpNearThreshold, kelpFarThreshold, along) + kelpFadeRaise * fade;
    }

    // Land is any in-bounds cell that is not ocean; the map edge is open sea, not land.
    private static bool TouchesLand(IntVec3 c, int width, int height, CellIndices indices, TerrainGrid terrain, TerrainDef shallow, TerrainDef deep)
    {
        for (int d = 0; d < 4; d++)
        {
            IntVec3 n = c + GenAdj.CardinalDirections[d];
            if (n.x < 0 || n.z < 0 || n.x >= width || n.z >= height) continue;
            TerrainDef def = terrain.TerrainAt(indices.CellToIndex(n));
            if (def != shallow && def != deep) return true;
        }
        return false;
    }
}
