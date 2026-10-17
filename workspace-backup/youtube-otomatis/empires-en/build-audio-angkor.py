#!/usr/bin/env python3
"""Gabung beat TTS Angkor jadi voiceover penuh + 0.8s jeda di beat dramatis
+ 4s silence pembuka untuk title card.
Hasil: audio/voiceover-angkor-2026-10-10.mp3, durasi-beat-angkor.json,
durasi-72-angkor.json, chapters-angkor.json
"""
import subprocess, json, os, random

BASE = "/home/hatch/workspace/youtube-otomatis/empires-en"
AUD = f"{BASE}/audio/2026-10-10"
QUEUE = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
PAUSE_BEATS = {11, 13, 14, 18}  # beat dengan [pause] di script
TITLE_SIL = 4.0  # title card pembuka
RND = random.Random(7)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

# 1. file silence
sil = os.path.join(AUD, "silence08.mp3")
if not os.path.exists(sil):
    subprocess.run([QUEUE, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-t", "0.8", "-c:a", "libmp3lame", "-b:a", "128k", sil],
                   capture_output=True, check=True)
sil4 = os.path.join(AUD, "silence4.mp3")
if not os.path.exists(sil4):
    subprocess.run([QUEUE, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-t", str(TITLE_SIL), "-c:a", "libmp3lame", "-b:a", "128k", sil4],
                   capture_output=True, check=True)

# 2. durasi tiap beat
beat_durs = {}
for n in range(1, 25):
    p = os.path.join(AUD, f"beat-{n:03d}.mp3")
    d = dur(p)
    if n in PAUSE_BEATS:
        d += 0.8
    beat_durs[n] = d
json.dump({"beat-000": TITLE_SIL,
           **{f"beat-{n:03d}": round(d, 2) for n, d in beat_durs.items()}},
          open(os.path.join(BASE, "durasi-beat-angkor.json"), "w"), indent=1)
total = sum(beat_durs.values()) + TITLE_SIL
print(f"Total voiceover: {total:.1f}s = {total/60:.1f} mnt")

# 3. concat: silence4 + beat + silence setelah beat pause
inputs, parts = [], []
inputs += ["-i", sil4]; parts.append("[0:a]"); idx = 1
for n in range(1, 25):
    inputs += ["-i", os.path.join(AUD, f"beat-{n:03d}.mp3")]
    parts.append(f"[{idx}:a]"); idx += 1
    if n in PAUSE_BEATS:
        inputs += ["-i", sil]
        parts.append(f"[{idx}:a]"); idx += 1
full = os.path.join(BASE, "audio", "voiceover-angkor-2026-10-10.mp3")
subprocess.run([QUEUE, "-y"] + inputs +
               ["-filter_complex", "".join(parts) + f"concat=n={idx}:v=0:a=1",
                "-c:a", "libmp3lame", "-b:a", "128k", full],
               capture_output=True, check=True)
print("OK voiceover:", full, f"({dur(full):.1f}s)")

# 4. durasi 73 segmen (title card + 3 gambar per beat, pacing bervariasi)
d73 = {"beat-000": TITLE_SIL}
ratios_cycle = [(0.38, 0.34, 0.28), (0.30, 0.38, 0.32), (0.34, 0.30, 0.36), (0.42, 0.28, 0.30)]
for n in range(1, 25):
    d = beat_durs[n]
    r = list(ratios_cycle[n % 4])
    j = RND.uniform(-0.03, 0.03)
    r[0] += j; r[2] -= j
    durs = [round(d * x, 2) for x in r]
    durs[2] = round(d - durs[0] - durs[1], 2)
    for k, sub in enumerate("abc"):
        d73[f"beat-{((n-1)*3 + k + 1):03d}"] = durs[k]
json.dump(d73, open(os.path.join(BASE, "durasi-73-angkor.json"), "w"), indent=1)
print("OK durasi-73:", round(sum(d73.values()), 1), "s / 73 segmen")

# 5. chapter timestamps dari batas beat (termasuk title card)
cum, chapters = 0.0, []
cum += TITLE_SIL
chapters.append("0:00")
for n in range(1, 25):
    m, s = divmod(int(cum), 60)
    chapters.append(f"{m}:{s:02d}")
    cum += beat_durs[n]
json.dump(chapters, open(os.path.join(BASE, "chapters-angkor.json"), "w"), indent=1)
print("Chapters:", chapters)
