"""Generate placeholder enemy sprite sheets: skeleton, shield skeleton, archer, armored knight.

Run from AshenVeil_Python/:  python tools/gen_enemies.py     (uses gen_player.py helpers)
Output: assets/characters/<enemy>.png + <enemy>.json. 96x96 frames, facing right, feet on row 88.
Rows: idle(4) walk(6) attack(6) hurt(2) death(6).
"""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image, ImageDraw
from gen_player import Shift, outline, settle, ang, F, OX, OY, GROUND

OUT = Path(__file__).resolve().parent.parent / "assets" / "characters"
BONE, BONE_D, BONE_L = (206, 198, 174), (120, 112, 98), (236, 230, 212)
EYE = (220, 40, 36)
STEEL, STEEL_D, STEEL_L = (86, 92, 108), (44, 48, 60), (150, 158, 176)
WOODC, RUST = (112, 72, 42), (140, 96, 70)
HOOD, HOOD_D = (46, 52, 58), (26, 30, 36)
PLUME = (150, 30, 36)


def humanoid(kind, p):
    q = dict(dx=0, hip_y=42, lean=0, ff=(5, 0), bf=(-4, 0), fh=(8, 8), bh=(-3, 9), wa=-70, bow=0.0, head_dx=0)
    q.update(p)
    im = Image.new("RGBA", (F, F), (0, 0, 0, 0)); d = Shift(ImageDraw.Draw(im))
    knight, archer = kind == "knight", kind == "archer"
    hx, hy = 28 + q["dx"], q["hip_y"]
    sx, sy = hx + q["lean"], hy - 13
    head = (sx + 2 + q["head_dx"], sy - 7)
    limb = STEEL if knight else (HOOD if archer else BONE)
    limb_d = STEEL_D if knight else (HOOD_D if archer else BONE_D)
    lw = 5 if knight else (3 if archer else 2)
    if archer or knight:  # cloak / cape behind
        col, cd = (HOOD, HOOD_D) if archer else (PLUME, (80, 16, 22))
        d.polygon([(sx - 2, sy), (sx + 3, sy + 2), (hx - 6, hy + 18), (hx - 13, hy + 9), (sx - 7, sy + 4)], fill=cd)
        d.polygon([(sx - 2, sy + 2), (sx + 1, sy + 4), (hx - 7, hy + 16), (hx - 11, hy + 10)], fill=col)

    def leg(foot, dark):
        fx, fy = hx + foot[0], GROUND - foot[1]
        kx, ky = (hx + fx) / 2 + 3, (hy + fy) / 2
        d.line([(hx, hy), (kx, ky), (fx, fy)], fill=limb_d if dark else limb, width=lw, joint="curve")
        d.rectangle([fx - 2, fy - 1, fx + 4, fy + 1], fill=STEEL_D if knight else (60, 54, 46))

    def arm(hand, dark):
        ax, ay = sx + hand[0], sy + hand[1]
        d.line([(sx, sy + 1), ((sx + ax) / 2, (sy + ay) / 2 + 2), (ax, ay)], fill=limb_d if dark else limb, width=lw - 1 if not knight else 4, joint="curve")
        d.rectangle([ax - 1, ay - 1, ax + 1, ay + 1], fill=STEEL if knight else BONE_L)
        return ax, ay
    leg(q["bf"], True)
    bax, bay = arm(q["bh"], True)
    if knight:
        d.polygon([(sx - 6, sy), (sx + 6, sy), (hx + 5, hy + 1), (hx - 5, hy + 1)], fill=STEEL)
        d.line([(sx - 6, sy), (sx + 6, sy)], fill=STEEL_L); d.line([(hx - 5, hy - 2), (hx + 5, hy - 2)], fill=(170, 130, 70))
        d.ellipse([sx - 8, sy - 3, sx + 0, sy + 4], fill=STEEL_L); d.ellipse([sx + 1, sy - 3, sx + 8, sy + 4], fill=STEEL)
    elif archer:
        d.polygon([(sx - 5, sy - 1), (sx + 5, sy - 1), (hx + 4, hy + 4), (hx - 4, hy + 4)], fill=HOOD)
        d.line([(sx, sy), (hx, hy + 3)], fill=HOOD_D)
    else:  # ribcage
        d.polygon([(sx - 3, sy), (sx + 3, sy), (hx + 2, hy), (hx - 2, hy)], fill=(34, 30, 30))
        d.line([(sx, sy - 1), (hx, hy + 1)], fill=BONE)
        for k in range(4):
            y = sy + 1 + k * 3
            d.line([(sx - 4 + k // 2, y), (sx + 4 - k // 2, y)], fill=BONE if k % 2 == 0 else BONE_D)
        d.rectangle([hx - 3, hy, hx + 3, hy + 2], fill=BONE_D)
    leg(q["ff"], False)
    # head
    if knight:
        d.ellipse([head[0] - 5, head[1] - 5, head[0] + 5, head[1] + 5], fill=STEEL)
        d.line([(head[0] - 1, head[1]), (head[0] + 5, head[1])], fill=(10, 10, 14), width=2)
        d.point((head[0] + 3, head[1]), fill=EYE)
        d.polygon([(head[0] - 3, head[1] - 5), (head[0] - 9, head[1] - 9), (head[0] - 7, head[1] - 2)], fill=PLUME)
    else:
        d.ellipse([head[0] - 4, head[1] - 4, head[0] + 4, head[1] + 4], fill=BONE)
        d.rectangle([head[0] - 2, head[1] + 3, head[0] + 3, head[1] + 5], fill=BONE_D)
        d.rectangle([head[0] + 0, head[1] - 1, head[0] + 3, head[1] + 1], fill=(20, 16, 18))
        d.point((head[0] + 2, head[1]), fill=EYE)
        if archer:
            d.pieslice([head[0] - 6, head[1] - 6, head[0] + 6, head[1] + 5], 170, 370, fill=HOOD)
    fax, fay = arm(q["fh"], False)
    # weapons
    wx, wy = ang(q["wa"])
    if kind == "skeleton":      # spear
        d.line([(fax - wx * 8, fay - wy * 8), (fax + wx * 26, fay + wy * 26)], fill=WOODC, width=1)
        tx, ty = fax + wx * 26, fay + wy * 26
        d.polygon([(tx + wx * 6, ty + wy * 6), (tx - wy * 2, ty + wx * 2), (tx + wy * 2, ty - wx * 2)], fill=STEEL_L)
    elif kind == "shield":      # short sword + round shield
        d.line([(fax, fay), (fax + wx * 16, fay + wy * 16)], fill=RUST, width=2)
        d.line([(fax + wx * 3, fay + wy * 3), (fax + wx * 15, fay + wy * 15)], fill=STEEL_L)
        sxp, syp = sx + 5, sy + 8
        d.ellipse([sxp - 6, syp - 7, sxp + 6, syp + 7], fill=WOODC, outline=STEEL_D)
        d.ellipse([sxp - 2, syp - 2, sxp + 2, syp + 2], fill=STEEL)
        d.line([(sxp, syp - 6), (sxp, syp + 6)], fill=(70, 44, 28))
    elif kind == "archer":      # bow, string, arrow
        bx, by = fax + 2, fay
        d.pieslice([bx - 4, by - 14, bx + 8, by + 14], 270, 90, fill=None, outline=WOODC, width=2)
        pull = q["bow"] * 8
        top, bot = (bx + 2, by - 13), (bx + 2, by + 13)
        d.line([top, (bx + 2 - pull, by), bot], fill=BONE_L)
        if q["bow"] > 0.05:
            d.line([(bx + 2 - pull, by), (bx + 18, by)], fill=WOODC)
            d.point((bx + 19, by), fill=STEEL_L)
        d.rectangle([bax - 1, bay - 1, bax + 1, bay + 1], fill=BONE_L)
    elif kind == "knight":      # greatsword
        d.line([(fax - wx * 4, fay - wy * 4), (fax + wx * 34, fay + wy * 34)], fill=STEEL_L, width=3)
        d.line([(fax + wx * 3, fay + wy * 3), (fax + wx * 33, fay + wy * 33)], fill=(230, 236, 246))
        gx, gy = ang(q["wa"] + 90)
        d.line([(fax + wx * 4 - gx * 5, fay + wy * 4 - gy * 5), (fax + wx * 4 + gx * 5, fay + wy * 4 + gy * 5)], fill=(170, 130, 70), width=2)
    return outline(im)


def anims(kind):
    R = range
    A = {}
    A["idle"] = [humanoid(kind, dict(hip_y=42 + b, lean=1 if kind != "knight" else 0)) for b in (0, 0, 1, 1)]
    walk = []
    for i in R(6):
        ph = i / 6 * 2 * math.pi
        walk.append(humanoid(kind, dict(hip_y=42 + int(abs(math.sin(ph))), lean=2,
                                         ff=(int(5 * math.sin(ph)) + 3, max(0, int(4 * math.cos(ph)))),
                                         bf=(int(-5 * math.sin(ph)) - 3, max(0, int(-4 * math.cos(ph)))))))
    A["walk"] = walk
    if kind == "skeleton":      # spear thrust
        H = [(2, 6), (-3, 6), (-4, 6), (12, 5), (14, 5), (6, 6)]; L = [0, -2, -3, 6, 7, 2]; FF = [5, 4, 3, 10, 12, 8]
        A["attack"] = [humanoid(kind, dict(dx=-5, lean=L[i], fh=H[i], wa=-5, ff=(FF[i], 0))) for i in R(6)]
    elif kind == "shield":      # overhead chop
        WA = [-120, -150, -160, -40, 40, 60]; H = [(4, -4), (2, -9), (1, -11), (9, 1), (11, 8), (9, 9)]; L = [0, -2, -3, 4, 6, 3]
        A["attack"] = [humanoid(kind, dict(lean=L[i], fh=H[i], wa=WA[i], ff=(5 + (i > 2) * 4, 0))) for i in R(6)]
    elif kind == "archer":      # draw, hold, release
        B = [0.1, 0.4, 0.7, 1.0, 1.0, 0.0]
        A["attack"] = [humanoid(kind, dict(fh=(11, 3), bh=(-3 + int(B[i] * 0), 3), bow=B[i], lean=0, ff=(6, 0), bf=(-6, 0))) for i in R(6)]
    else:                       # knight overhead slam
        WA = [-110, -150, -165, -60, 25, 35]; H = [(3, -5), (0, -11), (-1, -13), (8, 0), (11, 7), (10, 8)]
        L = [0, -3, -4, 5, 8, 6]; Y = [42, 44, 45, 42, 43, 43]
        A["attack"] = [humanoid(kind, dict(hip_y=Y[i], lean=L[i], fh=H[i], wa=WA[i], dx=-3, ff=(6 + (i > 2) * 5, 0))) for i in R(6)]
    base_wa = -5 if kind == "skeleton" else (-70 if kind != "knight" else -100)
    A["hurt"] = [humanoid(kind, dict(lean=-4, head_dx=-2, fh=(5, 10), wa=15)),
                 humanoid(kind, dict(lean=-6, head_dx=-3, hip_y=43, fh=(4, 11), wa=20))]
    death = []
    for a in (0, 20, 45, 70, 85, 90):
        b = humanoid(kind, dict(dx=16, lean=-5, hip_y=43, head_dx=-2, fh=(4, 12), wa=35))
        death.append(settle(b.rotate(a, resample=Image.NEAREST, center=(44 + OX, GROUND + OY))))
    A["death"] = death
    return A


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    order = ["idle", "walk", "attack", "hurt", "death"]
    prev_all = []
    for kind, fname in (("skeleton", "skeleton"), ("shield", "shield_skeleton"), ("archer", "archer"), ("knight", "armored_knight")):
        A = anims(kind)
        sheet = Image.new("RGBA", (F * 6, F * len(order)), (0, 0, 0, 0))
        meta = {"frame": F, "feet_row": GROUND + OY, "center_x": 28 + OX, "rows": []}
        for r, name in enumerate(order):
            meta["rows"].append({"name": name, "row": r, "frames": len(A[name])})
            for c, fr in enumerate(A[name]):
                sheet.alpha_composite(fr, (c * F, r * F))
        sheet.save(OUT / f"{fname}.png"); (OUT / f"{fname}.json").write_text(json.dumps(meta, indent=1))
        prev_all.append(sheet)
        a = np.array(sheet)[..., 3] > 0
        bad = [(r, c) for r in range(5) for c in range(6) if (lambda f: f.any() and (f[:, 0].any() or f[:, -1].any() or f[0].any() or f[-1].any()))(a[r * F:(r + 1) * F, c * F:(c + 1) * F])]
        print(fname, "edge-touching frames:", bad)
    prev = Image.new("RGBA", (F * 6 * 4, F * 5), (14, 18, 28, 255))
    for i, s in enumerate(prev_all):
        prev.alpha_composite(s, (i * F * 6, 0))
    prev.save(OUT / "_enemies_preview.png")


if __name__ == "__main__":
    main()
