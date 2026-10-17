#!/usr/bin/env python3
"""Ukur pusat & diameter roda secara lokal: iterasi bbox masker warna ban di kotak rapat
di sekitar estimasi awal (jendela rapat menyingkirkan garis sasis global)."""
import numpy as np
from PIL import Image
from pathlib import Path

W = Path.home() / "workspace/macam-macam/work/truk-kartun/work"

dark = lambda r, g, b: (r < 85) & (g < 85) & (b < 95)
darkblue = lambda r, g, b: (r < 75) & (g < 105) & (b < 140) & (b > r + 15)

JOBS = {
    "item00_key.png": (dark, [(528, 1011, 265), (1200, 1011, 265)]),
    "item01_key.png": (darkblue, [(317, 1011, 300), (624, 1011, 300), (1411, 1011, 300)]),
    "item03_key.png": (dark, [(1446, 966, 215), (937, 966, 215), (643, 966, 215)]),
    "item04_key.png": (dark, [(413, 922, 250), (682, 922, 250), (1392, 922, 250)]),
}

for name, (pred, ests) in JOBS.items():
    im = np.asarray(Image.open(W / name).convert("RGBA")).astype(int)
    H, Wd, _ = im.shape
    r, g, b, a = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
    mask = pred(r, g, b) & (a > 200)
    res = []
    for (cx, cy, d) in ests:
        for _ in range(4):
            half = int(d / 2 + 45)
            x0, x1 = max(0, cx - half), min(Wd, cx + half)
            y0, y1 = max(0, cy - half), min(H, cy + half)
            sub = mask[y0:y1, x0:x1]
            ys, xs = np.nonzero(sub)
            bx0, bx1 = x0 + xs.min(), x0 + xs.max()
            by0, by1 = y0 + ys.min(), y0 + ys.max()
            ncx, ncy = round((bx0 + bx1) / 2), round((by0 + by1) / 2)
            nd = max(bx1 - bx0, by1 - by0) + 1
            if (ncx, ncy, nd) == (cx, cy, d):
                break
            cx, cy, d = ncx, ncy, nd
        res.append((cx, cy, d))
    print(name, "->", res)
