"""Depth blur levels shared by underwater art (ticket 26 dive shadow, ticket 27 fish).

Each shape is prebuilt at every level so nothing is blurred while drawing; the game
crossfades neighbouring levels by MapComponent_FishStock.SwimDepthAt.
Blur radii are Gaussian sigmas in texels of the final texture.
"""
from PIL import Image, ImageFilter

# crisp = fish look B, medium = fish look A, soft = deeper than A.
BLUR_LEVELS = {"Crisp": 0.8, "Medium": 1.6, "Soft": 2.8}


def white_shape(draw_fn, blur, n=64, ss=8):
    """Draw a white shape supersampled ss times, blur it, and downsample to n x n RGBA.

    draw_fn(draw, scale) draws in final-texture units multiplied by scale.
    """
    a = Image.new("L", (n * ss, n * ss), 0)
    from PIL import ImageDraw
    draw_fn(ImageDraw.Draw(a), ss)
    if blur:
        a = a.filter(ImageFilter.GaussianBlur(blur * ss))
    a = a.resize((n, n), Image.LANCZOS)
    img = Image.new("RGBA", (n, n), (255, 255, 255, 0))
    img.putalpha(a)
    return img


def blur_levels(draw_fn, n=64, ss=8):
    """Return {level name: white RGBA texture} for every depth blur level."""
    return {name: white_shape(draw_fn, blur, n, ss) for name, blur in BLUR_LEVELS.items()}
