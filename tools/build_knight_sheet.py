"""Builds godot/assets/characters/player.png + player.json from the owner's Ashen Knight atlas
(4x3 grid of 384x342 cells: idle / run / attack). Missing animations are mapped from those frames.
Run from repo root: python3 tools/build_knight_sheet.py
"""
import json
import numpy as np
from PIL import Image, ImageEnhance

SRC = "godot/assets/characters/src/ashen_knight_spritesheet.png"
OUT_PNG = "godot/assets/characters/player.png"
OUT_JSON = "godot/assets/characters/player.json"
CW, CH = 384, 342
FRAME = 256          # frames are rendered at ~2x game size; player.gd scales the sprite by NODE_SCALE
SCALE = 0.48
NODE_SCALE = 0.5
FEET = 240
CX = 128

src = Image.open(SRC).convert("RGBA")


def anchor_x(c):
    """x of the body mass (armour/hood/legs, ignoring the red cape and thin sword) so frames line up."""
    a = np.array(c)
    op = a[:, :, 3] > 40
    red = (a[:, :, 0].astype(int) > a[:, :, 1].astype(int) + 50) & (a[:, :, 0].astype(int) > a[:, :, 2].astype(int) + 50)
    m = op & ~red
    m[:120, :] = False
    ys, xs = np.where(m)
    return float(xs.mean()) if len(xs) else CW / 2


def body_height(c):
    a = np.array(c)
    op = a[:, :, 3] > 40
    red = (a[:, :, 0].astype(int) > a[:, :, 1].astype(int) + 50) & (a[:, :, 0].astype(int) > a[:, :, 2].astype(int) + 50)
    rows = np.where((op & ~red).sum(1) > 6)[0]
    return float(rows.max() - rows.min())


def cell(row, col, target_h=None):
    c = src.crop((col * CW, row * CH, (col + 1) * CW, (row + 1) * CH))
    k = 1.0
    if target_h:  # normalise body height so the cycle doesn't pulse in size
        k = target_h / body_height(c)
    ax = anchor_x(c) * SCALE * k
    w, h = round(CW * SCALE * k), round(CH * SCALE * k)
    c = c.resize((w, h), Image.LANCZOS)
    c = ImageEnhance.Contrast(c).enhance(1.15)
    c = ImageEnhance.Color(c).enhance(1.1)
    r, g, b, al = c.split()
    r, g, b = [ImageEnhance.Brightness(ch).enhance(1.12) for ch in (r, g, b)]
    c = Image.merge("RGBA", (r, g, b, al))
    f = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    f.paste(c, (round(CX - ax), FEET - round(331 * SCALE * k)), c)
    return f


idle = [cell(0, i) for i in range(4)]
RUN_H = 232
run = [cell(1, i, RUN_H) for i in range(4)]
atk = [cell(2, i) for i in range(4)]


def fall_over(base, n):
    out = []
    for i in range(n):
        t = i / (n - 1)
        im = base.rotate(-85 * t, resample=Image.BICUBIC, center=(CX + 20, FEET))
        out.append(im)
    return out


import math

HIP_Y = 184          # hip line in the 256px idle frame
SPLIT_X = 128        # separates back leg (left) from front leg (right)
PIV_BACK = (112, HIP_Y)
PIV_FRONT = (150, HIP_Y)


def _split(base):
    """Upper body (incl. cape) / back leg / front leg layers of the clean idle pose."""
    a = np.array(base)
    op = a[:, :, 3] > 0
    red = (a[:, :, 0].astype(int) > a[:, :, 1].astype(int) + 50) & (a[:, :, 0].astype(int) > a[:, :, 2].astype(int) + 50)
    yy, xx = np.mgrid[0:FRAME, 0:FRAME]
    leg = op & ~red & (yy >= HIP_Y - 4)
    layers = []
    for sel in (op & ~leg, leg & (xx < SPLIT_X), leg & (xx >= SPLIT_X)):
        b = a.copy()
        b[~sel] = 0
        layers.append(Image.fromarray(b, "RGBA"))
    return layers


def pose(base, back_deg=0.0, front_deg=0.0, back_lift=0.0, front_lift=0.0, bob=0.0, lean=0.0):
    """Procedural pose from the clean idle frame: legs rotate about the hips, torso bobs/leans."""
    upper, back, front = _split(base)
    out = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    for layer, deg, lift, piv in ((back, back_deg, back_lift, PIV_BACK), (front, front_deg, front_lift, PIV_FRONT)):
        r = layer.rotate(deg, resample=Image.BICUBIC, center=piv)
        out.alpha_composite(r, (0, round(-lift - bob)))
    u = upper.rotate(-lean, resample=Image.BICUBIC, center=(CX, HIP_Y))
    out.alpha_composite(u, (0, round(-bob)))
    return out


def run_cycle(base, n=8):
    frames = []
    for i in range(n):
        ph = 2 * math.pi * i / n
        frames.append(pose(base,
                           back_deg=26 * math.sin(ph + math.pi), front_deg=26 * math.sin(ph),
                           back_lift=7 * max(0.0, math.cos(ph + math.pi)), front_lift=7 * max(0.0, math.cos(ph)),
                           bob=3 * abs(math.sin(ph)), lean=7))
    return frames


def jump_frames(base):
    return [pose(base, back_deg=-28, front_deg=34, back_lift=8, front_lift=14, bob=2, lean=3),
            pose(base, back_deg=-20, front_deg=28, back_lift=10, front_lift=10, bob=0, lean=2)]


def fall_frames(base):
    return [pose(base, back_deg=-12, front_deg=14, back_lift=0, front_lift=2, bob=0, lean=-2),
            pose(base, back_deg=-16, front_deg=18, back_lift=0, front_lift=3, bob=1, lean=-3)]


def roll(base, n=6):
    """Dodge roll: the clean pose shrunk and spun forward once around the body centre."""
    sz = round(FRAME * 0.62)
    small = base.resize((sz, sz), Image.LANCZOS)
    out = []
    for i in range(n):
        tmp = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
        tmp.paste(small, ((FRAME - sz) // 2, FEET - sz + 3), small)
        out.append(tmp.rotate(-360 * (i + 0.5) / n, resample=Image.BICUBIC, center=(CX, FEET - 42)))
    return out


ROWS = [
    ("idle", idle),
    ("run", run_cycle(idle[0])),
    ("jump", jump_frames(idle[0])),
    ("fall", fall_frames(idle[0])),
    ("dodge", roll(idle[0])),
    ("light1", [atk[0], atk[0], atk[1], atk[3], atk[3]]),
    ("light2", [atk[0], atk[2], atk[2], atk[3], atk[3]]),
    ("heavy", [atk[0], atk[0], atk[0], atk[2], atk[3], atk[3]]),
    ("skill", [atk[0], atk[1], atk[1], atk[2], atk[3], atk[3]]),
    ("hurt", [idle[0], idle[1]]),
    ("death", fall_over(idle[0], 6)),
]
cols = max(len(f) for _, f in ROWS)
sheet = Image.new("RGBA", (cols * FRAME, len(ROWS) * FRAME), (0, 0, 0, 0))
meta_rows = []
for r, (name, frames) in enumerate(ROWS):
    for i, fr in enumerate(frames):
        sheet.paste(fr, (i * FRAME, r * FRAME))
    meta_rows.append({"name": name, "row": r, "frames": len(frames)})
sheet.save(OUT_PNG)
json.dump({"frame": FRAME, "feet_row": FEET, "rows": meta_rows, "center_x": CX, "scale": NODE_SCALE}, open(OUT_JSON, "w"), indent=1)
print("wrote", OUT_PNG, sheet.size)
