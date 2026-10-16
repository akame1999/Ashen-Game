"""Generate the placeholder player sprite sheet (96x96 frames, facing right, one animation per row).

Run from AshenVeil_Python/:  python tools/gen_player.py     Needs: numpy, pillow.
Output: assets/characters/player.png and player.json (row order, frame counts).
"""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "characters"
F = 96
OX, OY = 16, 28   # offset of the old 64-space drawing inside the 96px frame
GROUND = 60          # ground line in drawing space (row 88 in the frame)
CLOAK, CLOAK_D, CLOAK_L = (112, 24, 34), (62, 14, 24), (160, 44, 48)
ARMOR, ARMOR_D, ARMOR_L = (50, 54, 66), (28, 30, 40), (112, 118, 134)
SKIN, HAIR, BLADE, BLADE_L = (206, 176, 156), (222, 226, 238), (190, 196, 210), (250, 252, 255)
GOLD = (190, 150, 80)


class Shift:
    """ImageDraw wrapper that translates drawing-space coordinates into frame coordinates."""
    def __init__(self, d):
        self.d = d

    @staticmethod
    def _pt(v):
        if isinstance(v[0], (tuple, list)):
            return [(x + OX, y + OY) for x, y in v]
        return [c + (OX if i % 2 == 0 else OY) for i, c in enumerate(v)]

    def line(self, xy, **k): self.d.line(self._pt(xy), **k)
    def polygon(self, xy, **k): self.d.polygon(self._pt(xy), **k)
    def ellipse(self, xy, **k): self.d.ellipse(self._pt(xy), **k)
    def rectangle(self, xy, **k): self.d.rectangle(self._pt(xy), **k)
    def pieslice(self, xy, *a, **k): self.d.pieslice(self._pt(xy), *a, **k)
    def point(self, xy, **k): self.d.point(self._pt([xy])[0], **k)


def ang(deg):
    return math.cos(math.radians(deg)), math.sin(math.radians(deg))


