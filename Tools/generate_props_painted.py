"""Painterly props -> Assets/Resources/Props/  (128 px/unit; same world size as the old 32 px/unit pixel props)
torch_stand 64x192, flame_0..2 64x96, glow 256x256, pillar_broken 104x288, pillar_short 104x160,
rubble 192x56, gravestone 80x120, chain 32x128 (vertically seamless, tiled by the scene builder).
Height-map lighting from the upper left (matches the painted ground), cool moon rim on the right edge,
moss/lichen, cracks, chips. Deterministic. Needs numpy + Pillow.  Run: python Tools/generate_props_painted.py"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_environment_painted import fbm, smooth, hexc   # noqa: E402  (shared periodic noise helpers)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Assets', 'Resources', 'Props')
os.makedirs(OUT, exist_ok=True)
SS = 3
LDIR = np.array([-0.55, -0.6, 0.58], np.float32)
LDIR /= np.linalg.norm(LDIR)
RIM = hexc('#6a68a8')
MOSS_D, MOSS_M, MOSS_H = hexc('#14241c'), hexc('#2a4630'), hexc('#5f7f45')


# ------------------------------------------------------------------ helpers
def new_mask(w, h):
    img = Image.new('L', (w * SS, h * SS), 0)
    return img, ImageDraw.Draw(img)


def to_np(img, w, h):
    return np.asarray(img.resize((w, h), Image.LANCZOS), np.float32) / 255.0


def blur(m, r):
    img = Image.fromarray(np.clip(m * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))
    return np.asarray(img, np.float32) / 255.0


def diffuse(height, strength):
    gy, gx = np.gradient(height)
    nx, ny = -gx * strength, -gy * strength
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + 1.0)
    return np.clip((nx * LDIR[0] + ny * LDIR[1] + LDIR[2]) * inv, 0, 1)


def shade(albedo, height, mask, strength=10.0, amb=0.34, ao=None, rim=0.45):
    d = diffuse(height, strength)
    rgb = albedo * (amb + 0.95 * d)[..., None]
    if ao is not None:
        rgb = rgb * ao[..., None]
    er = np.clip(mask - np.roll(mask, -2, 1), 0, 1)
    rgb = rgb + er[..., None] * RIM * rim
    return np.clip(rgb, 0, 255)


def save_rgba(rgb, alpha, name):
    out = np.concatenate([np.clip(rgb, 0, 255), np.clip(alpha, 0, 1)[..., None] * 255], 2)
    Image.fromarray(out.astype(np.uint8), 'RGBA').save(os.path.join(OUT, name + '.png'))


def stone_albedo(w, h, seed, base='#4a4658', hi='#6c6678'):
    g = fbm(w, h, 1.1, seed)
    m = fbm(w, h, 1.8, seed + 1)
    t = np.clip(0.35 + 0.55 * m + (g - 0.5) * 0.7, 0, 1)
    b, l = hexc(base), hexc(hi)
    return (b + (l - b) * t[..., None]) * (0.8 + 0.4 * g[..., None])


def cracks(w, h, seed, amount=0.6):
    n = fbm(w, h, 2.4, seed)
    c = 1 - smooth(0.0, 0.007, np.abs(n - 0.5))
    return c * smooth(0.45, 0.6, fbm(w, h, 2.0, seed + 1)) * amount


def moss_amount(h, w, seed, ground_rows, reach):
    """0..1 moss coverage, strongest at the bottom, creeping up with noise."""
    yy = np.arange(h, dtype=np.float32)[:, None]
    n = fbm(w, h, 1.5, seed)
    dist = (h - 1 - yy)
    return smooth(0, 1, 1 - dist / np.maximum(1.0, reach * (0.4 + 1.2 * n))) * smooth(0.0, 0.2, n + 0.35) * (dist >= 0)


def apply_moss(rgb, moss, seed):
    v = fbm(rgb.shape[1], rgb.shape[0], 1.2, seed)
    col = MOSS_D + (MOSS_M - MOSS_D) * np.clip((v - 0.25) * 2.4, 0, 1)[..., None]
    col = col + (MOSS_H - col) * np.clip((v - 0.6) * 2.0, 0, 0.7)[..., None]
    return rgb * (1 - moss[..., None] * 0.85) + col * (0.55 * moss[..., None] * 1.0)


# ------------------------------------------------------------------ pillars
def pillar(name, W, H, top_from_bottom, seed, plinth=30):
    rng = np.random.default_rng(seed)
    cx, sw = W / 2.0, W * 0.70
    top_y = H - top_from_bottom
    img, d = new_mask(W, H)
    img_s, ds = new_mask(W, H)
    s = SS
    d.rectangle([0, (H - plinth) * s, W * s, H * s], fill=255)                          # plinth base
    d.rectangle([5 * s, (H - plinth - 14) * s, (W - 5) * s, (H - plinth) * s], fill=255)  # second step
    pts = [(cx - sw / 2, H - plinth - 14)]
    # jagged broken top with a diagonal break plane
    n = 9
    for i in range(n + 1):
        x = cx - sw / 2 + sw * i / n
        slope = (i / n - 0.5) * rng.uniform(18, 44)
        pts.append((x, top_y + slope + rng.uniform(-10, 16) * (0 if i in (0, n) else 1)))
    pts.append((cx + sw / 2, H - plinth - 14))
    ds.polygon([(x * s, y * s) for x, y in pts], fill=255)
    shaft = to_np(img_s, W, H)
    base = np.maximum(to_np(img, W, H), shaft)

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = np.clip((xx - cx) / (sw / 2), -1, 1)
    cyl = np.sqrt(1 - u * u)
    height = blur(to_np(img, W, H), 3) * 0.55 + shaft * (0.3 + 1.7 * cyl) + (fbm(W, H, 1.2, seed) - 0.5) * 0.10
    albedo = stone_albedo(W, H, seed + 5)

    # drum joints on the shaft, plus a few chips
    ao = np.ones((H, W), np.float32)
    for jy in range(int(H - plinth - 14 - 56), int(top_y) - 40, -56):
        j = np.exp(-((yy - jy) / 1.6) ** 2)
        ao *= 1 - 0.7 * j * shaft
        height -= 0.12 * j * shaft
    ao *= 1 - cracks(W, H, seed + 9) * 0.8 * base
    rgb = shade(albedo, height, base, strength=14.0, ao=ao)
    rgb = apply_moss(rgb, moss_amount(H, W, seed + 20, plinth, 62) * base, seed + 30)
    save_rgba(rgb, base, name)


# ------------------------------------------------------------------ rubble
def blob(rng, cx, cy, r, squash=0.7, n=11):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * rng.uniform(0.72, 1.12)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * squash))
    return pts


def rubble(name, W, H, seed):
    rng = np.random.default_rng(seed)
    P = np.zeros((H, W, 3), np.float32)
    A = np.zeros((H, W), np.float32)
    stones = []
    for _ in range(13):
        x = float(rng.uniform(18, W - 18))
        edge = 1 - abs(x - W / 2) / (W / 2)                          # taller in the middle
        r = float(rng.uniform(11, 18) + 16 * edge * rng.random())
        stones.append((x, H - r * 0.7 - float(rng.uniform(0, 5)), r))
    stones.sort(key=lambda t: t[1])                                  # back (higher) to front (lower)
    for i, (x, y, r) in enumerate(stones):
        img, d = new_mask(W, H)
        d.polygon([(px * SS, py * SS) for px, py in blob(rng, x, y, r)], fill=255)
        m = to_np(img, W, H)
        height = blur(m, r * 0.35) * 1.0 + (fbm(W, H, 1.2, seed + i) - 0.5) * 0.12
        albedo = stone_albedo(W, H, seed + 40 + i, base='#3e3a4e', hi='#6a6478') * rng.uniform(0.85, 1.1)
        ao = 1 - 0.35 * smooth(0, 1, (np.mgrid[0:H, 0:W][0] - (y + r * 0.2)) / (r * 0.6 + 1))
        rgb = shade(albedo, height, m, strength=16.0, ao=np.clip(ao, 0.4, 1))
        P = P * (1 - m[..., None]) + rgb * m[..., None]
        A = m + A * (1 - m)
    moss = moss_amount(H, W, seed + 3, 0, 22) * A
    P = apply_moss(P, moss * 0.8, seed + 4)
    save_rgba(P, A, name)


# ------------------------------------------------------------------ gravestone
def gravestone(name, W, H, seed):
    rng = np.random.default_rng(seed)
    s = SS
    img, d = new_mask(W, H)
    x0, x1 = 9, W - 9
    d.rectangle([x0 * s, 44 * s, x1 * s, (H - 8) * s], fill=255)
    d.ellipse([x0 * s, 10 * s, x1 * s, 78 * s], fill=255)                 # arched top
    d.ellipse([(x0 - 6) * s, (H - 22) * s, (x1 + 6) * s, (H + 4) * s], fill=255)  # soil mound at the base
    m = to_np(img, W, H)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    slab = to_np(img, W, H) * (yy < H - 14)

    ci, cd = new_mask(W, H)                                                 # carved cross
    cd.rectangle([(W / 2 - 3.5) * s, 30 * s, (W / 2 + 3.5) * s, 78 * s], fill=255)
    cd.rectangle([(W / 2 - 15) * s, 44 * s, (W / 2 + 15) * s, 51 * s], fill=255)
    cross = to_np(ci, W, H)

    height = blur(m, 4) * 0.9 + slab * 0.25 - blur(cross, 1.0) * 0.30 + (fbm(W, H, 1.1, seed) - 0.5) * 0.12
    # inset bevel line following the slab outline
    inner = blur(slab, 6)
    height += smooth(0.55, 0.6, inner) * 0.05
    albedo = stone_albedo(W, H, seed + 2, base='#4e4a60', hi='#716b84')
    albedo = albedo * (1 - 0.45 * blur(cross, 0.8))[..., None]
    soil = (yy >= H - 16)[..., None] * hexc('#241d1a')
    albedo = np.where((yy >= H - 16)[..., None], soil * (0.7 + 0.6 * fbm(W, H, 1.0, seed + 3)[..., None]), albedo)
    ao = 1 - cracks(W, H, seed + 7) * 0.85 * slab
    ao *= 1 - 0.5 * blur(cross, 1.5) * 0.4
    rgb = shade(albedo, height, m, strength=12.0, ao=np.clip(ao, 0, 1))
    moss = moss_amount(H, W, seed + 11, 0, 44) * m
    rgb = apply_moss(rgb, moss, seed + 12)
    save_rgba(rgb, m, name)


# ------------------------------------------------------------------ torch stand (wrought iron)
def torch_stand(name, W, H, seed):
    s = SS
    cx = W / 2.0
    img, d = new_mask(W, H)
    cyl_img, cd = new_mask(W, H)                                            # round parts (pole, collars, feet)
    # tripod feet
    for sign in (-1, 1):
        cd.polygon([((cx + sign * 5) * s, (H - 56) * s), ((cx + sign * 24) * s, (H - 1) * s),
                    ((cx + sign * 18) * s, (H - 1) * s), ((cx + sign * 3) * s, (H - 50) * s)], fill=255)
    cd.rectangle([(cx - 4.5) * s, 52 * s, (cx + 4.5) * s, (H - 8) * s], fill=255)       # pole
    for cy in (84, 118, 150):                                                           # collars
        cd.rounded_rectangle([(cx - 9) * s, cy * s, (cx + 9) * s, (cy + 8) * s], radius=3 * s, fill=255)
    # basin: bowl + rim + three ribs
    d.polygon([((cx - 27) * s, 28 * s), ((cx + 27) * s, 28 * s), ((cx + 13) * s, 62 * s), ((cx - 13) * s, 62 * s)], fill=255)
    d.rounded_rectangle([(cx - 31) * s, 20 * s, (cx + 31) * s, 30 * s], radius=4 * s, fill=255)
    for sx in (-1, 0, 1):
        cd.line([((cx + sx * 4) * s, 60 * s), ((cx + sx * 22) * s, 30 * s)], fill=255, width=3 * s)
    cyl = to_np(cyl_img, W, H)
    bowl = to_np(img, W, H)
    m = np.maximum(cyl, bowl)

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = np.clip((xx - cx) / 9.0, -1, 1)
    height = blur(bowl, 2.5) * 0.9 + cyl * (0.3 + 0.9 * np.sqrt(1 - u * u * 0.9)) + (fbm(W, H, 1.2, seed) - 0.5) * 0.08
    iron = hexc('#403c4c')
    albedo = iron * (0.7 + 0.6 * fbm(W, H, 1.3, seed + 1))[..., None]
    rust = smooth(0.62, 0.78, fbm(W, H, 1.5, seed + 2))[..., None]
    albedo = albedo + (hexc('#6a4430') - albedo) * rust * 0.55
    rgb = shade(albedo, height, m, strength=18.0, amb=0.3, rim=0.5)
    # glowing embers in the basin (emissive) and warm light on the rim
    inner_i, idr = new_mask(W, H)
    idr.ellipse([(cx - 24) * s, 22 * s, (cx + 24) * s, 36 * s], fill=255)
    inner = to_np(inner_i, W, H) * bowl
    ember = (hexc('#ff8a30')[None, None, :] * (0.55 + 0.7 * fbm(W, H, 1.2, seed + 5))[..., None])
    rgb = rgb * (1 - inner[..., None] * 0.9) + ember * inner[..., None] * 0.9
    warm = smooth(0, 1, 1 - np.abs(yy - 26) / 14) * bowl * 0.35
    rgb = rgb + warm[..., None] * np.array([255, 130, 50], np.float32) * 0.5
    save_rgba(rgb, m, name)


# ------------------------------------------------------------------ flame frames, glow
def flame(name, seed, phase, w=64, h=96):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    s = (h - 1 - yy) / (h - 1.0)                                           # 0 base -> 1 tip
    nz = fbm(w, h, 1.5, seed)
    cx = w / 2 + 6.0 * np.sin(phase + s * 5.0) * s ** 1.3 + (nz - 0.5) * 10 * s
    hw = w * 0.34 * np.clip(1 - s, 0, 1) ** 0.78 * (0.75 + 0.55 * nz)
    i = np.clip(1 - np.abs(xx - cx) / np.maximum(hw, 0.5), 0, 1)
    i = i ** 0.9 * smooth(0.0, 0.05, s + 0.02) * (s < 0.995)
    heat = i * (0.55 + 0.5 * (1 - s))
    col = np.zeros((h, w, 3), np.float32)
    stops = [(0.0, (150, 28, 18)), (0.22, (235, 80, 24)), (0.45, (255, 150, 40)), (0.72, (255, 214, 110)), (1.0, (255, 246, 214))]
    for k in range(3):
        col[..., k] = np.interp(heat, [t for t, _ in stops], [c[k] for _, c in stops])
    alpha = smooth(0.0, 0.3, i) * smooth(0.02, 0.5, heat + 0.1 * i)
    # sparks
    rng = np.random.default_rng(seed)
    for _ in range(4):
        px, py = int(rng.integers(w // 3, 2 * w // 3)), int(rng.integers(2, h // 3))
        for dx in (0, 1):
            for dy in (0, 1):
                if 0 <= py + dy < h and 0 <= px + dx < w:
                    col[py + dy, px + dx] = (255, 210, 120)
                    alpha[py + dy, px + dx] = max(alpha[py + dy, px + dx], 0.85)
    a_img = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1))
    c_img = Image.fromarray(col.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    out = np.concatenate([np.asarray(c_img, np.float32), np.asarray(a_img, np.float32)[..., None]], 2)
    Image.fromarray(out.astype(np.uint8), 'RGBA').save(os.path.join(OUT, name + '.png'))


def glow(name, n=256):
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    r = np.sqrt((xx - n / 2 + 0.5) ** 2 + (yy - n / 2 + 0.5) ** 2) / (n / 2)
    a = np.exp(-r * r * 4.2) * (1 - smooth(0.75, 1.0, r))
    rgb = np.broadcast_to(np.array([255, 235, 215], np.float32), (n, n, 3))     # white-warm: TorchFlicker tints it
    save_rgba(np.array(rgb), a, name)


# ------------------------------------------------------------------ chain (vertically periodic)
def chain(name, W=32, H=128, seed=3):
    s = SS
    cx = W / 2.0
    img, d = new_mask(W, H)
    for k in range(-1, 3):                      # period 64: each link overlaps its neighbours, tiles seamlessly at 128
        off = 64 * k
        d.ellipse([(cx - 13) * s, (off - 8) * s, (cx + 13) * s, (off + 40) * s], outline=255, width=6 * s)      # face-on link
        d.rounded_rectangle([(cx - 4) * s, (off + 24) * s, (cx + 4) * s, (off + 72) * s], radius=4 * s, fill=255)  # edge-on link
    m = to_np(img, W, H)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    height = blur(m, 1.6) * 1.0 + (fbm(W, H, 1.2, seed) - 0.5) * 0.08
    albedo = hexc('#4a4654') * (0.7 + 0.7 * fbm(W, H, 1.3, seed + 1))[..., None]
    rust = smooth(0.58, 0.75, fbm(W, H, 1.4, seed + 2))[..., None]
    albedo = albedo + (hexc('#6e4630') - albedo) * rust * 0.6
    rgb = shade(albedo, height, m, strength=22.0, amb=0.32)
    save_rgba(rgb, m, name)


if __name__ == '__main__':
    pillar('pillar_broken', 104, 288, 250, 101)
    pillar('pillar_short', 104, 160, 122, 202)
    rubble('rubble', 192, 56, 303)
    gravestone('gravestone', 80, 120, 404)
    torch_stand('torch_stand', 64, 192, 505)
    for i, ph in enumerate((0.0, 2.1, 4.2)):
        flame('flame_%d' % i, 600 + i * 7, ph)
    glow('glow')
    chain('chain')
    print('painted props written to', os.path.abspath(OUT))
