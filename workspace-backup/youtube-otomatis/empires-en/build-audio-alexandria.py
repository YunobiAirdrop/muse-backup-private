#!/usr/bin/env python3
"""Gabung beat TTS Alexandria jadi voiceover penuh + 0.8s jeda di beat dramatis
+ 4s silence pembuka untuk title card. Juga: durasi per beat, durasi 73 segmen
(pacing bervariasi), chapters berjudul, dan SRT subtitle per beat.
Hasil: audio/voiceover-alexandria-2026-10-18.mp3, durasi-beat-alexandria.json,
durasi-73-alexandria.json, chapters-alexandria.json, subtitles-alexandria.srt
"""
import subprocess, json, os, random, textwrap

BASE = "/home/hatch/workspace/youtube-otomatis/empires-en"
AUD = f"{BASE}/audio/2026-10-18"
QUEUE = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
PAUSE_BEATS = {14, 19}  # jeda dramatis: malam kebakaran & misteri lokasi hilang
TITLE_SIL = 4.0
RND = random.Random(18)
beats = json.load(open(f"{BASE}/script/beats-alexandria.json"))

CHAPTER_TITLES = {
    0: "The Night We Lost Everything",
    1: "The Night We Lost Everything",
    2: "Alexandria Today",
    3: "One Scroll to Save",
    4: "Alexander's Dream",
    5: "The Wild Idea",
    6: "The First Copyright Pirates",
    7: "Inside the Brain of the World",
    8: "The First Search Engine",
    9: "Measuring the Earth",
    10: "Medicine Is Born Here",
    11: "Paid to Wonder",
    12: "The Fire",
    13: "48 BC: Caesar's Torch",
    14: "Midnight at the Harbor",
    15: "The Slow Death",
    16: "What We Lost",
    17: "A Scroll Could Rewrite History",
    18: "Cleopatra's Last Light",
    19: "The Sunken Library",
    20: "The Digs Go On",
    21: "Sentences from the Fire",
    22: "The Library Rises Again",
    23: "Memory Is a Choice",
    24: "Next: Pompeii",
}

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def srt_time(sec):
    h, rem = divmod(sec, 3600); m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):06.3f}".replace(".", ",")

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

beat_durs = {}
for n in range(1, 25):
    p = os.path.join(AUD, f"beat-{n:03d}.mp3")
    d = dur(p)
    if n in PAUSE_BEATS:
        d += 0.8
    beat_durs[n] = d
json.dump({"beat-000": TITLE_SIL,
           **{f"beat-{n:03d}": round(d, 2) for n, d in beat_durs.items()}},
          open(os.path.join(BASE, "durasi-beat-alexandria.json"), "w"), indent=1)
total = sum(beat_durs.values()) + TITLE_SIL
print(f"Total voiceover: {total:.1f}s = {total/60:.1f} mnt", flush=True)

inputs, parts = ["-i", sil4], ["[0:a]"]
idx = 1
for n in range(1, 25):
    inputs += ["-i", os.path.join(AUD, f"beat-{n:03d}.mp3")]
    parts.append(f"[{idx}:a]"); idx += 1
    if n in PAUSE_BEATS:
        inputs += ["-i", sil]
        parts.append(f"[{idx}:a]"); idx += 1
full = os.path.join(BASE, "audio", "voiceover-alexandria-2026-10-18.mp3")
subprocess.run([QUEUE, "-y"] + inputs +
               ["-filter_complex", "".join(parts) + f"concat=n={idx}:v=0:a=1",
                "-c:a", "libmp3lame", "-b:a", "128k", full],
               capture_output=True, check=True)
print("OK voiceover:", full, f"({dur(full):.1f}s)", flush=True)

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
json.dump(d73, open(os.path.join(BASE, "durasi-73-alexandria.json"), "w"), indent=1)
print("OK durasi-73:", round(sum(d73.values()), 1), "s / 73 segmen", flush=True)

cum = TITLE_SIL
chapters = [f"0:00 {CHAPTER_TITLES[1]}"]
for n in range(1, 25):
    m, s = divmod(int(cum), 60)
    chapters.append(f"{m}:{s:02d} {CHAPTER_TITLES[n + 1] if n + 1 in CHAPTER_TITLES else ''}".rstrip())
    cum += beat_durs[n]
json.dump(chapters, open(os.path.join(BASE, "chapters-alexandria.json"), "w"), indent=1)
print("Chapters:", len(chapters), flush=True)
for c in chapters:
    print(" ", c)

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
with open(os.path.join(BASE, "subtitles-alexandria.srt"), "w") as f:
    for i, st, en, tx in entries:
        f.write(f"{i}\n{srt_time(st)} --> {srt_time(en)}\n{tx}\n\n")
print("OK SRT:", len(entries), "entries", flush=True)
