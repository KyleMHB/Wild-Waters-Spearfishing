"""Steel-tipped pole spear candidate for Spearfishing. The approved pole spear v4 (art/pole-spear/pole_spear_art.py) with its
geometry, shaft colours, framing and 3 px black outward outline unchanged; only the broad barbed point is recoloured steel.
128 px per cell, horizontal with the tip to the right.
Usage: python -I steel_pole_spear_art.py <out_dir>. Writes SteelPoleSpear_A.png (128x128)."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

CAND = Path(sys.argv[1])
CAND.mkdir(parents=True, exist_ok=True)
SS = 8
INK = (12, 10, 10, 255)


def with_outline(layer, px):
    alpha = layer.getchannel("A").point(lambda v: 255 if v > 127 else 0)
    ring = alpha.filter(ImageFilter.MaxFilter(px * 2 + 1))
    base = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    base.paste(Image.new("RGBA", layer.size, INK), (0, 0), ring)
    base.alpha_composite(layer)
    return base


def spear():
    """v4's drawing with a steel head: light (206, 210, 212) on top, dark (150, 156, 162) below."""
    S = 128
    W = S * SS
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cy = W / 2
    sh = 6 * SS
    x_butt, x_base, x_tip = 5 * SS, 94 * SS, 123 * SS
    light, mid = (164, 122, 78, 255), (132, 94, 58, 255)
    d.rectangle([x_butt, cy - sh / 2, x_base + 4 * SS, cy + sh / 2], fill=mid)
    d.rectangle([x_butt, cy - sh / 2, x_base + 4 * SS, cy - sh / 6], fill=light)
    hw = 11 * SS
    back = x_base - 9 * SS
    notch = x_base - 1 * SS
    head_light, head_dark = (206, 210, 212, 255), (150, 156, 162, 255)
    upper = [(x_tip, cy), (x_base + 2 * SS, cy - hw), (back, cy - hw + 1 * SS), (notch, cy - sh / 2), (notch, cy)]
    lower = [(x_tip, cy), (x_base + 2 * SS, cy + hw), (back, cy + hw - 1 * SS), (notch, cy + sh / 2), (notch, cy)]
    d.polygon(lower, fill=head_dark)
    d.polygon(upper, fill=head_light)
    out = with_outline(img, 3 * SS)
    return out.resize((S, S), Image.LANCZOS)


spear().save(CAND / "SteelPoleSpear_A.png")
