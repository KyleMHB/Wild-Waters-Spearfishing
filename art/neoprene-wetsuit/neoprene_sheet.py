"""Contact sheet for the neoprene wetsuit candidates (gear-tiers ticket 05), beside the approved basic wetsuit.

Each block is one suit: the item at 2x and at game size, then the suit worn on Male, Female, Thin, Hulk and Fat facing south,
east and north, with a bald vanilla head (skin-tinted) and the approved glass mask, at 1.25x. The basic suit's committed
greyscale textures are tinted by a plain-leather colour, as the game does for stuff. Vanilla bodies and heads are used only
to place the views on the sheet; the sheet is review output (work/ is ignored), never committed.

Placement: body and head are 128 px textures on a 1.5-cell mesh, so 85.3 px per cell. The body type's headOffset
(x, 0.34) lifts the head 0.34 cells; x applies on east (and mirrored west) only.

Usage: python -I neoprene_sheet.py <candidates_dir> <repo_root> <vanilla Humanlike dir> <out.png>
<candidates_dir> is neoprene_wetsuit_art.py's output for all five body types."""
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

CAND = Path(sys.argv[1])
REPO = Path(sys.argv[2])
HUMAN = Path(sys.argv[3])
OUT = Path(sys.argv[4])

BODIES = ["Male", "Female", "Thin", "Hulk", "Fat"]
DIRS = ["south", "east", "north"]
HEAD_X = {"Male": 0.04, "Female": 0.10, "Thin": 0.09, "Hulk": 0.10, "Fat": 0.09}  # BodyTypeDef headOffset, RimWorld 1.6
HEAD_Z = 0.34
PPC = 128 / 1.5
SKIN = (236, 200, 166)
LEATHER = (166, 124, 84)  # a plain-leather tint for the stuffed basic suit
BG = (146, 138, 120)  # a sandy ground tone
TILE = 160  # 1.25x of a 128 px texture
APPAREL = REPO / "Textures/Things/Spearfishing/Apparel"
FONT = ImageFont.load_default(size=16)
SMALL = ImageFont.load_default(size=13)

SUITS = [
    ("Basic wetsuit (approved, plain-leather tint)", APPAREL / "Wetsuit/Wetsuit.png", lambda b, d: APPAREL / f"Wetsuit/Wetsuit_{b}_{d}.png", True),
] + [
    (f"Neoprene {k}: {label}", CAND / f"NeopreneWetsuit_{k}_{n}.png", (lambda k, n: lambda b, d: CAND / f"NeopreneWetsuit_{k}_{n}_{b}_{d}.png")(k, n), False)
    for k, n, label in [("A", "sidepanels", "side panels"), ("B", "yoke", "chest yoke"), ("C", "pads", "chest band and knee pads")]
]


def tint(img, colour):
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    rgb = ImageChops.multiply(Image.merge("RGB", (r, g, b)), Image.new("RGB", img.size, colour))
    return Image.merge("RGBA", (*rgb.split(), a))


def load(path, colour=None):
    img = Image.open(path).convert("RGBA")
    return tint(img, colour) if colour else img


def pawn(suit_path, body, direction):
    """Body silhouette is not drawn: the suit covers it. Then head, then the glass mask, each at its offset."""
    canvas = Image.new("RGBA", (128, 192), (0, 0, 0, 0))
    top = 48  # room above the body texture for the raised head
    canvas.alpha_composite(suit_path, (0, top))
    dx = round(HEAD_X[body] * PPC) if direction == "east" else 0
    dz = round(HEAD_Z * PPC)
    head = load(HUMAN / f"Heads/Male/Male_Average_Normal_{direction}.png", SKIN)
    canvas.alpha_composite(head, (dx, top - dz))
    mask = load(APPAREL / f"GlassMask/GlassMask_{direction}.png")
    canvas.alpha_composite(mask, (dx, top - dz))
    return canvas


def scaled(img, f):
    return img.resize((round(img.width * f), round(img.height * f)), Image.LANCZOS)


ITEM_W = 360
ROW = 165
BLOCK_H = 3 * ROW + 50
sheet = Image.new("RGB", (ITEM_W + 5 * TILE + 40, len(SUITS) * BLOCK_H + 70), BG)
d = ImageDraw.Draw(sheet)
d.text((20, 10), "Neoprene wetsuit candidates (ticket 05) beside the approved basic wetsuit.", fill=(20, 20, 20), font=FONT)
d.text((20, 32), "Worn views 1.25x with a vanilla head and the glass mask; item at 2x and at game size (64 px).", fill=(20, 20, 20), font=FONT)
for i, (label, item_path, worn_path, leather) in enumerate(SUITS):
    y0 = 70 + i * BLOCK_H
    d.line([(10, y0 - 8), (sheet.width - 10, y0 - 8)], fill=(90, 84, 72), width=2)
    d.text((20, y0), label, fill=(20, 20, 20), font=FONT)
    colour = LEATHER if leather else None
    it = load(item_path, colour)
    sheet.paste(scaled(it, 2), (20, y0 + 30), scaled(it, 2))
    small = scaled(it, 0.5)
    sheet.paste(small, (20, y0 + 300), small)
    d.text((90, y0 + 320), "game size", fill=(40, 40, 40), font=SMALL)
    for c, body in enumerate(BODIES):
        x = ITEM_W + c * TILE
        d.text((x + 55, y0), body, fill=(20, 20, 20), font=SMALL)
        for r, direction in enumerate(DIRS):
            view = pawn(load(worn_path(body, direction), colour), body, direction)
            big = scaled(view, TILE / 128)
            sheet.paste(big, (x, y0 - 45 + r * ROW), big)
    for r, direction in enumerate(DIRS):
        d.text((ITEM_W - 55, y0 + 90 + r * ROW), direction, fill=(40, 40, 40), font=SMALL)
OUT.parent.mkdir(parents=True, exist_ok=True)
sheet.save(OUT)
print(OUT)
