#!/usr/bin/env python3
"""InkTime 2026-10-14 SHORTS day: cut 3 shorts from 2026-10-13 long
(The Bronze Age Collapse). Letterbox on white (full whiteboard frame
preserved), hook text top, CTA overlay last 3s. All ffmpeg via ffmpeg-queue.sh.
Video timeline (title card 2.5s, bumper 4.593s between beat5/6):
  S1 beat1 hook     2.50 +38.40   (2.5-40.9)
  S2 beat3 ugarit 100.00 +58.00   (100.0-158.0)
  S3 beat7 reset  325.79 +46.20   (325.8-372.0, bumper-shifted)
"""
import subprocess, os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
SRC = os.path.join(BASE, "video", "inktime-2026-10-13-long.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUT = os.path.join(BASE, "shorts")
os.makedirs(OUT, exist_ok=True)

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
    ("2026-10-14-s1", 2.50, 38.40, "THE WORLD ENDED IN 50 YEARS", "COLLAPSED IN 50 YEARS"),
    ("2026-10-14-s2", 100.00, 58.00, "THE LAST LETTERS OF UGARIT", "STILL WRITING WHILE BURNING"),
    ("2026-10-14-s3", 325.79, 46.20, "THEY FORGOT HOW TO WRITE", "FORGOT HOW TO WRITE"),
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
    # thumbnail 1280x720 from segment frame +5s
    thumb = os.path.join(OUT, f"thumb-{name}.jpg")
    qrun(["-y", "-ss", f"{ss+5:.2f}", "-i", SRC, "-frames:v", "1",
          "-vf", f"scale=1280:720," + dt(thumbtxt, None, 84, 560),
          "-q:v", "3", thumb])
print("ALL DONE", flush=True)
