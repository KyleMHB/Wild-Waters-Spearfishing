"""Full-face mask, round 2: rebreather candidates for Spearfishing (gear tiers ticket 09). Procedural PIL drawing in the house
rendering of the approved glass mask, low-volume mask and dry snorkel (art/glass-mask, art/low-volume-mask, art/dry-snorkel): a
few flat two-tone shapes, a black outward outline and black lines between materials, no fine detail.

Round 1 (full_face_mask_art.py, a full-face visor with a built-in snorkel tube) was not approved: the author asked for a
rebreather instead of a snorkel tube on the spacer-tier mask. So the mask now breathes through a closed rebreather loop: a wide
visor over the eyes, a solid plasteel jaw shell over the nose and mouth with a chin valve, and a scrubber unit. It still covers
both the mask and snorkel slots and stays on the face, held by a rubber harness (the glossary avoids "diving helmet"). The
design is our own; the Subnautica games' masks were looked at as loose reference only, and none of their art is used.

Same contract as the tier below: an item sprite (128x128, Graphic_Single, drawSize 1, 4 px outline at the 8x master's scale,
exported at about 100 px across) and worn views (128x128 head textures, _south, _east and _north, 3 px outline) on vanilla's
128 px head frame (head about x 41-87, y 39-89). The mask's bottom stays at y 92 or above. West mirrors east in game, so every
view is symmetric or unhanded.

With no snorkel tube over the crown, the back of the head is what reads face down, so the candidates differ there:
  A back-canister: one horizontal scrubber canister across the back of the head on the harness pad, wider than the head, with
    a hose from each side of the jaw shell round to its ends.
  B cheek-scrubbers: a squared scrubber block on each side of the jaw shell, standing out past the head's sides, no hoses; from
    behind, the blocks frame the head below the harness pad.
  C twin-canisters: two upright scrubber canisters on the back pad, rising above the crown, with a hose from each side of the
    jaw shell.
All three share the front, the plasteel and charcoal palette and one orange accent (the dry snorkel's) on the chin valve and
canister caps.

Usage: python -I rebreather_mask_art.py <out_dir> [<vanilla_head_north.png>]
Writes FullFaceMask_<X>_<name>.png and its _south, _east and _north views, and contact_sheet.png. For the tier-below row it
first runs the approved candidates' own scripts (art/low-volume-mask, art/dry-snorkel) into <out_dir>/tier-below and reads
low-volume mask A and dry snorkel C from there. The optional vanilla head (an untinted north head dumped from the game, e.g.
work/vanilla-ref/head_Male_Average_Normal_north.png) is used only to place the north and face-down views on the sheet; it is
never written out and never goes into the textures. Without it the sheet uses the plain stand-in head.
"""
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

