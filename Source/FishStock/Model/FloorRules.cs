namespace Spearfishing;

// The sea floor's part in fishing (ADR 0013): reef and kelp are where fish are densest, so a dive over them succeeds more
// often and divers head for them. They never change capacity or stock; with fish stock management on they speed their
// water's regrowth (ADR 0016, FishStockModel). Plain C#, tested with the model.
public static class FloorRules
{
    // The catch chance's floor factor over reef and kelp (both kelp looks alike); bare floor is 1. A target for testing,
    // tuned so reef and kelp read clearly better than bare floor.
    public const float DenseFloorFactor = 1.5f;

    public const float BareFloorFactor = 1f;

    public static float FloorFactor(FloorMark mark) => mark == FloorMark.Bare ? BareFloorFactor : DenseFloorFactor;
}
