#!/usr/bin/env python3
"""Potong 3 shorts vertikal dari long Musa 2026-10-14 untuk upload 2026-10-15.
720x1280, hook 5 dtk pertama + CTA 3 dtk terakhir. Render via ffmpeg-queue.sh."""
import os, subprocess, sys

FF = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
LONG = "/home/hatch/workspace/kisah-alkitab/work/2026-10-14/out/kisah-alkitab-2026-10-14-long.mp4"
OUTD = "/home/hatch/workspace/kisah-alkitab/work/2026-10-15/shorts"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

SEGS = [
    # (start, durasi, hook_overlay, nama)
    (0.0, 45.0, "TERJEPIT DI TEPI LAUT", "s1"),
    (143.16, 56.84, "LAUT BERDIRI SEPERTI TEMBOK", "s2"),
    (373.10, 41.90, "TUHAN MEMBUKA JALAN", "s3"),
]
CTA = "SUBSCRIBE KISAH ALKITAB"

os.makedirs(OUTD, exist_ok=True)

def run(args):
    print("RUN:", " ".join(args[:6]), "...", flush=True)
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:], flush=True)
        raise SystemExit(f"ffmpeg gagal: {args[-1]}")

for ss, dd, hook, name in SEGS:
    out = f"{OUTD}/2026-10-15-{name}.mp4"
    hook_esc = hook.replace(":", "\\:")
    vf = (
        f"crop=405:720:437:0,scale=720:1280,"
        f"drawtext=fontfile={FONT}:text='{hook_esc}':fontsize=36:fontcolor=white:"
        f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=120:enable='between(t,0,5)',"
        f"drawtext=fontfile={FONT}:text='{CTA}':fontsize=34:fontcolor=yellow:"
        f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-140:enable='gte(t,{dd-3})'"
    )
    run([FF, "-y", "-ss", str(ss), "-i", LONG, "-t", str(dd),
         "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", out])
    # QC durasi + resolusi
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=width,height", "-show_entries", "format=duration",
                        "-of", "csv=p=0", out], capture_output=True, text=True)
    print(f"{name}: {r.stdout.strip()} -> {out}", flush=True)

print("SELESAI")
