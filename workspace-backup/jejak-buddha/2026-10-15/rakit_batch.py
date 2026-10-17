#!/usr/bin/env python3
"""Rakit-batch Jejak Buddha 2026-10-15: seg00 sudah jadi (per-segmen).
Sisa seg01-19 dirender dalam 2 batch single-pass (hemat antrean queue),
lalu concat + audio + mux. Semua via ffmpeg-queue.sh."""
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

def ft(slug):
    p = [os.path.join(FT, f) for f in os.listdir(FT) if f.startswith(slug + ".")]
    assert p, slug
    return sorted(p)[0]

CTA = "Subscribe Jejak Buddha"
SEGS = []
def add(slug, sd, sp, cx, cy, ovs=None):
    SEGS.append((slug, round(sd, 2), sp, cx, cy, ovs or []))

h = beats[0] / 4
add("golden-mist", h, 1.0, 0, 0, [("Enam Tahun Pertapaan", "lt(t,4)")])
add("cosumnes-river", h, 0.7, 160, 90)
add("wallowa-river", h, 0.5, 160, 90)
add("mountain-mist", beats[0] - 3 * h, 0.5, 160, 90)
h = beats[1] / 2
add("mountain-mist", h, 0.55, 100, 50, [("Alara Kalama \u2014 Uddaka Ramaputta", "lt(t,4)")])
add("running-stream", beats[1] - h, 0.75, 160, 90)
h = beats[2] / 2
add("stream-flowing", h, 1.0, 80, 0)
add("bidibidi-stream", beats[2] - h, 0.5, 0, 0)
h = beats[3] / 2
add("yogya-sunrise1", h, 1.0, 160, 90)
add("cosumnes-river", beats[3] - h, 0.7, 50, 30, [(CTA, "between(t,8,12)")])
add("candles-dolly", bdur, 1.0, 160, 90, [("Jejak Buddha", "lt(t,4)")])
add("yogya-sunrise1", 30.0, 1.0, 0, 0, [("Nasi Susu Sujata", "lt(t,4)")])
add("candles-dolly", (beats[4] - 30.0) / 2, 1.0, 50, 30)
add("white-candle", beats[4] - 30.0 - (beats[4] - 30.0) / 2, 1.0, 40, 0)
h = beats[5] / 2
add("lotus-timelapse", h, 1.0, 0, 0, [("Jalan Tengah", "lt(t,4)")])
add("statue-buddha", beats[5] - h, 1.0, 160, 90)
h = beats[6] / 2
add("vairochana", h, 1.0, 0, 0)
add("borobudur-2019-02", beats[6] - h, 1.0, 160, 90)
h = beats[7] / 2
add("borobudur-2019", h, 1.0, 160, 90)
add("sunrise-drachenberg", beats[7] - h, 1.0, 160, 90, [(CTA, f"gte(t,{beats[7]-h-10:.1f})")])

assert len(SEGS) == 20, len(SEGS)

def render_batch(idxs, out):
    target = sum(SEGS[i][1] for i in idxs)
    if os.path.exists(out) and abs(dur(out) - target) <= 1.5:
        print(f"batch {out} sudah ada, lewati", flush=True)
        return
    args = [FQ, "-y"]
    for gi, i in enumerate(idxs):
        slug, sd, sp, cx, cy, ovs = SEGS[i]
        src = ft(slug)
        cd = dur(src)
        loops = math.ceil(sd / (cd / sp)) + 1
        args += ["-stream_loop", str(loops), "-i", src]
    fc = ""
    for gi, i in enumerate(idxs):
        slug, sd, sp, cx, cy, ovs = SEGS[i]
        st = 1.0 / sp
        chain = (f"[{gi}:v]setpts={st:.4f}*PTS,"
                 f"scale=1440:810:force_original_aspect_ratio=increase,"
                 f"crop=1280:720:{cx}:{cy},fps=30,")
        for text, en in ovs:
            chain += (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize=44:"
                      f"fontcolor=white:borderw=3:bordercolor=black@0.85:"
                      f"x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.45:"
                      f"boxborderw=20:enable='{en}',")
        chain += (f"trim=duration={sd:.2f},setpts=PTS-STARTPTS,"
                  f"noise=alls=6:allf=t,format=yuv420p[v{gi}];")
        fc += chain
    fc += "".join(f"[v{gi}]" for gi in range(len(idxs)))
    fc += f"concat=n={len(idxs)}:v=1:a=0[vout]"
    r = subprocess.run(args + ["-filter_complex", fc, "-map", "[vout]", "-r", "30",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                               "-pix_fmt", "yuv420p", "-an", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"BATCH {out} FAILED:\n{r.stderr[-1500:]}")
        sys.exit(1)
    d2 = dur(out)
    print(f"batch {out}: {d2:.1f}s (target {target:.1f}s)", flush=True)
    assert abs(d2 - target) <= 1.5, "durasi batch meleset"

b1 = os.path.join(D, "batch1.mp4")
b2 = os.path.join(D, "batch2.mp4")
render_batch(list(range(1, 11)), b1)
render_batch(list(range(11, 20)), b2)

lst = os.path.join(D, "segs.txt")
with open(lst, "w") as f:
    f.write(f"file '{os.path.join(D, 'seg00.mp4')}'\n")
    f.write(f"file '{b1}'\n")
    f.write(f"file '{b2}'\n")
concat = os.path.join(D, "concat.mp4")
r = subprocess.run([FQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, text=True)
if r.returncode != 0:
    print(f"CONCAT FAILED:\n{r.stderr[-900:]}"); sys.exit(1)

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
