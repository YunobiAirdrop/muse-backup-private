#!/usr/bin/env python3
"""Ukur durasi tiap beat b16 + bumper via ffprobe -> data/durasi-beat-2026-10-18.json"""
import json, os, subprocess

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
dj = {}
for i in range(1, 75):
    p = os.path.join(W, "audio", f"b16-beat-{i:03d}.mp3")
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    dj[f"b16-beat-{i:03d}"] = float(r.stdout.strip())
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration", "-of", "csv=p=0",
                    os.path.join(W, "data", "bumper-weird-en.mp3")],
                   capture_output=True, text=True)
dj["b16-bumper"] = float(r.stdout.strip())
json.dump(dj, open(os.path.join(W, "data", "durasi-beat-2026-10-18.json"), "w"), indent=1)
total = sum(dj.values())
print(f"beats: {len(dj)-1}, total audio: {total:.1f}s ({total/60:.2f} mnt)")
