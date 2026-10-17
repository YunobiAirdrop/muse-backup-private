#!/usr/bin/env python3
"""Potong 3 shorts vertikal 720x1280 dari video/2026-10-12.mp4.
Rentang beat -> timestamp dari durasi-beat-2026-10-12.json."""
import subprocess, os, json

BASE = "/home/hatch/workspace/youtube-otomatis/truecrime-en"
VID = os.path.join(BASE, "video/2026-10-12.mp4")
SOD = os.path.join(BASE, "shorts")
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"

# (nama, beat_awal_1based, beat_akhir_1based_inklusif)
CLIPS = [
    ("2026-10-12-s1", 1, 5),
    ("2026-10-12-s2", 30, 35),
    ("2026-10-12-s3", 38, 43),
]

def main():
    dj = json.load(open(os.path.join(BASE, "audio/durasi-beat-2026-10-12.json")))
    durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(73)]
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    os.makedirs(SOD, exist_ok=True)
    for name, b1, b2 in CLIPS:
        start, end = cum[b1 - 1], cum[b2]
        out = os.path.join(SOD, f"{name}.mp4")
        vf = "crop=405:720:(in_w-405)/2:0,scale=720:1280"
        r = subprocess.run([FFQ, "-y", "-ss", f"{start:.2f}", "-to", f"{end:.2f}",
                            "-i", VID, "-vf", vf,
                            "-c:v", "libx264", "-preset", "veryfast",
                            "-pix_fmt", "yuv420p", "-r", "30",
                            "-c:a", "aac", "-b:a", "128k", out],
                           capture_output=True)
        if r.returncode != 0:
            print(f"GAGAL {name}: {r.stderr.decode()[-500:]}")
            continue
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration", "-of",
                            "default=noprint_wrappers=1:nokey=1", out],
                           capture_output=True, text=True)
        print(f"OK {name}: {float(d.stdout.strip()):.1f}s ({start:.0f}-{end:.0f})")

if __name__ == "__main__":
    main()
