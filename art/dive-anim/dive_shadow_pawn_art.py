"""Pawn-shaped dive shadow (ticket 26): a pawn seen from behind, head leading, one shape for all body types.

Our own drawing of a bold silhouette: a rounded body that tapers to the hips, with an
egg-shaped head above it. Its proportions follow vanilla's average (male) naked body and
average head seen from the north, measured in 128 px texture space; no pixels are copied.
White on transparent, tinted by the game. One texture per depth blur level (art/depth_blur.py).

Usage: python dive_shadow_pawn_art.py OUT_DIR
Writes DiveShadowPawn_Crisp.png, DiveShadowPawn_Medium.png and DiveShadowPawn_Soft.png (64 x 64).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from depth_blur import blur_levels  # noqa: E402

N = 64
# Measured space (128 px vanilla texture, head lifted by the body's head offset) to our 64 px texture:
# the silhouette runs y 10..107 there and fills y 5..59 here, leaving a margin for the soft blur.
K = 54 / 97


def to_tex(x, y):
    return 32 + (x - 64) * K, 5 + (y - 10) * K


def body_half_width(y):
    """Half-width of the body at height y in measured space (y 44..107)."""
    if y < 58:  # well-rounded top, no shoulders
        return 12 + math.sqrt(max(0.0, 196 - (58 - y) ** 2))
    if y <= 64:
        return 26
    if y <= 100:
        # Taper to the hips on an eased curve, as vanilla's outline does: it leaves the
        # widest point gently, narrows fastest around the waist and settles into the hips.
        t = (y - 64) / 36
        return 26 - 8 * (1 - math.cos(math.pi * t)) / 2
    return 11 + 7 * math.sqrt(max(0.0, 1 - ((y - 100) / 7) ** 2))


def draw_pawn(d, s):
    ys = [44 + i * 0.25 for i in range(int((107 - 44) / 0.25) + 1)]
    right = [to_tex(64 + body_half_width(y), y) for y in ys]
    left = [to_tex(64 - body_half_width(y), y) for y in reversed(ys)]
    d.polygon([(x * s, y * s) for x, y in right + left], fill=255)
    # Head: a wide crown over a narrower jaw, widest in its upper middle.
    for cx, cy, rx, ry in ((64, 31, 23, 21), (64, 44, 19.5, 18)):
        x0, y0 = to_tex(cx - rx, cy - ry)
        x1, y1 = to_tex(cx + rx, cy + ry)
        d.ellipse([x0 * s, y0 * s, x1 * s, y1 * s], fill=255)


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, img in blur_levels(draw_pawn, N).items():
        img.save(out / f"DiveShadowPawn_{name}.png")


if __name__ == "__main__":
    main()
