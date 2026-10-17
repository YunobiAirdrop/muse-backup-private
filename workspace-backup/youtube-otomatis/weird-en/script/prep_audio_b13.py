#!/usr/bin/env python3
"""Prep audio b13: jeda 1.3s setelah beat 37 (fakta paling gila: molasses 21 killed),
jeda 0.35s antar beat, SISIPKAN bumper-weird-en.mp3 setelah beat 59 (break natural
sebelum final round, ~50-60% durasi; dilarang detik 0). Concat voiceover + bumper,
ukur durasi segmen, tulis chapter starts. Jalankan SETELAH tts_b13.py selesai."""
import json, os, subprocess, sys

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
PAUSE = 0.35
N = 74
BUMPER_AFTER = 59  # sisipkan setelah beat ini

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
for i in range(1, N + 1):
    p = os.path.join(W, "audio", f"b13-beat-{i:03d}.mp3")
    assert os.path.exists(p) and os.path.getsize(p) > 1000, f"TTS hilang: {p}"

sil035 = os.path.join(W, "data", "silence-035.mp3")
if not (os.path.exists(sil035) and dur(sil035) > 0.3):
    run([Q, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-t", str(PAUSE), "-c:a", "libmp3lame", "-b:a", "128k", sil035])

# jeda dramatis 1.3s setelah beat 37 (21 orang tewas)
b37 = os.path.join(W, "audio", "b13-beat-037.mp3")
tmp37 = os.path.join(W, "audio", "b13-beat-037-p.mp3")
run([Q, "-y", "-i", b37, "-i", os.path.join(W, "data", "silence-1.3.mp3"),
     "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[a]", "-map", "[a]",
     "-c:a", "libmp3lame", "-b:a", "128k", tmp37])
os.replace(tmp37, b37)
print("beat-037 +silence 1.3s OK", flush=True)

# concat list: beat, jeda, ... + bumper setelah beat 59
lst = os.path.join(W, "data", "concat-list-b13.txt")
with open(lst, "w") as f:
    for i in range(1, N + 1):
        f.write(f"file '{W}/audio/b13-beat-{i:03d}.mp3'\n")
        if i == BUMPER_AFTER:
            f.write(f"file '{sil035}'\n")
            f.write(f"file '{W}/data/bumper-weird-en.mp3'\n")
            f.write(f"file '{sil035}'\n")
        elif i < N:
            f.write(f"file '{sil035}'\n")
gab = os.path.join(W, "audio", "gabungan-2026-10-13.mp3")
run([Q, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", gab])
print("concat OK", flush=True)

beat_dur = {f"b13-beat-{i:03d}": dur(os.path.join(W, "audio", f"b13-beat-{i:03d}.mp3")) for i in range(1, N + 1)}
bumper_dur = dur(os.path.join(W, "data", "bumper-weird-en.mp3"))
seg_dur = {}
for i in range(1, N + 1):
    k = f"b13-beat-{i:03d}"
    seg_dur[k] = beat_dur[k] + (PAUSE if i < N else 0.0)
seg_dur["b13-bumper"] = PAUSE + bumper_dur + PAUSE
json.dump(seg_dur, open(os.path.join(W, "data", "durasi-beat-2026-10-13.json"), "w"), indent=1)
tot = sum(seg_dur.values())
print(f"total segmen: {tot:.1f}s = {tot/60:.2f} min, bumper={bumper_dur:.2f}s", flush=True)

chapters = {1: "Hook: The Sticky Wave That Killed 21", 7: "Round 1: The Dancing Plague of 1518",
            16: "Round 2: The Kentucky Meat Shower", 25: "Round 3: The London Beer Flood",
            34: "Round 4: The Great Molasses Flood", 43: "Round 5: Exploding Trousers",
            51: "Round 6: Tunguska, the Sky Bomb", 60: "Final Round: The Rain of Fish",
            68: "The Verdict: Weirdest Moment Ever"}
cum = 2.5
starts, keys = {}, sorted(chapters)
for j, b in enumerate(keys):
    starts[str(b)] = {"start": round(cum, 2), "title": chapters[b]}
    nxt = keys[j + 1] if j + 1 < len(keys) else N + 1
    for i in range(b, nxt):
        k = f"b13-beat-{i:03d}"
        cum += seg_dur[k]
        if i == BUMPER_AFTER:
            cum += seg_dur["b13-bumper"]
for b in keys:
    t = starts[str(b)]["start"]
    print(f"{int(t//60)}:{int(t%60):02d} {starts[str(b)]['title']}")
json.dump(starts, open(os.path.join(W, "data", "chapter-starts-b13.json"), "w"), indent=1)
print("OK prep audio")
