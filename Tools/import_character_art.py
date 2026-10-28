"""Import externally made character frames (128x128 RGBA PNGs named idle_0.. etc.) into the project.
Usage: python Tools/import_character_art.py <folder containing Player/ and Husk/>
Each frame is (1) dropped to the ground line (lowest opaque pixel -> bottom row) and (2) shifted horizontally so the
torso centre sits on a fixed anchor, then placed on a wider 192x128 canvas so swords/capes are not cut off by the shift.
The importer pivot is then (ANCHOR_X / CANVAS_W, 0).  Keep ANCHOR_X / CANVAS_W in sync with SpriteImportProcessor.cs."""
import glob, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage   # pip install scipy

CANVAS_W, CANVAS_H, ANCHOR_X = 192, 128, 80
MIN_BLOB = 150
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Assets', 'Resources', 'Sprites')


def process(src, dst):
    im = Image.open(src).convert('RGBA')
    arr = np.array(im)
    # drop small detached specks left over from cropping/matting (anything under MIN_BLOB px that is not the main figure)
    lab, n = ndimage.label(arr[..., 3] > 8, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(np.ones_like(lab), lab, index=range(1, n + 1))
        for i, sz in enumerate(sizes, start=1):
            if sz < MIN_BLOB:
                arr[lab == i, 3] = 0
    im = Image.fromarray(arr, 'RGBA')
    a = arr[..., 3].astype(np.float32) / 255.0
    ys, xs = np.nonzero(a > 0.03)
    top, bot = ys.min(), ys.max()
    r0, r1 = int(top + (bot - top) * 0.35), int(top + (bot - top) * 0.60)     # torso band
    band = a[r0:r1]
    cx = (band * np.arange(a.shape[1])[None, :]).sum() / max(band.sum(), 1e-6)
    dx = int(round(ANCHOR_X - cx))
    dy = (CANVAS_H - 1) - int(bot)                                              # feet on the bottom row
    canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.alpha_composite(im, (dx, dy)) if (dx >= 0 and dy >= 0) else canvas.paste(im, (dx, dy), im)
    canvas.save(dst)
    return dx, dy


if __name__ == '__main__':
    root = sys.argv[1]
    for who in ('Player', 'Husk'):
        os.makedirs(os.path.join(OUT, who), exist_ok=True)
        for f in sorted(glob.glob(os.path.join(root, who, '*.png')) or glob.glob(os.path.join(root, 'Assets', 'Resources', 'Sprites', who, '*.png'))):
            dx, dy = process(f, os.path.join(OUT, who, os.path.basename(f)))
            print(who, os.path.basename(f), 'shift', dx, dy)
