"""Render the Workshop description images for Wild Waters: Spearfishing.

Usage:
  python tools/render_workshop_art.py            # every image into docs/images/workshop/

Method follows Lumen Stones' scripts/render-workshop-art.py (Pillow, shipped sprites, RimWorld font); the palette follows
tools/render_preview.py. Numbers come from Source/FishStock/Model and the defs, so the images follow tuning changes.
Inputs: Textures/, art/preview/ (approved in-game coast frames) and the RimWorld UI font (RimWordFont.ttf, not distributed
with this repository).
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images" / "workshop"
TEX = ROOT / "Textures"
TITLE_FONT = ROOT.parent / "Configurable Quality" / "artifacts" / "steam-page-mockup" / "RimWordFont.ttf"
BODY_FONT = Path("C:/Windows/Fonts/seguisb.ttf")

BG, CARD, EDGE = "#0b2430", "#123544", "#24505f"
INK, MUTED, SAND = "#eef2ea", "#a9bcbf", "#ecc470"
SEA, KELP, ROSE = "#8fd8e6", "#bcdc8c", "#f4a99c"
W = 1600

canvas = draw = None


# ---- Facts read from the mod ---------------------------------------------------------------------------------------------

def rule(name):
    source = (ROOT / "Source/FishStock/Model/FishStockRules.cs").read_text(encoding="utf-8")
    return float(re.search(r"\b" + name + r"\s*=\s*([\d.]+)f?", source).group(1))


def defs():
    """Every ThingDef in Defs/ by defName."""
    found = {}
    for path in (ROOT / "Defs").rglob("*.xml"):
        for node in ET.parse(path).getroot():
            name = node.findtext("defName")
            if node.tag == "ThingDef" and name:
                found[name] = node
    return found


DEFS = defs()
# Defs whose tech level comes from their vanilla parent (BaseMakeableGun) rather than their own XML.
INHERITED_TECH = {"Spearfishing_BandSpeargun": "Industrial"}


def gear_by_tier():
    """Gear (weapons and apparel with a texture and tech level) grouped by tech level, spears first."""
    tiers = {}
    for name, node in DEFS.items():
        tex, tech = node.findtext("graphicData/texPath"), node.findtext("techLevel") or INHERITED_TECH.get(name)
        if not tex or not tech or node.findtext("thingClass") or "Building" in tex or "Item" in tex:
            continue
        weapon = "Weapon" in tex
        tiers.setdefault(tech, []).append((not weapon, name, node.findtext("label"), tex))
    return {t: [(label, tex) for _, _, label, tex in sorted(items)] for t, items in tiers.items()}


# ---- Drawing helpers ------------------------------------------------------------------------------------------------------

def font(size, title=False):
    return ImageFont.truetype(str(TITLE_FONT if title else BODY_FONT), size)


def start(height, width=W):
    global canvas, draw, W
    W = width
    canvas = Image.new("RGBA", (W, height), BG)
    draw = ImageDraw.Draw(canvas)


def text(x, y, value, size=34, color=INK, title=False, center=False, right=False):
    if title:
        # The RimWorld font's capital O is decorative; its lowercase o reads as a plain O.
        value = value.upper().replace("O", "o")
    f = font(size, title)
    width = draw.textlength(value, font=f)
    x = x - width / 2 if center else x - width if right else x
    if x < 0 or x + width > W:
        raise ValueError("Text leaves the image: " + value)
    draw.text((x, y), value, font=f, fill=color, anchor="lt")


def lines(value, width, size):
    words, out = value.split(), [""]
    for word in words:
        trial = (out[-1] + " " + word).strip()
        if draw.textlength(trial, font=font(size)) <= width or not out[-1]:
            out[-1] = trial
        else:
            out.append(word)
    return out


def para(x, y, value, width, size=34, color=INK, center=False, gap=1.32):
    rows = lines(value, width, size)
    for i, row in enumerate(rows):
        text(x, y + i * size * gap, row, size, color, center=center)
    return y + len(rows) * size * gap


def card(box):
    draw.rounded_rectangle(box, radius=16, fill=CARD, outline=EDGE, width=2)


def sprite(path, box, max_scale=2.4, rotate=0, tint=None):
    """Fit a texture (path under Textures/ without .png, or an Image) into box, centred on its visible pixels."""
    im = path if isinstance(path, Image.Image) else Image.open(TEX / (path + ".png")).convert("RGBA")
    if rotate:
        im = im.rotate(rotate, Image.Resampling.BICUBIC, expand=True)
    if tint:
        im = Image.merge("RGBA", (*Image.new("RGB", im.size, tint).split(), im.getchannel("A")))
    im = im.crop(im.getbbox())
    scale = min(box[2] / im.width, box[3] / im.height, max_scale)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.Resampling.LANCZOS)
    canvas.alpha_composite(im, (int(box[0] + (box[2] - im.width) / 2), int(box[1] + (box[3] - im.height) / 2)))


def tile(path, box, crop=256):
    """A square of terrain overlay on sea-floor colour, with rounded corners."""
    x, y, size = box
    floor = Image.new("RGBA", (crop, crop), "#2d6b73")
    overlay = Image.open(TEX / (path + ".png")).convert("RGBA").crop((0, 0, crop, crop))
    floor.alpha_composite(overlay)
    floor = floor.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=18, fill=255)
    canvas.paste(floor, (x, y), mask)


def arrow(x0, y, x1, color=SAND):
    draw.line((x0, y, x1 - 16, y), fill=color, width=5)
    draw.polygon(((x1, y), (x1 - 20, y - 13), (x1 - 20, y + 13)), fill=color)


def slider(x, y, width, fraction, color):
    draw.rounded_rectangle((x, y, x + width, y + 12), radius=6, fill="#2f4d58")
    draw.rounded_rectangle((x, y, x + width * fraction, y + 12), radius=6, fill=color)
    cx = x + width * fraction
    draw.ellipse((cx - 20, y - 14, cx + 20, y + 26), fill=INK, outline=color, width=3)


def toggle(x, y, color):
    draw.rounded_rectangle((x, y, x + 150, y + 64), radius=32, fill=color)
    text(x + 22, y + 17, "ON", 28, BG)
    draw.ellipse((x + 94, y + 7, x + 144, y + 57), fill=INK)


def banner(title, height=230, art="coastline-shore.png"):
    """A strip of in-game coast behind the title, darkened so the lettering reads."""
    shore = Image.open(ROOT / "art/preview" / art).convert("RGBA")
    scale = W / shore.width
    shore = shore.resize((W, round(shore.height * scale)), Image.Resampling.LANCZOS)
    top = round(shore.height * 0.66) - height // 2  # open water and reef below the beach, clear of the pawn
    shore = ImageEnhance.Brightness(shore.crop((0, top, W, top + height))).enhance(0.55)
    canvas.alpha_composite(shore, (0, 0))
    draw.rectangle((0, height, W, height + 6), fill=SAND)
    f = font(92, True)
    value = title.upper().replace("O", "o")
    x = (W - draw.textlength(value, font=f)) / 2
    draw.text((x + 4, height / 2 + 4), value, font=f, fill="#06141b", anchor="lm")
    draw.text((x, height / 2), value, font=f, fill=INK, anchor="lm")


def save(name):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / (name + ".png")
    canvas.convert("RGB").save(path, optimize=True)
    print("Wrote", path.relative_to(ROOT))


# ---- Images ---------------------------------------------------------------------------------------------------------------

def hero():
    cap, limit = int(rule("CapacityCap")), rule("DefaultFishDownLimit")
    start(2000)
    banner("Spear the fish")
    for i, (heading, art, line, color, turn) in enumerate([
        ("Dive", "Things/Spearfishing/Weapon/PoleSpear", "Spear fish in the sea, lakes and rivers", SEA, 35),
        ("Share", "Things/Spearfishing/Item/RawFish/RawFish_c", "Every zone on a water draws one fish stock", SAND, 0),
        ("Restore", "Things/Spearfishing/Building/Hatchery", "Reefs and a hatchery bring fish back", KELP, 0),
    ]):
        left = 24 + i * 524
        card((left, 270, left + 504, 870))
        text(left + 252, 306, heading, 46, color, title=True, center=True)
        sprite(art, (left + 92, 400, 320, 260), max_scale=3.2, rotate=turn)
        para(left + 252, 724, line, 440, 40, color, center=True, gap=1.28)
    text(W / 2, 920, "Divers, fish shoals and gear for the water", 44, INK, center=True)
    text(W / 2, 978, "that RimWorld: Waves brings to your map.", 44, INK, center=True)

    card((24, 1070, 1576, 1500))
    text(64, 1108, "Your balance", 52, SAND, title=True)
    rows = [("Fish-down limit", f"{limit:.0%}", limit, SEA), ("Shark chance per trip", "1%", 0.05, ROSE)]
    for j, (label, value, fraction, color) in enumerate(rows):
        y = 1210 + j * 104
        text(70, y, label, 38, INK)
        text(1530, y, value, 38, color, right=True)
        slider(560, y + 18, 820, fraction, color)
    text(70, 1420, "Fish stock management", 38, INK)
    toggle(1380, 1404, KELP)
    text(560 + 410, 1430, f"Up to {cap} fish per water", 30, MUTED, center=True)

    card((24, 1530, 784, 1960))
    card((812, 1530, 1576, 1960))
    text(64, 1568, "Requirements", 48, SAND, title=True)
    y = para(64, 1650, "Harmony and RimWorld: Waves 1.3.0 or later.", 680, 38)
    para(64, y + 20, "Odyssey, Living Waters and Dubs Bad Hygiene supported.", 680, 34, MUTED)
    text(852, 1568, "Save games", 48, SAND, title=True)
    y = para(852, 1650, "Can be added mid-save.", 680, 38)
    para(852, y + 20, "Removal drops the mod's zones, buildings, gear and fish.", 680, 34, MUTED)
    save("spearfishing-description")


def features():
    cap, per_day = int(rule("CapacityCap")), 60
    start(1700)
    banner("Features", 200)
    boxes = [(24, 236, 784, 940), (812, 236, 1576, 940), (24, 968, 784, 1672), (812, 968, 1576, 1672)]
    for box in boxes:
        card(box)

    # Fish stock
    cx = 404
    text(cx, 272, "One stock per water", 46, SEA, title=True, center=True)
    draw.rounded_rectangle((104, 350, 704, 530), radius=18, fill="#2d6b73")
    for k, f in enumerate(["FishStocky", "FishLarge", "FishSlim", "FishLong", "FishStocky"]):
        sprite(f"Spearfishing/Dive/{f}_Crisp", (130 + k * 112, 372 + (k % 2) * 56, 90, 80), max_scale=1.6, rotate=(k % 2) * 18 - 8, tint="#173f48")
    text(cx, 560, f"1 fish per cell, up to {cap}", 38, INK, center=True)
    text(cx, 620, f"An ordinary sea regrows about {per_day} a day", 32, MUTED, center=True)
    text(cx, 700, "Reef and kelp draw fish:", 34, INK, center=True)
    text(cx, 748, "dives there land half again as often", 34, KELP, center=True)
    text(cx, 846, "Sea, deep lakes and deep rivers", 30, MUTED, center=True)

    # Recovery
    cx = 1194
    text(cx, 272, "Bring fish back", 46, KELP, title=True, center=True)
    for k, (art, label) in enumerate([
        ("Things/Spearfishing/Building/ArtificialReef/ArtificialReef", "Artificial reef"),
        ("UI/Designators/Spearfishing_RestoreSeaFloor", "Restore sea floor"),
        ("Things/Spearfishing/Building/Hatchery", "Hatchery"),
    ]):
        x = 852 + k * 240
        sprite(art, (x + 30, 380, 180, 180), max_scale=3.0)
        text(x + 120, 590, label, 30, INK, center=True)
    text(cx, 690, "Sink steel reef, replant cuttings,", 34, INK, center=True)
    text(cx, 738, "release hatchery fry", 34, INK, center=True)
    text(cx, 846, "Fish stock management, on by default", 30, MUTED, center=True)

    # Threats
    cx = 404
    text(cx, 1004, "Threats", 46, ROSE, title=True, center=True)
    tile("Spearfishing/Terrain/UrchinBarrenReef", (130, 1100, 230))
    tile("Spearfishing/Terrain/ReefOverlay", (444, 1100, 230))
    text(245, 1346, "Urchin barren", 30, ROSE, center=True)
    text(559, 1346, "Healthy reef", 30, KELP, center=True)
    text(cx, 1430, "Urchins and invasive predators", 34, INK, center=True)
    text(cx, 1478, "slow regrowth until divers cull them", 34, INK, center=True)
    text(cx, 1576, "About once a year, each with its own switch", 30, MUTED, center=True)

    # Sharks and snorkeling
    cx = 1194
    text(cx, 1004, "Deep water", 46, SEA, title=True, center=True)
    sprite("Spearfishing/Dive/SharkShadow_Crisp", (880, 1110, 280, 200), max_scale=1.1)
    sprite("Things/Spearfishing/Apparel/Snorkel/Snorkel", (1270, 1120, 200, 180), max_scale=2.4)
    text(1020, 1346, "Shark", 30, ROSE, center=True)
    text(1370, 1346, "Snorkeling", 30, SEA, center=True)
    text(cx, 1430, "A rare shark may steal a catch", 34, INK, center=True)
    text(cx, 1478, "Colonists snorkel to relax", 34, INK, center=True)
    text(cx, 1576, "Shark chance from 0 to 20%", 30, MUTED, center=True)
    save("spearfishing-features")


def getting_started():
    limit = rule("DefaultFishDownLimit")
    start(1100)
    banner("Getting started", 200)
    cols = [(24, 504), (548, 1052), (1096, 1576)]
    for left, right in cols:
        card((left, 236, right, 846))
    for (left, right), heading in zip(cols, ["Paint a zone", "Arm a diver", "Store fish"]):
        text((left + right) / 2, 272, heading, 44, SAND, title=True, center=True)

    cx = 264
    tile("Spearfishing/Terrain/KelpOverlayOlive", (cx - 120, 360, 240))
    draw.rounded_rectangle((cx - 120, 360, cx + 120, 600), radius=18, outline=SEA, width=5)
    text(cx, 640, "Zone menu", 36, INK, center=True)
    text(cx, 694, "on deep sea, lake or river", 30, MUTED, center=True)
    text(cx, 744, "over reef or kelp if you can", 30, KELP, center=True)

    cx = 800
    sprite("Things/Spearfishing/Weapon/PoleSpear", (cx - 210, 370, 210, 220), max_scale=2.2, rotate=40)
    sprite("Things/Spearfishing/Apparel/WoodenFins", (cx + 20, 380, 170, 200), max_scale=1.8)
    text(cx, 640, "Spear or speargun", 36, INK, center=True)
    text(cx, 694, "Enable Spearfishing", 30, MUTED, center=True)
    text(cx, 744, "in the Work tab", 30, MUTED, center=True)

    cx = 1336
    sprite("Things/Spearfishing/Item/RawFish/RawFish_c", (cx - 130, 380, 260, 220), max_scale=3.6)
    text(cx, 640, "Allow raw fish", 36, INK, center=True)
    text(cx, 694, "in a stockpile", 30, MUTED, center=True)
    text(cx, 744, "Divers drop it on the shore", 30, MUTED, center=True)

    arrow(510, 541, 542)
    arrow(1058, 541, 1090)
    draw.line(((1336, 846), (1336, 930), (264, 930), (264, 866)), fill=SAND, width=5)
    draw.polygon(((264, 850), (251, 872), (277, 872)), fill=SAND)
    text(800, 950, f"Divers stop when the water falls to its fish-down limit ({limit:.0%})", 34, SAND, center=True)
    text(800, 1024, "Snorkeling for recreation needs no gear, zone or research.", 30, MUTED, center=True)
    save("spearfishing-getting-started")


def gear_rows():
    """One image per tech level, for the Gear section's BBCode headings."""
    for tech, items in gear_by_tier().items():
        slot = 300
        start(380, max(len(items) * slot + 48, 1240))
        offset = (W - len(items) * slot) / 2
        for i, (label, tex) in enumerate(items):
            left = offset + i * slot
            card((left + 10, 20, left + slot - 10, 360))
            sprite(tex, (int(left + 50), 50, slot - 100, 200), max_scale=1.6)
            for j, row in enumerate(lines(label[0].upper() + label[1:], slot - 40, 32)):
                text(left + slot / 2, 272 + j * 40, row, 32, INK, center=True)
        save("spearfishing-gear-" + tech.lower())


if __name__ == "__main__":
    hero()
    features()
    getting_started()
    gear_rows()
