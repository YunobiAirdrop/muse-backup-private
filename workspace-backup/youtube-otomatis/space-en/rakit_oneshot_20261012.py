#!/usr/bin/env python3
"""Rakit 1-panggilan Cosmic Unknown 2026-10-11 (black hole) — jalur darurat antrean ffmpeg jenuh.
1x ffmpeg-queue: slideshow concat (durasi per gambar dari durasi-segmen-2026-10-11.json)
+ grain + vignette + overlay momen kunci + CTA tengah + subtitle terbakar + voiceover-full.
Dipakai karena rakit per-segmen (72x antre) ke-starve antrean 2026-10-12."""
import subprocess, os, json

BASE = "/home/hatch/workspace/youtube-otomatis/space-en"
GDIR = os.path.join(BASE, "gambar/2026-10-11")
AUDIO = os.path.join(BASE, "audio/2026-10-11/voiceover-full.mp3")
SRT = os.path.join(BASE, "script/subtitle-2026-10-11.srt")
TIMING = json.load(open(os.path.join(BASE, "script/timing-beat-2026-10-11.json")))
SEG = json.load(open(os.path.join(BASE, "script/durasi-segmen-2026-10-11.json")))
OUT = os.path.join(BASE, "video/2026-10-11.mp4")
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

starts, durs = TIMING["starts"], TIMING["beat_durs"]
names = []
for k in range(1, 19):
    for v in "abcd":
        names.append(f"beat-{k:03d}-{v}")
lst = os.path.join(BASE, "video/_slides_2026-10-11.txt")
with open(lst, "w") as f:
    for i, n in enumerate(names):
        f.write(f"file '{os.path.join(GDIR, n + '.webp')}'\n")
        f.write(f"duration {SEG[f'seg-{i+1:03d}']}\n")
    f.write(f"file '{os.path.join(GDIR, names[-1] + '.webp')}'\n")

filters = [
    "scale=1280:720:force_original_aspect_ratio=increase",
    "crop=1280:720",
    "fps=30",
    "eq=contrast=1.08:saturation=0.92:brightness=-0.02",
    "noise=alls=6:allf=t",
    "vignette=PI/5",
]
OVERLAYS = [(5, "PAST THE POINT OF NO RETURN"), (7, "4.3 MILLION SUNS IN OUR BACKYARD"),
            (8, "66 BILLION TIMES THE SUN"), (10, "BLACK HOLES SLOWLY EVAPORATE"),
            (12, "PHOTOGRAPHED APRIL 10 2019")]
for beat, teks in OVERLAYS:
    s = starts[f"beat-{beat:03d}"]; e = s + durs[f"beat-{beat:03d}"] + 0.45
    filters.append(f"drawtext=fontfile={FONT}:text='{teks}':fontsize=54:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=36:enable='between(t,{s:.2f},{e:.2f})'")
mid = TIMING["total"] / 2
filters.append(f"drawtext=fontfile={FONT}:text='SUBSCRIBE FOR DAILY COSMIC MYSTERIES':fontsize=44:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=100:enable='between(t,{mid-1.5:.2f},{mid+1.5:.2f})'")
srt_esc = SRT.replace("'", r"'\''")
filters.append(f"subtitles=filename='{srt_esc}':force_style='FontName=DejaVu Sans,FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H80000000,BorderStyle=1,Outline=2,Shadow=0,MarginV=28,Alignment=2'")
filters.append("format=yuv420p")

cmd = [FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", AUDIO,
       "-vf", ",".join(filters), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
       "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", OUT]
r = subprocess.run(cmd, capture_output=True, text=True)
print("rc", r.returncode)
if r.returncode != 0:
    print(r.stderr[-2000:])
else:
    print("OK ->", OUT)
