#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari video long Angkor (blur-fill + teks hook).
Penggunaan: python3 potong_shorts_angkor.py
"""
import subprocess, os

BASE = "/home/hatch/workspace/youtube-otomatis/empires-en"
QUEUE = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
VID = os.path.join(BASE, "video", "angkorwat-2026-10-10-upload.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ODIR = os.path.join(BASE, "shorts")
os.makedirs(ODIR, exist_ok=True)

# (ss, dur, hook_text) — diputuskan dari chapter setelah rakit
SHORTS = [
    ("2026-10-10-s1.mp4", None, None, "The Biggest City on Earth\nVanished in 100 Years"),
    ("2026-10-10-s2.mp4", None, None, "The Monsoon Failed\nfor DECADES"),
    ("2026-10-10-s3.mp4", None, None, "Lasers Found a City\nBigger Than London"),
]

def potong(out_name, ss, dur, hook):
    out = os.path.join(ODIR, out_name)
    tf = os.path.join(ODIR, out_name + ".hook.txt")
    open(tf, "w").write(hook)
    vf = (
        "split[a][b];"
        "[a]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,boxblur=18:1[bg];"
        "[b]scale=720:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,"
        f"drawtext=fontfile={FONT}:textfile='{tf}':fontsize=52:fontcolor=white:"
        "borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=140,"
        f"drawtext=fontfile={FONT}:text='LOST EMPIRES':fontsize=30:fontcolor=yellow:"
        "borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=h-90"
    )
    r = subprocess.run([QUEUE, "-y", "-ss", ss, "-t", dur, "-i", VID,
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
    hooks = {s[0]: s[3] for s in SHORTS}
    for spec in specs.split(","):
        name, ss, dur = spec.split("|")
        potong(name, ss, dur, hooks[name])
