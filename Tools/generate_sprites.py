"""Procedural dark-fantasy pixel-art character generator (original designs).
Run:  python3 Tools/generate_sprites.py   (needs Pillow)
Writes 128x128 PNG frames to Assets/Resources/Sprites/<Player|Husk>/<clip>_<n>.png (imported at 72 px/unit).
Poses are authored on a 64-unit grid and drawn at 2x so every limb gets plate/cloth detail.
Character faces right; feet on the bottom row; body centre at x=48 (pivot 0.375).
"""
import math, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stylize import stylize_sprite

S = 2
W = H = 64 * S
G = 63  # ground row on the 64 grid

def C(s):
    s = s.lstrip('#'); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4)) + (255,)
def dk(c, f): return tuple(int(v * f) for v in c[:3]) + (255,)
def lt(c, f): return tuple(min(255, int(v + (255 - v) * f)) for v in c[:3]) + (255,)

def palette(d, kind, slen):
    P = {k: C(v) for k, v in d.items()}
    P['cloak_lo'] = dk(P['cloak'], 0.62); P['hood_lo'] = dk(P['hood'], 0.6)
    P['armor_dk'] = dk(P['armor_lo'], 0.7); P['rivet'] = lt(P['armor_hi'], 0.4)
    P['blade_dk'] = dk(P['blade'], 0.62); P['gold'] = C('#c9a24a')
    P['slen'] = slen; P['kind'] = kind
    return P

PLAYER = palette(dict(
    cloak='#2b2540', cloak_hi='#4a3f72', hood='#221d33', hood_hi='#3d3460',
    face='#07050b', eye='#ffb64a', armor='#7d8699', armor_hi='#b4bdd0', armor_lo='#4d5468',
    scarf='#a3202c', scarf_hi='#d4414c', boot='#1c1828', leg='#2b2540', leg_back='#1e1a2c',
    blade='#cfd6e4', blade_edge='#ffffff', hilt='#8a6a3a', outline='#07050b'), 'knight', 18)

HUSK = palette(dict(
    cloak='#3b4a3a', cloak_hi='#5a7055', hood='#2f3a2c', hood_hi='#4a5d44',
    face='#120808', eye='#ff3a3a', armor='#6b5a4a', armor_hi='#9a8470', armor_lo='#43382e',
    scarf='#5a3a2a', scarf_hi='#7a5238', boot='#1a1a14', leg='#3b4a3a', leg_back='#2a3629',
    blade='#8a6a58', blade_edge='#b08a6a', hilt='#3a2a20', outline='#07050b'), 'husk', 14)

class Cv:
    """Draws in 64-grid coordinates onto a 128px RGBA canvas."""
    def __init__(self):
        self.im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.im)
    @staticmethod
    def p(q): return (q[0] * S, q[1] * S)
    def poly(self, pts, fill): self.d.polygon([self.p(q) for q in pts], fill=fill)
    def rect(self, x0, y0, x1, y1, fill): self.d.rectangle([x0 * S, y0 * S, x1 * S + S - 1, y1 * S + S - 1], fill=fill)
    def line(self, a, b, fill, w=1): self.d.line([self.p(a), self.p(b)], fill=fill, width=max(1, int(round(w * S))))
    def ell(self, b, fill): self.d.ellipse([b[0] * S, b[1] * S, b[2] * S + S - 1, b[3] * S + S - 1], fill=fill)
    def dot(self, x, y, fill, r=0.5): self.d.rectangle([x * S - r * S, y * S - r * S, x * S + r * S, y * S + r * S], fill=fill)

