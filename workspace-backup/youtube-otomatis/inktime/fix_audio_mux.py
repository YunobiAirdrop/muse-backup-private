#!/usr/bin/env python3
"""Fix-up: audio concat with ABSOLUTE paths + final grain mux.
(vconcat.mp4 444.5s already good; afull.mp3 came out 2.5s due to relative-path resolution.)"""
import subprocess, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
TMP = os.path.join(BASE, "video", "tmp")

def qrun(args):
    print("Q:", " ".join(args[:6]), "...", flush=True)
    r = subprocess.run([Q] + args, capture_output=True, text=True, cwd=BASE)
    if r.returncode != 0:
        print("FFMPEG FAIL:", r.stderr[-3000:], file=sys.stderr)
        sys.exit(1)

alst = os.path.join(TMP, "alist.txt")
with open(alst, "w") as f:
    f.write(f"file '{TMP}/silence.mp3'\n")
    for i in range(1, 6):
        f.write(f"file '{BASE}/audio/beat-{i:02d}.mp3'\n")
    f.write(f"file '{TMP}/bumper.mp3'\n")
    for i in range(6, 11):
        f.write(f"file '{BASE}/audio/beat-{i:02d}.mp3'\n")
qrun(["-y", "-f", "concat", "-safe", "0", "-i", alst, "-c", "copy",
      os.path.join(TMP, "afull.mp3")])
print("AUDIO DONE", flush=True)

qrun(["-y", "-i", os.path.join(TMP, "vconcat.mp4"), "-i", os.path.join(TMP, "afull.mp3"),
      "-vf", "noise=alls=6:allf=t,format=yuv420p",
      "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "128k",
      "-shortest", os.path.join(BASE, "video", "inktime-2026-10-11-long.mp4")])
print("FINAL DONE", flush=True)
