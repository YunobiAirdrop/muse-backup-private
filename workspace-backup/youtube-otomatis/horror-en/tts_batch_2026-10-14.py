#!/usr/bin/env python3
"""TTS 72 beats horror-en 2026-10-14 -> audio/beat-2026-10-14-NNN.mp3,
durasi-beat-2026-10-14.json, audio/gabungan-2026-10-14.mp3.
Voice: avocado_v2:briggs, speed 92, language en. Sanitasi WAJIB.
Scare beats (sil-22.mp3 2.2s): {4,24,33,47,58,66}; else sil-04.mp3.
"""
import subprocess, os, sys, json, time

WS = "/home/hatch/workspace/youtube-otomatis/horror-en"
SCRIPT = f"{WS}/script/2026-10-14.txt"
ADIR = f"{WS}/audio"
LOG = f"{WS}/tts-2026-10-14.log"
TTS = "/opt/hatch/bin/tts"
VOICE = "avocado_v2:briggs"
SCARE = {4, 24, 33, 47, 58, 66}
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
N = 72

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis")
from tts_sanitize import bersihkan_teks_tts

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def main():
    lines = [l.rstrip("\n") for l in open(SCRIPT) if l.strip()]
    assert len(lines) == N, f"butuh {N} baris, ada {len(lines)}"
    assert os.path.exists(TTS), f"tts tidak ada: {TTS}"
    log(f"mulai TTS {len(lines)} beats")
    for i, raw in enumerate(lines, 1):
        out = f"{ADIR}/beat-2026-10-14-{i:03d}.mp3"
        if os.path.exists(out) and dur(out) > 1.0:
            continue
        text = bersihkan_teks_tts(raw)
        assert text, f"beat {i} kosong setelah sanitasi"
        ok = False
        for attempt in (1, 2):
            r = subprocess.run(
                [TTS, "speak", "--voice", VOICE, "--speed", "92",
                 "--language", "en", "--output", out, "--text-stdin"],
                input=text.encode("utf-8"), capture_output=True, timeout=180)
            if r.returncode == 0 and os.path.exists(out) and dur(out) > 1.0:
                ok = True
                break
            log(f"  beat {i:03d} gagal (attempt {attempt}), retry...")
            time.sleep(5)
        if not ok:
            log(f"GAGAL TOTAL beat {i:03d}; BERHENTI")
            sys.exit(1)
        if i % 10 == 0:
            log(f"  {i}/{N} beats...")
    log("semua beats OK, ukur durasi...")
    dj = {}
    for i in range(1, N + 1):
        d = dur(f"{ADIR}/beat-2026-10-14-{i:03d}.mp3")
        assert d > 1.0, f"beat {i:03d} durasi {d}"
        dj[f"beat-{i:03d}"] = round(d, 3)
    json.dump(dj, open(f"{ADIR}/durasi-beat-2026-10-14.json", "w"), indent=1)
    log("rakit gabungan...")
    lst = f"{ADIR}/gabungan-list-2026-10-14.txt"
    with open(lst, "w") as f:
        for i in range(1, N + 1):
            sil = f"{ADIR}/sil-22.mp3" if i in SCARE else f"{ADIR}/sil-04.mp3"
            f.write(f"file '{sil}'\n")
            f.write(f"file '{ADIR}/beat-2026-10-14-{i:03d}.mp3'\n")
    gab = f"{ADIR}/gabungan-2026-10-14.mp3"
    r = subprocess.run([FQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c:a", "libmp3lame", "-b:a", "128k", gab],
                       capture_output=True, text=True)
    if r.returncode != 0:
        log(f"GAGAL concat gabungan: {r.stderr[-400:]}")
        sys.exit(1)
    d = dur(gab)
    log(f"OK: {gab} durasi {d/60:.2f} menit (target 7.8-9.0)")
    assert 470 <= d <= 545, f"durasi gabungan {d/60:.2f} mnt di luar target!"

if __name__ == "__main__":
    main()