def cape_layer(P, tip):
    c = Cv(); tx, ty = tip
    hem = [(tx + 8, ty), (tx + 6.5, ty - 2.5), (tx + 5.5, ty + 0.5), (tx + 3.5, ty - 2), (tx + 2.5, ty + 1), (tx + 1, ty - 3)]
    c.poly([(19, 26), (24, 26), (23, 42)] + hem + [(tx + 1, ty - 14), (16, 34)], P['cloak'])
    c.poly([(19, 28), (23, 40), (tx + 8, ty), (tx + 6.5, ty - 2.5), (tx + 5, ty - 8)], P['cloak_lo'])   # inner lining
    for k, (a, b) in enumerate((((20, 30), (tx + 5, ty - 4)), ((21, 34), (tx + 7, ty - 1)), ((18, 33), (tx + 2, ty - 8)))):
        c.line(a, b, P['cloak_hi'] if k != 1 else P['cloak_lo'], 0.5)
    c.line((19, 27), (tx + 1, ty - 13), P['cloak_hi'], 0.5)
    return c.im

def leg(c, hip, foot, col, P):
    fx, fy = foot
    c.line(hip, (fx, fy - 3), col, 4)
    k = ((hip[0] + fx) / 2 + 1, (hip[1] + fy) / 2)                # knee plate
    c.rect(int(k[0]) - 2, int(k[1]) - 1, int(k[0]) + 2, int(k[1]) + 1, P['armor_lo']); c.rect(int(k[0]) - 2, int(k[1]) - 1, int(k[0]) + 2, int(k[1]) - 1, P['armor'])
    c.rect(fx - 3, fy - 6, fx + 2, fy - 4, P['armor_lo'])         # greave
    c.rect(fx - 3, fy - 6, fx + 2, fy - 6, P['armor'])
    c.rect(fx - 3, fy - 3, fx + 4, fy, P['boot'])                 # boot + toe cap
    c.rect(fx + 2, fy - 2, fx + 4, fy, P['armor_dk']); c.rect(fx - 3, fy, fx + 4, fy, P['armor_dk'])

def sword(c, hand, ang, length, P):
    a = math.radians(ang); dx, dy = math.cos(a), math.sin(a); hx, hy = hand; px, py = -dy, dx
    if P['kind'] == 'husk':                                        # crude spiked club
        e = (hx + dx * length, hy + dy * length)
        c.line((hx - dx * 3, hy - dy * 3), (hx + dx * 3, hy + dy * 3), P['hilt'], 2)
        c.line((hx + dx * 3, hy + dy * 3), e, P['blade'], 4); c.line((hx + dx * 3, hy + dy * 3), e, P['blade_edge'], 1)
        for t in (0.45, 0.7, 0.92):
            sx, sy = hx + dx * length * t, hy + dy * length * t
            c.dot(sx + px * 2, sy + py * 2, P['armor_lo']); c.dot(sx - px * 2, sy - py * 2, P['armor_lo'])
        return
    c.line((hx - dx * 4, hy - dy * 4), (hx + dx, hy + dy), P['hilt'], 1.6)                 # wrapped grip
    c.dot(hx - dx * 4.5, hy - dy * 4.5, P['gold'], 1)                                       # pommel
    c.line((hx + px * 4, hy + py * 4), (hx - px * 4, hy - py * 4), P['gold'], 1.4)          # crossguard
    c.dot(hx + px * 4, hy + py * 4, P['gold'], 0.8); c.dot(hx - px * 4, hy - py * 4, P['gold'], 0.8)
    s0 = (hx + dx * 2, hy + dy * 2); e = (hx + dx * length, hy + dy * length)
    c.line(s0, e, P['blade_dk'], 3.4)
    c.line(s0, e, P['blade'], 2.4)
    c.line((s0[0] + dx, s0[1] + dy), (e[0] - dx * 2, e[1] - dy * 2), P['blade_dk'], 0.6)    # fuller
    c.line((s0[0] + px * 0.9, s0[1] + py * 0.9), (e[0] + px * 0.9, e[1] + py * 0.9), P['blade_edge'], 0.6)  # edge glint

