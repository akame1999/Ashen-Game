"""Generate pixel-art slash / impact effect sprite sheets (facing right).

Run from AshenVeil_Python/:  python tools/gen_slash_fx.py
Needs: numpy, pillow. Output: assets/fx/*.png (horizontal strips, RGBA).
Swap any PNG for hand-made art with the same frame size and the game will not care.
"""
from pathlib import Path
import math
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "assets" / "fx"
FRAME = 96  # frame size in px (square); strips are FRAME*N wide

# name: (frames, radius, thickness, start_deg, sweep_deg, palette dark->bright)
SLASHES = {
    "slash_light": (6, 34, 15, -80, 150, [(120, 150, 190), (190, 210, 235), (240, 245, 255), (255, 255, 255)]),
    "slash_heavy": (7, 40, 24, -95, 190, [(150, 70, 30), (230, 140, 60), (255, 210, 130), (255, 250, 220)]),
    "slash_skill": (7, 38, 20, -100, 200, [(40, 90, 170), (70, 160, 235), (150, 215, 255), (235, 250, 255)]),
}


def slash_sheet(frames, radius, thick, start, sweep, pal):
    sheet = np.zeros((FRAME, FRAME * frames, 4), np.uint8)
    cx, cy = FRAME * 0.30, FRAME * 0.52
    yy, xx = np.mgrid[0:FRAME, 0:FRAME].astype(float)
    dx, dy = xx - cx, yy - cy
    r = np.hypot(dx, dy)
    ang = np.degrees(np.arctan2(dy, dx))  # 0 = right, +90 = down
    for f in range(frames):
        t = (f + 1) / frames
        head = start + sweep * min(1.0, t * 1.15)       # leading edge angle
        tail = start + sweep * max(0.0, t - 0.55) * 1.15 # trailing edge angle
        u = (ang - start) / sweep                        # 0..1 along full arc
        within = (ang >= tail) & (ang <= head)
        along = np.clip((ang - tail) / max(head - tail, 1e-6), 0, 1)  # 0 tail .. 1 head
        taper = np.sin(np.clip(u, 0, 1) * math.pi) ** 0.7
        fade = 1.0 - max(0.0, (t - 0.7) / 0.3) * 0.9      # whole-effect fade-out
        half = thick * 0.5 * taper * (0.55 + 0.45 * along)
        # crescent is slightly off-centre: outer edge bulges
        d = r - radius
        inside = within & (np.abs(d) <= half)
        core = 1.0 - np.abs(d) / np.maximum(half, 1e-6)  # 1 centre .. 0 edge
        inten = np.clip(core * (0.35 + 0.65 * along) * fade, 0, 1)
        level = np.minimum((inten * len(pal)).astype(int), len(pal) - 1)
        frame = np.zeros((FRAME, FRAME, 4), np.uint8)
        for i, col in enumerate(pal):
            m = inside & (level == i) & (inten > 0.08)
            frame[m] = (*col, 255)
        # sparks flying off the leading edge
        rng = np.random.default_rng(f * 31 + frames)
        hx = cx + math.cos(math.radians(head)) * radius
        hy = cy + math.sin(math.radians(head)) * radius
        for _ in range(5 if t < 0.9 else 2):
            a = math.radians(head + rng.uniform(-25, 25))
            dist = rng.uniform(4, 16) * (0.4 + t)
            sx, sy = int(hx + math.cos(a) * dist), int(hy + math.sin(a) * dist)
            if 0 <= sx < FRAME and 0 <= sy < FRAME:
                frame[sy, sx] = (*pal[-1], 255)
        sheet[:, f * FRAME:(f + 1) * FRAME] = frame
    return Image.fromarray(sheet, "RGBA")


def impact_sheet(frames=6, pal=((255, 230, 150), (255, 150, 60), (200, 50, 40), (120, 20, 25))):
    """Radial hit spark burst, centred in each frame."""
    sheet = Image.new("RGBA", (FRAME * frames, FRAME), (0, 0, 0, 0))
    px = sheet.load()
    rng = np.random.default_rng(7)
    rays = [rng.uniform(0, 2 * math.pi) for _ in range(9)]
    for f in range(frames):
        t = (f + 1) / frames
        c = FRAME // 2
        for ra in rays:
            length = 6 + 26 * t
            for s in range(int(length)):
                k = s / length
                x = int(c + math.cos(ra) * (4 + s) + f * FRAME)
                y = int(c + math.sin(ra) * (4 + s))
                col = pal[min(int((k + t * 0.6) * len(pal)), len(pal) - 1)]
                if k > 0.15 or t < 0.5:
                    px[x, y] = (*col, int(255 * (1 - t * 0.7)))
        for dy in range(-3, 4):          # bright core flash on early frames
            for dx in range(-3, 4):
                if dx * dx + dy * dy <= 9 * (1 - t) + 1 and t < 0.6:
                    px[c + dx + f * FRAME, c + dy] = (255, 250, 220, 255)
    return sheet


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, args in SLASHES.items():
        slash_sheet(*args).save(OUT / f"{name}.png")
    impact_sheet().save(OUT / "impact_spark.png")
    # contact sheet for quick review (dark background)
    names = list(SLASHES) + ["impact_spark"]
    imgs = [Image.open(OUT / f"{n}.png") for n in names]
    w = max(i.width for i in imgs)
    prev = Image.new("RGBA", (w, FRAME * len(imgs)), (14, 18, 28, 255))
    for k, im in enumerate(imgs):
        prev.alpha_composite(im, (0, k * FRAME))
    prev.save(OUT / "_preview.png")
    print("wrote", [n + ".png" for n in names])


if __name__ == "__main__":
    main()
