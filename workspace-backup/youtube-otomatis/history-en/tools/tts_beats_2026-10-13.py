#!/usr/bin/env python3
"""TTS worker 2026-10-13 (dua tahap).
  python3 tts_beats_2026-10-13.py <b0> <b1>   -> TTS murni per beat (tanpa ffmpeg).
     Beat tanpa [JEDA]: langsung jadi audio/2026-10-13/beat-NNN.mp3
     Beat dengan [JEDA]: part disimpan di _jeda_staging/ + dicatat di manifest.
  python3 tts_beats_2026-10-13.py assemble    -> gabung part [JEDA] + 2.0s hening
     (memakai _silence2s.mp3, via ffmpeg-queue.sh) -> beat-NNN.mp3 final.
"""
import json, os, subprocess, sys, shutil
sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis")
from tts_sanitize import bersihkan_teks_tts

BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
TTS = "/opt/hatch/bin/tts"
VOICE = "avocado_v2:casper"
OUTDIR = f"{BASE}/audio/2026-10-13"
STAGING = f"{OUTDIR}/_jeda_staging"
MANIFEST = f"{STAGING}/_jeda_manifest.json"
SILENCE = f"{OUTDIR}/_silence2s.mp3"

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def dur_ok(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path])
    try:
        return float(r.stdout.strip()) > 0.5
    except ValueError:
        return False

def tts_part(text, out):
    for attempt in (1, 2):
        r = run([TTS, "speak", "--language", "en", "--voice", VOICE,
                 "--output", out, "--text-stdin"], input=bersihkan_teks_tts(text))
        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 1000:
            return True
    return False

def render_range(b0, b1):
    beats = {b["beat"]: b["text"] for b in json.load(
        open(f"{BASE}/beats/beats-2026-10-13.json"))}
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(STAGING, exist_ok=True)
    manifest = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    gagal = []
    for n in range(b0, b1 + 1):
        bid = f"beat-{n:03d}"
        out = os.path.join(OUTDIR, f"{bid}.mp3")
        if os.path.exists(out) and dur_ok(out):
            print(f"  {bid} sudah ada, skip", flush=True)
            continue
        parts = [p.strip() for p in beats[bid].split("[JEDA]")]
        parts = [p for p in parts if p]
        if len(parts) == 1:
            ok = tts_part(parts[0], out)
            if ok and dur_ok(out):
                print(f"  OK {bid}", flush=True)
            else:
                print(f"  GAGAL {bid}", flush=True); gagal.append(bid)
        else:
            sdir = os.path.join(STAGING, bid)
            os.makedirs(sdir, exist_ok=True)
            ok = True
            plist = []
            for i, p in enumerate(parts):
                pf = os.path.join(sdir, f"p{i}.mp3")
                if not (os.path.exists(pf) and dur_ok(pf)):
                    if not tts_part(p, pf) or not dur_ok(pf):
                        ok = False; break
                plist.append(pf)
            if ok:
                manifest[bid] = {"parts": plist, "n_jeda": len(parts) - 1}
                print(f"  STAGED {bid} ({len(parts)} part)", flush=True)
            else:
                print(f"  GAGAL {bid}", flush=True); gagal.append(bid)
    json.dump(manifest, open(MANIFEST, "w"), indent=1)
    print("gagal:", gagal if gagal else "tidak ada")

def assemble():
    manifest = json.load(open(MANIFEST))
    if not os.path.exists(SILENCE) or not dur_ok(SILENCE):
        print("silence file belum ada:", SILENCE); sys.exit(2)
    gagal = []
    for bid, m in sorted(manifest.items()):
        out = os.path.join(OUTDIR, f"{bid}.mp3")
        if os.path.exists(out) and dur_ok(out):
            print(f"  {bid} sudah ada, skip", flush=True); continue
        lst = os.path.join(STAGING, bid, "list.txt")
        segs = []
        for i, pf in enumerate(m["parts"]):
            segs.append(pf)
            if i < len(m["parts"]) - 1:
                segs.append(SILENCE)
        with open(lst, "w") as f:
            for s in segs:
                f.write(f"file '{s}'\n")
        r = run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                 "-c:a", "libmp3lame", "-b:a", "128k", out])
        if r.returncode == 0 and dur_ok(out):
            print(f"  OK {bid} (+{m['n_jeda']} jeda)", flush=True)
        else:
            print(f"  GAGAL {bid}", flush=True); gagal.append(bid)
    shutil.rmtree(STAGING, ignore_errors=True)
    print("gagal:", gagal if gagal else "tidak ada")

if __name__ == "__main__":
    if sys.argv[1] == "assemble":
        assemble()
    else:
        render_range(int(sys.argv[1]), int(sys.argv[2]))
