"""Render the Workshop preview image for Spearfishing.

Usage:
  python tools/render_preview.py            # candidates and a sheet in work/contact-sheets/
  python tools/render_preview.py --pick A   # writes About/Preview.png from that candidate

Inputs: the approved textures in Textures/, in-game coastline frames from the
approved promo (art/preview/), the Discord icon illustration
(.scratch/spearfishing/discord/icon.png) and the RimWorld UI font
(RimWordFont.ttf, not distributed with this repository).
Layout follows the author's other mods: 1280x720, title, art, tagline.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "Textures" / "Things" / "Spearfishing"
ICON = ROOT / ".scratch" / "spearfishing" / "discord" / "icon.png"
DEFAULT_FONT = ROOT.parent / "Configurable Quality" / "artifacts" / "steam-page-mockup" / "RimWordFont.ttf"
PREVIEW_ART = ROOT / "art" / "preview"
OUT_DIR = ROOT / "work" / "contact-sheets"

SIZE = (1280, 720)
BG_TOP = (28, 74, 84)
BG_BOTTOM = (8, 26, 36)
FOAM = (232, 240, 232)
SAND = (236, 196, 112)
TAGLINE = "DIVE  /  SPEAR  /  BRING IT HoME"


def background():
    w, h = SIZE
    img = Image.new("RGBA", SIZE)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        draw.line([(0, y), (w, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)) + (255,))
    # faint surface ripples, matching the icon's wave lines
    waves = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    wd = ImageDraw.Draw(waves)
    for x0, y0, length in ((60, 60, 300), (880, 40, 340), (500, 250, 220), (140, 470, 240), (960, 520, 260)):
        wd.arc([x0, y0, x0 + length // 2, y0 + 30], 200, 340, fill=(255, 255, 255, 34), width=4)
        wd.arc([x0 + length // 2, y0 - 10, x0 + length, y0 + 20], 20, 160, fill=(255, 255, 255, 34), width=4)
    img.alpha_composite(waves)
    return img


def coastline(name):
    """An in-game Waves coastline frame from the approved promo, darkened top and bottom for the text."""
    img = Image.open(PREVIEW_ART / name).convert("RGBA")
    scale = max(SIZE[0] / img.width, SIZE[1] / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (img.width - SIZE[0]) // 2, (img.height - SIZE[1]) // 2
    img = img.crop((left, top, left + SIZE[0], top + SIZE[1]))
    shade = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(SIZE[1]):
        t = y / (SIZE[1] - 1)
        # darker under the title and tagline, lighter through the gear row
        a = 150 * max(0.0, 1 - t / 0.32) ** 1.3 + 170 * max(0.0, (t - 0.72) / 0.28) ** 1.3 + 40
        sd.line([(0, y), (SIZE[0], y)], fill=(4, 14, 20, min(255, round(a))))
    img.alpha_composite(shade)
    return img


def sprite(path, size):
    img = Image.open(path).convert("RGBA")
    img = img.crop(img.getbbox())
    img.thumbnail((size, size), Image.LANCZOS) if max(img.size) >= size else None
    if max(img.size) < size:
        s = size / max(img.size)
        img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    return img


def place(canvas, img, center, shadow=True):
    x = round(center[0] - img.width / 2)
    y = round(center[1] - img.height / 2)
    if shadow:
        shade = Image.new("RGBA", img.size, (0, 0, 0, 0))
        shade.putalpha(img.split()[3].point(lambda a: a * 0.55))
        pad = 40
        layer = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
        layer.alpha_composite(shade, (pad, pad))
        layer = layer.filter(ImageFilter.GaussianBlur(14))
        canvas.alpha_composite(layer, (x - pad + 8, y - pad + 14))
    canvas.alpha_composite(img, (x, y))


def text(draw, center, value, font, fill, outline=0, max_width=None, anchor="mm"):
    # RimWordFont draws capital O as a decorative star; its lowercase o is plain.
    value = value.replace("O", "o")
    while max_width and font.getlength(value) > max_width and font.size > 12:
        font = font.font_variant(size=font.size - 2)
    draw.text(center, value, font=font, fill=fill, anchor=anchor,
              stroke_width=outline, stroke_fill=(6, 14, 18) if outline else None)


def candidate_a(font_path, canvas=None):
    """The approved gear in a row under the title."""
    canvas = canvas or background()
    draw = ImageDraw.Draw(canvas)
    text(draw, (640, 112), "SPEARFISHING", ImageFont.truetype(str(font_path), 112), FOAM, outline=5, max_width=1140)
    spear = sprite(TEX / "Weapon" / "SteelPoleSpear.png", 300).rotate(35, expand=True, resample=Image.BICUBIC)
    place(canvas, sprite(TEX / "Apparel" / "WoodenFins.png", 180), (170, 390))
    place(canvas, sprite(TEX / "Apparel" / "GlassMask" / "GlassMask.png", 180), (395, 370))
    place(canvas, spear, (635, 385))
    place(canvas, sprite(TEX / "Item" / "RawFish" / "RawFish_c.png", 200), (870, 380))
    place(canvas, sprite(TEX / "Apparel" / "Snorkel" / "Snorkel.png", 160), (1100, 385))
    text(draw, (640, 640), TAGLINE, ImageFont.truetype(str(font_path), 50), SAND, outline=3, max_width=1140)
    return canvas


def candidate_b(font_path):
    """The Discord illustration on the left, title and tagline on the right."""
    canvas = background()
    icon = Image.open(ICON).convert("RGBA").resize((720, 720), Image.LANCZOS)
    # fade the illustration's right edge into the background
    mask = Image.new("L", icon.size, 255)
    md = ImageDraw.Draw(mask)
    for x in range(560, 720):
        md.line([(x, 0), (x, 720)], fill=round(255 * (720 - x) / 160))
    icon.putalpha(mask)
    canvas.alpha_composite(icon, (0, 0))
    draw = ImageDraw.Draw(canvas)
    big = ImageFont.truetype(str(font_path), 104)
    text(draw, (990, 250), "SPEAR", big, FOAM, outline=5, max_width=520)
    text(draw, (990, 360), "FISHING", big, FOAM, outline=5, max_width=520)
    small = ImageFont.truetype(str(font_path), 42)
    for i, word in enumerate(("DIVE", "SPEAR", "BRING IT HoME")):
        text(draw, (990, 480 + i * 56), word, small, SAND, outline=3, max_width=520)
    return canvas


def wild_waters_title(draw, font_path):
    """The Wild Waters series name above the add-on's own name; the author wants Spearfishing to lead."""
    text(draw, (640, 58), "WILD WATERS", ImageFont.truetype(str(font_path), 52), SAND, outline=3, max_width=900)
    text(draw, (640, 158), "SPEARFISHING", ImageFont.truetype(str(font_path), 112), FOAM, outline=5, max_width=1140)


