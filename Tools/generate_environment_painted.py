"""Painterly, high-resolution ground + platform tiles -> Assets/Resources/Environment/
ground.png (256x256) and platform.png (256x128), 128 px/unit (same world size as the old 64px/32ppu tiles).
Hewn stone blocks lit from the upper left via a height-map normal, cracks, lichen, wet moss lip with
ragged blades, ambient occlusion in the joints. Seamless in X and (for the tiled middle) in Y.
Deterministic. Needs numpy + Pillow.  Run: python Tools/generate_environment_painted.py
checkpoint.png stays pixel art (generate_environment.py)."""
import os
import numpy as np
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Assets', 'Resources', 'Environment')
os.makedirs(OUT, exist_ok=True)
W = 256
LIP = 40          # top border in px (moss lip)
UNDER = 24        # platform underside border in px


def hexc(s):
    s = s.lstrip('#')
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def fbm(w, h, beta, seed):
    """Periodic 1/f^beta noise in 0..1 (FFT-filtered white noise, so it tiles in both axes)."""
    rng = np.random.default_rng(seed)
    f = np.fft.fft2(rng.standard_normal((h, w)))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    r = np.sqrt(fx * fx + fy * fy)
    r[0, 0] = 1.0
    f = f / (r ** beta)
    f[0, 0] = 0
    n = np.real(np.fft.ifft2(f))
    n -= n.min()
    return n / max(1e-6, n.max())


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def stone(h, rowh, seed):
    """Periodic hewn-stone block wall of size (h, W) as float RGB 0..255. h must be a multiple of rowh."""
    rng = np.random.default_rng(seed)
    nrows = h // rowh
    yy, xx = np.mgrid[0:h, 0:W].astype(np.float32)

    # warp so block edges look hand-cut, not ruler-straight
    wx = (fbm(W, h, 2.2, seed + 1) - 0.5) * 14
    wy = (fbm(W, h, 2.2, seed + 2) - 0.5) * 9
    xw = (xx + wx) % W
    yw = (yy + wy) % h

    d = np.zeros((h, W), np.float32)
    base_t = np.zeros((h, W), np.float32)      # per-block tone 0..1
    warm_t = np.zeros((h, W), np.float32)      # per-block warm/cool shift
    row_of = (yw // rowh).astype(int)
    for r in range(nrows):
        # random partition of W into 3-4 blocks of 56..110 px
        while True:
            n = int(rng.integers(3, 5))
            cuts = np.sort(rng.integers(40, W - 40, n - 1))
            widths = np.diff(np.concatenate([[0], cuts, [W]]))
            if widths.min() >= 56 and widths.max() <= 120:
                break
        edges = np.concatenate([[0], np.cumsum(widths)])
        tones = rng.random(n)
        warms = rng.random(n)
        m = row_of == r
        idx = np.clip(np.searchsorted(edges, xw[m], side='right') - 1, 0, n - 1)
        left = edges[idx]
        right = edges[idx + 1]
        top = r * rowh
        lx = xw[m] - left
        rx = right - xw[m]
        ty = yw[m] - top
        by = (top + rowh) - yw[m]
        d[m] = np.minimum(np.minimum(lx, rx), np.minimum(ty, by))
        base_t[m] = tones[idx]
        warm_t[m] = warms[idx]

    # height map: bevelled block faces + chisel grain + chips
    grain = fbm(W, h, 1.1, seed + 3)
    mid = fbm(W, h, 1.8, seed + 4)
    height = smooth(0, 6, d) * 0.5 + grain * 0.22 + mid * 0.18
    chips = fbm(W, h, 0.8, seed + 5)
    height -= smooth(0.78, 0.9, chips) * 0.25 * smooth(2, 14, d)

    gx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * 0.5
    gy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * 0.5
    s = 9.0
    nx, ny, nz = -gx * s, -gy * s, np.ones_like(gx)
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx * inv, ny * inv, nz * inv
    L = np.array([-0.55, -0.6, 0.58], np.float32)
    L /= np.linalg.norm(L)
    diffuse = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)

    # albedo: cool violet-grey stone, per-block tone + warmth, grain, lichen, cracks
    dark, light = hexc('#3a3646'), hexc('#6c6678')
    cool, warm = hexc('#4a4a66'), hexc('#6a5c58')
    t = (0.25 + 0.5 * base_t + (grain - 0.5) * 0.8)[..., None]
    col = dark + (light - dark) * np.clip(t, 0, 1)
    col = col * 0.7 + (cool + (warm - cool) * warm_t[..., None]) * 0.3 * (0.6 + grain[..., None] * 0.8)

    crack_n = fbm(W, h, 2.4, seed + 6)
    crack = 1 - smooth(0.0, 0.007, np.abs(crack_n - 0.5))
    crack *= smooth(3, 12, d) * smooth(0.45, 0.6, fbm(W, h, 2.0, seed + 8))   # only some blocks are cracked
    col = col * (1 - crack[..., None] * 0.75)

    lich = smooth(0.62, 0.72, fbm(W, h, 1.4, seed + 7)) * (0.35 + 0.65 * (1 - smooth(0, 26, d)))
    col = col + (hexc('#3d5a3f') - col) * (lich[..., None] * 0.55)

    mortar = hexc('#0c0a14')
    ao = 0.45 + 0.55 * smooth(0, 11, d)
    shade = (0.34 + 0.95 * diffuse) * ao
    out = col * shade[..., None]
    out = out + (mortar - out) * (1 - smooth(0.8, 2.8, d))[..., None]
    # faint cool rim on lit bevel edges
    rim = smooth(3, 7, d) * (1 - smooth(7, 12, d)) * np.clip(diffuse - 0.6, 0, 1)
    out = out + (hexc('#9a98c8') - out) * (rim[..., None] * 0.35)
    return np.clip(out, 0, 255)


