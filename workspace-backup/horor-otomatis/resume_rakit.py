#!/usr/bin/env python3
"""Lanjutkan perakitan video horor yang terputus VM restart.
Melewati segmen yang sudah valid, membangun yang rusak/hilang,
lalu concat + mux audio -> video/2026-10-04.mp4"""
import sys, os, glob, subprocess, shutil

BASE = "/home/hatch/workspace/horor-otomatis"
sys.path.insert(0, BASE)
from rakit_video import kenburns, dur

GDIR = os.path.join(BASE, "gambar/2026-10-04-final")
AUDIO = os.path.join(BASE, "audio/2026-10-04.mp3")
DURS = os.path.join(BASE, "audio/2026-10-04.durations.txt")
OUT = os.path.join(BASE, "video/2026-10-04.mp4")
TMPD = os.path.join(os.path.dirname(OUT), "_tmp_segs")

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
assert len(imgs) == len(durs) == 80, (len(imgs), len(durs))
os.makedirs(TMPD, exist_ok=True)

segs = []
for i, (img, seg_dur) in enumerate(zip(imgs, durs)):
    s = os.path.join(TMPD, f"s{i:02d}.mp4")
    if seg_ok(s, seg_dur):
        status = "skip"
    else:
        kenburns(img, seg_dur, i, s)
        status = "buat"
    segs.append(s)
    if status == "buat" or (i + 1) % 20 == 0:
        print(f"  {i+1}/80 {status}", flush=True)

lst = os.path.join(TMPD, "list.txt")
with open(lst, "w") as f:
    for s in segs:
        f.write(f"file '{s}'\n")
concat = os.path.join(TMPD, "concat.mp4")
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                "-c", "copy", concat], capture_output=True, check=True)
subprocess.run(["ffmpeg", "-y", "-i", concat, "-i", AUDIO,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-shortest", "-movflags", "+faststart", OUT],
               capture_output=True, check=True)
print(f"OK: {OUT} ({dur(OUT)/60:.1f} menit)", flush=True)
shutil.rmtree(TMPD)
