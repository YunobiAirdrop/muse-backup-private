#!/usr/bin/env python3
"""InkTime 2026-10-15 FIX: rebuild audio with decode-based concat filter (exact),
then final grain+mux -> TMP -> verify -> move. Reuses video/tmp/vconcat1015.mp4."""
import subprocess, os, sys, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
TMP = os.path.join(BASE, "video", "tmp")

def qrun(args):
    print("Q:", " ".join(args[:5]), "...", flush=True)
    r = subprocess.run([Q] + args, capture_output=True, text=True, cwd=BASE)
    if r.returncode != 0:
        print("FFMPEG FAIL:", r.stderr[-3000:], file=sys.stderr)
        sys.exit(1)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

auds = [os.path.join(BASE, "audio", f"ink1015-b{i}.mp3") for i in range(1, 11)]
sil = os.path.join(TMP, "silence1015.mp3")
bmp = os.path.join(TMP, "bumper1015.mp3")
order = [sil] + auds[:5] + [bmp] + auds[5:]
inputs, fc_in = [], []
for i, p in enumerate(order):
    inputs += ["-i", p]
    fc_in.append(f"[{i}:a]")
fc = "".join(fc_in) + f"concat=n={len(order)}:v=0:a=1[a]"
afull = os.path.join(TMP, "afull1015b.mp3")
qrun(["-y"] + inputs + ["-filter_complex", fc, "-map", "[a]",
      "-c:a", "libmp3lame", afull])
a_dur = dur(afull)
v_dur = dur(os.path.join(TMP, "vconcat1015.mp4"))
print(f"afull(b)={a_dur:.2f}s vconcat={v_dur:.2f}s", flush=True)
assert abs(a_dur - v_dur) < 2.0, "STILL MISMATCHED"

final_tmp = os.path.join(BASE, "video", "tmp", "inktime-2026-10-15-long-TMP.mp4")
qrun(["-y", "-i", os.path.join(TMP, "vconcat1015.mp4"), "-i", afull,
      "-vf", "noise=alls=6:allf=t,format=yuv420p",
      "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "128k",
      "-shortest", final_tmp])
f_dur = dur(final_tmp)
print(f"FINAL TMP={f_dur:.2f}s", flush=True)
assert abs(f_dur - v_dur) < 5.0, "FINAL DURATION MISMATCH — NOT MOVING"
final = os.path.join(BASE, "video", "inktime-2026-10-15-long.mp4")
shutil.move(final_tmp, final)
print("FINAL MOVED:", final, f"({f_dur:.1f}s)", flush=True)

# chapters (title 2.5s, bumper 4.593s between beat5/6)
durs = [dur(a) for a in auds]
titles = {1: "The library did not burn", 2: "All the world's books",
          3: "The greatest book heist", 4: "What was inside",
          5: "A stick, a well, the Earth", 6: "Alexandria: the ancient Google",
          7: "The fire that wasn't", 8: "Death by a thousand cuts",
          9: "What we actually lost", 10: "Knowledge is not automatic"}
bd = dur(bmp)
print("CHAPTERS:", flush=True)
t = 2.5
print("0:00 Intro - The Library of Alexandria", flush=True)
for i in range(1, 11):
    m, s = int(t // 60), int(t % 60)
    print(f"{m}:{s:02d} {titles[i]}", flush=True)
    t += durs[i - 1]
    if i == 5:
        t += bd
print(f"TOTAL: {t:.1f}s", flush=True)
