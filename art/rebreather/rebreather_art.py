"""Rebreather (gear tiers ticket 09) for Spearfishing: the approved candidate A, the cylinder, without its head strap, and the
game textures. Procedural PIL drawing in the house rendering of the approved low-volume mask A and dry snorkel C
(art/low-volume-mask, art/dry-snorkel): a few flat two-tone shapes, a black outward outline and black lines between materials,
no fine detail. The plasteel and orange palette is round 2's (art/full-face-mask/rebreather_mask_art.py).

The spacer tier's head piece is a small rebreather held in the mouth. It takes the snorkel's slot and draw layer, so it is worn
with a mask and draws over it, and it has no tube to the surface. It stays small, covering the mouth and staying within the face.
The design is our own, after a reference photo of a compact breathing unit held across a swimmer's mouth; no game's art is used.

Round 3 drew three candidates (A cylinder, B twin-cartridges, C puck), each with a thin rubber head strap round the nape and a
clip at the back. The author picked A on 2026-11-17 "but don add a backstrap", so this script draws A only, with no strap and no
clip: from behind and face down nothing shows, as the head hides the unit. Round 3's script is in git history
(SHA-256 d3348f12c7f1bd00fcd9fa8ac76497872be8f73115fa0aac7df31557bcf81649); see APPROVAL.md.
  A cylinder: one short rounded cylinder lying across the mouth, plasteel with rubber end caps and an orange centre band, on a
    rubber bite flange. Seen from the side, it is end-on: a round cap.

Same contract as the tier below: an item sprite (128x128, Graphic_Single, drawSize 1, 4 px outline at the 8x master's scale,
exported with its alpha bounds fitted to 100 px) and worn views (128x128 head textures, _south, _east and _north, 3 px outline)
on vanilla's 128 px head frame (head about x 41-87, y 39-89; the mouth about y 82-90 under the low-volume mask's nose pocket).
Nothing goes below y 92. West mirrors east in game, so every view is symmetric or unhanded. The north view is fully transparent
and still written, so the game never falls back to another facing's texture from behind.

Usage: python -I rebreather_art.py <out_dir> [<vanilla_head_north.png>]
Writes Rebreather_A_cylinder.png and its _south, _east and _north views and contact_sheet.png to <out_dir>, and the same four
images as the game textures Rebreather.png and Rebreather_<facing>.png to Textures/Things/Spearfishing/Apparel/Rebreather/.
For the tier-below row it runs the approved candidates' own scripts (art/low-volume-mask, art/dry-snorkel) into
<out_dir>/tier-below, unless an earlier run left them there, and reads low-volume mask A and dry snorkel C from there; low-volume
mask A is also the mask the rebreather is worn with on the sheet. The optional vanilla head (an untinted north head dumped from
the game, e.g. work/vanilla-ref/head_Male_Average_Normal_north.png) is used only to place the north and face-down views on the
sheet; it is never written out and never goes into the textures. Without it the sheet uses the plain stand-in head.
"""
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
GAME = TEX / "Things" / "Spearfishing" / "Apparel" / "Rebreather"
SS = 8
S = 128
W = S * SS
INK = (12, 10, 10, 255)
LIGHT, DARK = (178, 196, 202, 255), (118, 136, 146, 255)  # plasteel
RUBBER_LIGHT, RUBBER_DARK = (88, 92, 98, 255), (58, 60, 66, 255)
ACCENTS = {"orange": ((232, 128, 52, 255), (184, 90, 34, 255))}
SKIN, HAIR = (226, 184, 148, 255), (96, 66, 44, 255)
LINE = int(1.5 * SS)  # material line, 1.5 px at 128

# key: (name, accent)
STYLES = {"A": ("cylinder", "orange")}


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


def two_tone(d, box, light, dark, radius):
    """Black line, dark body, light upper half: the house treatment for one material plate."""
    x0, y0, x1, y1 = box
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=radius * SS, fill=INK)
    d.rounded_rectangle([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, y1 * SS - LINE], radius=max(0, radius * SS - LINE),
                        fill=dark)
    d.rounded_rectangle([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, (y0 + y1) / 2 * SS], radius=max(0, radius * SS - LINE),
                        fill=light)


def disc(d, cx, cy, r, light, dark):
    """A round plate: black line, dark body, light upper-left half."""
    d.ellipse([(cx - r) * SS - LINE, (cy - r) * SS - LINE, (cx + r) * SS + LINE, (cy + r) * SS + LINE], fill=INK)
    d.ellipse(p(cx - r, cy - r, cx + r, cy + r), fill=dark)
    d.chord(p(cx - r, cy - r, cx + r, cy + r), 135, 315, fill=light)


def slits(d, x0, x1, ys, h=0.7):
    for y in ys:
        d.rounded_rectangle(p(x0, y - h, x1, y + h), radius=h * SS, fill=INK)


# ---- The unit --------------------------------------------------------------------------------------------------------------

def cylinder(d, box, cap, accent):
    """A short scrubber cylinder lying across: rubber end caps, a plasteel body and an accent band at the middle."""
    x0, y0, x1, y1 = box
    al, ad = ACCENTS[accent]
    two_tone(d, box, RUBBER_LIGHT, RUBBER_DARK, (y1 - y0) / 2)
    two_tone(d, (x0 + cap, y0, x1 - cap, y1), LIGHT, DARK, 1.5)
    band = (x1 - x0) * 0.09
    cx = (x0 + x1) / 2
    two_tone(d, (cx - band, y0 - (y1 - y0) * 0.06, cx + band, y1 + (y1 - y0) * 0.06), al, ad, 1.5)


