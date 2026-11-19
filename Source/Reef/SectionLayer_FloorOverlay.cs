using RimWorld;
using UnityEngine;
using Verse;

namespace Spearfishing;

// Draws one mark of the reef grid (reef, or one look of kelp) as a sea-floor overlay. Waves covers open sea with an opaque water
// body from about five cells off the beach, which hides any terrain texture under it, so the art is a translucent tiling overlay
// drawn at Waves' sea-life render queue: over the water body, under the foam, as the sea life is. Without Waves' queue (Waves
// changed) it draws at the shader's own queue instead.
// Vertex alpha fades the overlay across the cell border around each patch, and deep cells are drawn fainter than shallow.
// Marks come from the map's reef grid (ADR 0008), at the depth of the ocean terrain over them.
// RimWorld creates one of each subclass per map section by reflection; it rebuilds when terrain changes, and the reef grid marks
// the same terrain flag dirty when it changes.
public abstract class SectionLayer_FloorOverlay : SectionLayer
{
    // Cells covered by one repeat of the overlay texture.
    private const float TileCells = 8f;
    private const float ShallowStrength = 1f, DeepStrength = 0.7f;

    protected SectionLayer_FloorOverlay(Section section) : base(section)
    {
        relevantChangeTypes = (ulong)MapMeshFlagDefOf.Terrain;
    }

    protected abstract FloorMark Mark { get; }

    protected abstract Material Material { get; }

    // Whether the map holds any of this mark at all, so most sections return at once.
    protected abstract bool AnyOnMap(MapComponent_FishStock floor);

    // Whether this layer draws a cell (it is in bounds): its mark where it grows now, so an urchin barren's cells draw the
    // barren look instead (SectionLayer_UrchinBarren).
    protected virtual bool Shows(MapComponent_FishStock floor, IntVec3 cell) => floor.LiveMarkAt(cell) == Mark;

    protected static Material MakeMaterial(string texturePath)
    {
        var texture = ContentFinder<Texture2D>.Get(texturePath);
        texture.wrapMode = TextureWrapMode.Repeat;
        // The same shader as Waves' water body, so day and night light the floor as they light the water over it.
        var material = new Material(ShaderDatabase.TransparentPostLight) { mainTexture = texture };
        if (WavesBridge.UnderwaterRenderQueue is { } queue) material.renderQueue = queue;
        return material;
    }

    public override void Regenerate()
    {
        ClearSubMeshes(MeshParts.All);
        var rect = section.CellRect;
        var grid = Map.terrainGrid;
        var floor = MapComponent_FishStock.Of(Map);
        if (floor == null || !AnyOnMap(floor)) return;
        bool any = false;
        // A patch cell just outside the section still fades into its border cells.
        foreach (var c in rect.ExpandedBy(1).ClipInsideMap(Map))
            if (Shows(floor, c)) { any = true; break; }
        if (!any) return;

        // Corner (x, z) is shared by the four cells around it; its alpha is their mean strength.
        int width = rect.Width + 1, height = rect.Height + 1;
        var alpha = new byte[width * height];
        for (int j = 0; j < height; j++)
            for (int i = 0; i < width; i++)
            {
                int x = rect.minX + i, z = rect.minZ + j;
                float sum = Strength(x - 1, z - 1) + Strength(x, z - 1) + Strength(x - 1, z) + Strength(x, z);
                alpha[j * width + i] = (byte)Mathf.RoundToInt(sum / 4f * 255f);
            }

        var mesh = GetSubMesh(Material);
        float altitude = AltitudeLayer.TerrainScatter.AltitudeFor() - 0.001f;
        var index = new int[width * height];
        for (int k = 0; k < index.Length; k++) index[k] = -1;
        for (int j = 0; j < height - 1; j++)
            for (int i = 0; i < width - 1; i++)
            {
                int a = j * width + i, b = a + 1, c = a + width, d = c + 1;
                if (alpha[a] == 0 && alpha[b] == 0 && alpha[c] == 0 && alpha[d] == 0) continue;
                int va = Vertex(a), vb = Vertex(b), vc = Vertex(c), vd = Vertex(d);
                mesh.tris.Add(va); mesh.tris.Add(vc); mesh.tris.Add(vd);
                mesh.tris.Add(va); mesh.tris.Add(vd); mesh.tris.Add(vb);
            }
        mesh.FinalizeMesh(MeshParts.All);

        int Vertex(int at)
        {
            if (index[at] >= 0) return index[at];
            int x = rect.minX + at % width, z = rect.minZ + at / width;
            index[at] = mesh.verts.Count;
            mesh.verts.Add(new Vector3(x, altitude, z));
            mesh.colors.Add(new Color32(255, 255, 255, alpha[at]));
            mesh.uvs.Add(new Vector3(x / TileCells, z / TileCells, 0f));
            return index[at];
        }

        // A mark under a bridge, floor or landfill is hidden: MarkAt needs the cell's top terrain to be ocean.
        float Strength(int x, int z)
        {
            var cell = new IntVec3(x, 0, z);
            if (!cell.InBounds(Map) || !Shows(floor, cell)) return 0f;
            return grid.TerrainAt(cell) == TerrainDefOf.WaterOceanDeep ? DeepStrength : ShallowStrength;
        }
    }
}

