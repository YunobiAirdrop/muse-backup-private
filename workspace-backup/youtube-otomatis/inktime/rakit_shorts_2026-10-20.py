#!/usr/bin/env python3
"""InkTime 2026-10-20 SHORTS: cut 3 shorts from 2026-10-19 long
("The Day the Sun Didn't Rise: The Tambora Eruption of 1815").
Letterbox on white, hook text top (first 4s), CTA overlay last 3s.
All ffmpeg via ffmpeg-queue.sh. Write to tmp/, verify duration, then move.
Long timeline: title card 2.5s; bumper between beat5/6 (chapter 4:36-7:10 unaffected).
  S1 beat1 hook (sun never rises)   2.50 +44.50  (2.5-47.0, beat2 at 52.0)
  S2 beat7 frankenstein            276.00 +44.00  (4:36-5:20)
  S3 beat9 bicycle ripple          378.00 +52.00  (6:18-7:10)
"""
import subprocess, os, sys, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
SRC = os.path.join(BASE, "video", "inktime-2026-10-19-long.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUT = os.path.join(BASE, "shorts")
TMP = os.path.join(OUT, "tmp_20261020")
os.makedirs(TMP, exist_ok=True)
assert os.path.exists(SRC), f"MISSING {SRC}"

def qrun(args):
    r = subprocess.run([Q] + args, capture_output=True, text=True, cwd=BASE)
    if r.returncode != 0:
        print("FFMPEG FAIL:", r.stderr[-2000:], file=sys.stderr); sys.exit(1)
    print("OK", args[-1], flush=True)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def dt(text, enable, size, y):
    t = text.replace("'", "").replace(":", " ").replace("%", "")
    s = (f"drawtext=fontfile={FONT}:text='{t}':fontcolor=black:fontsize={size}:"
         f"x=(w-text_w)/2:y={y}:borderw=2:bordercolor=white:box=1:"
         f"boxcolor=white@0.85:boxborderw=10")
    if enable:
        s += f":enable='{enable}'"
    return s

SHORTS = [
    ("2026-10-20-s1", 2.50, 44.50, "THE SUN NEVER ROSE", "SUN NEVER ROSE"),
    ("2026-10-20-s2", 276.00, 44.00, "A VOLCANO WROTE FRANKENSTEIN", "WROTE FRANKENSTEIN"),
    ("2026-10-20-s3", 378.00, 52.00, "A VOLCANO INVENTED THE BICYCLE", "INVENTED THE BICYCLE"),
]

for name, ss, exp_dur, hook, thumbtxt in SHORTS:
    tmpv = os.path.join(TMP, f"{name}.mp4")
    vf = (f"scale=720:405,pad=720:1280:0:(oh-ih)/2:color=white,"
          + dt(hook, "between(t,0,4)", 46, 200) + ","
          + dt("SUBSCRIBE!", f"between(t,{exp_dur-3:.2f},{exp_dur:.2f})", 52, 1020)
          + ",format=yuv420p")
    qrun(["-y", "-ss", f"{ss:.2f}", "-i", SRC, "-t", f"{exp_dur:.2f}",
          "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-r", "30",
          "-c:a", "aac", "-b:a", "128k", tmpv])
    got = dur(tmpv)
    assert abs(got - exp_dur) < 2.0, f"DUR MISMATCH {name}: {got} vs {exp_dur}"
    shutil.move(tmpv, os.path.join(OUT, f"{name}.mp4"))
    print(f"MOVED {name} ({got:.1f}s)", flush=True)

    tmpt = os.path.join(TMP, f"thumb-{name}.jpg")
    qrun(["-y", "-ss", f"{ss+5:.2f}", "-i", SRC, "-frames:v", "1",
          "-vf", f"scale=1280:720," + dt(thumbtxt, None, 84, 560),
          "-q:v", "3", tmpt])
    assert os.path.getsize(tmpt) > 20000, f"thumb too small {name}"
    shutil.move(tmpt, os.path.join(OUT, f"thumb-{name}.jpg"))
    print(f"THUMB {name} ok", flush=True)

print("ALL DONE", flush=True)
