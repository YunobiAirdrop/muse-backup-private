#!/usr/bin/env python3
"""Rebuild s1 (tardigrade hook) dari gambar beat-001..005.webp + audio beats 1-10.
- Gambar dinormalisasi per-input ke 2048x1152 (beat-004.webp aslinya 1920x1280!).
- Timing gambar mengikuti durasi AKTUAL mp3 (bukan JSON — JSON terbukti ngaco).
- Overlay 'SURVIVED OUTER SPACE' selama beat 4 (t aktual 14.93-17.71).
- Vertikal 9:16, 30fps, film grain.
"""
import os, subprocess, sys

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
OUT = os.path.join(W, "shorts", "2026-10-07-s1.mp4")
S1A = os.path.join(W, "video", "_tmp_segs", "s1-audio.mp3")

# durasi aktual per grup gambar (jumlah durasi mp3 beat aktual)
segs = [("beat-001.webp", 9.048), ("beat-002.webp", 8.664), ("beat-003.webp", 4.896),
        ("beat-004.webp", 7.296), ("beat-005.webp", 7.848)]

args = [Q, "-y"]
for img, dur in segs:
    args += ["-framerate", "30", "-loop", "1", "-t", str(dur),
             "-i", os.path.join(W, "gambar", img)]
args += ["-i", S1A]

norm = "".join(
    f"[{i}:v]scale=2048:1152:force_original_aspect_ratio=increase,"
    f"crop=2048:1152,setsar=1,fps=30[v{i}];" for i in range(5))
vcat = "".join(f"[v{i}]" for i in range(5)) + "concat=n=5:v=1:a=0"
dt = (f"drawtext=fontfile={FONT}:text='SURVIVED OUTER SPACE':fontsize=64:"
      f"fontcolor=white:borderw=3:bordercolor=black@0.9:"
      f"x=(w-text_w)/2:y=200:box=1:boxcolor=black@0.5:boxborderw=20:"
      f"enable='between(t,14.93,17.71)'")
vf = (f"{norm}{vcat},scale=720:1280:force_original_aspect_ratio=increase,"
      f"crop=720:1280,{dt},noise=alls=6:allf=t,format=yuv420p[v]")
args += ["-filter_complex", vf, "-map", "[v]", "-map", "5:a",
         "-c:v", "libx264", "-preset", "veryfast", "-r", "30",
         "-c:a", "aac", "-b:a", "128k", "-shortest",
         "-movflags", "+faststart", OUT]

print("[build-s1] start", flush=True)
r = subprocess.run(args, capture_output=True, text=True)
if r.returncode != 0:
    print("[build-s1] GAGAL:\n" + r.stderr[-800:], flush=True)
    sys.exit(1)
print("[build-s1] OK", flush=True)
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-show_entries", "stream=width,height", "-of", "csv=p=0", OUT],
                   capture_output=True, text=True).stdout.strip().replace("\n", " ")
print(f"VERIFY s1: {d} size={os.path.getsize(OUT)}", flush=True)
# cek frame tengah (harusnya gambar benar, bukan emu war)
fr = "/tmp/s1-check.jpg"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "5", "-i", OUT,
                "-frames:v", "1", "-q:v", "3", fr], capture_output=True)
print("frame check:", fr, os.path.getsize(fr), flush=True)
