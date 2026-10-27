"""Procedural pixel-art generator for placeholder character sprites.
Run:  python3 Tools/generate_sprites.py   (needs Pillow)
Writes 64x64 PNG frames to Assets/Resources/Sprites/<Player|Husk>/<clip>_<n>.png
Character is drawn facing right; feet on the bottom row; body centre at x=24.
"""
import math, os
from PIL import Image, ImageDraw
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stylize import stylize_sprite

W = H = 64
G = 63  # ground row

def C(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i+2], 16) for i in (0, 2, 4)) + (255,)

PLAYER = {k: C(v) for k, v in dict(
    cloak='#2b2540', cloak_hi='#3f3660', hood='#221d33', hood_hi='#372f50',
    face='#0b0912', eye='#ffb64a', armor='#7d8699', armor_hi='#aab3c6', armor_lo='#4d5468',
    scarf='#a3202c', scarf_hi='#cf3a45', boot='#1c1828', leg='#2b2540', leg_back='#1e1a2c',
    blade='#cfd6e4', blade_edge='#ffffff', hilt='#8a6a3a', outline='#07050b').items()}
PLAYER['slen'] = 18

HUSK = {k: C(v) for k, v in dict(
    cloak='#3b4a3a', cloak_hi='#52654f', hood='#2f3a2c', hood_hi='#44553f',
    face='#1a0d0d', eye='#ff3a3a', armor='#6b5a4a', armor_hi='#8c7864', armor_lo='#43382e',
    scarf='#5a3a2a', scarf_hi='#7a5238', boot='#1a1a14', leg='#3b4a3a', leg_back='#2a3629',
    blade='#8a6a58', blade_edge='#b08a6a', hilt='#3a2a20', outline='#07050b').items()}
HUSK['slen'] = 14

def pt(p): return (int(round(p[0])), int(round(p[1])))

def leg(d, hip, foot, col, P):
    fx, fy = foot
    d.line([pt(hip), (fx, fy - 2)], fill=col, width=4)
    d.rectangle([fx - 2, fy - 3, fx + 3, fy], fill=P['boot'])
    d.rectangle([fx - 2, fy - 3, fx + 3, fy - 3], fill=P['armor_lo'])

def cape_layer(P, tip):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    tx, ty = tip
    d.polygon([(19, 26), (24, 26), (23, 42), (tx + 8, ty), (tx + 1, ty - 3), (tx + 1, ty - 14), (16, 34)], fill=P['cloak'])
    d.line([(19, 28), (tx + 4, ty - 4)], fill=P['cloak_hi'], width=1)
    return im

def sword(d, hand, ang, length, P):
    a = math.radians(ang); dx, dy = math.cos(a), math.sin(a); hx, hy = hand
    d.line([pt((hx - dx * 3, hy - dy * 3)), pt(hand)], fill=P['hilt'], width=2)
    px, py = -dy, dx
    d.line([pt((hx + px * 3, hy + py * 3)), pt((hx - px * 3, hy - py * 3))], fill=P['hilt'], width=2)
    s = (hx + dx * 2, hy + dy * 2); e = (hx + dx * length, hy + dy * length)
    d.line([pt(s), pt(e)], fill=P['blade'], width=3)
    d.line([pt(s), pt(e)], fill=P['blade_edge'], width=1)

def upper_layer(P, hand, ang, back):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # far arm
    d.line([(20, 28), pt(back)], fill=P['cloak'], width=4)
    d.rectangle([back[0] - 1, back[1] - 1, back[0] + 1, back[1] + 1], fill=P['armor_lo'])
    # torso, tassets, chest plate, belt
    d.rectangle([18, 25, 29, 41], fill=P['cloak'])
    d.rectangle([18, 25, 19, 41], fill=P['cloak_hi'])
    d.polygon([(18, 40), (29, 40), (30, 46), (17, 46)], fill=P['cloak_hi'])
    d.rectangle([21, 27, 29, 35], fill=P['armor'])
    d.rectangle([21, 27, 29, 28], fill=P['armor_hi'])
    d.rectangle([21, 35, 29, 35], fill=P['armor_lo'])
    d.rectangle([18, 38, 29, 39], fill=P['boot'])
    d.rectangle([23, 38, 25, 39], fill=P['hilt'])
    # scarf
    d.rectangle([19, 23, 29, 25], fill=P['scarf'])
    d.rectangle([19, 23, 29, 23], fill=P['scarf_hi'])
    # hood
    d.polygon([(19, 24), (17, 15), (20, 8), (24, 4), (29, 8), (31, 15), (30, 24)], fill=P['hood'])
    d.polygon([(19, 24), (17, 15), (20, 8), (24, 4), (22, 12), (21, 24)], fill=P['hood_hi'])
    d.polygon([(25, 11), (30, 12), (30, 21), (25, 22), (24, 16)], fill=P['face'])
    d.rectangle([27, 15, 27, 16], fill=P['eye'])
    d.rectangle([29, 15, 29, 16], fill=P['eye'])
    # front arm + pauldron + sword
    d.line([(27, 28), pt(hand)], fill=P['cloak_hi'], width=4)
    d.ellipse([24, 24, 32, 31], fill=P['armor'])
    d.arc([24, 24, 32, 31], 180, 300, fill=P['armor_hi'])
    sword(d, hand, ang, P['slen'], P)
    d.rectangle([hand[0] - 1, hand[1] - 1, hand[0] + 1, hand[1] + 1], fill=P['armor_hi'])
    return im

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
    ld = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ld)
    leg(d, (21, 41), legs[0], P['leg_back'], P)
    leg(d, (26, 41), legs[1], P['leg'], P)
    img.alpha_composite(ld)
    up = upper_layer(P, hand, ang, back)
    img.paste(up, (lean, bob), up)
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
    print('generated', len(FRAMES) * 2, 'sprites')
