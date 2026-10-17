#!/usr/bin/env python3
"""REBUILD darurat Cosmic Unknown 2026-10-11 (black hole).
KONTEKS: build 2026-10-13 menimpa video/2026-10-11.mp4 dengan file TERPOTONG 81 dtk
(tanpa cek durasi, tanpa backup). Skrip ini build ke file TEMP dulu, verifikasi
durasi ~456.6 dtk, BARU pindahkan ke video/2026-10-11.mp4.
JANGAN PERNAH menimpa video final tanpa verifikasi durasi."""
import subprocess, os, json, shutil

BASE = "/home/hatch/workspace/youtube-otomatis/space-en"
GDIR = os.path.join(BASE, "gambar/2026-10-11")
AUDIO = os.path.join(BASE, "audio/2026-10-11/voiceover-full.mp3")
SRT = os.path.join(BASE, "script/subtitle-2026-10-11.srt")
TIMING = json.load(open(os.path.join(BASE, "script/timing-beat-2026-10-11.json")))
SEG = json.load(open(os.path.join(BASE, "script/durasi-segmen-2026-10-11.json")))
OUT_TMP = os.path.join(BASE, "video/_rebuild-2026-10-11.mp4")
OUT_FINAL = os.path.join(BASE, "video/2026-10-11.mp4")
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
EXPECTED = TIMING["total"]  # 456.6

def dur(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", f],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

starts, durs = TIMING["starts"], TIMING["beat_durs"]
names = []
for k in range(1, 19):
    for v in "abcd":
        names.append(f"beat-{k:03d}-{v}")
for n in names:  # semua gambar harus ada
    assert os.path.exists(os.path.join(GDIR, n + ".webp")), "gambar hilang: " + n
lst = os.path.join(BASE, "video/_slides_fix_2026-10-11.txt")
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
filters.append(f"subtitles=filename='{srt_esc}':force_style='FontName=DejaVu Sans,FontSize=22,BorderStyle=1,Outline=2,Alignment=2,MarginV=45'")
filters.append("format=yuv420p")

cmd = [FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", AUDIO,
       "-vf", ",".join(filters), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
       "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", OUT_TMP]
r = subprocess.run(cmd, capture_output=True, text=True)
print("rc", r.returncode)
if r.returncode != 0:
    print(r.stderr[-2000:]); raise SystemExit(1)
vd = dur(OUT_TMP)
print(f"video {vd:.1f}s (expected {EXPECTED:.1f}s)")
if abs(vd - EXPECTED) > 5.0:
    print("GAGAL: durasi tidak cocok — file final TIDAK ditimpa. Temp disimpan di", OUT_TMP)
    raise SystemExit(2)
shutil.move(OUT_TMP, OUT_FINAL)
print("OK ->", OUT_FINAL)
