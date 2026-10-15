"""Generate placeholder pixel-art tiles and props (stone, moss, wood, torch, banner, chain, ladder, statue).

Run from AshenVeil_Python/:  python tools/gen_tiles.py      Needs: numpy, pillow.
Output: assets/tiles/*.png (32x32 tiles in one strip) and assets/props/*.png.
"""
from pathlib import Path
import random
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent / "assets"
T = 32
STONE = [(30, 32, 42), (44, 47, 60), (62, 64, 76), (88, 88, 98)]
MORTAR = (20, 21, 29)
MOSS = [(36, 54, 34), (58, 82, 44), (92, 112, 58)]
WOOD = [(40, 26, 20), (66, 42, 28), (96, 64, 38), (128, 88, 50)]
IRON = [(22, 22, 28), (46, 46, 56), (84, 86, 98)]
RED = [(52, 14, 20), (98, 26, 32), (150, 44, 44)]
FLAME = [(190, 50, 20), (240, 130, 30), (255, 200, 80), (255, 245, 200)]


def bricks(seed, w=T, h=T, bw=16, bh=8, cols=STONE, moss_top=False, dark=False):
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), MORTAR + (255,))
    d = ImageDraw.Draw(im)
    for row in range(h // bh):
        off = (bw // 2) if row % 2 else 0
        for x in range(-off, w, bw):
            base = rnd.choice(cols[:3] if not dark else cols[:2])
            x0, y0 = max(x + 1, 0), row * bh + 1
            x1, y1 = min(x + bw - 1, w - 1), row * bh + bh - 1
            d.rectangle([x0, y0, x1, y1], fill=base + (255,))
            d.line([x0, y0, x1, y0], fill=cols[3] + (255,) if not dark else cols[2] + (255,))  # lit top edge
            for _ in range(5):  # speckle
                px, py = rnd.randint(x0, x1), rnd.randint(y0, y1)
                d.point((px, py), fill=rnd.choice(cols) + (255,))
    if moss_top:
        for x in range(w):
            depth = rnd.choice([2, 3, 3, 4, 6]) if rnd.random() < 0.8 else 1
            for y in range(depth):
                d.point((x, y), fill=MOSS[2 if y == 0 else 1] + (255,))
            if rnd.random() < 0.15:
                d.point((x, depth), fill=MOSS[0] + (255,))
    return im


def tileset():
    tiles = [
        ("stone", bricks(1)),
        ("stone_dark", bricks(2, dark=True)),
        ("stone_moss_top", bricks(3, moss_top=True)),
        ("stone_big", bricks(4, bw=32, bh=16)),
    ]
    # wood plank platform piece
    pl = Image.new("RGBA", (T, T), (0, 0, 0, 0)); d = ImageDraw.Draw(pl)
    d.rectangle([0, 0, T - 1, 11], fill=WOOD[1] + (255,))
    d.line([0, 0, T - 1, 0], fill=WOOD[3] + (255,)); d.line([0, 11, T - 1, 11], fill=WOOD[0] + (255,))
    for x in (0, 15):
        d.line([x, 0, x, 11], fill=WOOD[0] + (255,))
    for x, y in ((3, 5), (12, 5), (19, 5), (28, 5)):
        d.point((x, y), fill=IRON[2] + (255,))
    tiles.append(("plank", pl))
    # pillar segment
    pi = bricks(5, bw=32, bh=16, cols=STONE); d = ImageDraw.Draw(pi)
    d.rectangle([0, 0, 3, T - 1], fill=STONE[0] + (255,)); d.rectangle([T - 4, 0, T - 1, T - 1], fill=STONE[0] + (255,))
    tiles.append(("pillar", pi))
    sheet = Image.new("RGBA", (T * len(tiles), T), (0, 0, 0, 0))
    for i, (_, t) in enumerate(tiles):
        sheet.alpha_composite(t, (i * T, 0))
    (ROOT / "tiles").mkdir(parents=True, exist_ok=True)
    sheet.save(ROOT / "tiles" / "tileset.png")
    (ROOT / "tiles" / "tileset.txt").write_text(
        "32x32 tiles, left to right: " + ", ".join(n for n, _ in tiles) + "\n")


def torch(frames=4):
    W, H = 32, 48
    sheet = Image.new("RGBA", (W * frames, H), (0, 0, 0, 0))
    rnd = random.Random(11)
    for f in range(frames):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle([14, 26, 17, 46], fill=IRON[1] + (255,)); d.line([14, 26, 14, 46], fill=IRON[2] + (255,))
        d.polygon([(9, 24), (22, 24), (20, 30), (11, 30)], fill=IRON[1] + (255,))
        d.line([9, 24, 22, 24], fill=IRON[2] + (255,))
        sway = (-1, 0, 1, 0)[f]; hh = (13, 15, 12, 14)[f]
        for i, col in enumerate(FLAME):
            s = 1 - i * 0.22
            top = 24 - int(hh * s)
            d.polygon([(16 + sway * (i + 1) // 2, top), (16 - int(5 * s), 24), (16 + int(5 * s), 24)], fill=col + (255,))
        for _ in range(2):  # embers
            d.point((16 + rnd.randint(-6, 6), 8 + rnd.randint(0, 6)), fill=FLAME[2] + (255,))
        sheet.alpha_composite(im, (f * W, 0))
    sheet.save(ROOT / "props" / "torch.png")


def banner(frames=4):
    W, H = 48, 96
    sheet = Image.new("RGBA", (W * frames, H), (0, 0, 0, 0))
    for f in range(frames):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle([2, 0, 45, 4], fill=WOOD[2] + (255,)); d.line([2, 0, 45, 0], fill=WOOD[3] + (255,))
        for y in range(5, 84):
            sw = int(round(2 * __import__("math").sin(y / 14 + f * 1.57) * (y / 84)))
            d.line([6 + sw, y, 41 + sw, y], fill=RED[1] + (255,))
            d.point((6 + sw, y), fill=RED[0] + (255,)); d.point((41 + sw, y), fill=RED[0] + (255,))
            d.point((20 + sw, y), fill=RED[2] + (255,))
        for x in range(6, 42, 7):  # tattered hem
            n = 6 + (x * 7 + f * 3) % 9
            d.polygon([(x, 84), (x + 7, 84), (x + 3, 84 + n)], fill=RED[1] + (255,))
        cx = 24
        d.line([cx, 28, cx, 62], fill=(170, 80, 70, 255), width=2)       # sigil
        d.line([cx - 9, 40, cx + 9, 40], fill=(170, 80, 70, 255), width=2)
        d.ellipse([cx - 6, 36, cx + 6, 48], outline=(170, 80, 70, 255))
        sheet.alpha_composite(im, (f * W, 0))
    sheet.save(ROOT / "props" / "banner.png")


def chain():
    im = Image.new("RGBA", (16, 32), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k, y in enumerate((0, 16)):
        if k == 0:
            d.ellipse([4, y, 11, y + 14], outline=IRON[2] + (255,), width=2)
        else:
            d.line([7, y, 7, y + 14], fill=IRON[1] + (255,), width=3); d.line([6, y, 6, y + 14], fill=IRON[2] + (255,))
    im.save(ROOT / "props" / "chain.png")  # tile vertically


def ladder():
    im = Image.new("RGBA", (24, 32), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x in (2, 19):
        d.rectangle([x, 0, x + 2, 31], fill=WOOD[1] + (255,)); d.line([x, 0, x, 31], fill=WOOD[3] + (255,))
    for y in (6, 22):
        d.rectangle([4, y, 19, y + 2], fill=WOOD[2] + (255,)); d.line([4, y, 19, y], fill=WOOD[3] + (255,))
    im.save(ROOT / "props" / "ladder.png")  # tile vertically


def statue():
    W, H = 64, 112
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    S = lambda i: STONE[i] + (255,)
    d.rectangle([8, 96, 55, 111], fill=S(1)); d.rectangle([12, 88, 51, 97], fill=S(2)); d.line([12, 88, 51, 88], fill=S(3))
    d.polygon([(20, 88), (44, 88), (50, 40), (14, 40)], fill=S(1))          # robe
    d.polygon([(24, 88), (32, 88), (32, 44), (22, 44)], fill=S(2))           # lit side
    d.polygon([(14, 44), (2, 52), (6, 82), (16, 70)], fill=S(0))             # wings
    d.polygon([(50, 44), (62, 52), (58, 82), (48, 70)], fill=S(0))
    d.ellipse([22, 16, 42, 38], fill=S(1))                                   # hood
    d.ellipse([26, 24, 38, 38], fill=S(0))                                   # shadowed face
    d.polygon([(32, 10), (42, 20), (22, 20)], fill=S(1))
    d.rectangle([28, 50, 36, 62], fill=S(2))                                 # clasped hands
    for _ in range(40):                                                      # weathering
        x, y = random.randint(8, 56), random.randint(14, 108)
        if im.getpixel((x, y))[3]:
            d.point((x, y), fill=random.choice([S(0), S(3), MOSS[1] + (255,)]))
    im.save(ROOT / "props" / "statue_hooded.png")


def preview():
    pr = Image.new("RGBA", (420, 150), (14, 18, 28, 255))
    ts = Image.open(ROOT / "tiles" / "tileset.png"); pr.alpha_composite(ts, (4, 4))
    x = 4
    for n in ("torch", "banner", "statue_hooded", "chain", "ladder"):
        im = Image.open(ROOT / "props" / f"{n}.png")
        if n in ("chain", "ladder"):
            col = Image.new("RGBA", (im.width, 96)); [col.alpha_composite(im, (0, k * 32)) for k in range(3)]; im = col
        im = im.crop((0, 0, min(im.width, 64 if n != "torch" else 128), im.height))
        pr.alpha_composite(im, (x, 40)); x += im.width + 8
    pr.save(ROOT / "props" / "_preview.png")


if __name__ == "__main__":
    random.seed(3)
    (ROOT / "props").mkdir(parents=True, exist_ok=True)
    tileset(); torch(); banner(); chain(); ladder(); statue(); preview()
    print("tiles and props written")
