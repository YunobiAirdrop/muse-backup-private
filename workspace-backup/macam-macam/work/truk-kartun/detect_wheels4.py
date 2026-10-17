#!/usr/bin/env python3
"""Ukur roda (metode profil-bawah alfa):
- y_body dari profil jumlah alfa per baris (bodi berakhir, tinggal roda di bawahnya)
- segmen kolom dari bottom(x); B = level bawah tertinggi yang didukung >=70 kolom
  (menyaring elemen menggantung sempit seperti balok lengan truk sampah)
- r dari chord alfa pada y=B-25: r=(p^2+625)/50; cy=B-r; cx=pusat chord."""
import numpy as np
from PIL import Image
from pathlib import Path

W = Path.home() / "workspace/macam-macam/work/truk-kartun/work"

def longest_run(row, x0, x1):
    best, cur = (0, -1), None
    for x in range(x0, x1 + 1):
        if row[x] and cur is None:
            cur = x
        if (not row[x] or x == x1) and cur is not None:
            end = x if not row[x] else x + 1
            if end - cur > best[1] - best[0]:
                best = (cur, end)
            cur = None
    return best  # [start, end)

for name in ["item00_key.png", "item01_key.png", "item03_key.png", "item04_key.png"]:
    a = np.asarray(Image.open(W / name).convert("RGBA"))[..., 3] > 128
    H, Wd = a.shape
    counts = a.sum(axis=1)
    plateau = np.median(counts[600:900])
    y_body = next(y for y in range(800, H) if counts[y] < 0.55 * plateau)
    bottom = np.where(a.any(axis=0), H - 1 - np.argmax(a[::-1, :], axis=0), -1)
    cand = bottom > y_body + 25
    runs, x = [], 0
    while x < Wd:
        if cand[x]:
            x0 = x
            while x < Wd and (cand[x] or (x + 1 < Wd and cand[x + 1])):
                x += 1
            runs.append([x0, x - 1])
        else:
            x += 1
    wheels = []
    for x0, x1 in runs:
        if x1 - x0 < 120:
            continue
        seg = bottom[x0:x1 + 1]
        # B: level tertinggi dengan dukungan >=70 kolom dalam 8px
        B = None
        for lvl in range(seg.max(), y_body, -1):
            if (seg >= lvl - 8).sum() >= 70:
                B = lvl
                break
        if B is None:
            continue
        ya = B - 25
        s0, s1 = longest_run(a[ya], x0, x1)
        p = (s1 - s0) / 2
        if p < 40:
            continue
        r = (p * p + 625) / 50
        if not (85 <= r <= 200):
            continue
        wheels.append((round((s0 + s1) / 2), round(B - r), round(r)))
    print(name, f"(y_body={y_body}) -> (cx, cy, r):", wheels)
