"""Full-face mask candidates for Spearfishing (gear tiers ticket 09). Procedural PIL drawing in the house rendering of the
approved glass mask, low-volume mask and dry snorkel (art/glass-mask, art/low-volume-mask, art/dry-snorkel): a few flat
two-tone shapes, a black outward outline and black lines between materials, no fine detail.

The spacer mask: plasteel and an advanced component. It covers the eyes and mouth and does the work of both a mask and a
snorkel, so it is one piece: a single tall visor over the whole face in a plasteel frame, a charcoal rubber skirt where it
seals on the face, a four-point rubber harness, and a snorkel tube built into the frame with a dry valve on top. It stays on the
face (the glossary avoids "diving helmet"): from behind only the harness, its pad and the tube show over the hair.

Same contract as the tier below: an item sprite (128x128, Graphic_Single, drawSize 1, 4 px outline at the 8x master's scale,
exported at about 100 px across) and worn views (128x128 head textures, _south, _east and _north, 3 px outline) on vanilla's
128 px head frame (head about x 41-87, y 39-89). The mask's bottom stays at y 92 or above. West mirrors east in game, so the
east view has no handed detail.

The candidates answer where the tube goes and how the back reads face down:
  A top-tube: the tube rises from the top of the frame, centred; plasteel tube and back pad, orange valve (the dry snorkel's).
  B side-tube: A's mask with the tube on the wearer's left, placed exactly as the dry snorkel's; plasteel pad, orange valve.
  C top-tube-cyan: A's layout in white plasteel with a cyan valve and cyan back pad, a brighter spacer finish.

Usage: python -I full_face_mask_art.py <out_dir> [<vanilla_head_north.png>]
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

from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
WHITE_LIGHT, WHITE_DARK = (232, 236, 238, 255), (172, 180, 188, 255)
GLASS, GLASS_SHADE, GLASS_SHINE = (150, 206, 214, 255), (112, 170, 184, 255), (226, 244, 246, 255)
POCKET = (96, 150, 166, 255)  # the inner breathing pocket, seen through the visor on the item
RUBBER_LIGHT, RUBBER_DARK = (88, 92, 98, 255), (58, 60, 66, 255)
ORANGE_LIGHT, ORANGE_DARK = (232, 128, 52, 255), (184, 90, 34, 255)
CYAN_LIGHT, CYAN_DARK = (96, 206, 222, 255), (46, 146, 170, 255)
SKIN, HAIR = (226, 184, 148, 255), (96, 66, 44, 255)
LINE = int(1.5 * SS)  # material line, 1.5 px at 128

# key: (name, shell light, shell dark, valve light, valve dark, back pad light, back pad dark, tube placement)
STYLES = {
    "A": ("top-tube", PLASTEEL_LIGHT, PLASTEEL_DARK, ORANGE_LIGHT, ORANGE_DARK, PLASTEEL_LIGHT, PLASTEEL_DARK, "top"),
    "B": ("side-tube", PLASTEEL_LIGHT, PLASTEEL_DARK, ORANGE_LIGHT, ORANGE_DARK, PLASTEEL_LIGHT, PLASTEEL_DARK, "side"),
    "C": ("top-tube-cyan", WHITE_LIGHT, WHITE_DARK, CYAN_LIGHT, CYAN_DARK, CYAN_LIGHT, CYAN_DARK, "top"),
}


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


# ---- The mask seen from the front ----------------------------------------------------------------------------------------

def oval_two_tone(d, box, light, dark):
    """An oval plate: black line, dark body, light upper half."""
    d.ellipse(p(*box), fill=INK)
    d.ellipse(inset(box), fill=dark)
    d.chord(inset(box), 180, 360, fill=light)


def front(d, key, x0, y0, x1, y1, skirt, frame, pocket):
    """The mask from the front, filling (x0, y0)-(x1, y1): the charcoal skirt as a rim, the plasteel frame, then one tall visor
    over the whole face with a shade, one shine and, on the item, the inner breathing pocket showing through the glass."""
    _, light, dark, *_rest = STYLES[key]
    oval_two_tone(d, (x0, y0, x1, y1), RUBBER_LIGHT, RUBBER_DARK)
    f = (x0 + skirt, y0 + skirt, x1 - skirt, y1 - skirt)
    oval_two_tone(d, f, light, dark)
    g = (f[0] + frame, f[1] + frame, f[2] - frame, f[3] - frame)
    d.ellipse(p(*g), fill=INK)
    gi = inset(g)
    d.ellipse(gi, fill=GLASS_SHADE)
    w, h = gi[2] - gi[0], gi[3] - gi[1]
    d.ellipse([gi[0], gi[1], gi[2] - w * 0.12, gi[3] - h * 0.16], fill=GLASS)
    if pocket:
        cx = (gi[0] + gi[2]) / 2
        d.rounded_rectangle([cx - w * 0.2, gi[1] + h * 0.56, cx + w * 0.2, gi[1] + h * 0.9], radius=w * 0.14, fill=POCKET)
    d.ellipse([gi[0] + w * 0.16, gi[1] + h * 0.1, gi[0] + w * 0.38, gi[1] + h * 0.3], fill=GLASS_SHINE)


def port(d, key, box):
    """The plasteel boss where the tube leaves the frame."""
    _, light, dark, *_rest = STYLES[key]
    two_tone(d, box, light, dark, 1.5)


# ---- Item sprite ---------------------------------------------------------------------------------------------------------

def item(key, master=False):
    _, light, dark, vlight, vdark, _pl, _pd, place = STYLES[key]
    img, d = new()
    # Harness ends behind the frame: an upper and a lower strap out to each side.
    for y in (52, 88):
        strap(d, (8, y, 30, y + 9))
        strap(d, (98, y, 120, y + 9))
    if place == "top":
        tube(d, [(64, 34), (64, 12)], 11, light, dark)
        valve(d, 64, 16, 19, 15, vlight, vdark, vents=2)
        front(d, key, 22, 30, 106, 122, 5, 6, pocket=True)
        port(d, key, (56, 26, 72, 38))
    else:
        tube(d, j_path(96, 92, 114, 14, 12), 11, light, dark)
        valve(d, 114, 18, 19, 15, vlight, vdark, vents=2)
        front(d, key, 14, 30, 98, 122, 5, 6, pocket=True)
        port(d, key, (90, 84, 102, 100))
    return with_outline(img, 4 * SS) if master else finish(img, 4)


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
    _, light, dark, vlight, vdark, plight, pdark, place = STYLES[key]
    # South: the harness ends at the head's sides; the mask from the brow (y 51) to under the chin (y 92).
    s, d = new()
    for y in (58, 76):
        strap(d, (37, y, 50, y + 5))
        strap(d, (78, y, 91, y + 5))
    if place == "top":
        tube(d, [(64, 54), (64, 30)], 6, light, dark)
        valve(d, 64, 31, 10, 10, vlight, vdark, vents=0)
    else:
        tube(d, j_path(80, 80, 92, 30, 7), 6, light, dark)
        valve(d, 92, 31, 10, 10, vlight, vdark, vents=0)
    front(d, key, 45, 50, 83, 92, 2, 2.4, pocket=False)
    if place == "top":
        port(d, key, (60, 48, 68, 55))
    # East: facing right. The harness runs back over the side of the head; at the front the skirt seals on the face and the
    # visor stands proud of it as a dome.
    e, de = new()
    for y in (58, 76):
        strap(de, (46, y, 84, y + 5))
    if place == "top":
        tube(de, [(88, 54), (88, 30)], 6, light, dark)
        valve(de, 88, 31, 10, 10, vlight, vdark, vents=0)
    else:
        tube(de, [(86, 82), (56, 82)] + arc(56, 75, 7, 90, 180) + [(49, 30)], 6, light, dark)
        valve(de, 49, 31, 10, 10, vlight, vdark, vents=0)
    de.rounded_rectangle(p(80, 51, 88, 92), radius=3.5 * SS, fill=INK)
    de.rounded_rectangle(inset((80, 51, 88, 92)), radius=3.5 * SS - LINE, fill=RUBBER_DARK)
    de.rounded_rectangle([80 * SS + LINE, 51 * SS + LINE, 88 * SS - LINE, 64 * SS], radius=3 * SS, fill=RUBBER_LIGHT)
    dome = (70, 51, 101, 92)
    de.pieslice(p(*dome), -90, 90, fill=INK)
    de.pieslice(inset(dome), -90, 90, fill=dark)
    de.pieslice(inset(dome), -90, 0, fill=light)
    glass = (74, 55, 98, 88)
    de.pieslice(p(*glass), -90, 90, fill=INK)
    de.pieslice(inset(glass), -90, 90, fill=GLASS_SHADE)
    de.pieslice(inset(glass), -90, 30, fill=GLASS)
    de.ellipse(p(89, 58, 93, 64), fill=GLASS_SHINE)
    # The frame's edge where it meets the skirt, a plasteel band down the dome's flat side.
    de.rectangle(p(85, 52, 88, 91), fill=INK)
    de.rectangle([85 * SS + LINE / 2, 52 * SS + LINE, 88 * SS - LINE / 2, 91 * SS - LINE], fill=dark)
    de.rectangle([85 * SS + LINE / 2, 52 * SS + LINE, 88 * SS - LINE / 2, 70 * SS], fill=light)
    if place == "top":
        port(de, key, (84, 48, 92, 55))
    # North: the back of the head. Four harness straps meet a plasteel back pad (cyan on C), so the mask reads from behind and
    # face down against dark hair, and apart from the low-volume mask's charcoal pad. A top tube stands above the crown; a side
    # tube runs up the wearer's left, as the dry snorkel's does.
    n, dn = new()
    strap(dn, (40, 56, 58, 61))
    strap(dn, (70, 56, 88, 61))
    strap(dn, (40, 76, 58, 81))
    strap(dn, (70, 76, 88, 81))
    two_tone(dn, (53, 54, 75, 83), plight, pdark, 6)
    if place == "top":
        tube(dn, [(64, 44), (64, 30)], 6, light, dark)
        valve(dn, 64, 31, 10, 10, vlight, vdark, vents=0)
    else:
        tube(dn, [(43, 82), (43, 30)], 6, light, dark)
        valve(dn, 43, 31, 10, 10, vlight, vdark, vents=0)
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
    d.text((pad + 18, 16), "Full-face mask: candidates (gear tiers ticket 09)", font=font(30, True), fill=fg)
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
    subprocess.run(lvm_args, check=True)
    subprocess.run([sys.executable, "-I", str(ART / "dry-snorkel" / "dry_snorkel_art.py"), str(ds_dir)], check=True)
    lvm = [load(lvm_dir / f"LowVolumeMask_A_twin{s}.png") for s in ("", "_south", "_east", "_north")]
    ds = [load(ds_dir / f"DrySnorkel_C_black-orange{s}.png") for s in ("", "_south", "_east", "_north")]
    return ("Tier below (approved)\nlow-volume mask A\n+ dry snorkel C", [lvm[0], ds[0]],
            [lvm[1], ds[1]], [lvm[2], ds[2]], [lvm[3], ds[3]])


if __name__ == "__main__":
    rows = [tier_below()]
    for key, (name, *_rest) in STYLES.items():
        itm = export(item(key, master=True))
        itm.save(OUT / f"FullFaceMask_{key}_{name}.png")
        views = worn(key)
        for direction, im in zip(("south", "east", "north"), views):
            im.save(OUT / f"FullFaceMask_{key}_{name}_{direction}.png")
        rows.append((f"{key}: {name}", [itm], [views[0]], [views[1]], [views[2]]))
    sheet(rows, OUT / "contact_sheet.png")
    print(OUT / "contact_sheet.png")
