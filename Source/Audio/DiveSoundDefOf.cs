using RimWorld;
using Verse;

namespace Spearfishing;

// The swim and dive sounds (ticket 30), all retuned Core clips in Defs/SoundDefs/Sounds_Spearfishing.xml.
[DefOf]
public static class DiveSoundDefOf
{
    public static SoundDef Spearfishing_SwimStroke;
    public static SoundDef Spearfishing_DiveDown;
    public static SoundDef Spearfishing_Surface;
    public static SoundDef Spearfishing_Bubbles;

    static DiveSoundDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(DiveSoundDefOf));
}