def candidate_wild_waters(font_path, background_name, row, tagline):
    canvas = coastline(background_name)
    draw = ImageDraw.Draw(canvas)
    wild_waters_title(draw, font_path)
    xs = [170 + i * (930 / (len(row) - 1)) for i in range(len(row))]
    for x, (path, size, angle) in zip(xs, row):
        img = sprite(path, size)
        if angle:
            img = img.rotate(angle, expand=True, resample=Image.BICUBIC)
        place(canvas, img, (x, 400))
    text(draw, (640, 640), tagline, ImageFont.truetype(str(font_path), 50), SAND, outline=3, max_width=1140)
    return canvas


# The dive gear, then what the mod adds for looking after the water.
DIVE_AND_RESTOCK = [
    (TEX / "Apparel" / "WoodenFins.png", 170, 0),
    (TEX / "Weapon" / "SteelPoleSpear.png", 290, 35),
    (TEX / "Item" / "RawFish" / "RawFish_c.png", 190, 0),
    (TEX / "Building" / "Hatchery.png", 200, 0),
    (TEX / "Item" / "FryBatch.png", 160, 0),
]
GEAR_AND_HATCHERY = [
    (TEX / "Apparel" / "WoodenFins.png", 170, 0),
    (TEX / "Apparel" / "GlassMask" / "GlassMask.png", 170, 0),
    (TEX / "Weapon" / "SteelPoleSpear.png", 290, 35),
    (TEX / "Item" / "RawFish" / "RawFish_c.png", 190, 0),
    (TEX / "Building" / "Hatchery.png", 190, 0),
]

CANDIDATES = {
    "A": candidate_a,
    "B": candidate_b,
    "C": lambda font: candidate_a(font, coastline("coastline-shore.png")),
    # 2026-11-19 redo for the Wild Waters name and the reef, hatchery and restoration features
    "E": lambda font: candidate_wild_waters(font, "kelp-coast.png", DIVE_AND_RESTOCK, "DIVE  /  SPEAR  /  RESTOCK THE REEF"),
    "F": lambda font: candidate_wild_waters(font, "kelp-coast.png", GEAR_AND_HATCHERY, "SPEAR THE FISH  /  KEEP THE SEA ALIVE"),
    "G": lambda font: candidate_wild_waters(font, "coastline-shore.png", DIVE_AND_RESTOCK, "DIVE  /  SPEAR  /  RESTOCK THE REEF"),
}
SHOWN = "EFG"


def sheet(images):
    pad, label = 30, 50
    w = SIZE[0] // 2
    h = SIZE[1] // 2
    out = Image.new("RGB", (pad + len(images) * (w + pad), pad + label + h + pad + h // 3 + pad), (30, 30, 34))
    d = ImageDraw.Draw(out)
    font = ImageFont.truetype("arialbd.ttf", 26)
    for i, (name, img) in enumerate(images.items()):
        x = pad + i * (w + pad)
        d.text((x, pad), f"{name}  (1280x720 shown at half size; below, mod-list size)", fill=(230, 230, 230), font=font)
        out.paste(img.convert("RGB").resize((w, h), Image.LANCZOS), (x, pad + label))
        small = img.convert("RGB").resize((w // 3 * 2 // 2, h // 3 * 2 // 2), Image.LANCZOS)
        out.paste(small, (x, pad + label + h + pad))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT, help="path to RimWordFont.ttf")
    parser.add_argument("--pick", choices=sorted(CANDIDATES), help="write About/Preview.png from this candidate")
    args = parser.parse_args()
    if not args.font.is_file():
        raise SystemExit(f"Font not found: {args.font}. Pass --font with a local RimWordFont.ttf.")
    if args.pick:
        out = ROOT / "About" / "Preview.png"
        CANDIDATES[args.pick](args.font).convert("RGB").save(out, optimize=True)
        print(out)
        return
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    images = {name: fn(args.font) for name, fn in CANDIDATES.items() if name in SHOWN}
    for name, img in images.items():
        img.convert("RGB").save(OUT_DIR / f"preview-{name}.png")
    path = OUT_DIR / "preview-candidates.png"
    sheet(images).save(path)
    print(path)


if __name__ == "__main__":
    main()
