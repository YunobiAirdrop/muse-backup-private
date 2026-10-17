#!/usr/bin/env python3
"""Surgical bumper fix: replace v1's bumper video segment (229.612-234.205, text collision)
with a clean white card + centered 'InkTime'. Keeps v1's full audio track untouched.
Video: A=[0,229.612] + bumper_v(4.593s) + C=[234.233,end] (keyframe) -> concat -c copy.
Then mux with v1's original audio."""
import subprocess, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
TMP = os.path.join(BASE, "video", "tmp")
V1 = os.path.join(BASE, "video", "inktime-2026-10-11-long.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
A_END = 229.612
C_START = 234.233  # keyframe in v1
BUMP_D = 4.593

def qrun(args):
    print("Q:", " ".join(args[:5]), "...", flush=True)
    r = subprocess.run([Q] + args, capture_output=True, text=True, cwd=BASE)
    if r.returncode != 0:
        print("FFMPEG FAIL:", r.stderr[-3000:], file=sys.stderr)
        sys.exit(1)

# 1. bumper video card (white + InkTime + film grain to match)
qrun(["-y", "-v", "error", "-f", "lavfi", "-t", f"{BUMP_D:.3f}",
      "-i", "color=white:s=1280x720:r=30",
      "-vf", f"drawtext=fontfile={FONT}:text='InkTime':fontcolor=black@0.92:fontsize=96:x=(w-text_w)/2:y=(h-text_h)/2:borderw=3:bordercolor=white,noise=alls=6:allf=t,format=yuv420p",
      "-c:v", "libx264", "-preset", "veryfast", "-r", "30", "-an",
      os.path.join(TMP, "bumper_v.mp4")])
print("BUMPER_V DONE", flush=True)

# 2. cut A and C (video only, -c copy)
qrun(["-y", "-v", "error", "-i", V1, "-t", f"{A_END:.3f}",
      "-c:v", "copy", "-an", os.path.join(TMP, "A_v.mp4")])
qrun(["-y", "-v", "error", "-ss", f"{C_START:.3f}", "-i", V1,
      "-c:v", "copy", "-an", os.path.join(TMP, "C_v.mp4")])
print("CUTS DONE", flush=True)

# 3. concat video segments
lst = os.path.join(TMP, "vlist.txt")
with open(lst, "w") as f:
    f.write(f"file '{os.path.join(TMP, 'A_v.mp4')}'\n")
    f.write(f"file '{os.path.join(TMP, 'bumper_v.mp4')}'\n")
    f.write(f"file '{os.path.join(TMP, 'C_v.mp4')}'\n")
qrun(["-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
      "-c", "copy", os.path.join(TMP, "vfixed.mp4")])
print("VCONCAT DONE", flush=True)

# 4. mux fixed video + v1 original audio
qrun(["-y", "-v", "error", "-i", os.path.join(TMP, "vfixed.mp4"), "-i", V1,
      "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest",
      os.path.join(BASE, "video", "inktime-2026-10-11-long-FIXED.mp4")])
print("MUX DONE", flush=True)
