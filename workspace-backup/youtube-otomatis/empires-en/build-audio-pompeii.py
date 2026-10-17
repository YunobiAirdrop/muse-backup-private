#!/usr/bin/env python3
"""Gabung beat TTS Pompeii jadi voiceover penuh + 0.8s jeda di beat dramatis
+ 4s silence pembuka untuk title card. Juga: durasi per beat, durasi 73 segmen
(pacing bervariasi), chapters berjudul, dan SRT subtitle per beat.
Hasil: audio/voiceover-pompeii-2026-10-11.mp3, durasi-beat-pompeii.json,
durasi-73-pompeii.json, chapters-pompeii.json, subtitles-pompeii.srt
"""
import subprocess, json, os, random, textwrap

BASE = "/home/hatch/workspace/youtube-otomatis/empires-en"
AUD = f"{BASE}/audio/2026-10-11"
QUEUE = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
PAUSE_BEATS = {12, 16}  # jeda dramatis: kejatuhan & penemuan plaster cast
TITLE_SIL = 4.0
RND = random.Random(11)
beats = json.load(open(f"{BASE}/script/beats-pompeii.json"))

CHAPTER_TITLES = {
    0: "Death in a Single Morning",
    1: "Death in a Single Morning",
    2: "The Ruins Today",
    3: "Four Hours to Live",
    4: "A Roman Boomtown",
    5: "Bread, Bars, and Gladiators",
    6: "Painted Walls",
    7: "The Ground Warns",
    8: "The Boy Who Wrote It Down",
    9: "The Column Rises",
    10: "Stones from the Sky",
    11: "Night Without Night",
    12: "The Surge",
    13: "Buried for 17 Centuries",
    14: "1748: The Digging Begins",
    15: "The Molds of the Dead",
    16: "1863: The Plaster Casts",
    17: "A Paused Morning",
    18: "The Walls Talk",
    19: "A Mirror, Not a Tragedy",
    20: "The October Question",
    21: "The Mountain Still Breathes",
    22: "Sunset in the Forum",
    23: "What the Ash Preserved",
    24: "The Story Outlives Us All",
}

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def srt_time(sec):
    h, rem = divmod(sec, 3600); m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):06.3f}".replace(".", ",")

# 1. silence files
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
          open(os.path.join(BASE, "durasi-beat-pompeii.json"), "w"), indent=1)
total = sum(beat_durs.values()) + TITLE_SIL
print(f"Total voiceover: {total:.1f}s = {total/60:.1f} mnt", flush=True)

# 3. concat voiceover
inputs, parts = ["-i", sil4], ["[0:a]"]
idx = 1
for n in range(1, 25):
    inputs += ["-i", os.path.join(AUD, f"beat-{n:03d}.mp3")]
    parts.append(f"[{idx}:a]"); idx += 1
    if n in PAUSE_BEATS:
        inputs += ["-i", sil]
        parts.append(f"[{idx}:a]"); idx += 1
full = os.path.join(BASE, "audio", "voiceover-pompeii-2026-10-11.mp3")
subprocess.run([QUEUE, "-y"] + inputs +
               ["-filter_complex", "".join(parts) + f"concat=n={idx}:v=0:a=1",
                "-c:a", "libmp3lame", "-b:a", "128k", full],
               capture_output=True, check=True)
print("OK voiceover:", full, f"({dur(full):.1f}s)", flush=True)

# 4. durasi 73 segmen (title card + 3 gambar per beat, pacing bervariasi)
d73 = {"beat-000": TITLE_SIL}
ratios_cycle = [(0.38, 0.34, 0.28), (0.30, 0.38, 0.32),
                (0.34, 0.30, 0.36), (0.42, 0.28, 0.30)]
for n in range(1, 25):
    d = beat_durs[n]
    r = list(ratios_cycle[n % 4])
    j = RND.uniform(-0.03, 0.03)
    r[0] += j; r[2] -= j
    durs = [round(d * x, 2) for x in r]
    durs[2] = round(d - durs[0] - durs[1], 2)
    for k in range(3):
        d73[f"beat-{((n-1)*3 + k + 1):03d}"] = durs[k]
json.dump(d73, open(os.path.join(BASE, "durasi-73-pompeii.json"), "w"), indent=1)
print("OK durasi-73:", round(sum(d73.values()), 1), "s / 73 segmen", flush=True)

# 5. chapters berjudul dari batas beat
cum = TITLE_SIL
chapters = [f"0:00 {CHAPTER_TITLES[1]}"]
for n in range(1, 25):
    m, s = divmod(int(cum), 60)
    chapters.append(f"{m}:{s:02d} {CHAPTER_TITLES[n + 1] if n + 1 in CHAPTER_TITLES else ''}".rstrip())
    cum += beat_durs[n]
json.dump(chapters, open(os.path.join(BASE, "chapters-pompeii.json"), "w"), indent=1)
print("Chapters:", len(chapters), flush=True)

# 6. SRT: tiap beat dipecah per kalimat, durasi proporsional jumlah karakter
entries, cum = [], TITLE_SIL
idx = 1
for n in range(1, 25):
    text = beats[f"beat-{n:03d}"]
    sents = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(". ") if s.strip()]
    chunks, cur = [], ""
    for s in sents:
        if len(cur) + len(s) + 1 > 84 and cur:
            chunks.append(cur); cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur:
        chunks.append(cur)
    tot_chars = sum(len(c) for c in chunks) or 1
    t = cum
    for c in chunks:
        cd = beat_durs[n] * len(c) / tot_chars
        lines = textwrap.wrap(c, width=42)
        entries.append((idx, t, t + cd, "\n".join(lines[:2])))
        idx += 1; t += cd
    cum += beat_durs[n]
with open(os.path.join(BASE, "subtitles-pompeii.srt"), "w") as f:
    for i, st, en, tx in entries:
        f.write(f"{i}\n{srt_time(st)} --> {srt_time(en)}\n{tx}\n\n")
print("OK SRT:", len(entries), "entries", flush=True)