def upper_layer(P, hand, ang, back):
    c = Cv()
    # far arm: sleeve + bracer + gauntlet
    c.line((20, 28), back, P['cloak_lo'], 4)
    c.line((back[0] - 2, back[1] - 1), back, P['armor_lo'], 3)
    c.dot(back[0], back[1], P['armor_dk'], 1.2)
    # scarf tail trailing behind
    c.poly([(19, 24), (15, 27), (12, 33), (14, 34), (17, 30), (20, 27)], P['scarf']); c.line((16, 27), (13, 33), P['scarf_hi'], 0.5)
    # torso / tunic
    c.rect(18, 25, 29, 41, P['cloak']); c.rect(18, 25, 19, 41, P['cloak_hi']); c.rect(28, 30, 29, 41, P['cloak_lo'])
    # tassets (3 plates) + belt
    for i, x in enumerate((18, 21.5, 25)):
        c.poly([(x, 39), (x + 4, 39), (x + 4.5, 46 + (i % 2)), (x - 0.5, 46 + (i % 2))], P['cloak_hi'] if i != 1 else P['cloak'])
        c.line((x + 2, 40), (x + 2, 45), P['cloak_lo'], 0.5)
    c.rect(18, 38, 29, 39, P['boot']); c.rect(23, 38, 25, 39, P['gold']); c.rect(24, 38, 24, 39, P['hilt'])
    c.rect(18, 40, 20, 42, P['hilt']); c.rect(18, 40, 20, 40, P['gold'])                  # pouch
    # chest plate: segmented, with rivets and a sigil
    c.rect(21, 27, 29, 36, P['armor']); c.rect(21, 27, 29, 28, P['armor_hi']); c.rect(21, 27, 21, 36, P['armor_hi'])
    c.rect(21, 31, 29, 31, P['armor_lo']); c.rect(21, 35, 29, 36, P['armor_lo']); c.rect(28, 28, 29, 36, P['armor_lo'])
    c.line((25, 29), (25, 34), P['armor_dk'], 0.5); c.dot(23, 29, P['rivet'], 0.3); c.dot(27, 29, P['rivet'], 0.3)
    c.dot(23, 33, P['rivet'], 0.3); c.dot(27, 33, P['rivet'], 0.3)
    c.dot(25, 32, P['eye'], 0.4)                                                          # ember sigil
    # gorget + scarf
    c.rect(19, 23, 29, 25, P['scarf']); c.rect(19, 23, 29, 23, P['scarf_hi']); c.rect(23, 25, 24, 25, P['scarf_hi'])
    # hood: outer, rim light, inner shadow, seam, drooping point
    c.poly([(19, 24), (16.5, 15), (19.5, 8), (24, 3), (29, 7), (31.5, 15), (30, 24)], P['hood'])
    c.poly([(19, 24), (16.5, 15), (19.5, 8), (24, 3), (22, 11), (21, 24)], P['hood_hi'])
    c.poly([(30, 24), (31.5, 15), (29, 7), (28, 12), (28, 22)], P['hood_lo'])
    c.line((23, 4), (21.5, 22), P['hood_lo'], 0.5)                                         # seam
    c.poly([(24.5, 10.5), (30.5, 11.5), (30.5, 21.5), (24.5, 22), (23.5, 16)], P['face'])   # face void
    c.rect(26, 14, 27, 15, P['eye']); c.rect(29, 14, 30, 15, P['eye'])                      # glowing eyes
    if P['kind'] == 'husk':                                                                 # hollow, crooked grin + ragged hood hem
        c.line((26, 19), (29, 18.5), P['eye'], 0.5)
        c.poly([(19, 24), (21, 26), (23, 24.5), (25, 26.5), (27, 24.5), (29, 26), (30, 24)], P['hood'])
    # front arm: sleeve, bracer, pauldron plates, gauntlet
    c.line((27, 28), hand, P['cloak_hi'], 4)
    mx, my = (27 + hand[0]) / 2, (28 + hand[1]) / 2
    c.line((mx, my), hand, P['armor_lo'], 3.4); c.line((mx, my - 0.8), (hand[0], hand[1] - 0.8), P['armor'], 1)
    c.ell((23.5, 23.5, 32.5, 31), P['armor']); c.ell((24.5, 28, 32, 32.5), P['armor_lo'])
    c.d.arc([23.5 * S, 23.5 * S, 33 * S, 31.5 * S], 180, 300, fill=P['armor_hi'], width=2)
    c.dot(28, 26, P['rivet'], 0.35)
    sword(c, hand, ang, P['slen'], P)
    c.dot(hand[0], hand[1], P['armor_hi'], 1.4); c.dot(hand[0] - 0.4, hand[1] - 0.4, P['rivet'], 0.5)   # gauntlet
    return c.im

