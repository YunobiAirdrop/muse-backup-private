#!/bin/bash
# TTS per beat Dark Mind Files 2026-10-15 (background-safe, parallel, retry 1x)
BASE=/home/hatch/workspace/youtube-otomatis/mind-en
OUT=$BASE/audio/beat-2026-10-15
mkdir -p "$OUT"
cd "$BASE"
python3 - "$OUT" <<'EOF'
import json, subprocess, os, sys
sys.path.insert(0, '/home/hatch/workspace/youtube-otomatis')
from tts_sanitize import bersihkan_teks_tts, validasi_teks_tts
beats = json.load(open('script/beats-2026-10-15.json'))['beats']
outdir = sys.argv[1]
jobs = []
for b in beats:
    text = bersihkan_teks_tts(b['narration'])
    assert not validasi_teks_tts(text), b['id']
    mp3 = os.path.join(outdir, b['id'] + '.mp3')
    if os.path.exists(mp3) and os.path.getsize(mp3) > 1000:
        continue
    jobs.append((b['id'], text, mp3))
print(f"TTS todo: {len(jobs)}/{len(beats)}", flush=True)
import concurrent.futures
def one(job):
    bid, text, mp3 = job
    for attempt in range(2):
        r = subprocess.run(['tts', '--text-stdin', '--voice', 'avocado_v2:magnus',
                            '--speed', '78', '--language', 'en', '--output', mp3],
                           input=text.encode(), capture_output=True, timeout=180)
        if r.returncode == 0 and os.path.exists(mp3) and os.path.getsize(mp3) > 1000:
            return bid, True
    return bid, False
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    res = list(ex.map(one, jobs))
fails = [b for b, ok in res if not ok]
print("TTS gagal:", fails if fails else "tidak ada", flush=True)
sys.exit(1 if fails else 0)
EOF
echo "TTS_EXIT=$?"
