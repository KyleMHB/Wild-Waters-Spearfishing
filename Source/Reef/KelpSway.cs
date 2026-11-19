using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace Spearfishing;

// Sways the kelp floor in the swell by warping its texture coordinates over the static section mesh; the vertices, and so the
// faded patch edges, stay put. Each kelp section keeps Frames copies of its mesh over one swell, and draws the copy for the
// moment: on 1.7 a material's texture offset changed after its first draw never reached the screen (checked in game,
// 2026-11-18), so nothing is changed once drawn, as the shark keeps one pre-bent mesh per sway frame.
// - The surge runs along the art's current (art/kelp/kelp_art.py, CURRENT -28 degrees in image space), with a quick push and a
//   slow drain rather than an even swing, and a smaller drift across it.
// - It travels: each vertex is a little later in the swell the further it lies along the current, so a swell rolls through
//   the forest instead of the whole floor sliding at once.
// - Deep kelp moves less than shallow.
// Real time, as Waves' sea life and the dive shadows move, frozen while the game is paused.
internal static class KelpSway
{
    private const int Frames = 40;
    private const float Period = 5f;
    // One texture repeat is 512 px over 8 cells; the surge reaches about 12 px (a fifth of a cell) either way, the drift 4 px.
    private const float TexturePx = 512f, SurgePx = 12f, DriftPx = 4f, DeepScale = 0.45f;
    // Cells from one swell crest to the next along the current, and the spread of the drift across it.
    private const float Wavelength = 14f, CrossWavelength = 23f;
    // CURRENT in UV and map space alike (v and z up, so the image's y flips).
    private static readonly Vector2 Along = new(Mathf.Cos(28f * Mathf.Deg2Rad), Mathf.Sin(28f * Mathf.Deg2Rad));
    private static readonly Vector2 Across = new(-Along.y, Along.x);

    private static float clock;
    private static int lastFrame = -1, lastTick = -1;

    // The frame to draw this frame.
    internal static int Frame { get; private set; }

    // Called once per map per frame (Map.MapUpdate postfix, before the map draws); moves the swell on for the map on screen.
    internal static void MapUpdate(Map map)
    {
        if (lastFrame == Time.frameCount || Find.CurrentMap != map || !WorldRendererUtility.DrawingMap) return;
        lastFrame = Time.frameCount;
        // Ticks run by hand while paused (developer tools, the test runner) count as running.
        int tick = Find.TickManager.TicksGame;
        if (!Find.TickManager.Paused || tick != lastTick) clock = (clock + Mathf.Min(Time.unscaledDeltaTime, 0.1f)) % Period;
        lastTick = tick;
        Frame = Mathf.Min((int)(clock / Period * Frames), Frames - 1);
    }

    // One copy of a finalized kelp submesh per frame of the swell, sharing its vertices, triangles and colours.
    internal static Mesh[] BuildFrames(LayerSubMesh subMesh, Map map)
    {
        var verts = subMesh.verts;
        var depthScale = new float[verts.Count];
        for (int i = 0; i < verts.Count; i++) depthScale[i] = Mathf.Lerp(1f, DeepScale, DeepShare(map, verts[i]));

        var frames = new Mesh[Frames];
        var uvs = new Vector3[verts.Count];
        for (int f = 0; f < Frames; f++)
        {
            float phase = 2f * Mathf.PI * f / Frames;
            for (int i = 0; i < verts.Count; i++)
            {
                var p = new Vector2(verts[i].x, verts[i].z);
                float along = Vector2.Dot(p, Along) / Wavelength, across = Vector2.Dot(p, Across) / CrossWavelength;
                float surge = Surge(phase - 2f * Mathf.PI * along);
                float drift = Mathf.Sin(phase - 2f * Mathf.PI * (along * 0.5f + across) + 2f);
                Vector2 px = (Along * (surge * SurgePx) + Across * (drift * DriftPx)) * depthScale[i];
                uvs[i] = subMesh.uvs[i] + new Vector3(px.x / TexturePx, px.y / TexturePx, 0f);
            }
            var mesh = new Mesh { name = "KelpSway" }; // not translated
            mesh.SetVertices(verts);
            mesh.SetTriangles(subMesh.tris, 0);
            mesh.SetColors(subMesh.colors);
            mesh.SetUVs(0, new System.Collections.Generic.List<Vector3>(uvs));
            frames[f] = mesh;
        }
        return frames;
    }

    internal static void Release(Mesh[] frames)
    {
        if (frames == null) return;
        foreach (var mesh in frames) Object.Destroy(mesh);
    }

    // A swell's surge: quicker one way than back, from -1 to 1.
    private static float Surge(float a) => (Mathf.Sin(a) + 0.35f * Mathf.Sin(2f * a)) / 1.2f;

    // The share of the four cells around a mesh corner that are deep water.
    private static float DeepShare(Map map, Vector3 corner)
    {
        int x = Mathf.RoundToInt(corner.x), z = Mathf.RoundToInt(corner.z), deep = 0, any = 0;
        for (int dz = -1; dz <= 0; dz++)
            for (int dx = -1; dx <= 0; dx++)
            {
                var cell = new IntVec3(x + dx, 0, z + dz);
                if (!cell.InBounds(map)) continue;
                any++;
                if (map.terrainGrid.TerrainAt(cell) == TerrainDefOf.WaterOceanDeep) deep++;
            }
        return any == 0 ? 0f : (float)deep / any;
    }
}
