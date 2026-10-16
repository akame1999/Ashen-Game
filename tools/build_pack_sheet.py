#!/usr/bin/env python3
"""Build godot/assets/characters/player_<name>.png/.json from the Ashen Veil
Godot Complete Asset Pack (per-animation 160px strips) in the row layout that
Player/SheetUtil expect.

Usage: python3 tools/build_pack_sheet.py <pack_root> [male|female ...]
  <pack_root> is the folder that contains assets/characters/<name>/<anim>.png
"""
import json
import os
import sys
from PIL import Image

FRAME = 160
# game row name -> (pack strip name, frames to use)
ROWS = [
    ("idle", "idle", 6), ("run", "run", 8), ("jump", "jump_loop", 4),
    ("fall", "fall", 2), ("dodge", "dodge", 6), ("light1", "attack_light", 6),
    ("light2", "attack_light", 6), ("heavy", "attack_heavy", 8),
    ("skill", "skill", 6), ("hurt", "hurt", 3), ("death", "death", 6),
]
FEET_ROW = 140   # ground line used by the pack itself (sprite centre y=80 sits 60px above the origin)
CENTER_X = 80
SRC_DIR = "characters_combat"  # bodies without a sword; weapons are drawn separately at the hand
SCALE = 0.45     # 160px pack frames -> about the on-screen size of the knight


def build(pack_root, name, out_dir):
    src = os.path.join(pack_root, "assets", SRC_DIR, name)
    sheet = Image.new("RGBA", (FRAME * 8, FRAME * len(ROWS)), (0, 0, 0, 0))
    rows = []
    for r, (row_name, strip, n) in enumerate(ROWS):
        im = Image.open(os.path.join(src, strip + ".png")).convert("RGBA")
        assert im.size[1] == FRAME and im.size[0] >= n * FRAME, (strip, im.size)
        sheet.alpha_composite(im.crop((0, 0, n * FRAME, FRAME)), (0, r * FRAME))
        rows.append({"name": row_name, "row": r, "frames": n})
    sheet.save(os.path.join(out_dir, f"player_{name}.png"), optimize=True)
    meta = {"frame": FRAME, "feet_row": FEET_ROW, "rows": rows,
            "center_x": CENTER_X, "scale": SCALE}
    with open(os.path.join(out_dir, f"player_{name}.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print("built", name, sheet.size)


if __name__ == "__main__":
    pack = sys.argv[1]
    names = sys.argv[2:] or ["male", "female"]
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "godot", "assets", "characters")
    for n in names:
        build(pack, n, out)
