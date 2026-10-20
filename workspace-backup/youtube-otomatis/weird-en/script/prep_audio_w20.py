#!/usr/bin/env python3
"""Prep audio w20: jeda 0.35s antar beat, jeda dramatis 1.3s setelah beat 23
(fakta paling gila: 28 feet of nails), bumper owner disisipkan setelah beat 28.
Concat voiceover -> gabungan-2026-10-20.mp3, ukur durasi segmen, tulis chapter starts."""
import json, os, subprocess, sys

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
PAUSE = 0.12  # jeda antar beat (detik, dipadatkan agar total 9-10 mnt)
N = 74
BUMPER_AFTER = 28
DRAMA_BEAT = 23  # jeda 1.3s setelah beat ini

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

sil035 = os.path.join(W, "data", "silence-035.mp3")
if not (os.path.exists(sil035) and dur(sil035) > 0.3):
    run([Q, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-t", str(PAUSE), "-c:a", "libmp3lame", "-b:a", "128k", sil035])

# jeda dramatis 1.3s setelah beat paling gila (idempotent via marker)
drama_marker = os.path.join(W, "data", ".drama23-w20.done")
if not os.path.exists(drama_marker):
    bd = os.path.join(W, "audio", f"w20-beat-{DRAMA_BEAT:03d}.mp3")
    tmpd = os.path.join(W, "audio", f"w20-beat-{DRAMA_BEAT:03d}-p.mp3")
    run([Q, "-y", "-i", bd, "-i", os.path.join(W, "data", "silence-1.3.mp3"),
         "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[a]", "-map", "[a]",
         "-c:a", "libmp3lame", "-b:a", "128k", tmpd])
    os.replace(tmpd, bd)
    open(drama_marker, "w").write("ok")
    print(f"beat-{DRAMA_BEAT:03d} +1.3s drama OK", flush=True)
else:
    print(f"beat-{DRAMA_BEAT:03d} drama sudah pernah ditambah, dilewati", flush=True)

bumper = os.path.join(W, "data", "bumper-weird-en.mp3")
assert os.path.exists(bumper), "bumper-weird-en.mp3 hilang!"
bumper_dur = dur(bumper)
print(f"bumper dur: {bumper_dur:.2f}s", flush=True)

# concat list: beat, jeda, beat, jeda ... (bumper setelah beat 28)
items = []
for i in range(1, N + 1):
    items.append(os.path.join(W, "audio", f"w20-beat-{i:03d}.mp3"))
    if i == BUMPER_AFTER:
        items.append(bumper)
lst = os.path.join(W, "data", "concat-list-w20.txt")
with open(lst, "w") as f:
    for j, it in enumerate(items):
        f.write(f"file '{it}'\n")
        if j < len(items) - 1:
            f.write(f"file '{sil035}'\n")
gab = os.path.join(W, "audio", "gabungan-2026-10-20.mp3")
run([Q, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", gab])
print("concat OK", flush=True)

# durasi per item -> durasi segmen (item + jeda, item terakhir tanpa jeda)
beat_dur = {}
for i in range(1, N + 1):
    beat_dur[f"w20-beat-{i:03d}"] = dur(os.path.join(W, "audio", f"w20-beat-{i:03d}.mp3"))
beat_dur["w20-bumper"] = bumper_dur
seg_dur = {}
keys = [f"w20-beat-{i:03d}" for i in range(1, N + 1)]
keys.insert(BUMPER_AFTER, "w20-bumper")  # setelah beat 28
for j, k in enumerate(keys):
    seg_dur[k] = beat_dur[k] + (PAUSE if j < len(keys) - 1 else 0.0)
json.dump(seg_dur, open(os.path.join(W, "data", "durasi-beat-2026-10-20.json"), "w"), indent=1)
tot = sum(seg_dur.values())
print(f"total segmen: {tot:.1f}s = {tot/60:.2f} min", flush=True)
assert 540 <= tot <= 605, f"durasi {tot:.0f}s di luar target 9-10 menit!"

# chapter starts (offset title card 2.5s)
chapters = {
    1: "Hook: The 30-Year Fingernails",
    7: "Intro: The Weirdness Scale Battle",
    13: "Round 1: Eyeball Pop Record",
    21: "28 Feet of Fingernails (Perfect 10)",
    29: "Round 1 Recap, Round 2 Preview",
    33: "Big Mac Legend: 30,000 and Counting",
    41: "110 Tacos in 8 Minutes",
    49: "Round 3: 85 Spoons on One Body",
    55: "260 T-Shirts Worn at Once",
    60: "Loudest Burp Ever: 109.9 Decibels",
    65: "Final Scores and Champion Crowned",
    71: "Outro: Subscribe for Daily Weirdness",
}
cum = 2.5
starts, beat_starts = {}, {}
sk = sorted(chapters)
for j, k in enumerate(keys):
    beat_starts[k] = cum
    cum += seg_dur[k]
for j, b in enumerate(sk):
    starts[str(b)] = {"start": round(beat_starts[f"w20-beat-{b:03d}"], 2), "title": chapters[b]}
for b in sk:
    t = starts[str(b)]["start"]
    print(f"{int(t//60)}:{int(t%60):02d} {starts[str(b)]['title']}")
json.dump(starts, open(os.path.join(W, "data", "chapter-starts-w20.json"), "w"), indent=1)
print("OK prep audio w20")