// Reef, in the approved rock-shadow art (art/reef/APPROVAL.md).
public class SectionLayer_Reef : SectionLayer_FloorOverlay
{
    private static Material material;

    public SectionLayer_Reef(Section section) : base(section)
    {
    }

    protected override FloorMark Mark => FloorMark.Reef;
    protected override Material Material => material ??= MakeMaterial("Spearfishing/Terrain/ReefOverlay");
    protected override bool AnyOnMap(MapComponent_FishStock floor) => floor.ReefCellCount > 0;
}

// Kelp, swaying: drawn each frame with KelpSway's copy of its mesh for that moment of the swell.
// Waves' shore veil (WavesBridge.SeaArtRenderQueue) sweeps opaque water-coloured bands over the first 21 or so cells off the
// beach, which wiped the kelp out entirely as each swell passed. A faint second copy drawn just over the veil, where the dive
// shadow is, keeps the kelp showing dimly through a band, as if further below the swell.
public abstract class SectionLayer_Kelp : SectionLayer_FloorOverlay
{
    private const float ThroughSwell = 0.45f;
    private static readonly System.Collections.Generic.Dictionary<Material, Material> overVeil = new();
    private Mesh[] frames;

    protected SectionLayer_Kelp(Section section) : base(section)
    {
    }

    public override void Regenerate()
    {
        base.Regenerate();
        KelpSway.Release(frames);
        frames = null;
        // The overlay builds at most one submesh, for its one material.
        if (subMeshes.Count > 0 && subMeshes[0].finalized) frames = KelpSway.BuildFrames(subMeshes[0], Map);
    }

    public override void DrawLayer()
    {
        if (!Visible || frames == null) return;
        var subMesh = subMeshes[0];
        if (!subMesh.finalized || subMesh.disabled) return;
        var mesh = frames[KelpSway.Frame];
        Graphics.DrawMesh(mesh, Matrix4x4.identity, subMesh.material, subMesh.renderLayer);
        if (OverVeil(subMesh.material) is { } faint) Graphics.DrawMesh(mesh, Matrix4x4.identity, faint, subMesh.renderLayer);
    }

    // The faint copy of a kelp material over the veil, made once; null without the queue over the veil.
    private static Material OverVeil(Material under)
    {
        if (overVeil.TryGetValue(under, out var faint)) return faint;
        faint = WavesBridge.SeaArtRenderQueue is { } queue && queue != under.renderQueue
            ? new Material(under) { renderQueue = queue, color = new Color(1f, 1f, 1f, ThroughSwell) }
            : null;
        overVeil[under] = faint;
        return faint;
    }
}

// Kelp on cold coasts, brown (art/kelp/APPROVAL.md, B2).
public class SectionLayer_KelpBrown : SectionLayer_Kelp
{
    private static Material material;

    public SectionLayer_KelpBrown(Section section) : base(section)
    {
    }

    protected override FloorMark Mark => FloorMark.KelpBrown;
    protected override Material Material => material ??= MakeMaterial("Spearfishing/Terrain/KelpOverlayBrown");
    protected override bool AnyOnMap(MapComponent_FishStock floor) => floor.KelpCellCount > 0;
}

// Kelp on mild coasts, olive (art/kelp/APPROVAL.md, B).
public class SectionLayer_KelpOlive : SectionLayer_Kelp
{
    private static Material material;

    public SectionLayer_KelpOlive(Section section) : base(section)
    {
    }

    protected override FloorMark Mark => FloorMark.KelpOlive;
    protected override Material Material => material ??= MakeMaterial("Spearfishing/Terrain/KelpOverlayOlive");
    protected override bool AnyOnMap(MapComponent_FishStock floor) => floor.KelpCellCount > 0;
}
