#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari long b16 (bank untuk besok, TIDAK diupload hari ini).
Hook overlay 3 dtk pertama + CTA overlay 3 dtk terakhir. Tulis TEMP, verifikasi, pindah."""
import json, os, subprocess

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SRC = os.path.join(W, "video", "2026-10-18-final.mp4")

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

dj = json.load(open(os.path.join(W, "data", "durasi-beat-2026-10-18.json")))
TC, BUMPER_AFTER = 2.5, 28
starts, cum = {}, TC
for i in range(1, 75):
    starts[i] = cum
    cum += float(dj[f"b16-beat-{i:03d}"])
    if i == BUMPER_AFTER:
        cum += float(dj["b16-bumper"])

# (nama, beat_awal, beat_akhir_inklusif, hook_text)
SHORTS = [
    ("s1", 47, 52, "BANNED ON AIRPLANES"),      # surstromming
    ("s2", 55, 61, "THE WEIRDEST FOOD ON EARTH"),  # casu marzu champion
    ("s3", 31, 36, "POOP COFFEE"),              # kopi luwak
]

def dt(text, s, e, fs=52, y="h-220"):
    return (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize={fs}:"
            f"fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y={y}:enable='between(t,{s:.2f},{e:.2f})'")

for name, b0, b1, hook in SHORTS:
    ss = starts[b0]
    dur = starts[b1 + 1] - ss if b1 < 74 else cum - ss
    print(f"{name}: beats {b0}-{b1} -> ss={ss:.1f}s dur={dur:.1f}s", flush=True)
    assert 30 <= dur <= 65, f"durasi {dur:.1f}s di luar 30-65!"
    tmp = os.path.join(W, "shorts", f"2026-10-18-{name}-TEMP.mp4")
    final = os.path.join(W, "shorts", f"2026-10-18-{name}.mp4")
    assert not os.path.exists(final), f"{final} sudah ada!"
    vf = ("crop=ih*9/16:ih,scale=720:1280,"
          + dt(hook, 0, 3.0) + ","
          + dt("SUBSCRIBE!", dur - 3.0, dur, fs=64))
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
