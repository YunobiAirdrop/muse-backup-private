#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari long b15 (bank untuk besok, TIDAK diupload).
Hook overlay 3 dtk pertama + CTA overlay 3 dtk terakhir. Tulis TEMP, verifikasi, pindah."""
import os, subprocess, sys

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SRC = os.path.join(W, "video", "2026-10-15-final.mp4")

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

# (nama, start_detik, dur_detik, hook_text)
SHORTS = [
    ("s1", 355.5, 58.5, "YOUR BRAIN LIVES IN THE PAST"),
    ("s2", 150.3, 43.2, "A DAY LONGER THAN A YEAR"),
    ("s3", 208.7, 49.4, "EINSTEIN RUNS YOUR GPS"),
]

def dt(text, s, e, fs=52, y="h-220"):
    return (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize={fs}:"
            f"fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y={y}:enable='between(t,{s:.2f},{e:.2f})'")

for name, ss, dur, hook in SHORTS:
    tmp = os.path.join(W, "shorts", f"2026-10-15-{name}-TEMP.mp4")
    final = os.path.join(W, "shorts", f"2026-10-15-{name}.mp4")
    assert not os.path.exists(final), f"{final} sudah ada!"
    vf = ("crop=ih*9/16:ih,scale=720:1280,"
          + dt(hook, 0, 3.0) + ","
          + dt("SUBSCRIBE!", dur - 3.0, dur, fs=64))
    # hybrid seek: fast input seek ke (ss-5), lalu accurate output seek 5 dtk.
    # (-ss input + -t input saja TIDAK akurat: output jadi 66 dtk untuk target 58.5)
    r = subprocess.run([Q, "-y", "-ss", str(ss - 5), "-i", SRC,
                        "-ss", "5", "-t", str(dur),
                        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "21", "-c:a", "aac", "-b:a", "128k",
                        "-movflags", "+faststart", tmp],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{name} FFMPEG ERR:", r.stderr[-500:]); sys.exit(1)
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                         "format=duration", "-of", "csv=p=0", tmp],
                        capture_output=True, text=True)
    actual = float(pr.stdout.strip())
    if abs(actual - dur) > 5:
        print(f"{name} DURASI GAGAL: expected {dur}, got {actual}"); sys.exit(2)
    os.rename(tmp, final)
    print(f"OK {name}: {final} ({actual:.1f}s)", flush=True)
