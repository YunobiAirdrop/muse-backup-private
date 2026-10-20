#!/usr/bin/env python3
"""Rakit LONG Jejak Buddha 2026-10-20: Khotbah pertama di Taman Rusa Isipatana (pool #6).
Footage Wikimedia Commons reuse dari 2026-10-18 (lisensi aman, atribusi di deskripsi) + voiceover mudiwa.
1280x720 30fps + film grain. Render per-segmen via ffmpeg-queue.sh (resumable).
Bumper suara user disisipkan setelah beat3 (jeda natural, = posisi 50% untuk CTA)."""
import subprocess, os, math, sys

D = "/home/hatch/workspace/jejak-buddha/2026-10-20"
FT = "/home/hatch/workspace/jejak-buddha/2026-10-18/footage"
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
VO = os.path.join(D, "audio", "voiceover-full.mp3")

FILES = {
    "golden-mist": "reused-golden-mist.webm",
    "sunrise": "reused-sunrise-drachenberg.webm",
    "bodhgaya": "bodhgaya-mahabodhi.webm",
    "mountain-mist": "reused-mountain-mist.webm",
    "lotus": "reused-lotus-timelapse.webm",
    "chandavaram": "chandavaram-stupa.webm",
    "sanchi": "sanchi-stupa.ogv",
    "borobudur12": "borobudur-2012.ogv",
    "chiangmai": "chiangmai-temple.webm",
    "ajatsatru": "ajatsatru-03.webm",
    "oil-lamps": "reused-oil-lamps-bodhgaya.webm",
    "statue": "reused-statue-buddha.webm",
    "vairochana": "reused-vairochana.webm",
    "borobudur19": "reused-borobudur-2019.webm",
    "candles": "reused-candles-dolly.ogv",
    "flameless": "flameless-candle.webm",
    "borobudur19b": "reused-borobudur-2019-02.webm",
}

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def esc(t):
    return t.replace(":", "\\:").replace("'", "\u2019").replace(",", "\\,")

adur = dur(VO)
print(f"AUDIO: {adur:.1f}s", flush=True)

CTA = "Subscribe Jejak Buddha"
SEGS = []
def add(slug, sd, sp, cx, cy, ovs=None):
    SEGS.append((slug, round(sd, 2), sp, cx, cy, ovs or []))

# beat0: 0.0-61.0 (hook: taman rusa, roda Dhamma)
add("golden-mist", 20.0, 1.0, 0, 0)
add("sunrise", 20.0, 1.0, 160, 90)
add("bodhgaya", 21.0, 1.0, 160, 90)
# beat1: 61.0-110.9 (49 hari keheningan)
add("mountain-mist", 25.0, 1.0, 100, 50)
add("lotus", 24.9, 1.0, 0, 0)
# beat2: 110.9-157.7 (Brahma, keputusan mengajar)
add("chandavaram", 23.0, 1.0, 0, 0)
add("sanchi", 23.8, 1.0, 80, 0)
# beat3: 157.7-217.6 (perjalanan, Upaka, kedatangan lima petapa)
add("borobudur12", 20.0, 1.0, 0, 40,
    [("Isipatana \u2014 Taman Rusa, Sarnath", "lt(t,5)")])
add("chiangmai", 20.0, 1.0, 160, 90)
add("ajatsatru", 19.9, 1.0, 160, 90)
# bumper: 217.6-227.1 (CTA 50%)
add("oil-lamps", 9.4, 1.0, 0, 0,
    [("Jejak Buddha", "lt(t,4)"), (CTA, "between(t,5,9.4)")])
