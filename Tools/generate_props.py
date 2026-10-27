"""Procedural dark-fantasy props -> Assets/Resources/Props/ (32 px/unit).
torch_stand, flame_0..2, glow (soft radial, tinted in Unity), chain (8x32, tiles vertically),
pillar_broken, pillar_short, rubble, gravestone. Deterministic."""
import math, os, random
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Assets', 'Resources', 'Props')
os.makedirs(OUT, exist_ok=True)
BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))

def hexc(s): s = s.lstrip('#'); return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
STONE = [hexc(c) for c in ('#2b2738', '#322d42', '#3a3450')]
DARK, HI, MOSS, IRON, IRON_HI = hexc('#14111f'), hexc('#6a6296'), hexc('#2f4a3a'), hexc('#1f1c2a'), hexc('#4a4560')

def save(im, name): im.save(os.path.join(OUT, name + '.png'))

def stone_px(x, y, x0, x1, base):
    if x == x0: return mix(base, HI, 0.32)
    if x == x1 - 1: return mix(base, DARK, 0.5)
    if BAYER[y & 3][x & 3] / 16.0 < 0.16: return mix(base, DARK, 0.28)
    if (x + 3 * (y // 7)) % 9 == 0: return mix(base, DARK, 0.18)   # block seams
    return base

def column(W, H, x0, x1, top_fn, base_plinth, seed, moss=True):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); p = im.load(); r = random.Random(seed)
    for x in range(x0, x1):
        for y in range(top_fn(x), H):
            p[x, y] = stone_px(x, y, x0, x1, STONE[1]) + (255,)
    # plinth
    for x in range(x0 - 2, x1 + 2):
        for y in range(H - base_plinth, H):
            c = mix(STONE[2], DARK, 0.1) if y > H - base_plinth else mix(STONE[2], HI, 0.25)
            p[x, y] = stone_px(x, y, x0 - 2, x1 + 2, c) + (255,)
    for _ in range(5):                                    # hairline cracks
        cx, cy = r.randrange(x0 + 2, x1 - 2), r.randrange(top_fn(x0) + 4, H - base_plinth - 4)
        for k in range(r.randrange(4, 9)):
            if p[cx, cy][3]: p[cx, cy] = mix(STONE[0], DARK, 0.7) + (255,)
            cx += r.choice((-1, 0, 1)); cy += 1
    if moss:
        for y in range(H - 9, H):
            for x in range(x0 - 2, x1 + 2):
                if p[x, y][3] and BAYER[y & 3][x & 3] / 16.0 < (y - (H - 9)) / 9.0 * 0.8:
                    p[x, y] = mix(p[x, y][:3], MOSS, 0.7) + (255,)
    return im

def pillar_broken():
    r = random.Random(4); tops = {x: 6 + r.randrange(0, 10) + (3 if x % 5 == 0 else 0) for x in range(2, 24)}
    save(column(26, 72, 4, 22, lambda x: tops.get(x, 10), 8, 11), 'pillar_broken')

def pillar_short():
    r = random.Random(8); tops = {x: 12 + r.randrange(0, 6) for x in range(2, 24)}
    save(column(26, 40, 4, 22, lambda x: tops.get(x, 14), 7, 12), 'pillar_short')

def rubble():
    W, H = 48, 14; im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); r = random.Random(6)
    for cx, w, h in ((8, 10, 6), (18, 14, 9), (31, 11, 7), (40, 8, 5), (25, 8, 4)):
        base = STONE[r.randrange(3)]
        pts = [(cx - w // 2, H - 1), (cx - w // 2 + 1, H - h + 2), (cx - 1, H - h), (cx + w // 2 - 1, H - h + 2), (cx + w // 2, H - 1)]
        d.polygon(pts, fill=base + (255,))
        d.line([pts[1], pts[2], pts[3]], fill=mix(base, HI, 0.45) + (255,))        # lit upper edge
        d.line([pts[3], pts[4]], fill=mix(base, DARK, 0.5) + (255,))
    save(im, 'rubble')

def gravestone():
    W, H = 20, 30; im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); p = im.load()
    for y in range(H):
        for x in range(W):
            inside = 3 <= x < 17 and y >= 4 and ((x - 10) ** 2 / 49.0 + (y - 11) ** 2 / 49.0 <= 1 or y >= 11)
            if inside: p[x, y] = stone_px(x, y, 3, 17, STONE[1]) + (255,)
    for y in range(8, 18): p[10, y] = mix(STONE[0], DARK, 0.75) + (255,)           # carved cross
    for x in (8, 9, 10, 11, 12): p[x, 11] = mix(STONE[0], DARK, 0.75) + (255,)
    for y in range(H - 5, H):
        for x in range(2, 18):
            if BAYER[y & 3][x & 3] / 16.0 < (y - (H - 5)) / 5.0 * 0.8: p[x, y] = mix(p[x, y][:3] if p[x, y][3] else STONE[0], MOSS, 0.7) + (255,)
    save(im, 'gravestone')

def torch_stand():
    W, H = 16, 48; im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); p = im.load()
    for y in range(18, H):                                  # iron post
        for x in range(6, 10): p[x, y] = (IRON_HI if x == 6 else IRON) + (255,)
    for y in range(H - 5, H):                               # foot
        for x in range(3, 13): p[x, y] = (IRON_HI if y == H - 5 else IRON) + (255,)
    for y in range(12, 18):                                 # bowl
        inset = (y - 12) // 2
        for x in range(2 + inset, 14 - inset): p[x, y] = mix(IRON, IRON_HI, 0.4 if x < 6 else 0.0) + (255,)
    for x in range(1, 15): p[x, 11] = IRON_HI + (255,)      # rim
    for y in range(18, 34, 5):                              # bands
        for x in range(5, 11): p[x, y] = IRON_HI + (255,)
    save(im, 'torch_stand')