OUT = Path(sys.argv[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
VANILLA_HEAD = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
HERE = Path(__file__).resolve().parent
ART = HERE.parent
TEX = ART.parent / "Textures"
SS = 8
S = 128
W = S * SS
INK = (12, 10, 10, 255)
PLASTEEL_LIGHT, PLASTEEL_DARK = (178, 196, 202, 255), (118, 136, 146, 255)
GLASS, GLASS_SHADE, GLASS_SHINE = (150, 206, 214, 255), (112, 170, 184, 255), (226, 244, 246, 255)
RUBBER_LIGHT, RUBBER_DARK = (88, 92, 98, 255), (58, 60, 66, 255)
ORANGE_LIGHT, ORANGE_DARK = (232, 128, 52, 255), (184, 90, 34, 255)
SKIN, HAIR = (226, 184, 148, 255), (96, 66, 44, 255)
LINE = int(1.5 * SS)  # material line, 1.5 px at 128
LIGHT, DARK = PLASTEEL_LIGHT, PLASTEEL_DARK

STYLES = {"A": "back-canister", "B": "cheek-scrubbers", "C": "twin-canisters"}


def with_outline(layer, px):
    alpha = layer.getchannel("A").point(lambda v: 255 if v > 127 else 0)
    ring = alpha.filter(ImageFilter.MaxFilter(px * 2 + 1))
    base = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    base.paste(Image.new("RGBA", layer.size, INK), (0, 0), ring)
    base.alpha_composite(layer)
    return base


def finish(img, outline):
    return with_outline(img, outline * SS).resize((S, S), Image.LANCZOS)


def new():
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def p(*xy):
    return [v * SS for v in xy]


def inset(box, by=LINE):
    x0, y0, x1, y1 = box
    return [x0 * SS + by, y0 * SS + by, x1 * SS - by, y1 * SS - by]


def two_tone(d, box, light, dark, radius):
    """Black line, dark body, light upper half: the house treatment for one material plate."""
    x0, y0, x1, y1 = box
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=radius * SS, fill=INK)
    d.rounded_rectangle(inset(box), radius=max(0, radius * SS - LINE), fill=dark)
    d.rounded_rectangle([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, (y0 + y1) / 2 * SS], radius=max(0, radius * SS - LINE),
                        fill=light)


def strap(d, box):
    x0, y0, x1, y1 = box
    two_tone(d, box, RUBBER_LIGHT, RUBBER_DARK, (y1 - y0) / 2)


# ---- Tube and valve (the dry snorkel's construction) ------------------------------------------------------------------------

def stroke(d, pts, width, fill):
    """A thick polyline with round joins and caps, in 128 px units."""
    pts = [(x * SS, y * SS) for x, y in pts]
    w = width * SS
    d.line(pts, fill=fill, width=int(w), joint="curve")
    for x, y in pts:
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=fill)


def arc(cx, cy, r, a0, a1, n=10):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def tube(d, pts, width, light, dark):
    """Black line, dark body, a light stripe along one side."""
    stroke(d, pts, width + 3, INK)
    stroke(d, pts, width, dark)
    off = -width * 0.18
    stroke(d, [(x + off, y + off) for x, y in pts], width * 0.45, light)


def valve(d, x, y_bottom, width, height, light, dark, vents):
    """The dry valve on top of the tube: a rounded block wider than the tube, light on its left half."""
    x0, x1, y0 = x - width / 2, x + width / 2, y_bottom - height
    d.rounded_rectangle([(x0 - 1.5) * SS, (y0 - 1.5) * SS, (x1 + 1.5) * SS, (y_bottom + 1.5) * SS], radius=3.5 * SS, fill=INK)
    d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y_bottom * SS], radius=2.5 * SS, fill=dark)
    d.rounded_rectangle([x0 * SS, y0 * SS, x * SS, y_bottom * SS], radius=2.5 * SS, fill=light)
    for i in range(1, vents + 1):
        y = y0 + height * i / (vents + 1)
        d.rectangle([(x0 + 2) * SS, (y - 0.8) * SS, (x1 - 2) * SS, (y + 0.8) * SS], fill=INK)


def j_path(x_mouth, y_mouth, x_side, y_top, r):
    """Across to the side, round the bend, then straight up (the snorkels' path)."""
    return [(x_mouth, y_mouth), (x_side - r, y_mouth)] + arc(x_side - r, y_mouth - r, r, 90, 0) + [(x_side, y_top)]


# ---- Rebreather parts -----------------------------------------------------------------------------------------------------

def hose(d, pts, width):
    tube(d, pts, width, RUBBER_LIGHT, RUBBER_DARK)


def capsule(d, box, cap):
    """A horizontal scrubber canister: charcoal rubber end caps, a plasteel body and an orange band at the middle."""
    x0, y0, x1, y1 = box
    two_tone(d, box, RUBBER_LIGHT, RUBBER_DARK, (y1 - y0) / 2)
    two_tone(d, (x0 + cap, y0, x1 - cap, y1), LIGHT, DARK, 1.5)
    band = (x1 - x0) * 0.07
    cx = (x0 + x1) / 2
    two_tone(d, (cx - band, y0 - 1, cx + band, y1 + 1), ORANGE_LIGHT, ORANGE_DARK, 1.5)


def canister(d, box, cap):
    """An upright scrubber canister: a plasteel body with an orange cap on top."""
    x0, y0, x1, y1 = box
    two_tone(d, box, LIGHT, DARK, (x1 - x0) / 2)
    two_tone(d, (x0, y0, x1, y0 + cap), ORANGE_LIGHT, ORANGE_DARK, (x1 - x0) / 2.5)