def outline(img, col):
    src = img.load(); out = img.copy(); o = out.load()
    for y in range(H):
        for x in range(W):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and src[nx, ny][3] > 0:
                        o[x, y] = col; break
    return out

def frame(P, legs, lean=0, bob=0, cape=(12, 52), hand=(32, 36), ang=-55, back=(19, 38)):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    img.alpha_composite(cape_layer(P, cape))
    lc = Cv()
    leg(lc, (21, 41), legs[0], P['leg_back'], P)
    leg(lc, (26, 41), legs[1], P['leg'], P)
    img.alpha_composite(lc.im)
    up = upper_layer(P, hand, ang, back)
    img.paste(up, (lean * S, bob * S), up)
    return outline(img, P['outline'])

FRAMES = {
    'idle_0': dict(legs=((21, G), (27, G)), bob=0, cape=(12, 52), hand=(32, 36), ang=-55),
    'idle_1': dict(legs=((21, G), (27, G)), bob=1, cape=(11, 53), hand=(32, 37), ang=-52),
    'run_0': dict(legs=((17, 58), (31, G)), lean=2, bob=1, cape=(4, 49), hand=(33, 33), ang=-35, back=(15, 34)),
    'run_1': dict(legs=((24, 56), (25, G)), lean=2, bob=0, cape=(3, 47), hand=(33, 33), ang=-35, back=(15, 34)),
    'run_2': dict(legs=((31, G), (18, 58)), lean=2, bob=1, cape=(4, 49), hand=(33, 33), ang=-35, back=(15, 34)),
    'run_3': dict(legs=((25, G), (23, 56)), lean=2, bob=0, cape=(3, 47), hand=(33, 33), ang=-35, back=(15, 34)),
    'jump_0': dict(legs=((22, 53), (29, 56)), lean=1, bob=-1, cape=(14, 40), hand=(32, 32), ang=-80),
    'fall_0': dict(legs=((19, 58), (30, 60)), cape=(14, 38), hand=(32, 30), ang=-20),
    'attack_0': dict(legs=((19, G), (29, G)), lean=-2, bob=1, cape=(10, 52), hand=(23, 22), ang=-155, back=(16, 34)),
    'attack_1': dict(legs=((18, G), (31, G)), lean=3, cape=(8, 50), hand=(34, 29), ang=-3, back=(16, 36)),
    'attack_2': dict(legs=((18, G), (31, G)), lean=3, bob=1, cape=(8, 50), hand=(33, 37), ang=50, back=(17, 38)),
    'dash_0': dict(legs=((14, 60), (32, 59)), lean=5, bob=3, cape=(2, 50), hand=(30, 36), ang=175, back=(14, 36)),
    'hurt_0': dict(legs=((19, G), (28, G)), lean=-3, bob=2, cape=(15, 50), hand=(30, 38), ang=-120, back=(17, 36)),
}

if __name__ == '__main__':
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Assets', 'Resources', 'Sprites')
    for folder, pal in (('Player', PLAYER), ('Husk', HUSK)):
        os.makedirs(os.path.join(root, folder), exist_ok=True)
        for name, kw in FRAMES.items():
            stylize_sprite(frame(pal, **kw)).save(os.path.join(root, folder, name + '.png'))
    print('generated', len(FRAMES) * 2, 'sprites at', W, 'px')
