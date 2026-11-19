using Verse;

namespace Spearfishing;

// What one kind of threat event does (spec "Threat events", ADR 0015, ADR 0017). The framework (ticket 01) decides when an
// event may fire, keeps the registry and ends outbreaks when a switch goes off; each kind says where it can strike and what
// starting and ending an outbreak do to the water. Tickets 02 (urchins) and 03 (invasive predators) fill in Start and End in
// their own subclass and keep any per-outbreak state in their own saved data (the reef grid, the fish stock model).
public abstract class ThreatEvent
{
    public abstract ThreatKind Kind { get; }

    // The kind's own switch in the mod settings.
    public abstract bool SwitchOn { get; }

    // Whether the kind may be active at all: its switch and fish stock management both on (ADR 0015, revised).
    public bool Allowed => FishStockManagement.On && SwitchOn;

    // A cell in water this kind can strike on the map, or false when there is none.
    public abstract bool TryFindTarget(Map map, out IntVec3 cell);

    // An outbreak is starting in the water at outbreak.Cell; it is not yet in the registry. Return false to decline it.
    public virtual bool Start(Map map, Outbreak outbreak) => true;

    // An outbreak has ended (culled out, or a switch went off) and has left the registry: undo its effect on the water. Runs
    // once per outbreak, never for a kind with none active.
    public virtual void End(Map map, Outbreak outbreak)
    {
    }

    // The letter's named arguments: WATER ("sea", "lake" or "river") and whatever the kind's letter text adds.
    public virtual NamedArgument[] LetterArgs(Map map, Outbreak outbreak) => new[] { FryRelease.WaterLabel(map, outbreak.Cell).Named("WATER") };
}
