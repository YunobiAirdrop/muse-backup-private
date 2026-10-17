#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari long Great Attractor + ekor CTA ~4 dtk.
Hook teks besar 4 dtk pertama, overlay SUBSCRIBE di ekor CTA."""
import subprocess, os

BASE = "/home/hatch/workspace/youtube-otomatis/space-en"
FF = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
VID = os.path.join(BASE, "video/2026-10-16.mp4")
CTA = os.path.join(BASE, "audio/2026-10-15/_cta.mp3")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUTD = os.path.join(BASE, "shorts")

PLAN = [
    ("2026-10-16-s1.mp4", 0.00, 33.70, "PULLED BY NOTHING?"),
    ("2026-10-16-s2.mp4", 273.50, 35.00, "100,000 GALAXIES"),
    ("2026-10-16-s3.mp4", 365.00, 30.30, "BEYOND THE UNIVERSE?"),
]

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL:", " ".join(cmd)[:150]); print(r.stderr[-800:]); raise SystemExit(1)

def ts(s):
    return f"{int(s//3600):02d}:{int(s%3600//60):02d}:{s%60:06.3f}"

def dur(f):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0",f], capture_output=True, text=True).stdout)

os.makedirs(OUTD, exist_ok=True)
for fname, ss, dd, hook in PLAN:
    seg = os.path.join(OUTD, "_seg_" + fname)
    tail = os.path.join(OUTD, "_tail_" + fname)
    out = os.path.join(OUTD, fname)
    vf1 = (f"crop=406:720:(in_w-406)/2:0,scale=720:1280:flags=lanczos,"
           f"drawtext=fontfile={FONT}:text='{hook}':fontsize=64:fontcolor=white:"
           f"borderw=4:bordercolor=black:x=(w-text_w)/2:y=h*0.12:enable='between(t,0,4)',"
           f"format=yuv420p")
    run([FF,"-y","-v","error","-ss",ts(ss),"-i",VID,"-t",f"{dd:.2f}",
         "-vf",vf1,"-r","30","-c:v","libx264","-preset","veryfast","-crf","20",
         "-c:a","aac","-b:a","128k",seg])
    cta_d = dur(CTA)
    vf2 = (f"tpad=stop_mode=clone:stop_duration={cta_d:.2f},"
           f"drawtext=fontfile={FONT}:text='SUBSCRIBE!':fontsize=72:fontcolor=yellow:"
           f"borderw=5:bordercolor=black:x=(w-text_w)/2:y=h-220,"
           f"format=yuv420p")
    run([FF,"-y","-v","error","-i",seg,"-i",CTA,
         "-vf",vf2,"-map","0:v","-map","1:a",
         "-c:v","libx264","-preset","veryfast","-crf","20",
         "-c:a","aac","-b:a","128k","-shortest",tail])
    lst = os.path.join(OUTD, "_lst_" + fname + ".txt")
    open(lst,"w").write(f"file '{seg}'\nfile '{tail}'\n")
    run([FF,"-y","-v","error","-f","concat","-safe","0","-i",lst,
         "-c","copy",out])
    d = dur(out)
    print(f"OK {fname}: {d:.1f}s")
    for p in (seg, tail, lst):
        os.remove(p)
print("SHORTS OK")
