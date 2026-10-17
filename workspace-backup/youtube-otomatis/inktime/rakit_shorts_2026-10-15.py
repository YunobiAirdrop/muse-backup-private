#!/usr/bin/env python3
"""InkTime 2026-10-15 SHORTS bank: cut 3 shorts from 2026-10-15 long
(The Library of Alexandria). Letterbox on white, hook text top,
CTA overlay last 3s. All ffmpeg via ffmpeg-queue.sh.
Video timeline (title card 2.5s, bumper 4.593s between beat5/6):
  S1 beat1 hook        2.50 +40.00  (2.5-42.5)
  S2 beat5 eratosthenes 178.50 +47.00 (178.5-225.5)
  S3 beat9 what we lost 366.80 +44.00 (366.8-410.8)
"""
import subprocess, os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
SRC = os.path.join(BASE, "video", "inktime-2026-10-15-long.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUT = os.path.join(BASE, "shorts")
os.makedirs(OUT, exist_ok=True)
assert os.path.exists(SRC), f"MISSING {SRC}"

def qrun(args):
    r = subprocess.run([Q] + args, capture_output=True, text=True, cwd=BASE)
    if r.returncode != 0:
        print("FFMPEG FAIL:", r.stderr[-2000:], file=sys.stderr); sys.exit(1)
    print("OK", args[-1], flush=True)

def dt(text, enable, size, y):
    t = text.replace("'", "").replace(":", " ").replace("%", "")
    s = (f"drawtext=fontfile={FONT}:text='{t}':fontcolor=black:fontsize={size}:"
         f"x=(w-text_w)/2:y={y}:borderw=2:bordercolor=white:box=1:boxcolor=white@0.85:boxborderw=10")
    if enable: s += f":enable='{enable}'"
    return s

SHORTS = [
    ("2026-10-15-s1", 2.50, 40.00, "THE LIBRARY NEVER BURNED DOWN", "LIBRARY NEVER BURNED"),
    ("2026-10-15-s2", 178.50, 47.00, "HE MEASURED THE EARTH WITH A STICK", "MEASURED THE EARTH"),
    ("2026-10-15-s3", 366.80, 44.00, "90 PLAYS WRITTEN, ONLY 7 SURVIVED", "ONLY 7 SURVIVED"),
]
for name, ss, dur, hook, thumbtxt in SHORTS:
    out = os.path.join(OUT, f"{name}.mp4")
    vf = (f"scale=720:405,pad=720:1280:0:(oh-ih)/2:color=white,"
          + dt(hook, "between(t,0,4)", 46, 200) + ","
          + dt("SUBSCRIBE!", f"between(t,{dur-3:.2f},{dur:.2f})", 52, 1020)
          + ",format=yuv420p")
    qrun(["-y", "-ss", f"{ss:.2f}", "-i", SRC, "-t", f"{dur:.2f}",
          "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-r", "30",
          "-c:a", "aac", "-b:a", "128k", out])
    thumb = os.path.join(OUT, f"thumb-{name}.jpg")
    qrun(["-y", "-ss", f"{ss+5:.2f}", "-i", SRC, "-frames:v", "1",
          "-vf", f"scale=1280:720," + dt(thumbtxt, None, 84, 560),
          "-q:v", "3", thumb])
print("ALL DONE", flush=True)
