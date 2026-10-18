#!/usr/bin/env python3
"""Potong 3 shorts vertikal dari video BASE Lima Misteri 2026-10-18 + drawtext hook & CTA + burn-in subtitle.
s1=Brown Lady (beat 12), s2=Slenderman (beat 24), s3=Bhangarh (beat 34).
Penggunaan: python3 potong_shorts_final_2026-10-18.py
"""
import subprocess, os, json, re

BASE = "/home/hatch/workspace/lima-misteri"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SRC = os.path.join(BASE, "video", "video-2026-10-18-base.mp4")
DJUR = os.path.join(BASE, "audio", "2026-10-18-durations.json")
SCRIPT = os.path.join(BASE, "script", "2026-10-18.txt")
OUTDIR = os.path.join(BASE, "shorts")
TGL = "2026-10-18"
STYLE = "FontName=DejaVu Sans,FontSize=22,BorderStyle=1,Outline=2,Alignment=2,MarginV=45"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def parse_beats():
    txt = open(SCRIPT).read()
    chunks = re.split(r"^BEAT (\d+)$", txt, flags=re.M)
    out = []
    for i in range(1, len(chunks) - 1, 2):
        n = int(chunks[i])
        m = re.search(r"NARASI: (.*)", chunks[i + 1])
        out.append((n, m.group(1).strip() if m else ""))
    return sorted(out)

def fmt(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60); ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def potong(start, end, out, hook):
    srt = out.replace(".mp4", ".srt")
    beats = parse_beats()
    dj = json.load(open(DJUR))
    durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(len(dj))]
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    cues = []
    for n, nar in beats:
        if nar.strip() == "[JEDA]":
            continue
        t0, t1 = cum[n - 1], cum[n]
        if t1 <= start or t0 >= end:
            continue
        cues.append((max(t0, start) - start, min(t1, end) - start, nar))
    with open(srt, "w") as f:
        for i, (t0, t1, nar) in enumerate(cues, 1):
            f.write(f"{i}\n{fmt(t0)} --> {fmt(t1)}\n{nar}\n\n")
    print(f"  SRT: {len(cues)} cues -> {srt}", flush=True)
    vf = ("crop=405:720:437:0,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6:5:5:0.0,"
          f"subtitles='{srt}':force_style='{STYLE}',"
          f"drawtext=fontfile={FONT}:text='{hook}':fontsize=72:fontcolor=white:borderw=4:bordercolor=black:"
          f"x=(w-text_w)/2:y=165:enable='between(t\\,0\\,6)',"
          f"drawtext=fontfile={FONT}:text='SUBSCRIBE!':fontsize=80:fontcolor=yellow:borderw=4:bordercolor=black:"
          f"x=(w-text_w)/2:y=h-390:enable='between(t\\,42\\,45)'")
    r = subprocess.run([FFQ, "-y", "-ss", str(round(start, 2)), "-t", "45", "-i", SRC,
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
        ("s1", beat_time(12), "HANTU BROWN LADY"),
        ("s2", beat_time(24), "SLENDERMAN"),
        ("s3", beat_time(34), "KASTIL TERKUTUK"),
    ]
    for name, center, hook in windows:
        start = max(0.0, center - 22.5)
        if start + 45 > total:
            start = total - 45
        out = os.path.join(OUTDIR, f"{TGL}-{name}.mp4")
        print(f"{name}: mulai {start:.1f}s hook={hook}", flush=True)
        potong(start, start + 45, out, hook)

if __name__ == "__main__":
    main()