def scrubber(d, box, vents):
    """A squared scrubber block: plasteel, with a charcoal vent face."""
    x0, y0, x1, y1 = box
    two_tone(d, box, LIGHT, DARK, 3)
    m = (x1 - x0) * 0.22
    face = (x0 + m, y0 + (y1 - y0) * 0.3, x1 - m, y1 - m)
    two_tone(d, face, RUBBER_LIGHT, RUBBER_DARK, 1.5)
    for i in range(1, vents + 1):
        y = face[1] + (face[3] - face[1]) * i / (vents + 1)
        d.rectangle([(face[0] + 1.5) * SS, (y - 0.6) * SS, (face[2] - 1.5) * SS, (y + 0.6) * SS], fill=INK)


def chin_valve(d, cx, cy, r):
    """The exhale valve at the chin: a charcoal ring round an orange cap."""
    d.ellipse([(cx - r) * SS - LINE, (cy - r) * SS - LINE, (cx + r) * SS + LINE, (cy + r) * SS + LINE], fill=INK)
    d.ellipse(p(cx - r, cy - r, cx + r, cy + r), fill=RUBBER_DARK)
    c = r * 0.55
    d.ellipse([(cx - c) * SS - LINE, (cy - c) * SS - LINE, (cx + c) * SS + LINE, (cy + c) * SS + LINE], fill=INK)
    d.ellipse(p(cx - c, cy - c, cx + c, cy + c), fill=ORANGE_DARK)
    d.chord(p(cx - c, cy - c, cx + c, cy + c), 135, 315, fill=ORANGE_LIGHT)


# ---- The mask seen from the front ----------------------------------------------------------------------------------------

def front(d, x0, y0, x1, y1, skirt, frame, valve_r, vents):
    """The mask from the front, filling (x0, y0)-(x1, y1): a charcoal skirt where it seals, a rounded plasteel shell, a wide
    visor over the eyes in its upper half and the solid jaw shell below with the chin valve (and, on the item, two vent slits)."""
    w = x1 - x0
    two_tone(d, (x0, y0, x1, y1), RUBBER_LIGHT, RUBBER_DARK, w * 0.4)
    f = (x0 + skirt, y0 + skirt, x1 - skirt, y1 - skirt)
    fr = w * 0.4 - skirt
    two_tone(d, f, LIGHT, DARK, fr)
    h = f[3] - f[1]
    g = (f[0] + frame, f[1] + frame, f[2] - frame, f[1] + h * 0.56)
    gr = fr - frame
    d.rounded_rectangle(p(*g), radius=gr * SS, fill=INK)
    gi = inset(g)
    d.rounded_rectangle(gi, radius=gr * SS - LINE, fill=GLASS_SHADE)
    gw, gh = gi[2] - gi[0], gi[3] - gi[1]
    d.rounded_rectangle([gi[0], gi[1], gi[2] - gw * 0.1, gi[3] - gh * 0.24], radius=gr * SS - LINE, fill=GLASS)
    d.ellipse([gi[0] + gw * 0.12, gi[1] + gh * 0.14, gi[0] + gw * 0.3, gi[1] + gh * 0.42], fill=GLASS_SHINE)
    cx, cy = (x0 + x1) / 2, g[3] + (f[3] - g[3]) * 0.5
    chin_valve(d, cx, cy, valve_r)
    if vents:
        for side in (-1, 1):
            vx = cx + side * (valve_r + w * 0.13)
            for dy in (-2.2, 2.2):
                d.rounded_rectangle(p(vx - w * 0.06, cy + dy - 0.9, vx + w * 0.06, cy + dy + 0.9), radius=0.9 * SS, fill=INK)


