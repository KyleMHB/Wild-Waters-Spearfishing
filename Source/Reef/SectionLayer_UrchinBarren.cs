using UnityEngine;
using Verse;

namespace Spearfishing;

// An urchin barren (threat events ticket 02) drawn over the cells it grazed, in place of their reef or kelp: the approved
// drained look of the floor each cell keeps, with small dark urchins (art/urchin-barren/APPROVAL.md, candidate B). One layer
// per kept floor, drawn like the floor overlays (same queue, edge fade and deep strength). Barren kelp is still, so no sway.
// Culled cells waiting to regrow draw nothing, as bare sea floor.
public abstract class SectionLayer_UrchinBarren : SectionLayer_FloorOverlay
{
    protected SectionLayer_UrchinBarren(Section section) : base(section)
    {
    }

    protected override bool AnyOnMap(MapComponent_FishStock floor) => floor.BarrenCellCount > 0;

    protected override bool Shows(MapComponent_FishStock floor, IntVec3 cell) => floor.MarkAt(cell) == Mark && floor.IsBarren(cell);
}

public class SectionLayer_UrchinBarrenReef : SectionLayer_UrchinBarren
{
    private static Material material;

    public SectionLayer_UrchinBarrenReef(Section section) : base(section)
    {
    }

    protected override FloorMark Mark => FloorMark.Reef;
    protected override Material Material => material ??= MakeMaterial("Spearfishing/Terrain/UrchinBarrenReef");
}

public class SectionLayer_UrchinBarrenKelpBrown : SectionLayer_UrchinBarren
{
    private static Material material;

    public SectionLayer_UrchinBarrenKelpBrown(Section section) : base(section)
    {
    }

    protected override FloorMark Mark => FloorMark.KelpBrown;
    protected override Material Material => material ??= MakeMaterial("Spearfishing/Terrain/UrchinBarrenKelpBrown");
}

public class SectionLayer_UrchinBarrenKelpOlive : SectionLayer_UrchinBarren
{
    private static Material material;

    public SectionLayer_UrchinBarrenKelpOlive(Section section) : base(section)
    {
    }

    protected override FloorMark Mark => FloorMark.KelpOlive;
    protected override Material Material => material ??= MakeMaterial("Spearfishing/Terrain/UrchinBarrenKelpOlive");
}
