#!/usr/bin/env python3
"""Ukur roda dari kanal ALFA: roda = satu-satunya objek di strip bawah gambar.
cx & bottom B dari strip; jari-jari r dari lebar chord alfa pada y = B-25:
p^2 = r^2 - (r-25)^2  ->  r = (p^2 + 625) / 50 ; cy = B - r."""
import numpy as np
from PIL import Image
from pathlib import Path

W = Path.home() / "workspace/macam-macam/work/truk-kartun/work"

for name in ["item00_key.png", "item01_key.png", "item03_key.png", "item04_key.png"]:
    im = np.asarray(Image.open(W / name).convert("RGBA"))
    H, Wd = im.shape[:2]
    alpha = im[..., 3] > 128
    strip = alpha[H - 260:, :]
    colcount = strip.sum(axis=0)
    runs, x = [], 0
    while x < Wd:
        if colcount[x] > 10:
            x0 = x
            while x < Wd and colcount[x] > 10:
                x += 1
            runs.append([x0, x - 1])
        else:
            x += 1
    merged = []
    for rn in runs:
        if merged and rn[0] - merged[-1][1] < 40:
            merged[-1][1] = rn[1]
        else:
            merged.append(rn)
    out = []
    for x0, x1 in merged:
        if x1 - x0 < 60:
            continue
        sub = strip[:, x0:x1 + 1]
        ys, _ = np.nonzero(sub)
        B = (H - 260) + ys.max()
        ya = B - 25
        row = alpha[ya, max(0, x0 - 30): x1 + 31]
        # run alfa terpanjang pada baris itu
        best, cur = (0, 0), None
        for i, v in enumerate(row):
            if v and cur is None:
                cur = i
            if (not v or i == len(row) - 1) and cur is not None:
                end = i if not v else i
                if end - cur > best[1] - best[0]:
                    best = (cur, end)
                cur = None
        p = (best[1] - best[0]) / 2
        cx = max(0, x0 - 30) + (best[0] + best[1]) / 2
        r = (p * p + 625) / 50
        out.append((round(cx), round(B - r), round(r)))
    print(name, "-> (cx, cy, r):", out)
