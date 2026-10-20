#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari long w20 (bank; parent yang mengupload).
Hook overlay 3 dtk pertama + CTA overlay 3 dtk terakhir. Tulis TEMP, verifikasi, pindah."""
import json, os, subprocess

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SRC = os.path.join(W, "video", "2026-10-20-final.mp4")

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

dj = json.load(open(os.path.join(W, "data", "durasi-beat-2026-10-20.json")))
N, BUMPER_AFTER, TC = 74, 28, 2.5
keys = [f"w20-beat-{i:03d}" for i in range(1, N + 1)]
keys.insert(BUMPER_AFTER, "w20-bumper")
starts, cum = {}, TC
for k in keys:
    starts[k] = cum
    cum += float(dj[k])

# (nama, beat_awal, beat_akhir_inklusif, hook_text)
SHORTS = [
    ("s1", 21, 28, "30 YEARS. 28 FEET OF NAILS."),  # Lee Redmond champion
    ("s2", 60, 64, "109.9 DECIBELS"),               # loudest burp
    ("s3", 50, 54, "85 SPOONS. ONE BODY."),         # spoon man
]

def dt(text, s, e, fs=72, y="165"):
    return (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize={fs}:"
            f"fontcolor=white:borderw=4:bordercolor=black:"
            f"x=(w-text_w)/2:y={y}:enable='between(t,{s:.2f},{e:.2f})'")

for name, b0, b1, hook in SHORTS:
    ss = starts[f"w20-beat-{b0:03d}"]
    dur = starts[f"w20-beat-{b1+1:03d}"] - ss if b1 < N else cum - ss
    print(f"{name}: beats {b0}-{b1} -> ss={ss:.1f}s dur={dur:.1f}s", flush=True)
    assert 30 <= dur <= 65, f"durasi {dur:.1f}s di luar 30-65!"
    tmp = os.path.join(W, "shorts", f"2026-10-20-{name}-TEMP.mp4")
    final = os.path.join(W, "shorts", f"2026-10-20-{name}.mp4")
    assert not os.path.exists(final), f"{final} sudah ada!"
    vf = ("crop=ih*9/16:ih,scale=720:1280,"
          + dt(hook, 0, 5.0) + ","
          + dt("SUBSCRIBE!", dur - 3.0, dur, fs=80, y="h-260"))
    r = subprocess.run([Q, "-y", "-ss", str(max(0, ss - 5)), "-i", SRC,
                        "-ss", "5", "-t", str(dur),
                        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "21", "-c:a", "aac", "-b:a", "128k",
                        "-movflags", "+faststart", tmp],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{name} FFMPEG ERR:", r.stderr[-500:]); raise SystemExit(1)
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                         "format=duration", "-of", "csv=p=0", tmp],
                        capture_output=True, text=True)
    actual = float(pr.stdout.strip())
    if abs(actual - dur) > 5:
        print(f"{name} DURASI GAGAL: expected {dur}, got {actual}"); raise SystemExit(2)
    os.rename(tmp, final)
    print(f"OK {name}: {final} ({actual:.1f}s)", flush=True)
