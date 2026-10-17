#!/usr/bin/env python3
"""Prep audio b12: jeda 1.3s setelah beat 35 + jeda 0.35s antar beat,
concat voiceover, ukur durasi segmen (= beat + jeda), tulis chapter starts.
Jalankan SETELAH tts_b12.py selesai."""
import json, os, subprocess, sys

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
PAUSE = 0.35  # jeda antar beat (detik)
N = 73

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERR:", r.stderr[-400:]); sys.exit(1)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

os.chdir(W)

# 1. silence 0.35s (sekali saja)
sil035 = os.path.join(W, "data", "silence-035.mp3")
if not (os.path.exists(sil035) and dur(sil035) > 0.3):
    run([Q, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-t", str(PAUSE), "-c:a", "libmp3lame", "-b:a", "128k", sil035])

# 2. jeda dramatis 1.3s setelah beat 35 (fakta paling gila)
b14 = os.path.join(W, "audio", "b12-beat-035.mp3")
tmp14 = os.path.join(W, "audio", "b12-beat-035-p.mp3")
run([Q, "-y", "-i", b14, "-i", os.path.join(W, "data", "silence-1.3.mp3"),
     "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[a]", "-map", "[a]",
     "-c:a", "libmp3lame", "-b:a", "128k", tmp14])
os.replace(tmp14, b14)
print("beat-014 +silence OK", flush=True)

# 3. concat list: beat, jeda, beat, jeda, ...
lst = os.path.join(W, "data", "concat-list-b12.txt")
with open(lst, "w") as f:
    for i in range(1, N + 1):
        f.write(f"file '{W}/audio/b12-beat-{i:03d}.mp3'\n")
        if i < N:
            f.write(f"file '{sil035}'\n")
gab = os.path.join(W, "audio", "gabungan-2026-10-12.mp3")
run([Q, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", gab])
print("concat OK", flush=True)

# 4. durasi per beat -> durasi segmen (beat + jeda, beat terakhir tanpa jeda)
beat_dur = {}
for i in range(1, N + 1):
    beat_dur[f"b12-beat-{i:03d}"] = dur(os.path.join(W, "audio", f"b12-beat-{i:03d}.mp3"))
seg_dur = {}
for i in range(1, N + 1):
    k = f"b12-beat-{i:03d}"
    seg_dur[k] = beat_dur[k] + (PAUSE if i < N else 0.0)
json.dump(seg_dur, open(os.path.join(W, "data", "durasi-beat-2026-10-12.json"), "w"), indent=1)
tot = sum(seg_dur.values())
print(f"total segmen: {tot:.1f}s = {tot/60:.2f} min", flush=True)

# 5. chapter starts (offset title card 2.5s)
chapters = {1: "Hook: A Mirror the Size of a Country", 7: "Zone 1 Alien Land: Socotra", 16: "Sailing Stones of Death Valley", 25: "Zone 2 Fire: Danakil Depression", 33: "Naica Crystal Cave", 42: "Zone 3: Pink Lake Hillier", 50: "Salar de Uyuni Mirror", 58: "Catatumbo Everlasting Storm", 66: "The Verdict"}
cum = 2.5
starts = {}
keys = sorted(chapters)
for j, b in enumerate(keys):
    starts[str(b)] = {"start": round(cum, 2), "title": chapters[b]}
    nxt = keys[j + 1] if j + 1 < len(keys) else N + 1
    cum += sum(seg_dur[f"b12-beat-{i:03d}"] for i in range(b, nxt))
for b in keys:
    t = starts[str(b)]["start"]
    print(f"{int(t//60)}:{int(t%60):02d} {starts[str(b)]['title']}")
json.dump(starts, open(os.path.join(W, "data", "chapter-starts-b12.json"), "w"), indent=1)
print("OK prep audio")
