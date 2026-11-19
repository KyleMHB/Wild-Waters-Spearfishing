using RimWorld;
using Verse;

namespace Spearfishing;

// The storyteller incident of one threat kind (spec stories 1-6). The def holds the timing (Misc category, earliestDay 15,
// minRefireDays, baseChance; see Defs/Threats_Spearfishing.xml); this adds the switches, the target and the one-active-outbreak
// rule, starts the outbreak and sends the letter naming the water.
public abstract class IncidentWorker_Outbreak : IncidentWorker
{
    protected abstract ThreatKind Kind { get; }

    protected override bool CanFireNowSub(IncidentParms parms) => parms.target is Map map && ThreatEvents.CanStart(Kind, map, out _);

    protected override bool TryExecuteWorker(IncidentParms parms)
    {
        if (parms.target is not Map map || !ThreatEvents.CanStart(Kind, map, out IntVec3 cell)) return false;
        Outbreak outbreak = ThreatEvents.Of(map).Start(Kind, cell);
        if (outbreak == null) return false;
        SendStandardLetter(parms, new LookTargets(cell, map), ThreatEvents.For(Kind).LetterArgs(map, outbreak));
        return true;
    }
}

public class IncidentWorker_Urchins : IncidentWorker_Outbreak
{
    protected override ThreatKind Kind => ThreatKind.Urchins;
}

public class IncidentWorker_InvasivePredators : IncidentWorker_Outbreak
{
    protected override ThreatKind Kind => ThreatKind.InvasivePredators;
}
