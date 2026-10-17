#!/usr/bin/env python3
"""Generate voiceover per beat (mudiwa, id) lalu gabung jadi vo.mp3."""
import subprocess, os, sys

D = "/home/hatch/workspace/kisah-dharma/2026-10-15"
TTS = "/opt/hatch/bin/tts"
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"

with open(os.path.join(D, "tts-script.txt")) as f:
    lines = [l.strip() for l in f if l.strip().startswith("Narator:")]

beats = [l[len("Narator:"):].strip() for l in lines]
print(f"beats: {len(beats)}", flush=True)

outs = []
for i, text in enumerate(beats):
    out = os.path.join(D, f"_beat{i:02d}.mp3")
    r = subprocess.run([TTS, "speak", "--language", "id",
                        "--voice", "avocado_v2:mudiwa",
                        "--output", out, "--text-stdin", "--timeout-secs", "300"],
                       input=text.encode("utf-8"), capture_output=True)
    if r.returncode != 0 or not os.path.exists(out):
        print(f"BEAT {i} GAGAL:\n{r.stderr.decode()[-800:]}"); sys.exit(1)
    outs.append(out)
    print(f"beat {i:02d} ok ({os.path.getsize(out)} bytes)", flush=True)

lst = os.path.join(D, "_beats.txt")
with open(lst, "w") as f:
    for p in outs:
        f.write(f"file '{p}'\n")
vo = os.path.join(D, "vo.mp3")
r = subprocess.run([FQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", vo], capture_output=True, text=True)
if r.returncode != 0:
    print(f"CONCAT GAGAL:\n{r.stderr[-800:]}"); sys.exit(1)
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1", vo],
                   capture_output=True, text=True)
print(f"vo.mp3 durasi: {float(r.stdout.strip()):.1f}s", flush=True)
