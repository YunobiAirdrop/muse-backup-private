#!/usr/bin/env python3
"""Deteksi pusat & diameter roda dari PNG hasil chromakey (proyeksi kolom di pita roda)."""
import numpy as np
from PIL import Image
from pathlib import Path

W = Path.home() / "workspace/macam-macam/work/truk-kartun/work"

def detect(name, pred, min_count_frac=0.12):
    im = np.asarray(Image.open(W / name).convert("RGBA")).astype(int)
    H, Wd, _ = im.shape
    r, g, b, a = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
    mask = pred(r, g, b) & (a > 200)
    band = mask[int(H * 0.55):, :]
    colcount = band.sum(axis=0)
    thr = max(15, min_count_frac * colcount.max())
    runs = []
    x = 0
    while x < Wd:
        if colcount[x] > thr:
            x0 = x
            while x < Wd and colcount[x] > thr:
                x += 1
            runs.append((x0, x - 1))
        else:
            x += 1
    # gabung run berdekatan (<40px)
    merged = []
    for run in runs:
        if merged and run[0] - merged[-1][1] < 40:
            merged[-1] = (merged[-1][0], run[1])
        else:
            merged.append(list(run))
    out = []
    for x0, x1 in merged:
        sub = mask[:, x0:x1 + 1]
        ys, xs = np.nonzero(sub)
        if len(ys) < 500:
            continue
        bx0, bx1 = x0 + xs.min(), x0 + xs.max()
        by0, by1 = ys.min(), ys.max()
        d = max(bx1 - bx0, by1 - by0) + 1
        out.append((round((bx0 + bx1) / 2), round((by0 + by1) / 2), d,
                    (bx0, by0, bx1, by1)))
    print(name, "->", out)
    return out

dark = lambda r, g, b: (r < 85) & (g < 85) & (b < 95)
darkblue = lambda r, g, b: (r < 75) & (g < 105) & (b < 140) & (b > r + 15)
orange = lambda r, g, b: (r > 200) & (g > 70) & (g < 185) & (b < 90)

detect("item00_key.png", dark)
detect("item01_key.png", darkblue)
detect("item03_key.png", dark)
detect("item04_key.png", orange)
