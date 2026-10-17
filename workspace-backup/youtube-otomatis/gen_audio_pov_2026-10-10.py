#!/usr/bin/env python3
"""Generate per-beat TTS (mudiwa, id) untuk POV 2026-10-10 -> audio/2026-10-10/beat-NNN.mp3.
Paralel 6 worker. Narasi diambil dari script/2026-10-10.txt (tanpa [JEDA])."""
import re, os, sys, subprocess
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/youtube-otomatis"
SCRIPT = os.path.join(BASE, "script/2026-10-10.txt")
ADIR = os.path.join(BASE, "audio/2026-10-10")
TTS = "/opt/hatch/bin/tts"
WORKERS = 6

def beats():
    t = open(SCRIPT).read()
    out = []
    for m in re.finditer(r"BEAT (\d+):\n(.*?)\nGAMBAR:", t, re.S):
        n, nar = m.group(1), m.group(2).strip()
        nar = nar.replace("[JEDA]", "").strip()
        nar = re.sub(r"\s+", " ", nar)
        out.append((n, nar))
    return out

def one(item):
    n, nar = item
    out = os.path.join(ADIR, f"beat-{int(n):03d}.mp3")
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return f"skip {n}"
    r = subprocess.run([TTS, "speak", "--language", "id",
                        "--voice", "avocado_v2:mudiwa",
                        "--output", out, "--text-stdin",
                        "--timeout-secs", "180"],
                       input=nar.encode("utf-8"),
                       capture_output=True, timeout=240)
    if r.returncode != 0 or not os.path.exists(out) or os.path.getsize(out) == 0:
        return f"GAGAL {n}: {r.stderr.decode()[-300:]}"
    return f"ok {n}"

def main():
    os.makedirs(ADIR, exist_ok=True)
    items = beats()
    print(f"{len(items)} beat", flush=True)
    fails = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for res in ex.map(one, items):
            print(res, flush=True)
            if res.startswith("GAGAL"):
                fails.append(res)
    if fails:
        print(f"{len(fails)} GAGAL", flush=True)
        sys.exit(1)
    print("SELESAI SEMUA", flush=True)

if __name__ == "__main__":
    main()