# beat4: 227.1-285.7 (dua ekstrem + Jalan Tengah)
add("statue", 19.6, 1.0, 160, 90, [("Jalan Tengah", "lt(t,5)")])
add("vairochana", 19.6, 1.0, 0, 0)
add("borobudur19", 19.5, 1.0, 0, 0)
# beat5: 285.7-349.4 (Empat Kebenaran Mulia + Kondanna memahami)
add("candles", 21.2, 1.0, 160, 90, [("Empat Kebenaran Mulia", "lt(t,5)")])
add("bodhgaya", 21.2, 0.55, 0, 0, [("Kondanna Telah Memahami", "lt(t,5)")])
add("chiangmai", 21.3, 0.55, 50, 30)
# beat6: 349.4-394.3 (Sangha lahir, gaung khotbah)
add("flameless", 22.4, 1.0, 160, 90)
add("borobudur19b", 22.5, 1.0, 0, 0)
# beat7: 394.3-433.9 (penutup + CTA akhir)
add("sunrise", 19.8, 0.55, 160, 90)
add("golden-mist", 19.8, 0.55, 160, 90, [(CTA, "gte(t,10)")])

tot = sum(s[1] for s in SEGS)
print(f"SEGMEN: {len(SEGS)}, total {tot:.1f}s vs audio {adur:.1f}s", flush=True)
assert abs(tot - adur) < 0.5, "total segmen != durasi audio"

seg_files = []
for i, (slug, sd, sp, cx, cy, ovs) in enumerate(SEGS):
    out = os.path.join(D, f"seg{i:02d}.mp4")
    if os.path.exists(out) and abs(dur(out) - sd) <= 0.6:
        seg_files.append(out)
        print(f"[seg{i:02d}] {slug} sudah ada, lewati", flush=True)
        continue
    src = os.path.join(FT, FILES[slug])
    assert os.path.exists(src), src
    cd = dur(src)
    st = 1.0 / sp
    eff = cd / sp
    loops = math.ceil(sd / eff) + 1
    vf = (f"setpts={st:.4f}*PTS,scale=1440:810:force_original_aspect_ratio=increase,"
          f"crop=1280:720:{cx}:{cy},fps=30,")
    for text, en in ovs:
        vf += (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize=44:fontcolor=white:"
               f"borderw=3:bordercolor=black@0.85:x=(w-text_w)/2:y=h-150:"
               f"box=1:boxcolor=black@0.45:boxborderw=20:enable='{en}',")
    vf += "noise=alls=6:allf=t,format=yuv420p"
    r = subprocess.run([FQ, "-y", "-stream_loop", str(loops), "-i", src,
                        "-t", f"{sd:.2f}", "-vf", vf, "-r", "30",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                        "-pix_fmt", "yuv420p", "-an", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"SEG {i} FAILED:\n{r.stderr[-1200:]}")
        sys.exit(1)
    d2 = dur(out)
    if abs(d2 - sd) > 0.6:
        print(f"SEG {i} DURASI MELESET: target {sd:.1f}s real {d2:.1f}s")
        sys.exit(1)
    seg_files.append(out)
    print(f"[seg{i:02d}] {slug} {sd:.1f}s ok", flush=True)

lst = os.path.join(D, "segs.txt")
with open(lst, "w") as f:
    for p in seg_files:
        f.write(f"file '{p}'\n")
concat = os.path.join(D, "concat.mp4")
r = subprocess.run([FQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", concat],
                   capture_output=True, text=True)
if r.returncode != 0:
    print(f"CONCAT FAILED:\n{r.stderr[-900:]}"); sys.exit(1)

tmp = os.path.join(D, "final-temp.mp4")
final = os.path.join(D, "jejak-buddha-2026-10-20-upload.mp4")
r = subprocess.run([FQ, "-y", "-i", concat, "-i", VO, "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-movflags", "+faststart", tmp],
                   capture_output=True, text=True)
if r.returncode != 0:
    print(f"MUX FAILED:\n{r.stderr[-900:]}"); sys.exit(1)
vd, ad = dur(tmp), dur(VO)
print(f"TEMP dur: {vd:.1f}s (audio {ad:.1f}s)", flush=True)
assert abs(vd - ad) < 5, f"durasi meleset: video {vd:.1f} vs audio {ad:.1f}"
os.replace(tmp, final)
print(f"FINAL: {final} ({vd:.1f}s)", flush=True)
