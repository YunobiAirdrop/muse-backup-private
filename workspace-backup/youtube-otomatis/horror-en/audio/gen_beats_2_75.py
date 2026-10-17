#!/usr/bin/env python3
"""Sequential TTS generation for horror-en beats 2..75. Beat 1 already done."""
import json, subprocess, time, sys

SCRIPT = "/home/hatch/workspace/youtube-otomatis/horror-en/script/2026-10-05.txt"
AUDIO_DIR = "/home/hatch/workspace/youtube-otomatis/horror-en/audio"

with open(SCRIPT, encoding="utf-8") as f:
    lines = [ln.rstrip("\n") for ln in f]

assert len(lines) == 75, f"expected 75 lines, got {len(lines)}"
for i, ln in enumerate(lines, 1):
    assert ln.strip(), f"line {i} is empty"

retries = {}
failed = []

for n in range(2, 76):
    nnn = f"{n:03d}"
    out = f"{AUDIO_DIR}/beat-{nnn}.mp3"
    text = lines[n - 1]
    ok = False
    attempts = 0
    while attempts < 3 and not ok:
        attempts += 1
        r = subprocess.run(
            ["/opt/hatch/bin/tts", "speak",
             "--voice", "avocado_v2:briggs",
             "--language", "en",
             "--speed", "92",
             "--output", out,
             "--text-stdin"],
            input=text.encode("utf-8"),
            capture_output=True,
            timeout=180,
        )
        if r.returncode == 0:
            ok = True
        else:
            err = r.stderr.decode(errors="replace")[-500:]
            print(f"[beat-{nnn}] attempt {attempts} failed: {err}", flush=True)
            time.sleep(5)
    if attempts > 1:
        retries[nnn] = attempts
    if not ok:
        failed.append(nnn)
        print(f"[beat-{nnn}] FAILED after 3 attempts", flush=True)
    elif n % 10 == 0 or n == 75:
        print(f"[beat-{nnn}] done ({n}/75)", flush=True)

print("RETRIES:", json.dumps(retries))
print("FAILED:", json.dumps(failed))
