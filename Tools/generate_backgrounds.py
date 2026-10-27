"""Procedural dark-fantasy parallax layers -> Assets/Resources/Backgrounds/
sky.png (1024x512, pinned to camera) + far/mid/near.png (512x320, seamless horizontally, bottom-pivot)."""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stylize import stylize_layer, vignette_sky

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Assets', 'Resources', 'Backgrounds')
os.makedirs(OUT, exist_ok=True)
TW, TH = 512, 320

def C(s, a=255):
    s = s.lstrip('#'); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4)) + (a,)

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))

def periodic(x, terms):  # seamless over TW
    return sum(a * math.sin(2 * math.pi * k * x / TW + p) for a, k, p in terms)

def sky():
    W, H = 1024, 512
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    top, mid, hor = C('#07050f'), C('#1a1030'), C('#4a2a3a')
    for y in range(H):
        t = y / (H - 1)
        c = lerp(top, mid, t / 0.6) if t < 0.6 else lerp(mid, hor, (t - 0.6) / 0.4)
        d.line([(0, y), (W, y)], fill=c)
    rnd = random.Random(7)
    for _ in range(170):
        x, y = rnd.randrange(W), int(rnd.random() ** 1.6 * H * 0.7)
        b = rnd.choice([90, 140, 200]); d.point((x, y), fill=(b, b, b + 30, 255))
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    mx, my = 760, 150
    g.ellipse([mx - 110, my - 110, mx + 110, my + 110], fill=(190, 170, 230, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(28)); im.alpha_composite(glow)
    d = ImageDraw.Draw(im)
    d.ellipse([mx - 42, my - 42, mx + 42, my + 42], fill=C('#d9d4ea'))
    for cx, cy, r in ((mx - 14, my - 10, 9), (mx + 16, my + 14, 6), (mx + 8, my - 22, 4)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=C('#b9b3d0'))
    vignette_sky(im); stylize_layer(im, 'sky').save(os.path.join(OUT, 'sky.png'))

def far():
    im = Image.new('RGBA', (TW, TH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    terms = [(22, 3, .7), (14, 7, 2.1), (8, 13, 4.2), (4, 29, 1.0)]
    body, rim = C('#1b1533'), C('#2d2450')
    for x in range(TW):
        h = 255 + periodic(x, terms); y = int(TH - h)
        d.line([(x, y), (x, TH)], fill=body); d.line([(x, y), (x, y + 1)], fill=rim)
    # distant gothic keep on the ridge
    bx = 150; base = int(TH - (255 + periodic(bx, terms))) + 4
    d.rectangle([bx - 12, base - 74, bx + 12, base], fill=C('#120e26'))
    d.polygon([(bx - 15, base - 74), (bx, base - 104), (bx + 15, base - 74)], fill=C('#120e26'))
    d.rectangle([bx - 30, base - 40, bx - 14, base], fill=C('#120e26'))
    d.polygon([(bx - 32, base - 40), (bx - 22, base - 58), (bx - 12, base - 40)], fill=C('#120e26'))
    for wx, wy in ((bx - 2, base - 56), (bx - 24, base - 26)):
        d.rectangle([wx, wy, wx + 3, wy + 6], fill=C('#ffb64a'))
    stylize_layer(im, 'far').save(os.path.join(OUT, 'far.png'))

def tree(d, x, base, h, col, rnd):
    def branch(x0, y0, ang, ln, w, depth):
        x1, y1 = x0 + math.cos(ang) * ln, y0 - math.sin(ang) * ln
        d.line([(x0, y0), (x1, y1)], fill=col, width=max(1, int(w)))
        if depth > 0:
            for da in (-0.5, 0.45):
                branch(x1, y1, ang + da + rnd.uniform(-.2, .2), ln * rnd.uniform(.62, .78), w * .65, depth - 1)
    for off in (-TW, 0, TW):
        branch(x + off, base, math.pi / 2 + rnd.uniform(-.1, .1), h * .42, 6, 4)

def mid():
    im = Image.new('RGBA', (TW, TH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = C('#110e22'); rnd = random.Random(3)
    terms = [(6, 2, 1.3), (4, 5, .4), (2, 11, 2.6)]
    def gy(x): return int(TH - (176 + periodic(x, terms)))
    for x in range(TW):
        d.line([(x, gy(x)), (x, TH)], fill=col)
    for x, h in ((60, 105), (190, 85), (330, 115), (455, 95)):
        tree(d, x, gy(x) + 6, h, col, rnd)
    # broken stone arch
    ax = 262; b = gy(ax) + 4
    for px, ph in ((ax - 34, 95), (ax + 26, 70)):
        d.rectangle([px, b - ph, px + 12, b], fill=col)
        d.polygon([(px, b - ph), (px + 5, b - ph - 6), (px + 9, b - ph - 2), (px + 12, b - ph - 8), (px + 12, b - ph)], fill=col)
    d.arc([ax - 34, b - 135, ax + 38, b - 55], 180, 262, fill=col, width=9)
    # gravestones
    for gx in (110, 150, 400, 428):
        d.rectangle([gx, gy(gx) - 16, gx + 8, gy(gx) + 4], fill=col)
        d.ellipse([gx, gy(gx) - 20, gx + 8, gy(gx) - 12], fill=col)
    stylize_layer(im, 'mid').save(os.path.join(OUT, 'mid.png'))

def near():
    im = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    # drifting mist, wrapped so it tiles
    wide = Image.new('RGBA', (TW * 3, TH), (0, 0, 0, 0)); g = ImageDraw.Draw(wide); rnd = random.Random(11)
    for _ in range(9):
        x = rnd.randrange(TW); y = TH - rnd.randrange(150, 215); w = rnd.randrange(90, 170); h = rnd.randrange(12, 26)
        for off in (0, TW, 2 * TW):
            g.ellipse([x + off - w, y - h, x + off + w, y + h], fill=(120, 105, 160, 60))
    wide = wide.filter(ImageFilter.GaussianBlur(14))
    im.alpha_composite(wide.crop((TW, 0, 2 * TW, TH)))
    d = ImageDraw.Draw(im); col = C('#07050c'); rnd = random.Random(5)
    terms = [(5, 3, .5), (3, 8, 1.9)]
    def gy(x): return int(TH - (150 + periodic(x, terms)))
    for x in range(TW):
        d.line([(x, gy(x)), (x, TH)], fill=col)
    for x in range(0, TW, 3):  # grass blades
        h = rnd.randrange(5, 20)
        d.line([(x, gy(x) + 1), (x + rnd.randrange(-2, 3), gy(x) - h)], fill=col, width=1)
    for rx, rw, rh in ((70, 26, 14), (240, 34, 18), (410, 22, 10)):  # rocks
        d.ellipse([rx, gy(rx) - rh, rx + rw, gy(rx) + 8], fill=col)
    im.save(os.path.join(OUT, 'near.png'))

if __name__ == '__main__':
    sky(); far(); mid(); near(); print('backgrounds written to', os.path.abspath(OUT))