def end_cap(d, cx, cy, r, accent):
    """A cylinder seen end-on: a rubber cap with an accent ring round a plasteel centre."""
    al, ad = ACCENTS[accent]
    disc(d, cx, cy, r, RUBBER_LIGHT, RUBBER_DARK)
    disc(d, cx, cy, r * 0.62, al, ad)
    disc(d, cx, cy, r * 0.32, LIGHT, DARK)


# ---- Item sprite -----------------------------------------------------------------------------------------------------------

def item(key, master=False):
    """The unit from the front: the cylinder on its bite flange, with no strap."""
    _, accent = STYLES[key]
    img, d = new()
    two_tone(d, (48, 40, 80, 80), RUBBER_LIGHT, RUBBER_DARK, 10)  # bite flange behind the cylinder
    cylinder(d, (8, 46, 120, 74), 20, accent)
    for x in (36, 92):
        slits(d, x - 6, x + 6, [55, 60, 65])
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


# ---- Worn views (vanilla head frame) ---------------------------------------------------------------------------------------

def worn(key):
    _, accent = STYLES[key]
    # South: across the mouth, just under the low-volume mask's nose pocket (which ends at about y 82) and overlapping its
    # bottom edge, as a mouthpiece sits right under the nose.
    s, d = new()
    cylinder(d, (49, 77.5, 79, 87.5), 5.5, accent)
    # East: facing right. The unit stands just proud of the mouth, in front of the face like the mask's nose pocket: its bite
    # flange and the near end cap, end-on. No strap runs back across the cheek.
    e, de = new()
    two_tone(de, (86, 77, 94, 88), RUBBER_LIGHT, RUBBER_DARK, 3)  # bite flange
    end_cap(de, 95, 82.5, 5.4, accent)
    # North: the back of the head. The head hides the unit and there is no strap, so nothing is drawn.
    n, _ = new()
    return finish(s, 3), finish(e, 3), finish(n, 3)


# ---- Contact sheet (work output only, never shipped) -----------------------------------------------------------------------

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
    """rows: (label, [items], [south layers], [east layers], [north layers], [south layers with the glass mask]). Head tiles are
    1.5x the 128 px game textures; the item is shown at 1.5x and at game size (one cell at 64 px, vanilla's rendering scale)."""
    big, game = int(S * 1.5), 64
    cols = ["Item 1.5x", "Item game size", "South", "East", "North", "Face down", "South, glass mask"]
    pad, label_w, head_h, title_h, foot_h = 18, 230, 34, 92, 132
    cw = [big] * len(cols)
    width = label_w + sum(cw) + pad * (len(cw) + 1)
    row_h = big + pad
    height = title_h + head_h + row_h * len(rows) + foot_h
    bg, card, fg, dim = (30, 31, 34), (98, 96, 90), (236, 236, 236), (170, 170, 176)
    out = Image.new("RGB", (width, height), bg)
    d = ImageDraw.Draw(out)
    d.rectangle([pad, 22, pad + 5, 76], fill=(96, 206, 222))
    d.text((pad + 18, 16), "Rebreather, final: approved A without the head strap (gear tiers ticket 09)", font=font(30, True), fill=fg)
    d.text((pad + 18, 56), "In the snorkel's slot, worn with the approved low-volume mask A (south, east, north, face down) and with "
           "the approved glass mask (last column). Face-down tiles are offline composites.", font=font(17), fill=dim)
    x = label_w + pad
    for c, w in zip(cols, cw):
        tw = d.textlength(c, font=font(17))
        d.text((x + (w - tw) / 2, title_h + 4), c, font=font(17), fill=dim)
        x += w + pad
    for r, (label, items, south, east, north, glass) in enumerate(rows):
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
                 face_down(north, big),
                 on_head("south", *glass).resize((big, big), Image.NEAREST)]
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
        "Face down: approved look C (sunk shoulders + waterline ring) at the game's tuning; mask, then snorkel or rebreather.",
        "No strap and no tube: from behind and face down only the mask shows. The rebreather's north texture is empty.",
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
    return lvm, ds


if __name__ == "__main__":
    lvm, ds = tier_below()
    glass_south = load(TEX / "Things" / "Spearfishing" / "Apparel" / "GlassMask" / "GlassMask_south.png")
    rows = [("Tier below (approved)\nlow-volume mask A\n+ dry snorkel C", [lvm[0], ds[0]],
             [lvm[1], ds[1]], [lvm[2], ds[2]], [lvm[3], ds[3]], [glass_south, ds[1]])]
    GAME.mkdir(parents=True, exist_ok=True)
    for key, (name, _) in STYLES.items():
        itm = export(item(key, master=True))
        itm.save(OUT / f"Rebreather_{key}_{name}.png")
        views = worn(key)
        for direction, im in zip(("south", "east", "north"), views):
            im.save(OUT / f"Rebreather_{key}_{name}_{direction}.png")
        rows.append((f"{key}: {name}\n(no strap)", [itm], [lvm[1], views[0]], [lvm[2], views[1]], [lvm[3], views[2]],
                     [glass_south, views[0]]))
    # The approved candidate (A without its strap, 2026-11-17; APPROVAL.md) as the game textures, by the tier below's recipe:
    # the item from the 8x master fitted to 100 px, the worn views as drawn. West mirrors east in game.
    export(item("A", master=True)).save(GAME / "Rebreather.png")
    for direction, im in zip(("south", "east", "north"), worn("A")):
        im.save(GAME / f"Rebreather_{direction}.png")
    sheet(rows, OUT / "contact_sheet.png")
    print(OUT / "contact_sheet.png")
