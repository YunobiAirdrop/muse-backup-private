#!/usr/bin/env python3
"""InkTime 2026-10-19: parse script beats, sanitize, TTS (miles, en) -> audio/ink1019-bNN.mp3"""
import re, subprocess, sys, os
sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis")
from tts_sanitize import bersihkan_teks_tts, validasi_teks_tts

BASE = "/home/hatch/workspace/youtube-otomatis/inktime"
script = open(f"{BASE}/script/script-2026-10-19.txt").read()
beats = re.findall(r"=== BEAT (\d+).*?===\s*\nNARRATION:\n(.*?)\n\nVISUAL PLAN:", script, re.S)
assert len(beats) == 10, f"found {len(beats)} beats"
os.makedirs(f"{BASE}/audio", exist_ok=True)
total_words = 0
for n, text in beats:
    t = text.replace("~", " ").strip()
    t = bersihkan_teks_tts(t)
    probs = validasi_teks_tts(t)
    assert not probs, f"beat {n}: {probs}"
    total_words += len(t.split())
    out = f"{BASE}/audio/ink1019-b{n.zfill(2)}.mp3"
    r = subprocess.run(["/opt/hatch/bin/tts", "--text", t, "--voice", "avocado_v2:miles",
                        "--language", "en", "--output", out],
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0 or not os.path.exists(out):
        print(f"TTS FAIL beat {n}: {r.stderr[-500:]}", flush=True); sys.exit(1)
    print(f"beat {n}: {len(t.split())} words -> {out}", flush=True)
print(f"ALL TTS DONE, total {total_words} words", flush=True)
