namespace Spearfishing;

// What the reef grid holds for one cell (ADR 0008). Kelp is one floor with two looks (ticket 38): the same fish, drawn brown on
// cold coasts and olive on mild ones. The look is chosen once, when the map is made, and kept in the same byte, so it needs no
// other saved field. The values are saved: never renumber them. Saves from before kelp hold only 0 and 1.
public enum FloorMark : byte
{
    Bare = 0,
    Reef = 1,
    KelpBrown = 2,
    KelpOlive = 3,
}

public static class FloorMarkExtensions
{
    public static bool IsKelp(this FloorMark mark) => mark == FloorMark.KelpBrown || mark == FloorMark.KelpOlive;
}
