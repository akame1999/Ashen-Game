"""Procedural dark-fantasy environment tiles -> Assets/Resources/Environment/
ground.png (64x64, sliced: 10px mossy lip on top, tiles in X/Y), platform.png (64x32, lip on top + shadowed underside),
checkpoint.png (24x64 brazier pillar, pivot bottom-centre). All deterministic; 32 px/unit."""
import os, random
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Assets', 'Resources', 'Environment')
os.makedirs(OUT, exist_ok=True)
BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))

def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def hexc(s): s = s.lstrip('#'); return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))

STONE = [hexc(c) for c in ('#2b2738', '#322d42', '#3a3450', '#27233a')]
MORTAR, HI, MOSS, MOSS_HI = hexc('#14111f'), hexc('#6a6296'), hexc('#2f4a3a'), hexc('#4d7a52')

def bricks(W, H, y0, rnd):
    """Fill rows y0..H with offset bricks (seamless in X because brick width divides W)."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); p = im.load()
    bh, bw = 16, 32
    for y in range(y0, H):
        row = (y - y0) // bh
        off = (bw // 2) * (row % 2)
        for x in range(W):
            bx = ((x + off) % W) // bw + row * 7
            r = random.Random(bx * 131 + 17)
            base = STONE[r.randrange(len(STONE))]
            ly, lx = (y - y0) % bh, (x + off) % bw
            c = base
            if ly == 0 or lx == 0: c = MORTAR
            elif ly == 1 or lx == 1: c = mix(base, HI, 0.28)          # lit top/left edge of brick
            elif ly == bh - 1 or lx == bw - 1: c = mix(base, MORTAR, 0.45)
            elif BAYER[y & 3][x & 3] / 16.0 < 0.18 + rnd.random() * 0.1: c = mix(base, MORTAR, 0.25)
            p[x, y] = c + (255,)
    return im

def lip(im, W, rows, rnd, seed):
    """Mossy stone lip along the top; ragged periodic underside so the tile seams."""
    p = im.load(); r = random.Random(seed)
    drip = [r.randrange(0, 5) for _ in range(W // 4)]
    for x in range(W):
        depth = rows - 3 + drip[(x // 4) % len(drip)] % 4
        for y in range(depth + 1):
            t = y / max(1, depth)
            c = mix(MOSS_HI, MOSS, min(1, t * 1.4)) if y > 0 else mix(MOSS_HI, (170, 200, 150), 0.35)
            if BAYER[y & 3][x & 3] / 16.0 < 0.2 and y > 1: c = mix(c, MORTAR, 0.3)
            p[x, y] = c + (255,)
    return im

def ground():
    W = H = 64; rnd = random.Random(1)
    im = bricks(W, H, 0, rnd)
    # darken with depth so deep floors fade to black
    p = im.load()
    for y in range(H):
        for x in range(W):
            r, g, b, a = p[x, y]; k = 0.12 * (y / H)
            p[x, y] = mix((r, g, b), (4, 3, 8), k) + (a,)
    lip(im, W, 10, rnd, 5).save(os.path.join(OUT, 'ground.png'))

def platform():
    W, H = 64, 32; rnd = random.Random(2)
    im = bricks(W, H, 0, rnd); p = im.load()
    for y in range(H - 6, H):                    # shadowed underside, dithered
        k = (y - (H - 7)) / 6.0
        for x in range(W):
            if BAYER[y & 3][x & 3] / 16.0 < k * 0.9:
                p[x, y] = mix(p[x, y][:3], (6, 4, 12), 0.7) + (255,)
    lip(im, W, 10, rnd, 9).save(os.path.join(OUT, 'platform.png'))

def checkpoint():
    W, H = 24, 64; im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); p = im.load(); rnd = random.Random(3)
    def rect(x0, y0, x1, y1, base):
        for y in range(y0, y1):
            for x in range(x0, x1):
                c = base
                if x == x0: c = mix(base, HI, 0.3)
                elif x == x1 - 1: c = mix(base, MORTAR, 0.5)
                elif BAYER[y & 3][x & 3] / 16.0 < 0.15: c = mix(base, MORTAR, 0.25)
                p[x, y] = c + (255,)
    rect(4, 54, 20, 64, STONE[1]); rect(6, 20, 18, 54, STONE[2])     # plinth + shaft
    rect(2, 12, 22, 20, STONE[0])                                     # brazier bowl
    for y in range(8, 12):                                            # bowl rim
        for x in (2, 3, 20, 21): p[x, y] = STONE[2] + (255,)
    for y in range(26, 50, 6):                                        # carved rune notches
        for x in (10, 11, 12, 13): p[x, y] = mix(STONE[2], MORTAR, 0.7) + (255,)
    im.save(os.path.join(OUT, 'checkpoint.png'))

if __name__ == '__main__':
    ground(); platform(); checkpoint(); print('environment written to', os.path.abspath(OUT))
