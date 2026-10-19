#!/usr/bin/env python3
"""Generate TTS per beat sungai: id=1.0x, eg=0.90x, br=1.10x"""
import subprocess, os
WORK = "/home/hatch/workspace/fakta-bola-dunia/work"
ADIR = f"{WORK}/sungai-audio"
os.makedirs(ADIR, exist_ok=True)
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
PITCH = {'id': 1.0, 'eg': 0.90, 'br': 1.10}
beats = []
for line in open(f"{WORK}/script_sungai.txt"):
    n, spk, text = line.strip().split("|", 2)
    beats.append((int(n), spk, text))
for n, spk, text in beats:
    raw = f"{ADIR}/b{n:02d}_raw.mp3"
    out = f"{ADIR}/b{n:02d}.wav"
    if os.path.exists(out):
        print(f"b{n:02d} sudah ada, skip", flush=True); continue
    if not os.path.exists(raw):
        r = subprocess.run(["tts", "speak", "--text", text, "--voice",
            "avocado_v2:mudiwa", "--language", "id", "--output", raw],
            capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            print(f"TTS GAGAL b{n:02d}: {r.stderr[:200]}", flush=True); continue
    p = PITCH[spk]
    af = "aresample=44100" if p == 1.0 else f"asetrate=44100*{p},aresample=44100,atempo=1/{p}"
    r2 = subprocess.run(["/usr/bin/ffmpeg", "-y", "-v", "error", "-i", raw, "-af", af,
        "-ar", "44100", "-ac", "1", out], capture_output=True, text=True, timeout=120)
    print(f"b{n:02d} ({spk}, {p}) {'OK' if r2.returncode==0 else 'Pitch GAGAL: '+r2.stderr[:200]}", flush=True)
    if os.path.exists(raw): os.remove(raw)
print("SELESAI gen audio sungai")
