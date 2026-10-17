#!/usr/bin/env python3
"""Potong 3 shorts dari video/2026-10-07.mp4 (vertikal 9:16).
Ranges: s1=beats 1-10 (tardigrade hook), s2=beats 94-104 (pistol shrimp),
        s3=beats 43-52 (mantis shrimp punch).
"""
import json, os, subprocess

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
VID = os.path.join(W, "video", "2026-10-07.mp4")
OUTD = os.path.join(W, "shorts")
os.makedirs(OUTD, exist_ok=True)

dj = json.load(open(os.path.join(W, "data", "durasi-beat-2026-10-07.json")))
durs = [dj[f"w7-beat-{i+1:03d}"] for i in range(132)]
cum = [2.5]
for d in durs:
    cum.append(cum[-1] + d)

ranges = {
    "s1": (1, 10),    # hook tardigrade
    "s2": (94, 104),  # pistol shrimp
    "s3": (43, 52),   # mantis shrimp punch
}
for name, (a, b) in ranges.items():
    start = cum[a - 1]
    dur = cum[b] - cum[a - 1]
    out = os.path.join(OUTD, f"2026-10-07-{name}.mp4")
    print(f"{name}: start={start:.1f}s dur={dur:.1f}s", flush=True)
    r = subprocess.run(
        [Q, "-y", "-ss", str(start), "-t", str(dur), "-i", VID,
         "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-r", "30", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(f"GAGAL {name}:", r.stderr[-400:], flush=True)
    else:
        print(f"OK {name}", flush=True)
