"""Low-volume mask candidates for Spearfishing (gear tiers ticket 03). Procedural PIL drawing in the house rendering of the
approved glass mask (art/glass-mask): a few flat two-tone shapes, a black outward outline and black lines between materials,
no fine detail.

The industrial mask: a pressed steel frame, tempered glass and a skirt of chemfuel rubber. Where the glass mask is one wide
visor in a steel frame on a leather strap, this one sits low on the face: small lenses close to the eyes, a rubber skirt with a
nose pocket, and a rubber strap with steel buckles. The rubber is charcoal, not black, so the black material lines still show.

Same contract as the glass mask: an item sprite (128x128, Graphic_Single, drawSize 1, 4 px outline at the 8x master's scale,
exported at about 100 px across) and worn views for the EyeCover layer (128x128 head textures, _south, _east and _north, 3 px
outline) on vanilla's 128 px head frame (head about x 41-87, y 39-89, strap near y 70). Everything stays above y 82 so the
approved snorkel's mouthpiece (y 82-90) still fits under it. West mirrors east in game, so the east view has no handed detail.

Usage: python -I low_volume_mask_art.py <out_dir> [<vanilla_head_north.png>]
Writes LowVolumeMask_<X>_<name>.png and its _south, _east and _north views, contact_sheet.png, and the approved A twin's
game textures (APPROVAL.md): LowVolumeMask.png (item, export at 100 px) and LowVolumeMask_<dir>.png (worn views, unchanged). The optional vanilla head
(an untinted north head dumped from the game, e.g. work/vanilla-ref/head_Male_Average_Normal_north.png) is used only to place
the north and face-down views on the sheet; it is never written out on its own and never goes into the textures. Without it the
sheet uses the plain stand-in head the snorkel's sheet used.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
VANILLA_HEAD = Path(sys.argv[2]) if len(sys.argv) > 2 else None
HERE = Path(__file__).resolve().parent
TEX = HERE.parent.parent / "Textures"
APPAREL = TEX / "Things" / "Spearfishing" / "Apparel"
SS = 8
S = 128
W = S * SS
INK = (12, 10, 10, 255)
STEEL_LIGHT, STEEL_DARK = (196, 200, 204, 255), (138, 144, 150, 255)
GLASS, GLASS_SHADE, GLASS_SHINE = (150, 206, 214, 255), (112, 170, 184, 255), (226, 244, 246, 255)
RUBBER_LIGHT, RUBBER_DARK = (88, 92, 98, 255), (58, 60, 66, 255)
HIVIS_LIGHT, HIVIS_DARK = (232, 182, 54, 255), (190, 136, 30, 255)
SKIN, SKIN_DARK, HAIR = (226, 184, 148, 255), (196, 152, 118, 255), (96, 66, 44, 255)
LINE = int(1.5 * SS)  # material line, 1.5 px at 128

# Candidate: (name, strap light, strap dark, lens style)
STYLES = {
    "A": ("twin", RUBBER_LIGHT, RUBBER_DARK, "twin"),
    "B": ("lowvisor", RUBBER_LIGHT, RUBBER_DARK, "single"),
    "C": ("twin-hivis", HIVIS_LIGHT, HIVIS_DARK, "twin"),
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


def skirt(d, box, nose):
    """The rubber skirt: a wide rounded plate with a nose pocket hanging under its middle. nose = (x0, x1, y_bottom)."""
    x0, y0, x1, y1 = box
    nx0, nx1, ny = nose
    r = (y1 - y0) * 0.38
    nr = (nx1 - nx0) * 0.45
    # Ink silhouette of both, then the fills, so the pocket joins the skirt without a line between them.
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=r * SS, fill=INK)
    d.rounded_rectangle(p(nx0, (y0 + y1) / 2, nx1, ny), radius=nr * SS, fill=INK)
    d.rounded_rectangle(inset((x0, y0, x1, y1)), radius=r * SS - LINE, fill=RUBBER_DARK)
    d.rounded_rectangle(inset((nx0, (y0 + y1) / 2, nx1, ny)), radius=nr * SS - LINE, fill=RUBBER_DARK)
    d.rounded_rectangle([x0 * SS + LINE, y0 * SS + LINE, x1 * SS - LINE, (y0 + (y1 - y0) * 0.42) * SS], radius=r * SS - LINE,
                        fill=RUBBER_LIGHT)
    # One light stripe down the pocket's left side, as the fins and spear catch the light from the upper left.
    w = nx1 - nx0
    d.rounded_rectangle([(nx0 + w * 0.22) * SS, (y1 - 1) * SS, (nx0 + w * 0.42) * SS, (ny - w * 0.3) * SS], radius=w * 0.1 * SS,
                        fill=RUBBER_LIGHT)


def lens(d, box, rim, radius):
    """A pressed steel rim around tempered glass: black line, two-tone steel, black line, glass with a shade and one shine."""
    x0, y0, x1, y1 = box
    two_tone(d, box, STEEL_LIGHT, STEEL_DARK, radius)
    g = (x0 + rim, y0 + rim, x1 - rim, y1 - rim)
    gr = max(0.5, radius - rim)
    d.rounded_rectangle(p(*g), radius=gr * SS, fill=INK)
    gi = inset(g)
    d.rounded_rectangle(gi, radius=max(0, gr * SS - LINE), fill=GLASS_SHADE)
    d.rounded_rectangle([gi[0], gi[1], gi[2] - (gi[2] - gi[0]) * 0.14, gi[3] - (gi[3] - gi[1]) * 0.2],
                        radius=max(0, gr * SS - LINE), fill=GLASS)
    w, h = gi[2] - gi[0], gi[3] - gi[1]
    d.ellipse([gi[0] + w * 0.14, gi[1] + h * 0.14, gi[0] + w * 0.44, gi[1] + h * 0.42], fill=GLASS_SHINE)


def buckle(d, box):
    """A small pressed steel buckle where the strap meets the frame."""
    two_tone(d, box, STEEL_LIGHT, STEEL_DARK, 1.2)


def strap(d, box, light, dark):
    x0, y0, x1, y1 = box
    two_tone(d, box, light, dark, (y1 - y0) / 2)


def strap_loop(d, cx, cy, rx, ry, width, light):
    """The strap behind the item: a thick ellipse ring seen from the front."""
    d.ellipse(p(cx - rx, cy - ry, cx + rx, cy + ry), fill=INK)
    d.ellipse(inset((cx - rx, cy - ry, cx + rx, cy + ry)), fill=light)
    d.ellipse(p(cx - rx + width, cy - ry + width, cx + rx - width, cy + ry - width), fill=INK)
    d.ellipse(inset((cx - rx + width, cy - ry + width, cx + rx - width, cy + ry - width)), fill=(0, 0, 0, 0))


def front(d, key, x0, y0, x1, y1, rim, buckles=True):
    """The mask seen from the front, filling (x0, y0)-(x1, y1) with its skirt; the nose pocket hangs below y1."""
    _, light, dark, style = STYLES[key]
    w, h = x1 - x0, y1 - y0
    cx = (x0 + x1) / 2
    nose = (cx - w * 0.14, cx + w * 0.14, y1 + h * 0.34)
    skirt(d, (x0, y0, x1, y1), nose)
    m = w * 0.07  # skirt margin around the frame
    if style == "twin":
        gap = w * 0.05
        lw = (w - 2 * m - gap) / 2
        ly0, ly1 = y0 + h * 0.12, y1 - h * 0.18
        # Pressed steel bridge between the lenses, over the nose.
        two_tone(d, (cx - gap - 1, ly0 + (ly1 - ly0) * 0.25, cx + gap + 1, ly0 + (ly1 - ly0) * 0.6), STEEL_LIGHT, STEEL_DARK, 0.5)
        lens(d, (x0 + m, ly0, x0 + m + lw, ly1), rim, (ly1 - ly0) * 0.32)
        lens(d, (x1 - m - lw, ly0, x1 - m, ly1), rim, (ly1 - ly0) * 0.32)
    else:
        ly0, ly1 = y0 + h * 0.14, y1 - h * 0.24
        lens(d, (x0 + m, ly0, x1 - m, ly1), rim, (ly1 - ly0) * 0.3)
    if buckles:
        bh = h * 0.34
        by = y0 + h * 0.3
        bw = max(4, w * 0.07)
        buckle(d, (x0 - bw * 0.6, by, x0 + bw * 0.4, by + bh))
        buckle(d, (x1 - bw * 0.4, by, x1 + bw * 0.6, by + bh))


# ---- Item sprite ---------------------------------------------------------------------------------------------------------

def item(key, master=False):
    _, light, dark, _ = STYLES[key]
    img, d = new()
    strap_loop(d, 64, 68, 54, 30, 8, light)
    front(d, key, 14, 34, 114, 84, 6.5)
    return with_outline(img, 4 * SS) if master else finish(img, 4)


def export(master, fill=100):
    """The glass mask's and fins' recipe: fit the master's alpha bounds into `fill` px of the 128 canvas, centred, one uniform
    Lanczos reduction from the 8x master."""
    crop = master.crop(master.getchannel("A").getbbox())
    scale = fill / max(crop.size)
    small = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    canvas.alpha_composite(small, ((S - small.width) // 2, (S - small.height) // 2))
    return canvas


# ---- Worn views (vanilla head frame) ------------------------------------------------------------------------------------

def worn(key):
    _, light, dark, style = STYLES[key]
    # South: the strap ends show at the head's sides; the mask sits low on the eyes, the pocket over the nose, above y 82.
    s, d = new()
    strap(d, (37, 66, 46, 72), light, dark)
    strap(d, (82, 66, 91, 72), light, dark)
    front(d, key, 42, 58, 86, 76, 2.6, buckles=False)
    buckle(d, (40, 64, 46, 74))
    buckle(d, (82, 64, 88, 74))
    # East: facing right. The strap runs back over the side of the head; at the front the skirt stands proud of the face with
    # the glass at its front edge and the nose pocket under it.
    e, de = new()
    strap(de, (42, 66, 84, 72), light, dark)
    de.rounded_rectangle(p(82, 57, 95, 77), radius=5 * SS, fill=INK)
    de.rounded_rectangle(p(86, 72, 97, 83), radius=4 * SS, fill=INK)
    de.rounded_rectangle(inset((82, 57, 95, 77)), radius=5 * SS - LINE, fill=RUBBER_DARK)
    de.rounded_rectangle(inset((86, 72, 97, 83)), radius=4 * SS - LINE, fill=RUBBER_DARK)
    de.rounded_rectangle([82 * SS + LINE, 57 * SS + LINE, 95 * SS - LINE, 65 * SS], radius=4 * SS, fill=RUBBER_LIGHT)
    # Pressed steel frame edge, then the glass seen edge-on at the front.
    de.rectangle(p(89, 58, 93.5, 74), fill=INK)
    de.rectangle([89 * SS + LINE, 58 * SS + LINE, 93.5 * SS - LINE, 74 * SS - LINE], fill=STEEL_DARK)
    de.rectangle([89 * SS + LINE, 58 * SS + LINE, 93.5 * SS - LINE, 64 * SS], fill=STEEL_LIGHT)
    de.rounded_rectangle([93 * SS, 60 * SS, 96 * SS - LINE / 2, 72 * SS], radius=1.5 * SS, fill=GLASS)
    buckle(de, (79, 64, 85, 74))
    # North: the back of the head, also drawn turned for a face-down floater. One thin silicone strap across the back, at the
    # height of the strap ends in the south and east views, as the glass mask's leather strap is drawn; the rubber's charcoal
    # tells the two apart face down. The first draw (2026-11-17) had two straps on a wide back pad with side buckles: with a
    # 3 px outline each, the outlines merged into one dark block over the hair in game.
    n, dn = new()
    strap(dn, (39, 66, 89, 72), light, dark)
    return finish(s, 3), finish(e, 3), finish(n, 3)


# ---- Contact sheet (work output only, never shipped) ----------------------------------------------------------------------

def stand_in_head(direction):
    """A plain stand-in head on vanilla's frame, drawn here (the snorkel sheet's): not vanilla art."""
    img, d = new()
    box = (44, 39, 92, 89) if direction == "east" else (41, 39, 87, 89)
    d.rounded_rectangle(p(*box), radius=20 * SS, fill=SKIN)
    if direction == "north":
        d.rounded_rectangle(p(box[0], box[1], box[2], box[3] - 6), radius=20 * SS, fill=HAIR)
    else:
        d.rounded_rectangle(p(box[0], box[1], box[2], 52), radius=16 * SS, fill=HAIR)
    return finish(img, 3)


def vanilla_north_head():
    """The game's untinted north head, tinted as the game tints it (a multiply), with plain hair over the back of the head.
    The hair is a stand-in shape: vanilla hair textures were not available offline."""
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
    north head with its worn north views (mask under snorkel, as layers 66 and 67). Not an in-game capture."""
    cell = px / HEAD_CELLS
    tile = Image.new("RGBA", (px, px), WATER)
    hc = px / 2, px * 0.47  # head centre in the tile (the head sits a little above the texture's centre)
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


