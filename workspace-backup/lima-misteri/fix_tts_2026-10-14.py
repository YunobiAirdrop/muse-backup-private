#!/usr/bin/env python3
"""Perbaiki beat gagal TTS 2026-10-14: buat b014.mp3 (silence 2.5s) via FFQ (antre otomatis),
lalu tulis durations.json + durations.txt + gabung audio/2026-10-14.mp3.
Penggunaan: python3 fix_tts_2026-10-14.py
"""
import os, sys, subprocess, json, re

BASE = "/home/hatch/workspace/lima-misteri"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
TGL = "2026-10-14"
BDIR = os.path.join(BASE, "audio", "beats", TGL)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

# 1) b014 silence (FFQ menunggu slot otomatis, tanpa timeout keras)
b14 = os.path.join(BDIR, "b014.mp3")
if not (os.path.exists(b14) and os.path.getsize(b14) > 1000):
    print("buat b014 (silence 2.5s) — antre FFQ...", flush=True)
    r = subprocess.run([FFQ, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                        "-t", "2.5", "-c:a", "libmp3lame", "-q:a", "4", b14],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(b14):
        print("GAGAL b014:", r.stderr[-1000:]); sys.exit(1)
print(f"b014 OK ({dur(b14):.2f}s)")

# 2) durations
beats = sorted(int(re.match(r"b(\d+)\.mp3", f).group(1))
               for f in os.listdir(BDIR) if re.match(r"b\d+\.mp3$", f))
assert beats == list(range(1, 75)), f"beats tidak lengkap: {len(beats)}"
durmap = {}
for n in beats:
    p = os.path.join(BDIR, f"b{n:03d}.mp3")
    assert os.path.getsize(p) > 1000, f"file kecil: {p}"
    durmap[f"beat-{n:03d}"] = round(dur(p), 3)
with open(os.path.join(BASE, "audio", f"{TGL}-durations.json"), "w") as f:
    json.dump(durmap, f, indent=1)
with open(os.path.join(BASE, "audio", f"{TGL}.durations.txt"), "w") as f:
    f.write("\n".join(f"{durmap[f'beat-{n:03d}']:.3f}" for n in beats) + "\n")

# 3) gabung (absolute path)
lst = os.path.join(BDIR, "list.txt")
with open(lst, "w") as f:
    for n in beats:
        f.write(f"file '{os.path.join(BDIR, f'b{n:03d}.mp3')}'\n")
out = os.path.join(BASE, "audio", f"{TGL}.mp3")
r = subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", out], capture_output=True, text=True)
if r.returncode != 0:
    print("GAGAL concat:", r.stderr[-1000:]); sys.exit(1)
d = dur(out)
print(f"OK: {out} ({d/60:.1f} mnt), total beats {d:.0f}s")
