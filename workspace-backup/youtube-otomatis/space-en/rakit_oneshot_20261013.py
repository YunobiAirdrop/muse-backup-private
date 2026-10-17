#!/usr/bin/env python3
"""Rakit 1-panggilan Cosmic Unknown 2026-10-13 (Oumuamua).
Audio: 19 segmen (beats 001-014, 015a, 015b4, 016-018) + jeda 0.7s antar beat
+ jeda dramatis 2s setelah beat-007 + bumper 4.01s setelah beat-009 (~50%).
72 gambar (4 per beat), durasi shot bervariasi, grain, vignette,
overlay momen kunci y=36 (tanpa '%'), CTA tengah 3s, subtitle terbakar.
Playlist concat ABSOLUTE path; verifikasi ffprobe sebelum mux."""
import subprocess, os, json, re, random

BASE = "/home/hatch/workspace/youtube-otomatis/space-en"
GDIR = os.path.join(BASE, "gambar/2026-10-13")
ADIR = os.path.join(BASE, "audio/2026-10-13")
BUMPER = os.path.join(BASE, "audio/2026-10-11/_bumper.mp3")
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUT = os.path.join(BASE, "video/2026-10-13.mp4")
SRT = os.path.join(BASE, "script/subtitle-2026-10-13.srt")
random.seed(13)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL:", " ".join(cmd)[:200]); print(r.stderr[-1500:]); raise SystemExit(1)
    return r

def dur(f):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0",f], capture_output=True, text=True).stdout)

# --- 1. silence + audio list ---
sil07 = os.path.join(ADIR, "_sil07.mp3"); sil2 = os.path.join(ADIR, "_sil2.mp3")
run([FFQ,"-y","-f","lavfi","-i","anullsrc=r=44100:cl=stereo:d=0.7","-c:a","libmp3lame","-b:a","128k",sil07])
run([FFQ,"-y","-f","lavfi","-i","anullsrc=r=44100:cl=stereo:d=2.0","-c:a","libmp3lame","-b:a","128k",sil2])

segs = [f"beat-{k:03d}.mp3" for k in range(1,15)] + ["beat-015a.mp3","beat-015b4.mp3"] + [f"beat-{k:03d}.mp3" for k in range(16,19)]
beat_label = [f"beat-{k:03d}" for k in range(1,15)] + ["beat-015","beat-015"] + [f"beat-{k:03d}" for k in range(16,19)]
seg_durs = [dur(os.path.join(ADIR, s)) for s in segs]

items = []  # (path, label_untuk_subtitle)
for i, s in enumerate(segs):
    items.append((os.path.join(ADIR, s), beat_label[i]))
    if i < len(segs)-1:
        items.append((sil07, None))
        if beat_label[i] == "beat-007":
            items.append((sil2, None))          # jeda dramatis
    if beat_label[i] == "beat-009":
        items.append((BUMPER, None))            # bumper tengah video

alist = os.path.join(ADIR, "_audiolist-2026-10-13.txt")
with open(alist, "w") as f:
    for p, _ in items:
        f.write(f"file '{p}'\n")               # ABSOLUTE path
afull = os.path.join(ADIR, "voiceover-full-2026-10-13.mp3")
run([FFQ,"-y","-f","concat","-safe","0","-i",alist,"-c","copy",afull])
afull_dur = dur(afull)
expected = sum(dur(p) for p,_ in items)
print(f"afull {afull_dur:.1f}s (expected {expected:.1f}s)")
assert abs(afull_dur - expected) < 2.0, "durasi audio tidak cocok!"

# --- 2. timing per beat + SRT ---
starts, beat_durs = {}, {}
t = 0.0
for p, lab in items:
    d = dur(p)
    if lab and lab not in starts:
        starts[lab] = t; beat_durs[lab] = 0.0
    if lab:
        beat_durs[lab] += d
    t += d
total = t
json.dump({"starts":starts,"beat_durs":beat_durs,"total":total},
          open(os.path.join(BASE,"script/timing-beat-2026-10-13.json"),"w"), indent=1)

