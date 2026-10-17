#!/usr/bin/env python3
"""Rakit 1-panggilan Cosmic Unknown 2026-10-16 (Great Attractor).
Audio: 18 segmen + jeda 1.5s antar beat + jeda dramatis 2.5s setelah beat-010
+ bumper setelah beat-010 (~55%). 72 gambar (4 per beat), durasi shot bervariasi,
durasi slide dari GAP TIMELINE AUDIO (slide_k = starts[k+1]-starts[k]), grain,
vignette, overlay momen kunci y=36 (tanpa %, tanpa apostrof, escape colon),
title card, CTA tengah+akhir, subtitle terbakar.
Playlist concat ABSOLUTE path; tulis TEMP + verifikasi ffprobe BARU pindah ke final."""
import subprocess, os, json, random

BASE = "/home/hatch/workspace/youtube-otomatis/space-en"
GDIR = os.path.join(BASE, "gambar/2026-10-16")
ADIR = os.path.join(BASE, "audio/2026-10-16")
BTXT = os.path.join(BASE, "script/beats-2026-10-16")
BUMPER = os.path.join(BASE, "audio/2026-10-11/_bumper.mp3")
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUT = os.path.join(BASE, "video/2026-10-16.mp4")
SRT = os.path.join(BASE, "script/subtitle-2026-10-16.srt")
random.seed(16)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL:", " ".join(cmd)[:200]); print(r.stderr[-1500:]); raise SystemExit(1)
    return r

def dur(f):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0",f], capture_output=True, text=True).stdout)

# --- 1. silence + audio list ---
sil15 = os.path.join(ADIR, "_sil15.mp3"); sil25 = os.path.join(ADIR, "_sil25.mp3")
run([FFQ,"-y","-f","lavfi","-i","anullsrc=r=44100:cl=stereo:d=1.5","-c:a","libmp3lame","-b:a","128k",sil15])
run([FFQ,"-y","-f","lavfi","-i","anullsrc=r=44100:cl=stereo:d=2.5","-c:a","libmp3lame","-b:a","128k",sil25])

segs = [f"beat-{k:03d}.mp3" for k in range(1,19)]
items = []  # (path, label)
for i, s in enumerate(segs):
    lab = f"beat-{i+1:03d}"
    items.append((os.path.join(ADIR, s), lab))
    if i < len(segs)-1:
        items.append((sil15, None))
        if lab == "beat-010":
            items.append((sil25, None))          # jeda dramatis
    if lab == "beat-010":
        items.append((BUMPER, None))            # bumper ~55%

alist = os.path.join(ADIR, "_audiolist-2026-10-16.txt")
with open(alist, "w") as f:
    for p, _ in items:
        f.write(f"file '{p}'\n")               # ABSOLUTE path
afull = os.path.join(ADIR, "voiceover-full-2026-10-16.mp3")
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
          open(os.path.join(BASE,"script/timing-beat-2026-10-16.json"),"w"), indent=1)

def srt_time(x):
    h=int(x//3600); m=int(x%3600//60); s=int(x%60); ms=int(round((x%1)*1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

cues, idx = [], 1
for lab in sorted(starts, key=lambda k: starts[k]):
    txt = open(os.path.join(BTXT, f"{lab}.txt")).read()
    words = txt.split()
    per = max(1, len(words)//max(1,int(beat_durs[lab]//4)))
    chunks = [" ".join(words[i:i+per]) for i in range(0,len(words),per)]
    cd = beat_durs[lab]/len(chunks)
    for j, ch in enumerate(chunks):
        a = starts[lab]+j*cd; b = a+cd
        cues.append(f"{idx}\n{srt_time(a)} --> {srt_time(b)}\n{ch}\n"); idx += 1
open(SRT,"w").write("\n".join(cues))
print("SRT cues:", len(cues))

# --- 3. gambar: 4 per beat, durasi dari GAP TIMELINE (bukan speech-only) ---
ratios = [(0.30,0.22,0.26,0.22),(0.24,0.28,0.24,0.24),(0.26,0.24,0.28,0.22),(0.22,0.30,0.22,0.26)]
names = []
for k in range(1,19):
    for v in "abcd": names.append(f"beat-{k:03d}-{v}")
for n in names:
    assert os.path.exists(os.path.join(GDIR, n+".webp")), f"gambar hilang: {n}"
span = {}
labs = [f"beat-{k:03d}" for k in range(1,19)]
for i, lab in enumerate(labs):
    span[lab] = (starts[labs[i+1]] - starts[lab]) if i < 17 else (total - starts[lab])
lst = os.path.join(BASE, "video/_slides_2026-10-16.txt")
with open(lst,"w") as f:
    ri = 0
    for k in range(1,19):
        lab = f"beat-{k:03d}"
        bd = span[lab]
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
OVERLAYS = [(2,"600 KILOMETERS PER SECOND"),
            (4,"250 MILLION LIGHT YEARS AWAY"),
            (5,"THE ZONE OF AVOIDANCE"),
            (7,"LANIAKEA SUPERCLUSTER"),
            (10,"100,000 GALAXIES")]
for beat, teks in OVERLAYS:
    s = starts[f"beat-{beat:03d}"]; e = s + span[f"beat-{beat:03d}"]
    filters.append(f"drawtext=fontfile={FONT}:text='{teks}':fontsize=54:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=36:enable='between(t,{s:.2f},{e:.2f})'")
# title card detik 1-5
filters.append(f"drawtext=fontfile={FONT}:text='THE GREAT ATTRACTOR':fontsize=72:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,1.0,5.0)'")
filters.append(f"drawtext=fontfile={FONT}:text='SOMETHING INVISIBLE IS PULLING OUR GALAXY':fontsize=34:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2+50:enable='between(t,1.0,5.0)'")
# CTA tengah + akhir
mid = total/2
filters.append(f"drawtext=fontfile={FONT}:text='SUBSCRIBE FOR DAILY COSMIC MYSTERIES':fontsize=44:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=36:enable='between(t,{mid-1.5:.2f},{mid+1.5:.2f})'")
filters.append(f"drawtext=fontfile={FONT}:text='SUBSCRIBE FOR DAILY COSMIC MYSTERIES':fontsize=44:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-120:enable='between(t,{total-4.0:.2f},{total:.2f})'")
srt_esc = SRT.replace("'","'\\''")
filters.append(f"subtitles=filename='{srt_esc}':force_style='FontName=DejaVu Sans,FontSize=22,BorderStyle=1,Outline=2,Alignment=2,MarginV=45'")
filters.append("format=yuv420p")

# TWO-STEP: render video-only dulu, lalu mux audio (pola terbukti)
VID_TMP = os.path.join(BASE, "video/_videoonly-2026-10-16.mp4")
OUT_TMP = os.path.join(BASE, "video/_final-2026-10-16.mp4")
run([FFQ,"-y","-f","concat","-safe","0","-i",lst,
     "-vf",",".join(filters),"-c:v","libx264","-preset","veryfast","-crf","20",
     "-an","-movflags","+faststart",VID_TMP])
run([FFQ,"-y","-i",VID_TMP,"-i",afull,
     "-c:v","copy","-c:a","aac","-b:a","128k","-shortest",
     "-movflags","+faststart",OUT_TMP])
vd = dur(OUT_TMP)
print(f"video {vd:.1f}s (audio {afull_dur:.1f}s)")
assert abs(vd - afull_dur) < 5.0, "durasi video/audio tidak cocok!"
assert 540 <= vd <= 600, f"durasi {vd:.1f}s di luar target 540-600!"
os.replace(OUT_TMP, OUT)
print("OK ->", OUT)
