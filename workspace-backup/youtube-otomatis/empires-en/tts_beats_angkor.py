#!/usr/bin/env python3
"""TTS voiceover per beat (Angkor), 4 concurrent workers, 1 retry on failure."""
import json, subprocess, time, os
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/youtube-otomatis/empires-en"
AUD = f"{BASE}/audio/2026-10-10"
os.makedirs(AUD, exist_ok=True)
beats = json.load(open(f"{BASE}/script/beats-angkor.json"))

def run_beat(n, attempt=0):
    key = f"beat-{n:03d}"
    out = f"{AUD}/{key}.mp3"
    try:
        r = subprocess.run(
            ["/opt/hatch/bin/tts", "speak", "--language", "en",
             "--voice", "avocado_v2:History", "--speed", "95",
             "--output", out, "--text-stdin"],
            input=beats[key].encode(), capture_output=True, timeout=300)
        if r.returncode != 0 or b'"ok":true' not in r.stdout:
            raise RuntimeError(r.stderr.decode()[:200] or r.stdout.decode()[:200])
        print(f"OK {key}", flush=True)
        return True
    except Exception as e:
        if attempt == 0:
            print(f"RETRY {key}: {e}", flush=True)
            time.sleep(120)
            return run_beat(n, attempt=1)
        print(f"FAILED {key}: {e}", flush=True)
        return False

with ThreadPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(run_beat, range(1, 25)))
print("DONE:", sum(results), "/24 ok", flush=True)
