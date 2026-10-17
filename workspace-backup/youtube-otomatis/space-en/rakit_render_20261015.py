#!/usr/bin/env python3
"""Render BERAT Fermi Paradox 2026-10-15 via ffmpeg-queue (langkah 4-5).
Prep (audio/timing/SRT/slides) sudah dikerjakan di rakit_oneshot_20261015.py
bagian 1-3 / skrip prep terpisah. Tulis TEMP + verifikasi BARU pindah ke final."""
import subprocess, os, json

BASE = "/home/hatch/workspace/youtube-otomatis/space-en"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUT = os.path.join(BASE, "video/2026-10-15.mp4")
SRT = os.path.join(BASE, "script/subtitle-2026-10-15.srt")
LST = os.path.join(BASE, "video/_slides_2026-10-15.txt")
AFULL = os.path.join(BASE, "audio/2026-10-15/voiceover-full-2026-10-15.mp3")

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL:", " ".join(cmd)[:200]); print(r.stderr[-1500:]); raise SystemExit(1)
    return r

def dur(f):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0",f], capture_output=True, text=True).stdout)

t = json.load(open(os.path.join(BASE, "script/timing-beat-2026-10-15.json")))
starts, beat_durs, total = t["starts"], t["beat_durs"], t["total"]
afull_dur = dur(AFULL)
print(f"afull {afull_dur:.1f}s, total {total:.1f}s")

filters = [
    "scale=1280:720:force_original_aspect_ratio=increase",
    "crop=1280:720",
    "fps=30",
    "eq=contrast=1.08:saturation=0.92:brightness=-0.02",
    "noise=alls=6:allf=t",
    "vignette=PI/5",
]
OVERLAYS = [(3,"THE DRAKE EQUATION"),
            (4,"400 BILLION STARS"),
            (7,"THE GREAT FILTER"),
            (11,"THE DARK FOREST"),
            (13,"100,000 LIGHT-YEARS ACROSS")]
for beat, teks in OVERLAYS:
    s = starts[f"beat-{beat:03d}"]; e = s + beat_durs[f"beat-{beat:03d}"] + 0.45
    filters.append(f"drawtext=fontfile={FONT}:text='{teks}':fontsize=54:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=36:enable='between(t,{s:.2f},{e:.2f})'")
mid = total/2
filters.append(f"drawtext=fontfile={FONT}:text='SUBSCRIBE FOR DAILY COSMIC MYSTERIES':fontsize=44:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=36:enable='between(t,{mid-1.5:.2f},{mid+1.5:.2f})'")
srt_esc = SRT.replace("'","'\\''")
filters.append(f"subtitles=filename='{srt_esc}':force_style='FontName=DejaVu Sans,FontSize=22,BorderStyle=1,Outline=2,Alignment=2,MarginV=45'")
filters.append("format=yuv420p")

VID_TMP = os.path.join(BASE, "video/_videoonly-2026-10-15.mp4")
OUT_TMP = os.path.join(BASE, "video/_final-2026-10-15.mp4")
run([FFQ,"-y","-f","concat","-safe","0","-i",LST,
     "-vf",",".join(filters),"-c:v","libx264","-preset","veryfast","-crf","20",
     "-an","-movflags","+faststart",VID_TMP])
run([FFQ,"-y","-i",VID_TMP,"-i",AFULL,
     "-c:v","copy","-c:a","aac","-b:a","128k","-shortest",
     "-movflags","+faststart",OUT_TMP])
vd = dur(OUT_TMP)
print(f"video {vd:.1f}s (audio {afull_dur:.1f}s)")
assert abs(vd - afull_dur) < 5.0, "durasi video/audio tidak cocok!"
assert 540 <= vd <= 600, f"durasi {vd:.1f}s di luar target 540-600!"
os.replace(OUT_TMP, OUT)
print("OK ->", OUT)
