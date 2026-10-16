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


def roll(base, n=4):
    """Dodge roll: the crouched run pose shrunk and spun forward around the body centre."""
    small = base.resize((round(FRAME * 0.72), round(FRAME * 0.72)), Image.LANCZOS)
    out = []
    for i in range(n):
        f = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
        cy = FEET - 50
        # sit the shrunken pose so its feet are at the ground, then rotate about the body centre
        tmp = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
        tmp.paste(small, ((FRAME - small.width) // 2, FEET - small.height + 4), small)
        out.append(tmp.rotate(-90 * i - 20 * (i > 0), resample=Image.BICUBIC, center=(CX, cy)))
    return out


ROWS = [
    ("idle", idle),
    ("run", run),
    ("jump", [run[1], run[2]]),
    ("fall", [run[0], run[3]]),
    ("dodge", roll(run[1])),
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
