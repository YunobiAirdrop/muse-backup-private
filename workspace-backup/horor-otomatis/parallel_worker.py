#!/usr/bin/env python3
"""Worker paralel: bangun segmen [start, end) untuk video horor 2026-10-04."""
import sys, os, glob, subprocess

BASE = "/home/hatch/workspace/horor-otomatis"
sys.path.insert(0, BASE)
from rakit_video import kenburns

START, END = int(sys.argv[1]), int(sys.argv[2])
GDIR = os.path.join(BASE, "gambar/2026-10-04-final")
DURS = os.path.join(BASE, "audio/2026-10-04.durations.txt")
TMPD = os.path.join(BASE, "video/_tmp_segs")

def seg_ok(path, expect_dur):
    if not os.path.exists(path) or os.path.getsize(path) < 50000:
        return False
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return False
    return abs(float(r.stdout.strip()) - expect_dur) < 0.5

imgs = sorted(glob.glob(os.path.join(GDIR, "*.webp")))
durs = [float(x.strip()) for x in open(DURS) if x.strip()]
for i in range(START, END):
    s = os.path.join(TMPD, f"s{i:02d}.mp4")
    if seg_ok(s, durs[i]):
        print(f"  worker s{i:02d} skip", flush=True)
    else:
        kenburns(imgs[i], durs[i], i, s)
        print(f"  worker s{i:02d} buat", flush=True)
print("worker selesai", flush=True)
