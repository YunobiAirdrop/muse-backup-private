#!/usr/bin/env python3
"""Rakit LONG Jejak Buddha 2026-10-15: Pertapaan dan Jalan Tengah.
Footage Wikimedia Commons (lisensi aman, atribusi di deskripsi) + voiceover mudiwa.
1280x720 30fps + film grain. Render per-segmen via ffmpeg-queue.sh (resumable).
Bumper suara user disisipkan setelah beat3 (jeda natural)."""
import subprocess, os, math, sys

D = "/home/hatch/workspace/jejak-buddha/2026-10-15"
FT = os.path.join(D, "footage")
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-jejakbuddha.wav"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def esc(t):
    return t.replace(":", "\\:").replace("'", "\u2019").replace(",", "\\,")

beats = [dur(os.path.join(D, "audio", f"beat{i}.mp3")) for i in range(8)]
bdur = dur(BUMPER)
print("beats:", [f"{b:.1f}" for b in beats], "bumper:", f"{bdur:.1f}", flush=True)

def ft(slug):
    p = [os.path.join(FT, f) for f in os.listdir(FT) if f.startswith(slug + ".")]
    assert p, slug
    return sorted(p)[0]

CTA = "Subscribe Jejak Buddha"
# (slug, dur_seg, slowmo_sp, crop_x, crop_y, overlays)
# overlays: list of (text, enable_expr)
SEGS = []
def add(slug, sd, sp, cx, cy, ovs=None):
    SEGS.append((slug, round(sd, 2), sp, cx, cy, ovs or []))

# beat0 (hook, ~120s): sungai + kabut
h = beats[0] / 4
add("golden-mist", h, 1.0, 0, 0, [("Enam Tahun Pertapaan", "lt(t,4)")])
add("cosumnes-river", h, 0.7, 160, 90)
add("wallowa-river", h, 0.5, 160, 90)
add("mountain-mist", beats[0] - 3 * h, 0.5, 160, 90)

# beat1 (dua guru, ~62s)
h = beats[1] / 2
add("mountain-mist", h, 0.55, 100, 50, [("Alara Kalama \u2014 Uddaka Ramaputta", "lt(t,4)")])
add("running-stream", beats[1] - h, 0.75, 160, 90)

# beat2 (pertapaan keras, ~63s)
h = beats[2] / 2
add("stream-flowing", h, 1.0, 80, 0)
add("bidibidi-stream", beats[2] - h, 0.5, 0, 0)

# beat3 (ambang kematian + kenangan, ~60s)
h = beats[3] / 2
add("yogya-sunrise1", h, 1.0, 160, 90)
# CTA 50%: absolut 50% dari total audio ada di segmen ini (t relatif dihitung di bawah)
add("cosumnes-river", beats[3] - h, 0.7, 50, 30, [(CTA, "between(t,8,12)")])

# bumper (tengah, jeda natural)
add("candles-dolly", bdur, 1.0, 160, 90, [("Jejak Buddha", "lt(t,4)")])

# beat4 (Sujata, ~74s)
add("yogya-sunrise1", 30.0, 1.0, 0, 0, [("Nasi Susu Sujata", "lt(t,4)")])  # pakai ke-2, crop beda
add("candles-dolly", (beats[4] - 30.0) / 2, 1.0, 50, 30)
add("white-candle", beats[4] - 30.0 - (beats[4] - 30.0) / 2, 1.0, 40, 0)

# beat5 (jalan tengah, ~61s)
h = beats[5] / 2
add("lotus-timelapse", h, 1.0, 0, 0, [("Jalan Tengah", "lt(t,4)")])
add("statue-buddha", beats[5] - h, 1.0, 160, 90)

# beat6 (Bodh Gaya, ~62s)
h = beats[6] / 2
add("vairochana", h, 1.0, 0, 0)
add("borobudur-2019-02", beats[6] - h, 1.0, 160, 90)

# beat7 (penutup, ~58s)
h = beats[7] / 2
add("borobudur-2019", h, 1.0, 160, 90)
add("sunrise-drachenberg", beats[7] - h, 1.0, 160, 90, [(CTA, f"gte(t,{beats[7]-h-10:.1f})")])

seg_files = []
for i, (slug, sd, sp, cx, cy, ovs) in enumerate(SEGS):
    out = os.path.join(D, f"seg{i:02d}.mp4")
    if os.path.exists(out) and abs(dur(out) - sd) <= 0.6:
        seg_files.append(out)
        print(f"[seg{i:02d}] {slug} sudah ada, lewati", flush=True)
        continue
    src = ft(slug)
    cd = dur(src)
    st = 1.0 / sp
    eff = cd / sp
    loops = math.ceil(sd / eff) + 1
    vf = f"setpts={st:.4f}*PTS,scale=1440:810:force_original_aspect_ratio=increase,crop=1280:720:{cx}:{cy},fps=30,"
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

# audio full: beat0-3 + bumper + beat4-7
VO = os.path.join(D, "audio", "voiceover-full.mp3")
if not os.path.exists(VO):
    inputs = []
    for i in range(4): inputs += ["-i", os.path.join(D, "audio", f"beat{i}.mp3")]
    inputs += ["-i", BUMPER]
    for i in range(4, 8): inputs += ["-i", os.path.join(D, "audio", f"beat{i}.mp3")]
    fc = "".join(f"[{k}:a]aresample=44100[aa{k}];" for k in range(9))
    fc += "".join(f"[aa{k}]" for k in range(9)) + "concat=n=9:v=0:a=1[aout]"
    r = subprocess.run([FQ, "-y"] + inputs + ["-filter_complex", fc, "-map", "[aout]",
                        "-c:a", "libmp3lame", "-b:a", "128k", VO],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"AUDIO FAILED:\n{r.stderr[-900:]}"); sys.exit(1)
print(f"AUDIO dur: {dur(VO):.1f}s", flush=True)

# mux ke TEMP dulu, verifikasi durasi, baru move ke final
tmp = os.path.join(D, "final-temp.mp4")
final = os.path.join(D, "jejak-buddha-2026-10-15-upload.mp4")
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
