"""Generate placeholder parallax background layers (tileable horizontally, 1280x540).

Run from AshenVeil_Python/:  python tools/gen_parallax.py      Needs: numpy, pillow.
Drawn at 640x270 then upscaled 2x (nearest) for chunky pixels.
Layers (back to front): 0_sky, 1_castle, 2_aqueduct, 3_ruins, 4_foreground.
"""
from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "parallax"
W, H = 640, 270


def noise(w, h, cell, seed):
    rng = np.random.default_rng(seed)
    g = rng.random((h // cell + 2, w // cell))
    g = np.concatenate([g, g[:, :1]], axis=1)
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((w + cell, h + 2 * cell), Image.BICUBIC)
    return np.array(im)[:h, :w] / 255.0


def finish(im, name):
    im.resize((W * 2, H * 2), Image.NEAREST).save(OUT / f"{name}.png")


def sky():
    ys = np.linspace(0, 1, H)[:, None]
    top, bot = np.array([7, 10, 26]), np.array([46, 66, 104])
    a = (top + (bot - top) * (ys ** 1.4))[:, None, :] * np.ones((1, W, 1))
    img = np.broadcast_to(a, (H, W, 3)).copy()
    mx, my, mr = 190, 84, 40
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot(xx - mx, yy - my)
    glow = np.clip(1 - dist / 170, 0, 1) ** 2.2
    img += glow[..., None] * np.array([40, 56, 84])
    n = noise(W, H, 32, 5) * 0.6 + noise(W, H, 12, 6) * 0.4
    cloud = np.clip((n - 0.5) * 3.2, 0, 1) * np.clip(1 - dist / 230, 0.25, 1)
    cloud_col = np.array([18, 26, 50]) + glow[..., None] * np.array([70, 80, 100])
    img = img * (1 - cloud[..., None] * 0.75) + cloud_col * cloud[..., None] * 0.75
    rng = np.random.default_rng(3)
    for _ in range(90):
        sx, sy = rng.integers(0, W), rng.integers(0, 140)
        img[sy, sx] = np.clip(img[sy, sx] + rng.integers(60, 150), 0, 255)
    disk = dist <= mr
    crat = noise(W, H, 6, 9)
    moon = np.where(crat[..., None] > 0.62, [150, 170, 200], [206, 218, 236])
    shade = np.clip((xx - mx) / (mr * 2) + 0.5, 0, 1)[..., None] * 25
    img[disk] = (moon - shade)[disk]
    finish(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA"), "0_sky")


def castle():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col, edge, win = (24, 34, 62, 255), (46, 62, 100, 255), (236, 160, 76, 255)
    prof = (noise(W, 8, 64, 21)[0] * 40).astype(int)
    for x in range(W):
        top = 150 + prof[x] - (30 if 330 < x < 640 else 0)
        d.line([(x, top), (x, H)], fill=(20, 29, 54, 255))
        d.point((x, top), fill=edge)
    rng = np.random.default_rng(4)
    towers = [(380, 40, 70), (420, 28, 110), (462, 36, 90), (505, 24, 130), (545, 34, 82), (585, 26, 100), (350, 22, 60)]
    base_y = 150
    d.rectangle([340, base_y - 40, 625, base_y + 10], fill=col)
    for x, w, h in towers:
        top = base_y - h
        d.rectangle([x, top, x + w, base_y + 8], fill=col)
        d.line([(x, top), (x, base_y)], fill=edge)
        d.polygon([(x - 3, top), (x + w + 3, top), (x + w / 2, top - w * 1.3)], fill=col)
        d.line([(x - 3, top), (x + w / 2, top - w * 1.3)], fill=edge)
        for wy in range(top + 8, base_y, 11):
            for wx in range(x + 5, x + w - 3, 9):
                if rng.random() < 0.45:
                    d.rectangle([wx, wy, wx + 2, wy + 4], fill=win)
    d.rectangle([300, base_y - 12, 340, base_y + 10], fill=col)
    finish(im, "1_castle")


def aqueduct():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col, edge = (22, 30, 56, 255), (50, 66, 104, 255)
    top, bot = 128, 196
    d.rectangle([0, top, W, bot], fill=col); d.line([(0, top), (W, top)], fill=edge)
    d.rectangle([0, top - 6, W, top - 3], fill=col)
    for x in range(0, W, 8):
        d.rectangle([x, top - 9, x + 4, top - 6], fill=col)
    for i in range(10):
        cx = 32 + 64 * i
        d.rectangle([cx - 21, top + 26, cx + 21, bot + 2], fill=(0, 0, 0, 0))
        d.pieslice([cx - 21, top + 5, cx + 21, top + 47], 180, 360, fill=(0, 0, 0, 0))
        d.arc([cx - 22, top + 4, cx + 22, top + 48], 180, 360, fill=edge)
    rng = np.random.default_rng(8)
    for x in (120, 250, 470):                      # waterfall streaks + mist
        for k in range(14):
            d.line([(x + k % 5, bot), (x + k % 5, H)], fill=(78, 108, 150, 110))
    for _ in range(26):                            # pines
        x = int(rng.integers(0, W)); h = int(rng.integers(26, 56))
        for t in range(4):
            y = H - h + t * h // 4
            d.polygon([(x - 6 - t * 2, y + h // 3), (x + 6 + t * 2, y + h // 3), (x, y)], fill=(14, 22, 40, 255))
        d.rectangle([x - 1, H - 6, x + 1, H], fill=(14, 22, 40, 255))
    finish(im, "2_aqueduct")


def ruins():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col, edge, win = (13, 17, 32, 255), (36, 46, 74, 255), (232, 150, 70, 255)
    rng = np.random.default_rng(12)
    x = 0
    while x < W:
        w = int(rng.integers(36, 90)); top = int(rng.integers(150, 205))
        d.rectangle([x, top, x + w, H], fill=col); d.line([(x, top), (x + w, top)], fill=edge)
        for cx in range(x + 2, x + w - 4, 12):
            if rng.random() < 0.7:
                d.rectangle([cx, top - 5, cx + 5, top], fill=col)
        if rng.random() < 0.5 and w > 50:
            wx = x + w // 2
            d.rectangle([wx - 5, top + 18, wx + 5, top + 44], fill=(0, 0, 0, 0))
            d.pieslice([wx - 5, top + 12, wx + 5, top + 24], 180, 360, fill=(0, 0, 0, 0))
            if rng.random() < 0.6:
                d.rectangle([wx - 2, top + 26, wx + 2, top + 38], fill=win)
        x += w
    for px in (60, 210, 380, 560):
        h = int(rng.integers(60, 110))
        d.rectangle([px, H - h - 40, px + 14, H], fill=col); d.line([(px, H - h - 40), (px + 14, H - h - 40)], fill=edge)
        d.rectangle([px - 3, H - h - 46, px + 17, H - h - 40], fill=col)
    finish(im, "3_ruins")


def foreground():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col, edge = (5, 7, 13, 255), (22, 28, 44, 255)
    rng = np.random.default_rng(15)
    for px, w in ((10, 34), (590, 40)):                 # big pillars with arch springers
        d.rectangle([px, 0, px + w, H], fill=col); d.line([(px + w, 0), (px + w, H)], fill=edge)
    d.polygon([(44, 0), (44, 46), (96, 0)], fill=col)           # arch springers
    d.polygon([(590, 0), (590, 46), (538, 0)], fill=col)
    for _ in range(30):                                  # hanging vines
        x = int(rng.integers(0, W)); l = int(rng.integers(10, 60))
        d.line([(x, 0), (x + int(rng.integers(-3, 3)), l)], fill=(10, 18, 14, 255), width=1)
    for _ in range(70):                                  # ground brush
        x = int(rng.integers(0, W)); r = int(rng.integers(5, 16))
        d.ellipse([x - r, H - r - int(rng.integers(0, 12)), x + r, H + r], fill=col)
    for _ in range(40):                                  # red leaves
        x, y = int(rng.integers(0, W)), int(rng.integers(215, 262))
        d.rectangle([x, y, x + 1, y + 1], fill=(112, 26, 36, 255))
    finish(im, "4_foreground")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for f in (sky, castle, aqueduct, ruins, foreground):
        f()
    comp = Image.open(OUT / "0_sky.png").convert("RGBA")
    for n in ("1_castle", "2_aqueduct", "3_ruins", "4_foreground"):
        comp.alpha_composite(Image.open(OUT / f"{n}.png"))
    comp.crop((0, 0, 1280, 540)).resize((960, 405)).save(OUT / "_preview.png")
    print("parallax layers written")
