using Verse;

namespace Spearfishing;

// Urchins (spec stories 7-16): sea only, on reef or kelp. Start turns a patch around outbreak.Cell into an urchin barren
// (ticket 02); culling the last barren cell ends the outbreak (MapComponent_FishStock.CullUrchins).
public sealed class UrchinThreat : ThreatEvent
{
    public override ThreatKind Kind => ThreatKind.Urchins;

    public override bool SwitchOn => SpearfishingMod.Settings == null || SpearfishingMod.Settings.urchinEvents;

    // A random reef or kelp cell that shows and grows (marks hidden under landfill or a bridge don't count, nor do cells still
    // grazed by an earlier outbreak). Reef and kelp lie only on ocean terrain, so the cell is always in the sea.
    public override bool TryFindTarget(Map map, out IntVec3 cell)
    {
        cell = IntVec3.Invalid;
        MapComponent_FishStock floor = MapComponent_FishStock.Of(map);
        if (floor == null || floor.ReefCellCount + floor.KelpCellCount == 0) return false;
        int seen = 0;
        int count = map.cellIndices.NumGridCells;
        // One pass, picking uniformly among the cells that qualify.
        for (int i = 0; i < count; i++)
        {
            if (floor.LiveMarkAt(i) == FloorMark.Bare || floor.BodyAt(map.cellIndices.IndexToCell(i)) < 0) continue;
            seen++;
            if (Rand.Range(0, seen) == 0) cell = map.cellIndices.IndexToCell(i);
        }
        return seen > 0;
    }

    // About 10 to 20 connected reef or kelp cells around the target turn barren; declined if none would.
    public override bool Start(Map map, Outbreak outbreak) => MapComponent_FishStock.Of(map)?.StartBarren(outbreak.Cell) > 0;

    // Switched off (urchins or fish stock management), every barren and recovering cell gets its reef or kelp back at once.
    // Culled out, nothing is barren any more and the culled cells keep recovering over their own 5 days.
    public override void End(Map map, Outbreak outbreak) => MapComponent_FishStock.Of(map)?.EndBarren(andRecovering: !Allowed);
}
