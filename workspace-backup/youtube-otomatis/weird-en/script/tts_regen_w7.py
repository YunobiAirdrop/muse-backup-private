#!/usr/bin/env python3
"""Regenerasi TTS semua beat w7 dengan speed 120 (pacing konsisten), paralel 10."""
import json, os, subprocess
from concurrent.futures import ThreadPoolExecutor

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
batches = json.load(open(os.path.join(W, "data", "batches-w7.json")))
jobs = []
for b in batches.values():
    for e in b:
        jobs.append((e["num"], e["tts"]))

def gen(job):
    num, text = job
    out = os.path.join(W, "audio", f"w7-beat-{num}.mp3")
    r = subprocess.run(
        ["/opt/hatch/bin/tts", "speak", "--language", "en",
         "--voice", "avocado_v2:miles", "--speed", "120",
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
