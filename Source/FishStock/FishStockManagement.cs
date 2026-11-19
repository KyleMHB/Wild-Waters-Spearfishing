namespace Spearfishing;

// Fish stock management (ADR 0015): one mod setting, on by default, that switches how the water regrows and what the zone's
// inspect panel adds. Flipping it never touches a body's stock. Ticket 07's fish-down limit reads On for its stop rule.
public static class FishStockManagement
{
    public static bool On => SpearfishingMod.Settings == null || SpearfishingMod.Settings.fishStockManagement;

    public static RegrowthRule Rule => On ? RegrowthRule.Logistic : RegrowthRule.Flat;
}
