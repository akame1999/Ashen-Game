"""Builds godot/assets/characters/player.png + player.json from the owner's Ashen Knight atlas
(4x3 grid of 384x342 cells: idle / run / attack). Missing animations are mapped from those frames.
Run from repo root: python3 tools/build_knight_sheet.py
"""
import json
from PIL import Image

SRC = "godot/assets/characters/src/ashen_knight_spritesheet.png"
OUT_PNG = "godot/assets/characters/player.png"
OUT_JSON = "godot/assets/characters/player.json"
CW, CH = 384, 342
FRAME = 128
SCALE = 0.24
FEET = 120
CX = 64

src = Image.open(SRC).convert("RGBA")


def cell(row, col):
    c = src.crop((col * CW, row * CH, (col + 1) * CW, (row + 1) * CH))
    w, h = round(CW * SCALE), round(CH * SCALE)
    c = c.resize((w, h), Image.LANCZOS)
    f = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    f.paste(c, ((FRAME - w) // 2, FEET - round(331 * SCALE)), c)
    return f


idle = [cell(0, i) for i in range(4)]
run = [cell(1, i) for i in range(4)]
atk = [cell(2, i) for i in range(4)]


def fall_over(base, n):
    out = []
    for i in range(n):
        t = i / (n - 1)
        im = base.rotate(-85 * t, resample=Image.BICUBIC, center=(CX + 10, FEET))
        out.append(im)
    return out


ROWS = [
    ("idle", idle),
    ("run", run),
    ("jump", [run[1], run[2]]),
    ("fall", [run[0], run[3]]),
    ("dodge", [run[3], run[0], run[1], run[2]]),
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
json.dump({"frame": FRAME, "feet_row": FEET, "rows": meta_rows, "center_x": CX}, open(OUT_JSON, "w"), indent=1)
print("wrote", OUT_PNG, sheet.size)
