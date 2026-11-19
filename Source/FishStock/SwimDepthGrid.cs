using System.Collections.Generic;
using RimWorld;
using Verse;

namespace Spearfishing;

// How deep each fishing water cell reads, from 0 (shallowest) to 1 (deepest), for the visuals (ticket 22) and the fish
// (ticket 23). It is a look, not a sounding: the distance to the nearest land blended with the terrain, so a deep-ocean
// cell far out is deepest, shallow ocean stays in the shallow half, and the chest-deep river is the shallow end.
// Built from the terrain alone, on the first question after a terrain change, never per frame, and never saved.
public sealed class SwimDepthGrid
{
    // Cells of open water over which the depth ramps from the shore value to the terrain's deepest.
    private const float RampCells = 8f;

    private readonly Map map;
    private float[] depth;
    private bool dirty = true;

    public SwimDepthGrid(Map map) => this.map = map;

    // Times the grid was built, for the developer tests.
    public static int Builds { get; private set; }

    public void Notify_TerrainChanged() => dirty = true;

    // 0 to 1 on fishing water, below zero elsewhere (land, ice, shallow fresh water, out of bounds).
    public float DepthAt(IntVec3 cell)
    {
        if (!cell.InBounds(map)) return -1f;
        if (dirty) Build();
        return depth[map.cellIndices.CellToIndex(cell)];
    }

    // Distance in steps (8-connected) from every cell that is not fishing water, then the terrain's blend. The map edge is
    // not shore, so open sea running off the map stays deep.
    private void Build()
    {
        dirty = false;
        Builds++;
        CellIndices indices = map.cellIndices;
        TerrainGrid terrain = map.terrainGrid;
        int count = indices.NumGridCells, sizeX = map.Size.x, sizeZ = map.Size.z;
        depth ??= new float[count];
        var steps = new int[count];
        var queue = new Queue<int>();
        for (int i = 0; i < count; i++)
        {
            if (WavesBridge.IsFishingWater(terrain.TerrainAt(i))) steps[i] = int.MaxValue;
            else
            {
                steps[i] = 0;
                queue.Enqueue(i);
            }
        }
        while (queue.Count > 0)
        {
            int i = queue.Dequeue();
            int x = i % sizeX, z = i / sizeX, next = steps[i] + 1;
            for (int dz = -1; dz <= 1; dz++)
            for (int dx = -1; dx <= 1; dx++)
            {
                int nx = x + dx, nz = z + dz;
                if ((dx == 0 && dz == 0) || nx < 0 || nz < 0 || nx >= sizeX || nz >= sizeZ) continue;
                int n = nz * sizeX + nx;
                if (steps[n] <= next) continue;
                steps[n] = next;
                queue.Enqueue(n);
            }
        }
        for (int i = 0; i < count; i++)
        {
            TerrainDef def = terrain.TerrainAt(i);
            if (steps[i] == 0) depth[i] = -1f;
            else
            {
                // A map with no land at all leaves every step at MaxValue: all open water.
                float ramp = steps[i] == int.MaxValue ? 1f : UnityEngine.Mathf.Clamp01((steps[i] - 1) / RampCells);
                depth[i] = Blend(def, ramp);
            }
        }
    }

    private static float Blend(TerrainDef def, float ramp)
    {
        if (def == TerrainDefOf.WaterMovingChestDeep) return 0f;
        if (def == TerrainDefOf.WaterOceanShallow) return UnityEngine.Mathf.Lerp(0f, 0.5f, ramp);
        // Deep ocean and the deep lake.
        return UnityEngine.Mathf.Lerp(0.3f, 1f, ramp);
    }
}