def srt_time(x):
    h=int(x//3600); m=int(x%3600//60); s=int(x%60); ms=int(round((x%1)*1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

cues, idx = [], 1
for lab in sorted(starts, key=lambda k: starts[k]):
    txt = open(os.path.join(ADIR, f"{lab}.txt")).read() if lab != "beat-015" else \
          open(os.path.join(ADIR,"beat-015a.txt")).read()+" "+open(os.path.join(ADIR,"beat-015b4.txt")).read()
    words = txt.split()
    per = max(1, len(words)//max(1,int(beat_durs[lab]//4)))
    chunks = [" ".join(words[i:i+per]) for i in range(0,len(words),per)]
    cd = beat_durs[lab]/len(chunks)
    for j, ch in enumerate(chunks):
        a = starts[lab]+j*cd; b = a+cd
        cues.append(f"{idx}\n{srt_time(a)} --> {srt_time(b)}\n{ch}\n"); idx += 1
open(SRT,"w").write("\n".join(cues))
print("SRT cues:", len(cues))

# --- 3. gambar: 4 per beat, durasi bervariasi ---
ratios = [(0.30,0.22,0.26,0.22),(0.24,0.28,0.24,0.24),(0.26,0.24,0.28,0.22),(0.22,0.30,0.22,0.26)]
names = []
for k in range(1,19):
    for v in "abcd": names.append(f"beat-{k:03d}-{v}")
lst = os.path.join(BASE, "video/_slides_2026-10-13.txt")
with open(lst,"w") as f:
    ri = 0
    for k in range(1,19):
        lab = f"beat-{k:03d}"
        bd = beat_durs[lab]
        r = ratios[ri % 4]; ri += 1
        for j, v in enumerate("abcd"):
            f.write(f"file '{os.path.join(GDIR, f'beat-{k:03d}-{v}.webp')}'\n")
            f.write(f"duration {bd*r[j]:.3f}\n")
    f.write(f"file '{os.path.join(GDIR, names[-1] + '.webp')}'\n")

# --- 4. filter video ---
filters = [
    "scale=1280:720:force_original_aspect_ratio=increase",
    "crop=1280:720",
    "fps=30",
    "eq=contrast=1.08:saturation=0.92:brightness=-0.02",
    "noise=alls=6:allf=t",
    "vignette=PI/5",
]
OVERLAYS = [(3,"FIRST INTERSTELLAR OBJECT EVER SEEN"),
            (5,"400 METERS OF SOLID MYSTERY"),
            (7,"ACCELERATED WITH NO VISIBLE ENGINE"),
            (9,"HARVARD\\: COULD IT BE ALIEN TECH"),
            (13,"OLDER THAN THE SUN ITSELF")]
for beat, teks in OVERLAYS:
    s = starts[f"beat-{beat:03d}"]; e = s + beat_durs[f"beat-{beat:03d}"] + 0.45
    filters.append(f"drawtext=fontfile={FONT}:text='{teks}':fontsize=54:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=36:enable='between(t,{s:.2f},{e:.2f})'")
mid = total/2
filters.append(f"drawtext=fontfile={FONT}:text='SUBSCRIBE FOR DAILY COSMIC MYSTERIES':fontsize=44:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=36:enable='between(t,{mid-1.5:.2f},{mid+1.5:.2f})'")
srt_esc = SRT.replace("'","'\\''")
filters.append(f"subtitles=filename='{srt_esc}':force_style='FontName=DejaVu Sans,FontSize=22,BorderStyle=1,Outline=2,Alignment=2,MarginV=45'")
filters.append("format=yuv420p")

# TWO-STEP (2026-10-14): 1-step (concat video + audio + filter berat) pernah gagal
# "Error opening output files: Invalid argument" tanpa sebab jelas. Render video-only
# dulu (terbukti jalan), lalu mux audio via -c:v copy.
VID_TMP = os.path.join(BASE, "video/_videoonly-2026-10-13.mp4")
OUT_TMP = os.path.join(BASE, "video/_final-2026-10-13.mp4")
cmd1 = [FFQ,"-y","-f","concat","-safe","0","-i",lst,
        "-vf",",".join(filters),"-c:v","libx264","-preset","veryfast","-crf","20",
        "-an","-movflags","+faststart",VID_TMP]
run(cmd1)
cmd2 = [FFQ,"-y","-i",VID_TMP,"-i",afull,
        "-c:v","copy","-c:a","aac","-b:a","128k","-shortest",
        "-movflags","+faststart",OUT_TMP]
run(cmd2)
vd = dur(OUT_TMP)
print(f"video {vd:.1f}s (audio {afull_dur:.1f}s)")
assert abs(vd - afull_dur) < 5.0, "durasi video/audio tidak cocok!"
os.replace(OUT_TMP, OUT)
print("OK ->", OUT)
