#!/usr/bin/env python3
"""Rakit 3-langkah history-en 2026-10-11 (pengganti single-pass 72-input yang deadlock).
A: gabungan audio via concat demuxer (pola terbukti) -> audio/2026-10-11/gabungan-2026-10-11.mp3
B: video-only single pass dari imglist + drawtext terjadwal -> video/_silent-2026-10-11.mp4
C: mux copy -> video/2026-10-11.mp4 ; verifikasi ffprobe tiap langkah.
Semua ffmpeg via ffmpeg-queue.sh. Tanpa karakter persen di teks drawtext.
"""
import subprocess, json, os, sys

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
ADIR = os.path.join(BASE, "audio", "2026-10-11")
GAB = os.path.join(ADIR, "gabungan-2026-10-11.mp3")
SILENT = os.path.join(BASE, "video", "_silent-2026-10-11.mp4")
OUT = os.path.join(BASE, "video", "2026-10-11.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W = json.load(open("/home/hatch/workspace/youtube-otomatis/history-en/work-2026-10-11/windows.json"))
WINS = {int(k): v for k, v in W["wins"].items()}
BUMPER_WIN = W["bumper"]
TOTAL = W["total"]
OVERLAYS = {int(k): v for k, v in W["overlays"].items()}

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def run(cmd, label):
    print(f"[{label}] mulai...", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[{label}] GAGAL:\n", (r.stderr or "")[-2500:]); sys.exit(1)
    print(f"[{label}] OK", flush=True)

def tf(name, text):
    p = f"/home/hatch/workspace/youtube-otomatis/history-en/work-2026-10-11/he11-{name}.txt"
    open(p, "w").write(text)
    return p

# A: audio gabungan
if not (os.path.exists(GAB) and dur(GAB) > 600):
    run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", "/home/hatch/workspace/youtube-otomatis/history-en/work-2026-10-11/audiolist.txt",
         "-c:a", "libmp3lame", "-b:a", "128k", GAB], "A-audio")
print(f"audio gabungan: {dur(GAB):.1f}s", flush=True)

# B: video silent single pass
if not (os.path.exists(SILENT) and dur(SILENT) > 600):
    vf = ("scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1,fps=30,"
          "eq=contrast=1.08:saturation=0.92:brightness=-0.02,noise=alls=6:allf=t,vignette=PI/5")
    vf += (f",drawtext=fontfile={FONT}:textfile={tf('t1','1347:')}:fontsize=110:fontcolor=white:"
           "x=(w-text_w)/2:y=h/2-140:enable='between(t,0,3)'")
    vf += (f",drawtext=fontfile={FONT}:textfile={tf('t2','THE BLACK DEATH CAME ON SHIPS')}:fontsize=46:fontcolor=#ffd97a:"
           "x=(w-text_w)/2:y=h/2+10:enable='between(t,0,3)'")
    for idx, text in OVERLAYS.items():
        s, e = WINS[idx]
        vf += (f",drawtext=fontfile={FONT}:textfile={tf(f'ov{idx}', text)}:fontsize=46:"
               "fontcolor=white:borderw=2:bordercolor=black@0.8:"
               f"x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.55:boxborderw=24:enable='between(t,{s:.2f},{e:.2f})'")
    cta = tf('cta', 'Subscribe!')
    bs, be = BUMPER_WIN
    vf += (f",drawtext=fontfile={FONT}:textfile={cta}:fontsize=54:fontcolor=#ffd97a:"
           "borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=60:box=1:boxcolor=black@0.55:boxborderw=20:"
           f"enable='between(t,{bs:.2f},{be:.2f})'")
    vf += (f",drawtext=fontfile={FONT}:textfile={cta}:fontsize=54:fontcolor=#ffd97a:"
           "borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=60:box=1:boxcolor=black@0.55:boxborderw=20:"
           f"enable='between(t,{TOTAL-5:.2f},{TOTAL:.2f})'")
    vf += ",format=yuv420p"
    run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", "/home/hatch/workspace/youtube-otomatis/history-en/work-2026-10-11/imglist.txt",
         "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
         "-r", "30", "-an", SILENT], "B-video")
print(f"video silent: {dur(SILENT):.1f}s", flush=True)
assert abs(dur(SILENT) - dur(GAB)) < 2.5, "durasi video & audio terpaut jauh"

# C: mux
run([FFQ, "-y", "-i", SILENT, "-i", GAB,
     "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
     "-shortest", "-movflags", "+faststart", OUT], "C-mux")
print(f"FINAL: {OUT} ({dur(OUT):.1f}s = {dur(OUT)/60:.2f} menit)", flush=True)
os.remove(SILENT)
