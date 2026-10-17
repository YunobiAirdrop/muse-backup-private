#!/usr/bin/env python3
"""Worker render segmen b12 untuk rentang [i0, i1) (0-based, i1 eksklusif).
Judul card dirender oleh rakit_b12.py. Adaptasi worker_b10.py untuk b12.
Pakai: python3 worker_b12.py 0 37   /   python3 worker_b12.py 37 73
"""
import subprocess, os, glob, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rakit_b12 import kenburns, load_overlays, dur, W

def main():
    i0, i1 = int(sys.argv[1]), int(sys.argv[2])
    gdir = os.path.join(W, "gambar")
    overlays = load_overlays()
    imgs = sorted(glob.glob(os.path.join(gdir, "b12-beat-*.webp")))
    dj = json.load(open(os.path.join(W, "data", "durasi-beat-2026-10-12.json")))
    tmpd = os.path.join(W, "video", "_tmp_segs_b12")
    os.makedirs(tmpd, exist_ok=True)
    done = 0
    for i in range(i0, i1):
        key = f"b12-beat-{i+1:03d}"
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        if os.path.exists(s) and dur(s) >= float(dj[key]) * 0.9:
            done += 1
            continue
        if os.path.exists(s):
            os.remove(s)
        ov = overlays.get(key)
        ok = False
        for _ in range(2):
            if kenburns(imgs[i], float(dj[key]), i, s,
                        overlay=ov[0] if ov else None,
                        overlay_dur=ov[1] if ov else None):
                ok = True
                break
        if not ok:
            print(f"GAGAL s{i:03d}", flush=True); sys.exit(1)
        done += 1
        if done % 5 == 0:
            print(f"worker[{i0}-{i1}]: {done}/{i1-i0}", flush=True)
    print(f"worker[{i0}-{i1}] SELESAI", flush=True)

if __name__ == "__main__":
    main()