def side_profile(img, d):
    """The mask facing east: the skirt sealing on the face, the shell standing proud of it as a dome, glass over its upper
    part, the jaw shell below and the chin valve at the front."""
    d.rounded_rectangle(p(80, 51, 88, 92), radius=3.5 * SS, fill=INK)
    d.rounded_rectangle(inset((80, 51, 88, 92)), radius=3.5 * SS - LINE, fill=RUBBER_DARK)
    d.rounded_rectangle([80 * SS + LINE, 51 * SS + LINE, 88 * SS - LINE, 64 * SS], radius=3 * SS, fill=RUBBER_LIGHT)
    dome = (70, 51, 101, 92)
    d.pieslice(p(*dome), -90, 90, fill=INK)
    d.pieslice(inset(dome), -90, 90, fill=DARK)
    d.pieslice(inset(dome), -90, 0, fill=LIGHT)
    # Glass over the upper part only: drawn on its own layer and cut off at the jaw line.
    glass = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    dg = ImageDraw.Draw(glass)
    gbox = (74, 55, 98, 90)
    dg.pieslice(p(*gbox), -90, 90, fill=INK)
    dg.pieslice(inset(gbox), -90, 90, fill=GLASS_SHADE)
    dg.pieslice(inset(gbox), -90, 10, fill=GLASS)
    dg.ellipse(p(89, 58, 93, 64), fill=GLASS_SHINE)
    dg.rectangle([0, 73.5 * SS, W, W], fill=INK)
    keep = Image.new("L", (W, W), 0)
    ImageDraw.Draw(keep).pieslice(p(*gbox), -90, 90, fill=255)
    keep.paste(0, (0, int(73.5 * SS + LINE), W, W))
    glass.putalpha(ImageChops.multiply(glass.getchannel("A"), keep))
    img.alpha_composite(glass)
    d.rectangle(p(85, 52, 88, 91), fill=INK)
    d.rectangle([85 * SS + LINE / 2, 52 * SS + LINE, 88 * SS - LINE / 2, 91 * SS - LINE], fill=DARK)
    d.rectangle([85 * SS + LINE / 2, 52 * SS + LINE, 88 * SS - LINE / 2, 70 * SS], fill=LIGHT)
    chin_valve(d, 97, 83, 3.6)


# ---- Item sprite ---------------------------------------------------------------------------------------------------------

def item(key, master=False):
    img, d = new()
    fbox = (24, 22, 104, 118)
    if key == "A":
        for sx in (1, -1):
            hose(d, mirror([(34, 100), (22, 100)] + arc(22, 88, 12, 90, 180) + [(10, 32)], sx), 7)
        capsule(d, (2, 4, 126, 32), 18)
        for y in (48, 72):
            strap(d, (12, y, 30, y + 9))
            strap(d, (98, y, 116, y + 9))
        front(d, *fbox, 5, 6, 9, True)
    elif key == "B":
        for y in (40, 62):
            strap(d, (6, y, 30, y + 9))
            strap(d, (98, y, 122, y + 9))
        front(d, *fbox, 5, 6, 9, False)
        scrubber(d, (4, 74, 34, 112), 2)
        scrubber(d, (94, 74, 124, 112), 2)
    else:
        for sx in (1, -1):
            hose(d, mirror([(34, 100), (25, 100)] + arc(25, 88, 12, 90, 180) + [(13, 74)], sx), 7)
        canister(d, (2, 12, 24, 78), 12)
        canister(d, (104, 12, 126, 78), 12)
        for y in (40, 62):
            strap(d, (16, y, 30, y + 9))
            strap(d, (98, y, 112, y + 9))
        front(d, *fbox, 5, 6, 9, True)
    return with_outline(img, 4 * SS) if master else finish(img, 4)


def mirror(pts, sx):
    return pts if sx == 1 else [(S - x, y) for x, y in pts]


