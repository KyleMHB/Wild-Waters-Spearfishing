using HarmonyLib;
using UnityEngine;
using Verse;

namespace Spearfishing;

// Hides a diver's body, apparel, spear and shadow while under the water, for every draw phase so the pawn is skipped
// consistently. The name label and the dive's progress bar are drawn elsewhere and stay, so the player can still find them.
[HarmonyPatch(typeof(Pawn), nameof(Pawn.DynamicDrawPhaseAt))]
internal static class Patch_Pawn_DynamicDrawPhaseAt
{
    private static bool Prefix(Pawn __instance) => !DiveVisuals.Hides(__instance);
}

// Draws a pawn floating at the surface face down (ticket 18): the back of the head whichever way they face, with headgear,
// and no body. For a swimmer the game already hides the body and sinks the head, but it also drops headgear and clothes,
// which would hide the glass mask's strap and the snorkel; those flags come back here, NoBody stays. Body apparel hangs
// under the body node, so it stays hidden with the body. GetDrawParms feeds both the parallel pre-draw and the draw, so
// the two agree. Portraits, the colonist bar and statues also come through here and are left alone. Any other pawn, and a
// diver not swimming (ashore, entering the water, wading), is not touched at all.
// The back of the head is the north view, but a pawn travelling east drawn facing north reads as sliding sideways (the
// user's report on 2026-11-16), so the whole draw is turned about the pawn's centre to the way it travels: the north view
// turned by the heading, with north at 0 and clockwise like Rot4's angles.
[HarmonyPatch(typeof(PawnRenderer), "GetDrawParms")]
internal static class Patch_PawnRenderer_GetDrawParms
{
    private const PawnRenderFlags OffMap = PawnRenderFlags.Portrait | PawnRenderFlags.Cache | PawnRenderFlags.Statue;

    private static void Postfix(ref PawnDrawParms __result)
    {
        if (DiveVisuals.LookOf(__result.pawn) != DiveVisuals.Look.FaceDown || (__result.flags & OffMap) != 0) return;
        __result.facing = Rot4.North;
        __result.matrix *= Matrix4x4.Rotate(Quaternion.AngleAxis(DiveVisuals.FaceDownHeadingOf(__result.pawn), Vector3.up));
        __result.flags |= PawnRenderFlags.Clothes | PawnRenderFlags.Headgear | PawnRenderFlags.NoBody;
        DiveVisuals.Notify_FaceDownDraw();
    }
}

// A swimmer on a sea trip holds the spear at their right side, half in the water (ticket 35). The game draws a carried
// weapon from the render tree's carried node with the body's position and the 4-way facing only: the face-down draw's
// turned matrix never reaches it, so face down (forced north) it was one fixed carry pose just south of the body's centre,
// where the sunk head is drawn, and face up the 4-way carry pose over the sunk head. Only the carry pose is replaced:
// aiming, a carried thing and the worn apparel extras are drawn as the game draws them.
[HarmonyPatch(typeof(PawnRenderUtility), nameof(PawnRenderUtility.DrawCarriedWeapon))]
internal static class Patch_PawnRenderUtility_DrawCarriedWeapon
{
    private static bool Prefix(ThingWithComps weapon, Vector3 drawPos) =>
        weapon?.ParentHolder is not Pawn_EquipmentTracker equipment || !DiveVisuals.TryDrawSwimSpear(equipment.pawn, weapon, drawPos);
}

// The glass mask and snorkel stay on a swimmer's head (ticket 34). For a swimming pawn the game clears the Headgear and
// Clothes flags (PawnRenderer.ParallelGetPreRenderResults), so outside the face-down look, which brings them back above,
// a swimmer heading out, looking up or swimming home lost the mask and snorkel. Here only those head nodes (and the dry
// snorkel's and rebreather's, gear tiers tickets 04 and 09) get the
// flags back, in this call's own copy of the parameters: every other hat and helmet stays hidden as Waves and the game
// draw a swimmer, and hair and beard keep the skip flags the game already worked out from the cleared flags. Read only,
// as it runs on the draw threads; portraits, the colonist bar and statues are left alone.
[HarmonyPatch(typeof(PawnRenderNodeWorker_Apparel_Head), nameof(PawnRenderNodeWorker_Apparel_Head.CanDrawNow))]
internal static class Patch_PawnRenderNodeWorker_Apparel_Head_CanDrawNow
{
    private const PawnRenderFlags OffMap = PawnRenderFlags.Portrait | PawnRenderFlags.Cache | PawnRenderFlags.Statue;
    private const PawnRenderFlags Worn = PawnRenderFlags.Headgear | PawnRenderFlags.Clothes;

    private static void Prefix(PawnRenderNode n, ref PawnDrawParms parms)
    {
        if (!parms.swimming || (parms.flags & Worn) == Worn || (parms.flags & OffMap) != 0) return;
        ThingDef def = n.apparel?.def;
        if (def != null && (def == DiveGearDefOf.Spearfishing_GlassMask || def == DiveGearDefOf.Spearfishing_Snorkel ||
                            def == DrySnorkelDefOf.Spearfishing_DrySnorkel || def == RebreatherDefOf.Spearfishing_Rebreather) && DiveVisuals.On)
            parms.flags |= Worn;
        // The low-volume mask (gear tiers ticket 03) stays on the same way.
        if (def != null && def == DiveGearDefOf.Spearfishing_LowVolumeMask && DiveVisuals.On)
            parms.flags |= Worn;
    }
}

// The frame hook for the shadows and burst, and the kelp's sway. Each returns at once with nothing to do.
[HarmonyPatch(typeof(Map), nameof(Map.MapUpdate))]
internal static class Patch_Map_MapUpdate
{
    private static void Postfix(Map __instance)
    {
        DiveVisuals.MapUpdate(__instance);
        KelpSway.MapUpdate(__instance);
    }
}
