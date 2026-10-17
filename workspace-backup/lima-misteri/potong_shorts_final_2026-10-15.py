#!/usr/bin/env python3
"""Potong 3 shorts vertikal dari video BASE Lima Misteri 2026-10-15 (tanpa overlay long) + drawtext hook & CTA.
s1=Teke Teke (beat 13), s2=Resurrection Mary (beat 25), s3=Centralia (beat 37).
Penggunaan: python3 potong_shorts_final_2026-10-15.py
"""
import subprocess, os, json

BASE = "/home/hatch/workspace/lima-misteri"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SRC = os.path.join(BASE, "video", "video-2026-10-15-base.mp4")
DJUR = os.path.join(BASE, "audio", "2026-10-15-durations.json")
OUTDIR = os.path.join(BASE, "shorts")
TGL = "2026-10-15"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def potong(start, out, hook):
    vf = ("crop=405:720:437:0,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6:5:5:0.0,"
          f"drawtext=fontfile={FONT}:text='{hook}':fontsize=72:fontcolor=white:borderw=4:bordercolor=black:"
          f"x=(w-text_w)/2:y=165:enable='between(t\\,0\\,6)',"
          f"drawtext=fontfile={FONT}:text='SUBSCRIBE!':fontsize=80:fontcolor=yellow:borderw=4:bordercolor=black:"
          f"x=(w-text_w)/2:y=h-390:enable='between(t\\,42\\,45)'")
    r = subprocess.run([FFQ, "-y", "-ss", str(start), "-t", "45", "-i", SRC,
                        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("GAGAL potong:", r.stderr[-800:]); raise SystemExit(1)
    print(f"OK: {out} ({dur(out):.0f}s)", flush=True)

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    dj = json.load(open(DJUR))
    durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(len(dj))]
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    total = cum[-1]

    def beat_time(n):
        return (cum[n - 1] + cum[n]) / 2

    windows = [
        ("s1", beat_time(15), "KAPAL PALING BERHANTU"),
        ("s2", beat_time(25), "MANUSIA MELOMPAT"),
        ("s3", beat_time(41), "PULAU TERLARANG"),
    ]
    for name, center, hook in windows:
        start = max(0.0, center - 22.5)
        if start + 45 > total:
            start = total - 45
        out = os.path.join(OUTDIR, f"{TGL}-{name}.mp4")
        print(f"{name}: mulai {start:.1f}s hook={hook}", flush=True)
        potong(round(start, 2), out, hook)

if __name__ == "__main__":
    main()
