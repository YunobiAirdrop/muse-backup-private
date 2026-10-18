#!/usr/bin/env python3
"""Rakit LONG Jejak Buddha 2026-10-18: Pencerahan di bawah pohon Bodhi (pool #5).
Footage Wikimedia Commons (lisensi aman, atribusi di deskripsi) + voiceover mudiwa.
1280x720 30fps + film grain. Render per-segmen via ffmpeg-queue.sh (resumable).
Bumper suara user sudah digabung di voiceover-full.mp3 setelah beat3."""
import subprocess, os, math, sys

D = "/home/hatch/workspace/jejak-buddha/2026-10-18"
FT = os.path.join(D, "footage")
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
VO = os.path.join(D, "audio", "voiceover-full.mp3")

FILES = {
    "bodhgaya-mahabodhi": "bodhgaya-mahabodhi.webm",
    "chandavaram-stupa": "chandavaram-stupa.webm",
    "sanchi-stupa": "sanchi-stupa.ogv",
    "chiangmai-temple": "chiangmai-temple.webm",
    "borobudur-2012": "borobudur-2012.ogv",
    "flameless-candle": "flameless-candle.webm",
    "oil-lamps-bodhgaya": "reused-oil-lamps-bodhgaya.webm",
    "candles-dolly": "reused-candles-dolly.ogv",
    "lotus-timelapse": "reused-lotus-timelapse.webm",
    "golden-mist": "reused-golden-mist.webm",
    "sunrise-drachenberg": "reused-sunrise-drachenberg.webm",
    "borobudur-2019": "reused-borobudur-2019.webm",
    "mountain-mist": "reused-mountain-mist.webm",
    "vairochana": "reused-vairochana.webm",
    "borobudur-2019-02": "reused-borobudur-2019-02.webm",
    "statue-buddha": "reused-statue-buddha.webm",
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

# beat0: 0-59.81 (cold open, serangan Mara)
add("mountain-mist", 20.0, 0.5, 100, 50)
add("candles-dolly", 20.0, 1.0, 160, 90)
add("golden-mist", 19.81, 1.0, 0, 0)
# beat1: 59.81-98.14 (perjalanan ke Bodh Gaya)
add("borobudur-2012", 19.16, 0.5, 80, 0, [("Bodh Gaya", "lt(t,5)")])
add("bodhgaya-mahabodhi", 19.17, 1.0, 160, 90)
# beat2: 98.14-152.67 (Mara + bhumisparsha)
add("chiangmai-temple", 27.26, 1.0, 160, 90,
    [("Bhumisparsha \u2014 Bumi Jadi Saksi", "lt(t,5)")])
add("sanchi-stupa", 13.64, 0.5, 80, 0)
add("chandavaram-stupa", 13.63, 1.0, 0, 0)
# beat3: 152.67-201.51 (tiga jaga malam)
add("lotus-timelapse", 24.42, 1.0, 0, 0, [("Tiga Pengetahuan", "lt(t,5)")])
add("statue-buddha", 24.42, 1.0, 160, 90)
# bumper: 201.51-210.94 (CTA 50% = 210.1 -> overlay di sini)
add("oil-lamps-bodhgaya", 9.43, 0.55, 0, 0,
    [("Jejak Buddha", "lt(t,4)"), (CTA, "between(t,6,9.4)")])
# beat4: 210.94-263.07 (Empat Kebenaran Mulia)
add("vairochana", 26.06, 1.0, 0, 0, [("Empat Kebenaran Mulia", "lt(t,5)")])
add("borobudur-2019-02", 26.07, 1.0, 160, 90)
# beat5: 263.07-326.24 (fajar pencerahan)
add("sunrise-drachenberg", 31.58, 0.5, 160, 90)
add("borobudur-2019", 12.70, 1.0, 0, 0)
add("flameless-candle", 4.00, 1.0, 160, 90)
add("candles-dolly", 14.89, 1.0, 50, 30)
# beat6: 326.24-366.25 (tujuh minggu + keputusan mengajar)
add("bodhgaya-mahabodhi", 20.00, 0.55, 0, 0)
add("chiangmai-temple", 20.01, 0.55, 50, 30)
# beat7: 366.25-420.19 (penutup + CTA akhir)
add("borobudur-2012", 27.00, 0.55, 0, 40)
add("golden-mist", 26.95, 0.55, 160, 90, [(CTA, "gte(t,17)")])

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
final = os.path.join(D, "jejak-buddha-2026-10-18-upload.mp4")
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