def moss_lip(img, seed, extra_depth=0):
    """Paint a wet mossy lip with ragged blades over the top LIP rows of float-RGBA img (H,W,4)."""
    rng = np.random.default_rng(seed)
    n1 = fbm(W, 1, 1.5, seed + 11)[0]
    thick = 15 + 13 * n1                                   # lip thickness per column
    drips = np.zeros(W, np.float32)
    for _ in range(9):                                      # a few longer drips
        x0 = int(rng.integers(0, W))
        wdt = int(rng.integers(5, 12))
        ln = int(rng.integers(6, 12))
        for k in range(wdt):
            drips[(x0 + k) % W] = max(drips[(x0 + k) % W], ln * np.sin(np.pi * (k + 0.5) / wdt))
    thick = np.minimum(thick + drips, LIP - 1)
    blade = fbm(W, 1, 0.6, seed + 12)[0]
    blade_h = 4 + 5 * blade                                 # blades poking above the lip line
    tex = fbm(W, LIP + 8, 1.2, seed + 13)
    tex2 = fbm(W, LIP + 8, 0.7, seed + 14)
    m_dark, m_mid, m_hi = hexc('#14241c'), hexc('#2a4630'), hexc('#6b8a4a')
    for y in range(LIP):
        for x in range(W):
            top_line = blade_h[x]                           # y < top_line -> mostly transparent grass
            if y >= thick[x]:
                continue
            depth = y / max(1.0, thick[x])
            v = tex[y, x] * 0.6 + tex2[y, x] * 0.4
            c = m_dark + (m_mid - m_dark) * np.clip((v - 0.25) * 2.4, 0, 1)
            c = c + (m_hi - c) * (np.clip(1 - depth * 2.6, 0, 1) * np.clip((v - 0.35) * 2.0, 0, 0.8))
            c = c * (1 - 0.55 * smooth(0.55, 1.0, depth))   # shadowed, wet underside
            img[y, x, :3] = c
            img[y, x, 3] = 255
    # tiny stone-shadow under the lip so it sits on the block
    for x in range(W):
        y0 = int(thick[x])
        for k in range(12):
            y = y0 + k
            if y < img.shape[0]:
                f = 1 - k / 12.0
                img[y, x, :3] *= (1 - 0.5 * f * f)
    return img


def depth_fog(arr, y_from, y_to, k):
    h = arr.shape[0]
    g = np.clip((np.arange(h) - y_from) / max(1, y_to - y_from), 0, 1)[:, None, None]
    deep = np.array([6, 5, 12], np.float32)
    arr[..., :3] = arr[..., :3] * (1 - g * k) + deep * (g * k)
    return arr


def save(arr, name):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(OUT, name))


def ground():
    mid_h = 256 - LIP                       # 216 = 3 rows of 72 (tiled middle, periodic)
    s = stone(mid_h, 72, 21)
    full = np.concatenate([s[mid_h - LIP:], s], 0)          # top border continues the periodic pattern
    rgba = np.concatenate([full, np.full((256, W, 1), 255, np.float32)], 2)
    rgba = moss_lip(rgba, 5)
    rgba = depth_fog(rgba, LIP, 256, 0.35)
    save(rgba, 'ground.png')


def platform():
    mid_h = 128 - LIP - UNDER               # 64 = one row (periodic)
    s = stone(mid_h, 64, 33)
    full = np.concatenate([s[mid_h - LIP + 0:] if LIP <= mid_h else np.tile(s, (2, 1, 1))[-LIP:], s, np.tile(s, (2, 1, 1))[:UNDER]], 0)
    rgba = np.concatenate([full, np.full((128, W, 1), 255, np.float32)], 2)
    rgba = moss_lip(rgba, 9)
    # shadowed underside: darkens toward the bottom, cold bounce from the void
    y0 = 128 - UNDER - 6
    g = smooth(y0, 127, np.arange(128).astype(np.float32))[:, None, None]
    rgba[..., :3] = rgba[..., :3] * (1 - 0.72 * g) + np.array([10, 8, 22], np.float32) * (0.72 * g)
    save(rgba, 'platform.png')


if __name__ == '__main__':
    ground()
    platform()
    print('painted environment written to', os.path.abspath(OUT))
