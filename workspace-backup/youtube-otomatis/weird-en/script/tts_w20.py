#!/usr/bin/env python3
"""TTS semua beat w20 (weird-en 2026-10-20), voice Miles EN, speed 78, paralel 10.
WAJIB sanitasi teks via tts_sanitize.py (aturan 2026-10-18: tanpa label naskah)."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis"))
from tts_sanitize import bersihkan_teks_tts, validasi_teks_tts

batches = json.load(open(os.path.join(W, "data", "batches-w20.json")))
jobs = []
for b in batches.values():
    for e in b:
        jobs.append((e["num"], e["tts"]))

bad = 0
for num, text in jobs:
    t = bersihkan_teks_tts(text)
    probs = validasi_teks_tts(t)
    if probs:
        print(f"TTS SANITIZE FAIL beat {num}: {probs}")
        bad += 1
if bad:
    sys.exit(f"{bad} beat gagal sanitasi TTS")

def gen(job):
    num, text = job
    t = bersihkan_teks_tts(text)
    out = os.path.join(W, "audio", f"w20-beat-{num:03d}.mp3")
    r = subprocess.run(
        ["/opt/hatch/bin/tts", "speak", "--language", "en",
         "--voice", "avocado_v2:miles", "--speed", "78",
         "--text-stdin", "--output", out],
        input=t, capture_output=True, text=True, timeout=180)
    if r.returncode != 0 or not os.path.exists(out) or os.path.getsize(out) < 1000:
        return (num, False, r.stderr[-200:] if r.stderr else "no output")
    return (num, True, "")

with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(gen, jobs))

fails = [r for r in results if not r[1]]
print(f"OK: {len(results)-len(fails)}/{len(results)}")
for f in fails:
    print("FAIL:", f)
