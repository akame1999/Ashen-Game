"""Painterly parallax layers -> Assets/Resources/Backgrounds/  (64 px/unit, same world size as the old 32 px/unit set)
sky.png  2048x1024  moonlit cloudy sky, pinned to the camera
far.png  1024x640   hazy ridges + ruined keep, seamless in X, bottom pivot
mid.png  1024x640   ruined walls/arches + dead trees, ground fog, seamless in X
near.png 1024x640   dark foreground grass/reeds + drifting mist, seamless in X
Atmospheric perspective: far is hazy/violet, near is almost black. Deterministic. Needs numpy + Pillow.
Run: python Tools/generate_backgrounds_painted.py"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Assets', 'Resources', 'Backgrounds')
os.makedirs(OUT, exist_ok=True)
W, H = 1024, 640
SS = 2   # supersampling for drawn silhouettes


def hexc(s):
    s = s.lstrip('#')
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def fbm(w, h, beta, seed):
    """Periodic 1/f^beta noise 0..1 (tiles in both axes)."""
    rng = np.random.default_rng(seed)
    f = np.fft.fft2(rng.standard_normal((h, w)))
    r = np.sqrt(np.fft.fftfreq(w)[None, :] ** 2 + np.fft.fftfreq(h)[:, None] ** 2)
    r[0, 0] = 1.0
    f = f / (r ** beta)
    f[0, 0] = 0
    n = np.real(np.fft.ifft2(f))
    n -= n.min()
    return (n / max(1e-6, n.max())).astype(np.float32)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def grad(h, stops):
    """Vertical gradient (h rows) from [(t, hex), ...] -> (h,1,3)."""
    ts = np.array([s[0] for s in stops])
    cs = np.stack([hexc(s[1]) for s in stops])
    t = np.linspace(0, 1, h)
    out = np.stack([np.interp(t, ts, cs[:, k]) for k in range(3)], 1)
    return out[:, None, :].astype(np.float32)


class Canvas:
    """Premultiplied float RGBA canvas with 'over' compositing of a flat/array colour through a mask."""
    def __init__(self, w, h):
        self.p = np.zeros((h, w, 3), np.float32)
        self.a = np.zeros((h, w), np.float32)

    def over(self, rgb, mask):
        m = np.clip(mask, 0, 1)
        self.p = self.p * (1 - m[..., None]) + rgb * m[..., None]
        self.a = m + self.a * (1 - m)

    def save(self, name):
        a = np.maximum(self.a, 1e-4)[..., None]
        rgb = np.clip(self.p / a, 0, 255)
        rgba = np.concatenate([rgb, self.a[..., None] * 255], 2)
        Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(OUT, name))


def draw_mask(fn, w=W, h=H):
    img = Image.new('L', (w * SS, h * SS), 0)
    d = ImageDraw.Draw(img)
    fn(d, SS)
    return np.asarray(img.resize((w, h), Image.LANCZOS), np.float32) / 255.0


def ridge_mask(h_px, base=0):
    yy = np.arange(H, dtype=np.float32)[:, None]
    return np.clip(h_px[None, :] - (H - 1 - yy) - base + 0.5, 0, 1)


def rim_light(h_px, x_scale=1.0):
    """Per-column rim strength: edges that descend toward the moon side (right) catch light."""
    slope = (np.roll(h_px, -2) - np.roll(h_px, 2)) * 0.25
    return np.clip(-slope * 0.9, 0, 1) * x_scale


def mist(c, seed, y0, y1, color, strength):
    n = fbm(W, H, 2.4, seed)
    yy = np.arange(H, dtype=np.float32)[:, None]
    band = smooth(y0, y1, yy) * (1 - smooth(y1, y1 + (H - y1) * 1.0 + 1, yy) * 0)
    m = band * (0.35 + 0.9 * smooth(0.35, 0.8, n)) * strength
    c.over(hexc(color), np.broadcast_to(m, (H, W)))


# ---------------------------------------------------------------- sky
def sky():
    SW, SH = 2048, 1024
    rgb = np.broadcast_to(grad(SH, [(0, '#04030a'), (0.35, '#0e0a1f'), (0.65, '#241438'), (0.85, '#4a2740'), (1, '#6a3a44')]),
                          (SH, SW, 3)).copy()
    yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
    mx, my = 1520.0, 300.0
    dist = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2)

    # soft moon halo (cool white-violet)
    halo = np.exp(-dist / 230.0) * 0.55 + np.exp(-dist / 70.0) * 0.5
    rgb += halo[..., None] * np.array([70, 60, 105], np.float32)

    # banked clouds, lit from the moon side
    n = fbm(SW, SH, 2.7, 3)
    n2 = fbm(SW, SH, 2.0, 4)
    band = smooth(0.12, 0.35, yy / SH) * (1 - smooth(0.62, 0.9, yy / SH))
    cloud = smooth(0.40, 0.62, n * 0.8 + n2 * 0.25) * band
    lit = np.exp(-dist / 520.0)
    ccol = hexc('#140e26')[None, None, :] + (hexc('#7c72a8') - hexc('#140e26'))[None, None, :] * (lit * smooth(0.5, 0.9, n2))[..., None]
    rgb = rgb * (1 - cloud[..., None] * 0.85) + ccol * cloud[..., None] * 0.85

    # stars (soft), fewer through clouds and near the horizon
    rng = np.random.default_rng(11)
    star = np.zeros((SH, SW), np.float32)
    for _ in range(520):
        x, y = int(rng.integers(2, SW - 2)), int(rng.random() ** 1.5 * SH * 0.62)
        b = float(rng.choice([0.35, 0.6, 1.0]))
        star[y, x] = max(star[y, x], b)
        if b > 0.5:
            star[y, x - 1] = star[y, x + 1] = star[y - 1, x] = star[y + 1, x] = b * 0.35
    rgb += (star * (1 - cloud * 0.9) * (1 - smooth(0.45, 0.7, yy / SH)))[..., None] * np.array([200, 205, 255], np.float32)

    # moon disc with maria/craters and limb darkening
    r = 82.0
    disc = np.clip(r - dist + 0.5, 0, 1)
    surf = fbm(SW, SH, 2.2, 9) * 0.6 + fbm(SW, SH, 1.1, 10) * 0.4
    tex = 0.42 + 0.75 * smooth(0.25, 0.75, surf)
    limb = np.sqrt(np.clip(1 - (dist / r) ** 2, 0, 1))
    mcol = hexc('#d9d4ea')[None, None, :] * (tex * (0.55 + 0.45 * limb))[..., None]
    mcol *= 1 - cloud[..., None] * 0.55
    rgb = rgb * (1 - disc[..., None]) + mcol * disc[..., None]

    rgb *= (1 - 0.35 * smooth(0.55, 1.0, np.sqrt(((xx - SW / 2) / (SW / 2)) ** 2 + ((yy - SH * 0.45) / (SH * 0.6)) ** 2)))[..., None]  # vignette
    rgba = np.concatenate([rgb, np.full((SH, SW, 1), 255, np.float32)], 2)
    Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(OUT, 'sky.png'))


# ---------------------------------------------------------------- far
def far():
    c = Canvas(W, H)
    haze_top, haze_bot = '#5a4a72', '#3a2c52'
    x = np.arange(W)
    # two ridge lines, back one lighter / hazier
    for i, (seed, base, amp, col_a, col_b) in enumerate([(21, 0.34, 0.26, '#5c4c78', '#43345e'), (22, 0.26, 0.22, '#3c2f58', '#2a2044')]):
        n = fbm(W, 1, 1.8, seed)[0]
        ridged = 1 - np.abs(2 * n - 1)
        hp = H * (base + amp * (0.55 * ridged + 0.45 * n))
        m = ridge_mask(hp)
        col = np.broadcast_to(grad(H, [(0, col_a), (1, col_b)]), (H, W, 3)).copy()
        tex = fbm(W, H, 1.6, seed + 30)
        col *= (0.55 + 0.9 * tex)[..., None]
        yy = np.arange(H, dtype=np.float32)[:, None]
        edge = (hp[None, :] - (H - 1 - yy))
        rim = rim_light(hp) [None, :] * np.exp(-np.clip(edge, 0, None) / 7.0) * (edge > 0)
        col += rim[..., None] * np.array([70, 62, 100], np.float32)
        c.over(col, m)
        mist(c, seed + 50, H * (0.55 - i * 0.1), H * 0.95, '#6d5c8c', 0.22)

    # ruined keep: towers, curtain wall, broken crenellation, a few ember windows
    def keep(d, s):
        bx = 330
        gy = H - 64
        d.rectangle([(bx) * s, (gy - 150) * s, (bx + 340) * s, (H) * s], fill=255)                # curtain wall
        for k in range(0, 340, 34):                                                               # crenellations (some missing)
            if (k // 34) % 5 != 2:
                d.rectangle([(bx + k) * s, (gy - 172) * s, (bx + k + 20) * s, (gy - 148) * s], fill=255)
        d.rectangle([(bx + 40) * s, (gy - 330) * s, (bx + 118) * s, H * s], fill=255)               # left tower
        d.polygon([((bx + 32) * s, (gy - 330) * s), ((bx + 79) * s, (gy - 420) * s), ((bx + 126) * s, (gy - 330) * s)], fill=255)
        d.rectangle([(bx + 214) * s, (gy - 262) * s, (bx + 282) * s, H * s], fill=255)             # right tower, broken top
        d.polygon([((bx + 214) * s, (gy - 262) * s), ((bx + 236) * s, (gy - 300) * s), ((bx + 250) * s, (gy - 270) * s),
                   ((bx + 268) * s, (gy - 292) * s), ((bx + 282) * s, (gy - 262) * s)], fill=255)
        d.rectangle([(bx + 150) * s, (gy - 440) * s, (bx + 176) * s, (gy - 150) * s], fill=255)     # spire
        d.polygon([((bx + 144) * s, (gy - 440) * s), ((bx + 163) * s, (gy - 520) * s), ((bx + 182) * s, (gy - 440) * s)], fill=255)
        # gate arch carved out
        d.ellipse([(bx + 138) * s, (gy - 60) * s, (bx + 188) * s, (gy - 10) * s], fill=0)
        d.rectangle([(bx + 138) * s, (gy - 36) * s, (bx + 188) * s, H * s], fill=0)
    m = draw_mask(keep)
    col = np.broadcast_to(grad(H, [(0, '#2a2142'), (1, '#1b1530')]), (H, W, 3)).copy()
    col *= (0.85 + 0.3 * fbm(W, H, 1.5, 41))[..., None]
    # light catching the right edge of each mass
    edge_r = np.clip(m - np.roll(m, -3, 1), 0, 1)
    col += edge_r[..., None] * np.array([85, 75, 125], np.float32)
    c.over(col, m)
    # dim ember windows
    win = draw_mask(lambda d, s: [d.rectangle([(x0) * s, (y0) * s, (x0 + 7) * s, (y0 + 15) * s], fill=255)
                                  for x0, y0 in ((372, 292), (410, 402), (565, 396), (512, 232), (638, 330))])
    c.over(np.array([255, 150, 60], np.float32), win * 0.85)
    mist(c, 61, H * 0.62, H * 1.0, '#7a68a0', 0.38)
    c.save('far.png')


# ---------------------------------------------------------------- mid
def tree(d, rng, x, y, ang, length, width, depth, s):
    if depth == 0 or length < 6:
        return
    x2 = x + math.cos(ang) * length
    y2 = y - math.sin(ang) * length
    for off in (-W, 0, W):
        d.line([((x + off) * s, y * s), ((x2 + off) * s, y2 * s)], fill=255, width=max(1, int(width * s)))
    n = 2 if depth > 2 else int(rng.integers(1, 3))
    for _ in range(n):
        tree(d, rng, x2, y2, ang + rng.uniform(-0.75, 0.75), length * rng.uniform(0.62, 0.8), width * 0.66, depth - 1, s)


def mid():
    c = Canvas(W, H)
    rng = np.random.default_rng(5)

    # distant ground swell
    n = fbm(W, 1, 1.9, 71)[0]
    hp = H * (0.10 + 0.07 * n)
    gcol = np.broadcast_to(grad(H, [(0, '#1b1530'), (1, '#0e0a18')]), (H, W, 3)).copy()
    c.over(gcol, ridge_mask(hp))

    # ruined walls with arches (all well inside the tile so it stays seamless)
    def ruins(d, s):
        base = H - 40
        for x0, wdt, ht in ((60, 150, 210), (330, 120, 150), (640, 190, 250), (900, 100, 120)):
            d.rectangle([x0 * s, (base - ht) * s, (x0 + wdt) * s, H * s], fill=255)
            for k in range(0, wdt - 18, 28):                                    # broken top edge
                cut = int(rng.integers(0, 34))
                d.rectangle([(x0 + k) * s, (base - ht) * s, (x0 + k + 22) * s, (base - ht + cut) * s], fill=0)
            if wdt >= 120:                                                      # arch opening
                ax = x0 + wdt // 2 - 28
                d.ellipse([ax * s, (base - 110) * s, (ax + 56) * s, (base - 54) * s], fill=0)
                d.rectangle([ax * s, (base - 82) * s, (ax + 56) * s, H * s], fill=0)
    m = draw_mask(ruins)
    col = np.broadcast_to(grad(H, [(0, '#1c1630'), (1, '#0b0814')]), (H, W, 3)).copy()
    col *= (0.8 + 0.45 * fbm(W, H, 1.4, 81))[..., None]
    edge_r = np.clip(m - np.roll(m, -3, 1), 0, 1)
    top_e = np.clip(m - np.roll(m, 3, 0), 0, 1)
    col += (edge_r * 1.0 + top_e * 0.6)[..., None] * np.array([58, 52, 92], np.float32)
    c.over(col, m)

    # dead trees (drawn into one mask, wrapped across the seam)
    def trees(d, s):
        for tx in (-10, 205, 500, 770, 960):
            tx = tx + float(rng.uniform(-12, 12))
            tree(d, rng, tx, H - 28, math.pi / 2 + rng.uniform(-0.12, 0.12), float(rng.uniform(95, 130)), float(rng.uniform(15, 20)), 6, s)
    t = draw_mask(trees)
    tcol = np.broadcast_to(grad(H, [(0, '#150f24'), (1, '#07050d')]), (H, W, 3)).copy()
    edge_r = np.clip(t - np.roll(t, -2, 1), 0, 1)
    tcol += edge_r[..., None] * np.array([48, 44, 78], np.float32)
    c.over(tcol, t)

    # ground fog hugging the base, a touch of moon-violet
    mist(c, 91, H * 0.7, H * 1.0, '#473a6a', 0.55)
    # dark ground strip so the layer sits on something
    g2 = fbm(W, 1, 2.0, 99)[0]
    c.over(hexc('#06040b'), ridge_mask(H * (0.035 + 0.02 * g2)))
    c.save('mid.png')


# ---------------------------------------------------------------- near
def near():
    c = Canvas(W, H)
    rng = np.random.default_rng(13)

    def blades(d, s):
        for _ in range(420):
            x = float(rng.uniform(0, W)); hgt = float(rng.uniform(26, 96) * (1.7 if rng.random() < 0.08 else 1.0))
            lean = float(rng.uniform(-22, 22)); wdt = float(rng.uniform(1.6, 3.2))
            pts = []
            for k in range(8):
                t = k / 7.0
                pts.append((x + lean * t * t, H - 1 - hgt * t))
            for off in (-W, 0, W):
                d.line([((px + off) * s, py * s) for px, py in pts], fill=255, width=max(1, int(wdt * s)))
        # a few tall reeds with seed heads
        for _ in range(14):
            x = float(rng.uniform(0, W)); hgt = float(rng.uniform(150, 260)); lean = float(rng.uniform(-30, 30))
            pts = [(x + lean * (k / 7) ** 2, H - 1 - hgt * k / 7) for k in range(8)]
            for off in (-W, 0, W):
                d.line([((px + off) * s, py * s) for px, py in pts], fill=255, width=int(2.2 * s))
                ex, ey = pts[-1]
                d.ellipse([(ex + off - 3) * s, (ey - 12) * s, (ex + off + 3) * s, (ey + 6) * s], fill=255)
    m = draw_mask(blades)
    base = fbm(W, 1, 2.0, 5)[0]
    m = np.maximum(m, ridge_mask(H * (0.03 + 0.03 * base)))
    col = np.broadcast_to(grad(H, [(0, '#0f0c18'), (1, '#040308')]), (H, W, 3)).copy()
    edge_r = np.clip(m - np.roll(m, -2, 1), 0, 1)
    col += edge_r[..., None] * np.array([36, 40, 62], np.float32)
    c.over(col, m)
    # thin drifting mist in front of the grass (low alpha, never hides the play area)
    mist(c, 17, H * 0.82, H * 1.0, '#54487a', 0.28)
    c.save('near.png')


if __name__ == '__main__':
    sky(); far(); mid(); near()
    print('painted backgrounds written to', os.path.abspath(OUT))
