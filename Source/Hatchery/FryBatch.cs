using Verse;

namespace Spearfishing;

// A full batch of fry in its pail (fish recovery ticket 04). It keeps its hatchery and that hatchery's choice of water, so
// choosing other water moves a pail still waiting; it also keeps its own copy of the water, so a pail outlives its hatchery
// and a dropped pail is picked up again.
public class FryBatch : ThingWithComps
{
    private int fish;
    private IntVec3 targetCell = IntVec3.Invalid;
    private Thing hatchery;

    public int Fish => fish;

    public void Init(int fish, Thing hatchery, IntVec3 target)
    {
        this.fish = fish;
        this.hatchery = hatchery;
        targetCell = target;
    }

    // The water the fry go to: the hatchery's current choice while it stands, else the pail's own, re-resolved like the
    // hatchery's if that cell is no longer fishing water.
    public IntVec3 Target
    {
        get
        {
            CompHatchery source = hatchery is { Destroyed: false } ? hatchery.TryGetComp<CompHatchery>() : null;
            IntVec3 now = source?.TargetCell ?? FryRelease.Resolve(MapHeld, targetCell, PositionHeld);
            if (now.IsValid) targetCell = now;
            return now;
        }
    }

    public override string GetInspectString()
    {
        string text = base.GetInspectString();
        Map map = MapHeld;
        IntVec3 target = map == null ? IntVec3.Invalid : Target;
        string line = target.IsValid
            ? "Spearfishing_FryPailInspect".Translate(fish, FryRelease.WaterLabel(map, target))
            : "Spearfishing_FryPailNoWater".Translate(fish);
        return text.NullOrEmpty() ? line : text + "\n" + line;
    }

    public override void ExposeData()
    {
        base.ExposeData();
        if (Scribe.mode == LoadSaveMode.Saving && hatchery is { Destroyed: true }) hatchery = null;
        Scribe_Values.Look(ref fish, "fish");
        Scribe_Values.Look(ref targetCell, "targetCell", IntVec3.Invalid);
        Scribe_References.Look(ref hatchery, "hatchery");
    }
}