def flames():
    W, H = 16, 24
    tips = ((8, 0), (6, 2), (10, 1))
    for i, (tx, ty) in enumerate(tips):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.polygon([(2, 23), (1, 16), (4, 10), (tx - 1, ty + 8), (tx, ty), (tx + 2, ty + 8), (12, 10), (15, 16), (14, 23)], fill=(255, 110, 28, 255))
        d.polygon([(4, 23), (3, 17), (6, 12), (tx, ty + 7), (10, 12), (13, 17), (12, 23)], fill=(255, 182, 74, 255))
        d.polygon([(6, 23), (6, 18), (tx, ty + 11), (10, 18), (10, 23)], fill=(255, 240, 190, 255))
        save(im, 'flame_%d' % i)

def glow():
    S = 96; im = Image.new('RGBA', (S, S)); p = im.load()
    for y in range(S):
        for x in range(S):
            d = math.hypot(x - S / 2 + .5, y - S / 2 + .5) / (S / 2)
            a = max(0.0, 1 - d) ** 2.2
            p[x, y] = (255, 255, 255, int(255 * a))
    save(im, 'glow')

def chain():
    W, H = 8, 32; im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(2):                                      # 16 px period => tiles seamlessly
        y = k * 16
        d.rounded_rectangle([2, y, 5, y + 11], radius=2, outline=IRON_HI + (255,), width=1)   # link seen edge-on
        d.line([(3, y + 1), (3, y + 10)], fill=IRON + (255,))
        d.rectangle([1, y + 12, 6, y + 15], fill=IRON + (255,))                              # link seen face-on
        d.line([(1, y + 12), (6, y + 12)], fill=IRON_HI + (255,))
    save(im, 'chain')

if __name__ == '__main__':
    pillar_broken(); pillar_short(); rubble(); gravestone(); torch_stand(); flames(); glow(); chain()
    print('props written to', os.path.abspath(OUT))
