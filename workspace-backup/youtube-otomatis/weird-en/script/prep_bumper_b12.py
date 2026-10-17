#!/usr/bin/env python3
"""Sisipkan bumper suara clone user (bumper-weird-en.wav, 3.75s) SETELAH beat 37
(CTA tengah video, jeda natural — BUKAN detik 0) ke gabungan b12.
Rebuild gabungan dari file beat (beat 035 sudah berisi silence 1.3s dari prep),
tambah durasi bumper ke segmen 037, hitung ulang durasi + chapter starts.
Idempoten: berhenti bila data/b12-bumper-done.json sudah ada.
Jalankan SETELAH prep_audio_b12.py selesai."""
import json, os, subprocess, sys

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
PAUSE = 0.35
N = 73
CTA_BEAT = 37
BUMPER_WAV = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-weird-en.wav"
MARKER = os.path.join(W, "data", "b12-bumper-done.json")

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERR:", r.stderr[-400:]); sys.exit(1)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

if os.path.exists(MARKER):
    print("bumper sudah disisipkan, skip"); sys.exit(0)
assert os.path.exists(BUMPER_WAV), "bumper wav tidak ada"

os.chdir(W)
# 1. bumper wav -> mp3 (samakan parameter silence/beat: 44100 stereo 128k)
bmp = os.path.join(W, "data", "bumper-weird-en.mp3")
run([Q, "-y", "-i", BUMPER_WAV, "-ar", "44100", "-ac", "2",
     "-c:a", "libmp3lame", "-b:a", "128k", bmp])
bdur = dur(bmp)
print(f"bumper mp3 OK: {bdur:.2f}s", flush=True)

# 2. rebuild concat: beat, jeda, ... setelah beat 37 sisipkan bumper (lalu jeda normal)
sil035 = os.path.join(W, "data", "silence-035.mp3")
lst = os.path.join(W, "data", "concat-list-b12-bumper.txt")
with open(lst, "w") as f:
    for i in range(1, N + 1):
        f.write(f"file '{W}/audio/b12-beat-{i:03d}.mp3'\n")
        if i == CTA_BEAT:
            f.write(f"file '{bmp}'\n")
        if i < N:
            f.write(f"file '{sil035}'\n")
gab_new = os.path.join(W, "audio", "gabungan-2026-10-12-bumper.mp3")
run([Q, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", gab_new])
os.replace(gab_new, os.path.join(W, "audio", "gabungan-2026-10-12.mp3"))
print("gabungan+bumper OK", flush=True)

# 3. durasi segmen baru: seg 37 += durasi bumper
beat_dur = {}
for i in range(1, N + 1):
    beat_dur[f"b12-beat-{i:03d}"] = dur(os.path.join(W, "audio", f"b12-beat-{i:03d}.mp3"))
seg_dur = {}
for i in range(1, N + 1):
    k = f"b12-beat-{i:03d}"
    seg_dur[k] = beat_dur[k] + (PAUSE if i < N else 0.0)
seg_dur[f"b12-beat-{CTA_BEAT:03d}"] += bdur
json.dump(seg_dur, open(os.path.join(W, "data", "durasi-beat-2026-10-12.json"), "w"), indent=1)
tot = sum(seg_dur.values())
print(f"total segmen baru: {tot:.1f}s = {tot/60:.2f} min", flush=True)

# 4. chapter starts (peta sama dengan prep_audio_b12.py, offset title card 2.5s)
chapters = {1: "Hook: A Mirror the Size of a Country", 7: "Zone 1 Alien Land: Socotra",
            16: "Sailing Stones of Death Valley", 25: "Zone 2 Fire: Danakil Depression",
            33: "Naica Crystal Cave", 42: "Zone 3: Pink Lake Hillier",
            50: "Salar de Uyuni Mirror", 58: "Catatumbo Everlasting Storm", 66: "The Verdict"}
cum = 2.5
starts = {}
keys = sorted(chapters)
for j, b in enumerate(keys):
    starts[str(b)] = {"start": round(cum, 2), "title": chapters[b]}
    nxt = keys[j + 1] if j + 1 < len(keys) else N + 1
    cum += sum(seg_dur[f"b12-beat-{i:03d}"] for i in range(b, nxt))
json.dump(starts, open(os.path.join(W, "data", "chapter-starts-b12.json"), "w"), indent=1)
json.dump({"bumper_dur": bdur, "after_beat": CTA_BEAT}, open(MARKER, "w"), indent=1)
print("OK bumper selesai")
