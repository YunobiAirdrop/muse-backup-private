#!/usr/bin/env python3
"""TTS semua beat b12 (weird-en 2026-10-10), speed 120, voice Miles, paralel 10."""
import json, os, subprocess
from concurrent.futures import ThreadPoolExecutor

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
batches = json.load(open(os.path.join(W, "data", "batches-b12.json")))
jobs = []
for b in batches.values():
    for e in b:
        jobs.append((e["num"], e["tts"]))

def gen(job):
    num, text = job
    out = os.path.join(W, "audio", f"b12-beat-{num}.mp3")
    r = subprocess.run(
        ["/opt/hatch/bin/tts", "speak", "--language", "en",
         "--voice", "avocado_v2:miles", "--speed", "78",
         "--text-stdin", "--output", out],
        input=text, capture_output=True, text=True, timeout=120)
    if r.returncode != 0 or not os.path.exists(out) or os.path.getsize(out) < 1000:
        return (num, False, r.stderr[-200:] if r.stderr else "no output")
    return (num, True, "")

with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(gen, jobs))

fails = [r for r in results if not r[1]]
print(f"OK: {len(results)-len(fails)}/{len(results)}")
for f in fails:
    print("FAIL:", f)