def figure(p):
    """Render one frame. p: dict of pose parameters (see defaults below)."""
    q = dict(dx=0, hip_y=42, lean=0, stoop=0, ff=(5, 0), bf=(-4, 0), fh=(9, 8), bh=(-3, 9),
             sword=-60, sway=2, head_dx=0)
    q.update(p)
    im = Image.new("RGBA", (F, F), (0, 0, 0, 0)); d = Shift(ImageDraw.Draw(im))
    hx, hy = 28 + q["dx"], q["hip_y"]
    sx, sy = hx + q["lean"], hy - 13 + q["stoop"]
    head = (sx + 2 + q["head_dx"], sy - 7)
    fl = lambda x, y: (x, y)
    # cape (behind everything)
    s = q["sway"]
    d.polygon([(sx - 2, sy), (sx + 2, sy + 2), (hx - 5 - s, hy + 18), (hx - 12 - s * 1.4, hy + 10), (sx - 6, sy + 4)], fill=CLOAK)
    d.polygon([(sx - 2, sy + 2), (sx + 1, sy + 4), (hx - 6 - s, hy + 16), (hx - 10 - s * 1.2, hy + 11)], fill=CLOAK_D)
    d.line([(sx - 3, sy + 3), (hx - 8 - s, hy + 13)], fill=CLOAK_L)

    def leg(foot, dark):
        fx, fy = hx + foot[0], GROUND - foot[1]
        kx, ky = (hx + fx) / 2 + 3, (hy + fy) / 2
        d.line([(hx, hy), (kx, ky), (fx, fy)], fill=ARMOR_D if dark else ARMOR, width=4, joint="curve")
        d.rectangle([fx - 2, fy - 1, fx + 4, fy + 1], fill=(30, 22, 22))
    leg(q["bf"], True)

    def arm(hand, dark):
        ax, ay = sx + hand[0], sy + hand[1]
        ex, ey = (sx + ax) / 2, (sy + ay) / 2 + 2
        d.line([(sx, sy + 1), (ex, ey), (ax, ay)], fill=ARMOR_D if dark else ARMOR, width=3, joint="curve")
        d.rectangle([ax - 1, ay - 1, ax + 1, ay + 1], fill=SKIN)
        return ax, ay
    arm(q["bh"], True)
    d.polygon([(sx - 4, sy), (sx + 4, sy), (hx + 3, hy + 1), (hx - 3, hy + 1)], fill=ARMOR)       # torso
    d.line([(sx - 4, sy), (sx + 4, sy)], fill=ARMOR_L); d.line([(hx - 3, hy - 1), (hx + 3, hy - 1)], fill=GOLD)
    d.polygon([(sx - 5, sy - 1), (sx + 5, sy - 1), (sx + 4, sy + 3), (sx - 4, sy + 3)], fill=CLOAK_L)  # collar
    leg(q["ff"], False)
    d.ellipse([head[0] - 4, head[1] - 4, head[0] + 4, head[1] + 4], fill=SKIN)                     # head
    d.pieslice([head[0] - 5, head[1] - 5, head[0] + 5, head[1] + 4], 180, 360, fill=HAIR)
    d.line([(head[0] - 4, head[1] - 2), (head[0] - 7 - s // 2, head[1] + 4)], fill=HAIR, width=2)
    d.point((head[0] + 2, head[1]), fill=(40, 30, 40))
    # front arm + sword
    ax, ay = arm(q["fh"], False)
    dx_, dy_ = ang(q["sword"])
    d.line([(ax, ay), (ax + dx_ * 24, ay + dy_ * 24)], fill=BLADE, width=2)
    d.line([(ax + dx_ * 4, ay + dy_ * 4), (ax + dx_ * 23, ay + dy_ * 23)], fill=BLADE_L, width=1)
    gx, gy = ang(q["sword"] + 90)
    d.line([(ax + dx_ * 3 - gx * 3, ay + dy_ * 3 - gy * 3), (ax + dx_ * 3 + gx * 3, ay + dy_ * 3 + gy * 3)], fill=GOLD, width=2)
    return outline(im)


def outline(im):
    a = np.array(im); al = a[..., 3] > 0
    grow = al.copy()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        grow |= np.roll(np.roll(al, dy, 0), dx, 1)
    edge = grow & ~al
    a[edge] = (12, 10, 16, 255)
    return Image.fromarray(a, "RGBA")


def settle(im):
    """Shift a rotated frame up so its lowest pixel rests on the ground line (row GROUND+OY)."""
    a = np.array(im)[..., 3] > 0
    if not a.any():
        return im
    low = np.argwhere(a).max(0)[0]
    dy = low - (GROUND + OY)
    if dy <= 0:
        return im
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(im, (0, -dy))
    return out


def idle():
    return [figure(dict(hip_y=42 + b, lean=l, sway=2 + b, fh=(9, 8 - b), sword=-60 - b * 4))
            for b, l in ((0, 0), (0, 1), (1, 1), (1, 0))]


def run():
    fr = []
    for i in range(6):
        ph = i / 6 * 2 * math.pi
        fr.append(figure(dict(hip_y=42 + int(abs(math.sin(ph)) * 2) - 1, lean=4, sway=7,
                              ff=(int(9 * math.sin(ph)) + 3, max(0, int(7 * math.cos(ph)))),
                              bf=(int(-9 * math.sin(ph)) - 3, max(0, int(-7 * math.cos(ph)))),
                              fh=(7, 7), bh=(-5, 8), sword=-25 + int(5 * math.sin(ph)))))
    return fr


def jump():
    return [figure(dict(hip_y=36, lean=1, ff=(6, 10), bf=(-4, 6), sway=-2, fh=(8, 3), sword=-80)),
            figure(dict(hip_y=36, lean=1, ff=(4, 2), bf=(-3, 0), sway=-5, fh=(8, 3), sword=-70))]


def fall():
    return [figure(dict(hip_y=36, lean=2, ff=(4, 0), bf=(-3, 0), sway=-6, fh=(8, 0), sword=-70)),
            figure(dict(hip_y=36, lean=2, ff=(5, 0), bf=(-3, 0), sway=-8, fh=(8, -2), sword=-65))]


def dodge():
    base = figure(dict(hip_y=47, lean=6, stoop=3, ff=(4, 14), bf=(-3, 12), fh=(5, 7), bh=(-2, 8), sword=140, sway=3))
    out = []
    for a in (-70, -160, -250, -340):
        out.append(settle(base.rotate(a, resample=Image.NEAREST, center=(28 + OX, 46 + OY))))
    return out


def light1():
    A = [-140, -110, -20, 35, 50]; L = [-2, -3, 3, 5, 3]
    H = [(-2, -8), (0, -10), (9, 2), (10, 7), (10, 9)]; FF = [4, 4, 8, 10, 8]
    return [figure(dict(lean=L[i], fh=H[i], sword=A[i], ff=(FF[i], 0), sway=3 + i)) for i in range(5)]


def light2():
    A = [50, 70, 20, -60, -100]; L = [3, 4, 4, 2, 0]
    H = [(8, 10), (8, 10), (10, 2), (8, -6), (4, -11)]; FF = [8, 9, 10, 8, 6]
    return [figure(dict(lean=L[i], fh=H[i], sword=A[i], ff=(FF[i], 0), sway=4)) for i in range(5)]


def heavy():
    A = [-160, -175, -120, -10, 45, 50]; L = [-4, -6, -2, 6, 8, 6]
    Y = [43, 45, 44, 41, 42, 43]; H = [(-3, -9), (-4, -12), (2, -10), (10, 0), (12, 9), (11, 10)]
    FF = [5, 4, 6, 11, 12, 11]
    return [figure(dict(dx=5, hip_y=Y[i], lean=L[i], fh=H[i], sword=A[i], ff=(FF[i], 0), bf=(-6, 0), sway=3 + i)) for i in range(6)]


def skill():
    A = [-10, -5, 0, 0, 0, -10]; H = [(2, 6), (-2, 6), (8, 5), (14, 4), (14, 4), (8, 5)]
    L = [0, -3, 4, 8, 8, 3]; FF = [5, 3, 9, 14, 14, 8]
    return [figure(dict(hip_y=44 if i in (1, 2, 3, 4) else 42, lean=L[i], fh=H[i], sword=A[i], ff=(FF[i], 0), bf=(-7, 0), sway=2 + i)) for i in range(6)]


def hurt():
    return [figure(dict(lean=-5, head_dx=-2, fh=(5, 12), sword=60, sway=5)),
            figure(dict(lean=-7, hip_y=43, head_dx=-3, fh=(4, 12), sword=70, sway=6, ff=(3, 0)))]


def death():
    out = []
    for a in (0, 22, 48, 70, 84, 90):
        base = figure(dict(dx=16, lean=-5, hip_y=43, head_dx=-2, fh=(4, 12), sword=100, sway=4))
        out.append(settle(base.rotate(a, resample=Image.NEAREST, center=(44 + OX, GROUND + OY))))
    return out


ANIMS = [("idle", idle), ("run", run), ("jump", jump), ("fall", fall), ("dodge", dodge),
         ("light1", light1), ("light2", light2), ("heavy", heavy), ("skill", skill),
         ("hurt", hurt), ("death", death)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cols = 6
    sheet = Image.new("RGBA", (F * cols, F * len(ANIMS)), (0, 0, 0, 0))
    meta = {"frame": F, "feet_row": GROUND + OY, "center_x": 28 + OX, "rows": []}
    for r, (name, fn) in enumerate(ANIMS):
        frames = fn()
        meta["rows"].append({"name": name, "row": r, "frames": len(frames)})
        for c, fr in enumerate(frames):
            sheet.alpha_composite(fr, (c * F, r * F))
    sheet.save(OUT / "player.png")
    (OUT / "player.json").write_text(json.dumps(meta, indent=1))
    prev = Image.new("RGBA", sheet.size, (14, 18, 28, 255)); prev.alpha_composite(sheet)
    prev.save(OUT / "_player_preview.png")
    print("rows:", [(r["name"], r["frames"]) for r in meta["rows"]])


if __name__ == "__main__":
    main()
