"""Dark-fantasy art pass (moody, high-contrast, painterly-pixel look). Original work, not ripped from any game.
Used by generate_sprites.py / generate_backgrounds.py at save time (pure per-pixel, so output is deterministic)."""
from PIL import Image, ImageFilter

BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))

def _mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def _lum(c): return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]

def stylize_sprite(img, rim=(150, 170, 255), warm=(255, 150, 70), glow_cols=((255, 182, 74), (255, 58, 58))):
    """Rim light from upper-right (cool moon), warm bounce on lower-left, coloured outline, eye glow, foot fog."""
    W, H = img.size
    src = img.load()
    out = img.copy(); o = out.load()
    def solid(x, y): return 0 <= x < W and 0 <= y < H and src[x, y][3] > 0
    for y in range(H):
        for x in range(W):
            r, g, b, a = src[x, y]
            if a == 0: continue
            c = (r, g, b)
            edge_top = not solid(x, y - 1); edge_right = not solid(x + 1, y)
            edge_left = not solid(x - 1, y); edge_bot = not solid(x, y + 1)
            if _lum(c) < 14:                       # outline pixel: tint toward neighbours' colour, never pure black
                nb = [src[nx, ny][:3] for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)) if solid(nx, ny) and _lum(src[nx, ny][:3]) >= 14]
                if nb:
                    m = tuple(sum(p[i] for p in nb) // len(nb) for i in range(3))
                    o[x, y] = _mix((8, 6, 14), m, 0.22) + (a,)
                continue
            if (edge_top or edge_right) and _lum(c) > 20:       # rim light (stronger on already-lit surfaces)
                o[x, y] = _mix(c, rim, 0.55 + min(0.25, _lum(c) / 400)) + (a,)
            elif edge_left or edge_bot:                          # shadowed edge + warm bounce
                o[x, y] = _mix(_mix(c, (0, 0, 8), 0.35), warm, 0.06) + (a,)
            else:
                # soft form shading: darker toward lower-left via dithered step
                t = (x - W * 0.3) / W - (y - H * 0.5) / H
                if t < -0.15 and BAYER[y & 3][x & 3] < 7: o[x, y] = _mix(c, (0, 0, 10), 0.22) + (a,)
    # foot fog: dithered fade into ground mist on the lowest rows
    fog = (70, 60, 100)
    for y in range(H - 7, H):
        k = (y - (H - 7)) / 7.0
        for x in range(W):
            if o[x, y][3] and BAYER[y & 3][x & 3] / 16.0 < k * 0.55:
                o[x, y] = _mix(o[x, y][:3], fog, 0.55) + (o[x, y][3],)
    # glow around emissive pixels (eyes, etc.)
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gp = glow.load()
    for y in range(H):
        for x in range(W):
            p = src[x, y]
            if p[3] and any(p[:3] == gc for gc in glow_cols):
                gp[x, y] = p[:3] + (255,)
    halo = glow.filter(ImageFilter.GaussianBlur(2.2))
    hp = halo.load()
    for y in range(H):
        for x in range(W):
            if o[x, y][3] == 0 and hp[x, y][3] > 28:
                o[x, y] = hp[x, y][:3] + (min(110, hp[x, y][3] // 2),)
    for y in range(H):  # keep the hot core bright
        for x in range(W):
            p = src[x, y]
            if p[3] and any(p[:3] == gc for gc in glow_cols): o[x, y] = _mix(p[:3], (255, 255, 230), 0.35) + (255,)
    return out

def stylize_layer(img, kind):
    """Colour grade + dithered fog. Horizontal-seamless (no x-dependent gradients)."""
    img = img.convert('RGBA'); W, H = img.size; px = img.load()
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a == 0: continue
            c = (r, g, b)
            t = y / (H - 1)
            if kind == 'sky':                       # moody violet-teal grade + vignette-free horizon haze
                c = _mix(c, (40, 70, 95), 0.10 * t)
            elif kind in ('far', 'mid'):
                haze = (60, 70, 110) if kind == 'far' else (45, 45, 80)
                k = (0.28 if kind == 'far' else 0.14) * (1 - t)       # atmospheric perspective toward the top
                if BAYER[y & 3][x & 3] / 16.0 < k * 2: c = _mix(c, haze, 0.5)
            px[x, y] = c + (a,)
    return img

def vignette_sky(img, strength=0.55):
    W, H = img.size; px = img.load()
    for y in range(H):
        for x in range(W):
            dx = (x - W / 2) / (W / 2); dy = (y - H / 2) / (H / 2)
            d = min(1.0, (dx * dx * 0.7 + dy * dy) ** 0.5)
            k = max(0.0, d - 0.55) / 0.45 * strength
            r, g, b, a = px[x, y]
            px[x, y] = _mix((r, g, b), (2, 1, 6), k) + (a,)
    return img
