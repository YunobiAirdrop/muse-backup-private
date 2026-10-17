#!/usr/bin/env python3
"""Rakit video shorts countryball 1080x1920."""
import subprocess, json, os

WORK = "/home/hatch/workspace/fakta-bola-dunia/work"
OUT = "/home/hatch/workspace/fakta-bola-dunia/output/angka-seram-part1.mp4"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"

# (beat_num, image, speaker_label)
BEATS = [
    ("01", "id-ball.webp", "INDONESIA"),
    ("02", "cn-ball.webp", "CHINA"),
    ("03", "jp-ball.webp", "JEPANG"),
    ("04", "id-ball.webp", "INDONESIA"),
    ("05", "jp-ball.webp", "JEPANG"),
    ("06", "cn-ball.webp", "CHINA"),
    ("07", "id-ball.webp", "INDONESIA"),
    ("08", "angka-13.webp", "JEPANG"),
    ("09", "angka-13.webp", "CHINA"),
    ("10", "id-ball.webp", "INDONESIA"),
    ("11", "cn-ball.webp", "CHINA"),
    ("12", "angka-4.webp", "INDONESIA"),
    ("13", "angka-4.webp", "CHINA"),
    ("14", "jp-ball.webp", "JEPANG"),
    ("15", "id-ball.webp", "INDONESIA"),
]

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

segs = []
for num, img, speaker in BEATS:
    a = dur(f"{WORK}/beat{num}.mp3")
    a_fast = a / 1.2
    vdur = a_fast + 0.35  # jeda antar beat
    frames = int(vdur * 30)
    seg = f"{WORK}/seg{num}.mp4"
    # zoompan halus + teks nama pembicara
    vf = (
        f"scale=2160:3840:force_original_aspect_ratio=increase,"
        f"crop=2160:3840,"
        f"zoompan=z='min(1.0+0.0012*on,1.12)':d={frames}:s=1080x1920:fps=30,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        f"text='{speaker}':fontsize=54:fontcolor=white:borderw=4:bordercolor=black:"
        f"x=(w-text_w)/2:y=90"
    )
    af = f"atempo=1.2,apad,atrim=0:{vdur:.3f}"
    cmd = [FFQ, "-y", "-loop", "1", "-i", f"{WORK}/{img}",
           "-i", f"{WORK}/beat{num}.mp3",
           "-vf", vf, "-af", af,
           "-t", f"{vdur:.3f}", "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "23", "-c:a", "aac", "-b:a", "128k",
           "-shortest", seg]
    print(f"beat{num}: {speaker} {vdur:.2f}s", flush=True)
    subprocess.run(cmd, check=True, capture_output=True)
    segs.append(seg)

# concat
lst = f"{WORK}/concat.txt"
with open(lst, "w") as f:
    for s in segs:
        f.write(f"file '{s}'\n")
subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                "-c", "copy", OUT], check=True, capture_output=True)

total = dur(OUT)
print(f"SELESAI: {OUT} ({total:.1f}s)")