def export(master, fill=100):
    """The tier below's recipe: fit the master's alpha bounds into `fill` px of the 128 canvas, centred, one uniform Lanczos
    reduction from the 8x master."""
    crop = master.crop(master.getchannel("A").getbbox())
    scale = fill / max(crop.size)
    small = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    canvas.alpha_composite(small, ((S - small.width) // 2, (S - small.height) // 2))
    return canvas


# ---- Worn views (vanilla head frame) ------------------------------------------------------------------------------------

def worn(key):
    # South: the harness ends at the head's sides; the mask from the brow (y 51) to under the chin (y 92).
    s, d = new()
    if key == "A":
        # The canister's ends stand out past the head's sides, and the hoses run round to them.
        capsule(d, (33, 62, 95, 74), 9)
        d.rectangle(p(42, 61, 86, 75), fill=(0, 0, 0, 0))
        for sx in (1, -1):
            hose(d, mirror([(50, 85), (39, 74)], sx), 4)
    if key == "C":
        # The canisters' tops show over the crown.
        canister(d, (49, 30, 61, 46), 7)
        canister(d, (67, 30, 79, 46), 7)
    for y in (58, 72):
        strap(d, (37, 52 + (y - 58), 50, 57 + (y - 58)))
        strap(d, (78, 52 + (y - 58), 91, 57 + (y - 58)))
    if key == "C":
        for sx in (1, -1):
            hose(d, mirror([(50, 85), (40, 82)], sx), 4)
    front(d, 45, 50, 83, 92, 2, 2.4, 3.4, False)
    if key == "B":
        scrubber(d, (34, 70, 48, 91), 0)
        scrubber(d, (80, 70, 94, 91), 0)
    # East: facing right. The harness runs back over the side of the head to the back of the head.
    e, de = new()
    if key == "A":
        hose(de, [(82, 85), (54, 85), (44, 74)], 4)
        two_tone(de, (36, 60, 50, 76), RUBBER_LIGHT, RUBBER_DARK, 6)  # the canister end-on
    if key == "C":
        hose(de, [(82, 85), (50, 85), (44, 74)], 4)
        canister(de, (36, 28, 50, 76), 8)
    for y in (52, 66):
        strap(de, (46, y, 84, y + 5))
    if key == "B":
        scrubber(de, (64, 70, 82, 91), 0)
    side_profile(e, de)
    # North: the back of the head. The harness meets a back pad, which carries the scrubber canister(s) on A and C.
    n, dn = new()
    for y in (52, 66):
        strap(dn, (38, y, 58, y + 5))
        strap(dn, (70, y, 90, y + 5))
    if key == "B":
        scrubber(dn, (33, 70, 45, 91), 0)
        scrubber(dn, (83, 70, 95, 91), 0)
        two_tone(dn, (53, 50, 75, 76), LIGHT, DARK, 6)
        chin_valve(dn, 64, 63, 3)  # the pad's orange relief valve, so B reads from behind as well
    else:
        two_tone(dn, (53, 50, 75, 80), RUBBER_LIGHT, RUBBER_DARK, 6)
    if key == "A":
        for sx in (1, -1):
            hose(dn, mirror([(38, 72), (41, 86)], sx), 4)
        capsule(dn, (33, 60, 95, 75), 9)
    if key == "C":
        for sx in (1, -1):
            hose(dn, mirror([(54, 74), (42, 86)], sx), 4)
        canister(dn, (48, 30, 62, 76), 8)
        canister(dn, (66, 30, 80, 76), 8)
    return finish(s, 3), finish(e, 3), finish(n, 3)


# ---- Contact sheet (work output only, never shipped) ----------------------------------------------------------------------

def stand_in_head(direction):
    """A plain stand-in head on vanilla's frame, drawn here (the snorkel sheets'): not vanilla art."""
    img, d = new()
    box = (44, 39, 92, 89) if direction == "east" else (41, 39, 87, 89)
    d.rounded_rectangle(p(*box), radius=20 * SS, fill=SKIN)
    if direction == "north":
        d.rounded_rectangle(p(box[0], box[1], box[2], box[3] - 6), radius=20 * SS, fill=HAIR)
    else:
        d.rounded_rectangle(p(box[0], box[1], box[2], 52), radius=16 * SS, fill=HAIR)
    return finish(img, 3)


def vanilla_north_head():
    """The game's untinted north head, tinted as the game tints it (a multiply), with plain hair over the back of the head
    (the low-volume mask sheet's treatment). The hair is a stand-in shape: vanilla hair textures were not available offline."""
    src = Image.open(VANILLA_HEAD).convert("RGBA")
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    px, po = src.load(), out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            tint = HAIR if (y < 82 and r > 60) else SKIN
            po[x, y] = (r * tint[0] // 181, g * tint[1] // 181, b * tint[2] // 181, a)
    return out


def head(direction):
    if direction == "north" and VANILLA_HEAD:
        return vanilla_north_head()
    return stand_in_head(direction)


def on_head(direction, *layers):
    tile = head(direction).copy()
    for layer in layers:
        tile.alpha_composite(layer)
    return tile


def load(path):
    return Image.open(path).convert("RGBA")


def tinted(img, rgb, alpha):
    t = Image.new("RGBA", img.size, rgb + (0,))
    t.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    return t


# The approved face-down look C (art/face-down): shoulders and a waterline ring under the head, at the tuning the game uses.
# The same composite as the low-volume mask sheet's, used for every row.
WATER = (62, 98, 88, 255)
SHADOW, RING = (8, 20, 26), (215, 240, 255)
HEAD_CELLS = 1.5  # a humanlike head texture spans 1.5 cells
FACE_DOWN = [("Shoulders", SHADOW, 0.5, 0.95, 0.38), ("Waterline", RING, 0.45, 1.0, 0.10)]


def face_down(north_layers, px):
    """An offline composite of the face-down floater at `px` pixels per head texture: water, the shoulders and ring, then the
    north head with its worn north views in draw order. Not an in-game capture."""
    cell = px / HEAD_CELLS
    tile = Image.new("RGBA", (px, px), WATER)
    hc = px / 2, px * 0.47
    for name, rgb, alpha, size, dz in FACE_DOWN:
        tex = load(TEX / "Spearfishing" / "Dive" / f"{name}.png").resize((int(size * cell), int(size * cell)), Image.LANCZOS)
        tile.alpha_composite(tinted(tex, rgb, alpha), (int(hc[0] - tex.width / 2), int(hc[1] + dz * cell - tex.height / 2)))
    tile.alpha_composite(on_head("north", *north_layers).resize((px, px), Image.LANCZOS), (0, int(px * 0.03)))
    return tile


def font(size, bold=False):
    for name in (("segoeuib.ttf" if bold else "segoeui.ttf"), "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def side_by_side(images, tile_px, each_px):
    """Two items in one tile, each at each_px, for the tier-below row."""
    tile = Image.new("RGBA", (tile_px, tile_px), (0, 0, 0, 0))
    gap = (tile_px - each_px * len(images)) // (len(images) + 1)
    for i, im in enumerate(images):
        tile.alpha_composite(im.resize((each_px, each_px), Image.LANCZOS), (gap + i * (each_px + gap), (tile_px - each_px) // 2))
    return tile


def sheet(rows, path):
    """rows: (label, [items], [south layers], [east layers], [north layers]). Head tiles are 1.5x the 128 px game textures; the
    item is shown at 1.5x and at game size (one cell at 64 px, vanilla's rendering scale)."""
    big, game = int(S * 1.5), 64
    cols = ["Item 1.5x", "Item game size", "South", "East", "North", "Face down"]
    pad, label_w, head_h, title_h, foot_h = 18, 230, 34, 92, 104
    cw = [big, big, big, big, big, big]
    width = label_w + sum(cw) + pad * (len(cw) + 1)
    row_h = big + pad
    height = title_h + head_h + row_h * len(rows) + foot_h
    bg, card, fg, dim = (30, 31, 34), (98, 96, 90), (236, 236, 236), (170, 170, 176)
    out = Image.new("RGB", (width, height), bg)
    d = ImageDraw.Draw(out)
    d.rectangle([pad, 22, pad + 5, 76], fill=(96, 206, 222))
    d.text((pad + 18, 16), "Full-face mask, round 2: rebreather candidates (gear tiers ticket 09)", font=font(30, True), fill=fg)
    d.text((pad + 18, 56), "Beside the tier below: the approved low-volume mask A worn with the approved dry snorkel C. Face-down "
           "tiles are offline composites, not in-game captures.", font=font(17), fill=dim)
    x = label_w + pad
    for c, w in zip(cols, cw):
        tw = d.textlength(c, font=font(17))
        d.text((x + (w - tw) / 2, title_h + 4), c, font=font(17), fill=dim)
        x += w + pad
    for r, (label, items, south, east, north) in enumerate(rows):
        y = title_h + head_h + r * row_h
        d.multiline_text((pad, y + big / 2 - 24), label, font=font(20, r > 0), fill=fg)
        if len(items) == 1:
            i_big, i_game = items[0].resize((big, big), Image.LANCZOS), items[0].resize((game, game), Image.LANCZOS)
        else:
            i_big, i_game = side_by_side(items, big, S * 3 // 4), side_by_side(items, big, game)
        tiles = [i_big, i_game,
                 on_head("south", *south).resize((big, big), Image.NEAREST),
                 on_head("east", *east).resize((big, big), Image.NEAREST),
                 on_head("north", *north).resize((big, big), Image.NEAREST),
                 face_down(north, big)]
        x = label_w + pad
        for t, w in zip(tiles, cw):
            ty = y + (big - t.height) // 2
            if t.getpixel((0, 0))[3] == 255:
                out.paste(t.convert("RGB"), (x, ty))
            else:
                d.rounded_rectangle([x, y, x + w, y + big], radius=10, fill=card)
                out.paste(t, (x + (w - t.width) // 2, ty), t)
            x += w + pad
    notes = [
        "Item game size: the 128 px texture drawn at one cell, 64 px per cell (vanilla's scale). Tier-below items: 0.75x each at "
        "1.5x, 64 px each at game size.",
        ("South and east heads are a plain stand-in drawn by the script; the north and face-down head is vanilla's "
         "Male_Average_Normal north texture, tinted, with stand-in hair." if VANILLA_HEAD else
         "All heads are a plain stand-in drawn by the script, not vanilla art."),
        "Face down: approved look C (sunk shoulders + waterline ring) at the game's tuning; tier below as mask then snorkel.",
    ]
    for i, note in enumerate(notes):
        d.text((pad, height - foot_h + 12 + i * 28), note, font=font(16), fill=dim)
    out.save(path)


def tier_below():
    """Run the approved candidates' own scripts and load low-volume mask A and dry snorkel C."""
    lvm_dir, ds_dir = OUT / "tier-below" / "low-volume-mask", OUT / "tier-below" / "dry-snorkel"
    lvm_args = [sys.executable, "-I", str(ART / "low-volume-mask" / "low_volume_mask_art.py"), str(lvm_dir)]
    if VANILLA_HEAD:
        lvm_args.append(str(VANILLA_HEAD))
    # The approved scripts are slow, so a tier-below folder from an earlier run is reused.
    if not (lvm_dir / "LowVolumeMask_A_twin_north.png").exists():
        subprocess.run(lvm_args, check=True)
    if not (ds_dir / "DrySnorkel_C_black-orange_north.png").exists():
        subprocess.run([sys.executable, "-I", str(ART / "dry-snorkel" / "dry_snorkel_art.py"), str(ds_dir)], check=True)
    lvm = [load(lvm_dir / f"LowVolumeMask_A_twin{s}.png") for s in ("", "_south", "_east", "_north")]
    ds = [load(ds_dir / f"DrySnorkel_C_black-orange{s}.png") for s in ("", "_south", "_east", "_north")]
    return ("Tier below (approved)\nlow-volume mask A\n+ dry snorkel C", [lvm[0], ds[0]],
            [lvm[1], ds[1]], [lvm[2], ds[2]], [lvm[3], ds[3]])


if __name__ == "__main__":
    rows = [tier_below()]
    for key, name in STYLES.items():
        itm = export(item(key, master=True))
        itm.save(OUT / f"FullFaceMask_{key}_{name}.png")
        views = worn(key)
        for direction, im in zip(("south", "east", "north"), views):
            im.save(OUT / f"FullFaceMask_{key}_{name}_{direction}.png")
        rows.append((f"{key}: {name}", [itm], [views[0]], [views[1]], [views[2]]))
    sheet(rows, OUT / "contact_sheet.png")
    print(OUT / "contact_sheet.png")
