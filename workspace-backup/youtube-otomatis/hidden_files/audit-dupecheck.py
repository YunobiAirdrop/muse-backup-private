#!/usr/bin/env python3
"""Bandingkan pasangan video kandidat duplikat via dHash frame.
Usage: audit-dupecheck.py (baca pasangan dari argv JSON atau default)."""
import json, os, subprocess, sys, glob
from PIL import Image
import numpy as np

D = os.path.expanduser("~/workspace/youtube-otomatis/hidden_files/audit-2026-10-19")

def dhash(im, h=8):
    im = im.convert("L").resize((h+1, h), Image.LANCZOS)
    a = np.asarray(im, dtype=np.int16)
    diff = (a[:, 1:] > a[:, :-1]).astype(np.uint8).flatten()
    return diff

def ham(a, b):
    return int(np.bitwise_xor(a, b).sum())

def frames_of(slug, vid, n=12):
    fn = f"{D}/vids/{slug}__{vid}.mp4"
    if not os.path.exists(fn):
        return None
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","csv=p=0",fn], capture_output=True, text=True)
    try: dur = float(r.stdout.strip())
    except: return None
    out = []
    td = f"/tmp/dupe_{slug}_{vid}"
    os.makedirs(td, exist_ok=True)
    for i in range(n):
        t = dur * (i+0.5) / n
        fp = f"{td}/f{i:02d}.jpg"
        subprocess.run(["ffmpeg","-y","-v","error","-ss",str(round(t,1)),"-i",fn,
                        "-frames:v","1","-vf","scale=160:90",fp],
                       timeout=120, capture_output=True)
        if os.path.exists(fp):
            out.append(dhash(Image.open(fp)))
    return out

def sim(fa, fb):
    if not fa or not fb: return None
    # tiap frame a cari jarak min ke frame b; rata-rata
    ds = [min(ham(a, b) for b in fb) for a in fa]
    return round(sum(ds)/len(ds), 1)

pairs = json.loads(sys.argv[1]) if len(sys.argv) > 1 else []
cache = {}
for slug, va, vb, label in pairs:
    ka, kb = (slug, va), (slug, vb)
    if ka not in cache: cache[ka] = frames_of(slug, va)
    if kb not in cache: cache[kb] = frames_of(slug, vb)
    s = sim(cache[ka], cache[kb])
    la = "OK " if cache[ka] else "MISS"
    lb = "OK " if cache[kb] else "MISS"
    verdict = "DUPLIKAT-KUAT" if s is not None and s < 8 else ("mirip" if s is not None and s < 16 else "beda")
    print(f"{label}: sim={s} [{la}/{lb}] -> {verdict}")
