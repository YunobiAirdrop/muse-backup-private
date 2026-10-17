#!/usr/bin/env python3
"""InkTime 536 assembly v2: SATU render video (filter_complex) + concat audio + final mux.
Hanya ~4 grab slot antrean (bukan ~15) agar tidak starvation di tengah herd."""
import subprocess, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
TMP = os.path.join(BASE, "video", "tmp")
os.makedirs(TMP, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def qrun(args):
    print("Q:", " ".join(args[:6]), "...", flush=True)
    r = subprocess.run([Q] + args, capture_output=True, text=True, cwd=BASE)
    if r.returncode != 0:
        print("FFMPEG FAIL:", r.stderr[-3000:], file=sys.stderr)
        sys.exit(1)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

TITLE_D = 2.5
durs = [dur(os.path.join(BASE, "audio", f"beat-{i:02d}.mp3")) for i in range(1, 11)]
print("audio durs:", [round(d, 1) for d in durs], "total:", round(sum(durs), 1), flush=True)

def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")

def dt(text, enable=None, size=64, y="h-120"):
    s = (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontcolor=black@0.92:"
         f"fontsize={size}:x=(w-text_w)/2:y={y}:borderw=3:bordercolor=white")
    if enable:
        s += f":enable='{enable}'"
    return s

# ---- 1. SATU render: title card + 10 segmen via filter_complex ----
inputs = ["-loop", "1", "-t", str(TITLE_D), "-i", "gambar/ink536-b01.webp"]
for i in range(1, 11):
    inputs += ["-loop", "1", "-t", f"{durs[i-1]:.3f}", "-i", f"gambar/ink536-b{i:02d}.webp"]

fc = []
labels = []
# segmen 0: title card
fc.append(
    f"[0:v]scale=1280:720,drawbox=x='iw*t/{TITLE_D}':y=0:w=iw:h=ih:color=white:t=fill,"
    f"{dt('INKTIME', size=110, y='(h-text_h)/2-90')},"
    f"{dt('THE YEAR 536 - THE WORST YEAR TO BE ALIVE', size=44, y='(h-text_h)/2+60')},"
    f"trim=0:{TITLE_D},setpts=PTS-STARTPTS[s0]")
labels.append("[s0]")
overlays = {1: ("THE SUN WENT OUT", None), 6: ("SUBSCRIBE!", "between(t,0,3)"),
            7: ("25-50 MILLION DEAD", None)}
for i in range(1, 11):
    d = durs[i - 1]
    chain = f"[{i}:v]scale=1280:720,drawbox=x='iw*t/{d:.3f}':y=0:w=iw:h=ih:color=white:t=fill"
    if i in overlays:
        chain += "," + dt(*overlays[i])
    chain += f",trim=0:{d:.3f},setpts=PTS-STARTPTS[s{i}]"
    fc.append(chain)
    labels.append(f"[s{i}]")
fc.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0[vcat]")
qrun(["-y"] + inputs + ["-filter_complex", ";".join(fc),
      "-map", "[vcat]", "-c:v", "libx264", "-preset", "veryfast", "-r", "30",
      os.path.join(TMP, "vconcat.mp4")])
print("VIDEO CONCAT DONE", flush=True)

# ---- 2. audio: 2.5s silence + 10 beats ----
qrun(["-y", "-f", "lavfi", "-t", str(TITLE_D), "-i", "anullsrc=r=44100:cl=stereo",
      "-c:a", "libmp3lame", os.path.join(TMP, "silence.mp3")])
alst = os.path.join(TMP, "alist.txt")
with open(alst, "w") as f:
    f.write("file 'silence.mp3'\n")
    for i in range(1, 11):
        f.write(f"file '../audio/beat-{i:02d}.mp3'\n")
qrun(["-y", "-f", "concat", "-safe", "0", "-i", alst, "-c", "copy",
      os.path.join(TMP, "afull.mp3")])
print("AUDIO DONE", flush=True)

# ---- 3. final: grain + mux ----
qrun(["-y", "-i", os.path.join(TMP, "vconcat.mp4"), "-i", os.path.join(TMP, "afull.mp3"),
      "-vf", "noise=alls=6:allf=t,format=yuv420p",
      "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "128k",
      "-shortest", os.path.join(BASE, "video", "inktime-2026-10-09-long.mp4")])
print("FINAL DONE", flush=True)
