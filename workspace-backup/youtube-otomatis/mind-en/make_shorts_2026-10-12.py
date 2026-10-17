#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari long Dark Mind Files 2026-10-12.
Penggunaan: python3 make_shorts_2026-10-12.py
"""
import json, subprocess, os

BASE = "/home/hatch/workspace/youtube-otomatis/mind-en"
VIN = f"{BASE}/video/2026-10-12-ov.mp4"
DURJ = f"{BASE}/audio/durasi-beat-2026-10-12.json"
OUTD = f"{BASE}/shorts/2026-10-12"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

SHORTS = [
    ("short1-favor", 11, 15, ["THE TINY FAVOR", "THAT CONTROLS YOU"]),
    ("short2-joke", 20, 24, ["IT WAS NOT", "JUST A JOKE"]),
    ("short3-silence", 59, 63, ["THE SILENCE", "IS THE TEST"]),
]

def hook_vf(lines):
    parts = []
    for i, ln in enumerate(lines):
        y = 120 + i * 78
        parts.append(
            f"drawtext=fontfile={FONT}:text='{ln}':fontsize=58:fontcolor=white:"
            f"borderw=4:bordercolor=black:x=(w-text_w)/2:y={y}"
        )
    return ",".join(parts)

def main():
    d = json.load(open(DURJ))
    durs = [float(d[f"beat-{i+1:03d}"]) for i in range(75)]
    cum = [0.0]
    for x in durs:
        cum.append(cum[-1] + x)
    os.makedirs(OUTD, exist_ok=True)
    for nama, b1, b2, hook_lines in SHORTS:
        s, e = cum[b1 - 1], cum[b2]
        out = f"{OUTD}/{nama}.mp4"
        vf = (
            f"crop=608:1080:656:0,scale=1080:1920,"
            f"eq=contrast=1.06:saturation=0.95,"
            + hook_vf(hook_lines)
        )
        print(f"  {nama}: {s:.1f}s -> {e:.1f}s ({e-s:.0f} dtk)", flush=True)
        r = subprocess.run([FFQ, "-y", "-ss", f"{s:.2f}", "-to", f"{e:.2f}",
                            "-i", VIN, "-vf", vf,
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                            "-movflags", "+faststart", out],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-1500:]); raise SystemExit(1)
        print(f"  OK: {out}", flush=True)

if __name__ == "__main__":
    main()