def sheet(rows, path):
    """Rows of (label, item, south, east, north, snorkel north). Every head tile is 1.5x the 128 px game texture; the item is
    shown at 1.5x and at its game size (1 cell, 128 px texture at 1x)."""
    big = int(S * 1.5)
    snork = {dname: load(APPAREL / "Snorkel" / f"Snorkel_{dname}.png") for dname in ("south", "east", "north")}
    cols = ["Item 1.5x", "Item 1x", "South", "East", "North", "South + snorkel", "Face down", "Face down + snorkel"]
    pad, label_w, head_h, title_h, foot_h = 18, 190, 34, 92, 80
    cw = [big, S, big, big, big, big, big, big]
    width = label_w + sum(cw) + pad * (len(cw) + 1)
    row_h = big + pad
    height = title_h + head_h + row_h * len(rows) + foot_h
    bg, card, fg, dim = (30, 31, 34), (98, 96, 90), (236, 236, 236), (170, 170, 176)
    out = Image.new("RGB", (width, height), bg)
    d = ImageDraw.Draw(out)
    d.rectangle([pad, 22, pad + 5, 76], fill=(232, 182, 54))
    d.text((pad + 18, 16), "Low-volume mask: candidates (gear tiers ticket 03)", font=font(30, True), fill=fg)
    d.text((pad + 18, 56), "Beside the approved glass mask. Head tiles are 1.5x the 128 px game textures; face-down tiles are "
           "offline composites, not in-game captures.", font=font(17), fill=dim)
    x = label_w + pad
    for c, w in zip(cols, cw):
        tw = d.textlength(c, font=font(17))
        d.text((x + (w - tw) / 2, title_h + 4), c, font=font(17), fill=dim)
        x += w + pad
    for r, (label, itm, s, e, n) in enumerate(rows):
        y = title_h + head_h + r * row_h
        d.text((pad, y + big / 2 - 12), label, font=font(20, r > 0), fill=fg)
        snor = [on_head("south", s, snork["south"])]
        tiles = [itm.resize((big, big), Image.LANCZOS), itm,
                 on_head("south", s).resize((big, big), Image.NEAREST),
                 on_head("east", e).resize((big, big), Image.NEAREST),
                 on_head("north", n).resize((big, big), Image.NEAREST),
                 snor[0].resize((big, big), Image.NEAREST),
                 face_down([n], big), face_down([n, snork["north"]], big)]
        x = label_w + pad
        for t, w in zip(tiles, cw):
            ty = y + (big - t.height) // 2
            if t.getpixel((0, 0))[3] == 255:
                out.paste(t.convert("RGB"), (x, ty))
            else:
                d.rounded_rectangle([x, ty, x + t.width, ty + t.height], radius=10, fill=card)
                out.paste(t, (x, ty), t)
            x += w + pad
    foot = ("South and east heads are a plain stand-in drawn by the script (the snorkel sheet's); the north and face-down head "
            "is vanilla's Male_Average_Normal north texture, tinted, with stand-in hair." if VANILLA_HEAD else
            "All heads are a plain stand-in drawn by the script (the snorkel sheet's), not vanilla art.")
    d.text((pad, height - foot_h + 14), foot, font=font(16), fill=dim)
    d.text((pad, height - foot_h + 40), "Face down: approved look C (sunk shoulders + waterline ring) at the game's tuning; mask "
           "strap under the snorkel, as layers 66 and 67.", font=font(16), fill=dim)
    out.save(path)


if __name__ == "__main__":
    rows = []
    gm = APPAREL / "GlassMask"
    rows.append(("Glass mask\n(approved)", load(gm / "GlassMask.png"), load(gm / "GlassMask_south.png"),
                 load(gm / "GlassMask_east.png"), load(gm / "GlassMask_north.png")))
    for key, (name, *_rest) in STYLES.items():
        itm = export(item(key, master=True))
        itm.save(OUT / f"LowVolumeMask_{key}_{name}.png")
        views = worn(key)
        for direction, im in zip(("south", "east", "north"), views):
            im.save(OUT / f"LowVolumeMask_{key}_{name}_{direction}.png")
        rows.append((f"{key}: {name}", itm, *views))
    sheet(rows, OUT / "contact_sheet.png")
    # Approved: A twin. The item goes through the glass mask's 100 px export; the worn views are already at their game size.
    export(item("A", master=True)).save(OUT / "LowVolumeMask.png")
    for direction, im in zip(("south", "east", "north"), worn("A")):
        im.save(OUT / f"LowVolumeMask_{direction}.png")
