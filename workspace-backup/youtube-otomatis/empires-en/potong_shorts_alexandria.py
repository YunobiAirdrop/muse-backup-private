#!/usr/bin/env python3
"""Potong 3 shorts vertikal 1080x1920 dari video long Alexandria
(blur-fill + teks hook + CTA subscribe 3 detik terakhir).
Penggunaan: SHORTS_SPECS='name|ss|dur,...' python3 potong_shorts_alexandria.py
"""
import subprocess, os

BASE = "/home/hatch/workspace/youtube-otomatis/empires-en"
QUEUE = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
VID = os.path.join(BASE, "video", "alexandria-2026-10-18-upload.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ODIR = os.path.join(BASE, "shorts")
os.makedirs(ODIR, exist_ok=True)

HOOKS = {
    "2026-10-18-s1.mp4": "Half a Million Books\nGone in One Night",
    "2026-10-18-s2.mp4": "They Stole Every Book\nFrom Every Ship",
    "2026-10-18-s3.mp4": "He Measured Earth\nWith a Stick",
}

def potong(out_name, ss, dur, hook):
    out = os.path.join(ODIR, out_name)
    tf = os.path.join(ODIR, out_name + ".hook.txt")
    open(tf, "w").write(hook)
    cta0 = dur - 3
    vf = (
        "split[a][b];"
        "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=18:1[bg];"
        "[b]scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,"
        f"drawtext=fontfile={FONT}:textfile='{tf}':fontsize=72:fontcolor=white:"
        "borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=180,"
        f"drawtext=fontfile={FONT}:text='LOST EMPIRES':fontsize=40:fontcolor=yellow:"
        "borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=h-120,"
        f"drawtext=fontfile={FONT}:text='SUBSCRIBE':fontsize=64:fontcolor=white:"
        "borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=h-320:"
        f"enable='between(t,{cta0},{dur})'"
    )
    r = subprocess.run([QUEUE, "-y", "-ss", str(ss), "-t", str(dur), "-i", VID,
                        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("GAGAL", out_name, r.stderr[-500:])
    else:
        print("OK", out_name)
    os.remove(tf)

if __name__ == "__main__":
    specs = os.environ.get("SHORTS_SPECS")
    if not specs:
        print("Set SHORTS_SPECS='name|ss|dur,name|ss|dur,...'"); raise SystemExit(1)
    for spec in specs.split(","):
        name, ss, dur = spec.split("|")
        potong(name, ss, float(dur), HOOKS[name])
