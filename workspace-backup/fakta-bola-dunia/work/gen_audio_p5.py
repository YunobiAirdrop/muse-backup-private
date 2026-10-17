#!/usr/bin/env python3
"""Generate TTS per beat dengan mudiwa, lalu pitch-shift per karakter.
id: 1.0x, cn: 0.90x, jp: 1.10x"""
import subprocess, os
WORK = "/home/hatch/workspace/fakta-bola-dunia/work"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
PITCH = {'id': 1.0, 'cn': 0.90, 'jp': 1.10}

beats = []
for line in open(f"{WORK}/script_p4.txt"):
    n, spk, text = line.strip().split("|", 2)
    beats.append((int(n), spk, text))

for n, spk, text in beats:
    raw = f"{WORK}/p5audio/b{n:02d}_raw.mp3"
    out = f"{WORK}/p5audio/b{n:02d}.wav"
    if os.path.exists(out):
        print(f"b{n:02d} sudah ada, skip", flush=True)
        continue
    # TTS mudiwa Indonesia
    r = subprocess.run(
        ["tts", "speak", "--text", text, "--voice", "avocado_v2:mudiwa",
         "--language", "id", "--output", raw],
        capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"TTS GAGAL b{n:02d}: {r.stderr[:200]}", flush=True)
        continue
    p = PITCH[spk]
    if p == 1.0:
        af = "aresample=44100"
    else:
        af = f"asetrate=44100*{p},aresample=44100,atempo=1/{p}"
    r2 = subprocess.run(
        [FFQ, "-y", "-v", "error", "-i", raw, "-af", af,
         "-ar", "44100", "-ac", "1", out],
        capture_output=True, text=True, timeout=60)
    if r2.returncode != 0:
        print(f"Pitch GAGAL b{n:02d}: {r2.stderr[:200]}", flush=True)
    else:
        print(f"b{n:02d} ({spk}, pitch {p}) OK", flush=True)
    if os.path.exists(raw):
        os.remove(raw)
print("SELESAI gen audio")
