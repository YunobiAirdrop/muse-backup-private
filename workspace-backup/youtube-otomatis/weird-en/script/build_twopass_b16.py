#!/usr/bin/env python3
"""Two-pass assembly b16 FIX (2026-10-18): single-pass memberi timestamp video
NGACO (demuxer concat + filter_complex: durasi segmen bergeser, video 629.84s
vs audio 636.29s, A/V tidak sinkron). Two-pass:
  Pass 1: imglist -> concat -> fps=30,scale,pad -> intermediate CFR (terverifikasi).
  Pass 2: intermediate + audio -> drawtext overlay + CTA + noise + vignette -> final.
Tulis ke TEMP, verifikasi durasi PER STREAM, baru pindah ke final."""
import json, os, subprocess, sys

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
N = 74
BUMPER_AFTER = 28
TC = 2.5

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

os.chdir(W)
dj = json.load(open("data/durasi-beat-2026-10-18.json"))
batches = json.load(open("data/batches-b16.json"))
ov_by_beat = {}
for b in batches.values():
    for e in b:
        if "overlay" in e:
            ov_by_beat[int(e["num"])] = e["overlay"]

tc_png = "/tmp/titlecard_b16.webp"
assert os.path.exists(tc_png), "titlecard hilang"

segs = [(tc_png, TC, "titlecard")]
for i in range(1, N + 1):
    k = f"b16-beat-{i:03d}"
    img = os.path.join(W, "gambar", f"{k}.webp")
    assert os.path.exists(img), f"gambar hilang: {img}"
    segs.append((img, float(dj[k]), k))
    if i == BUMPER_AFTER:
        segs.append((os.path.join(W, "gambar", "b16-bumper.webp"),
                     float(dj["b16-bumper"]), "b16-bumper"))

starts, cum = {}, TC
for img, d, key in segs[1:]:
    starts[key] = cum
    cum += d
total = sum(d for _, d, _ in segs)
print(f"total expected: {total:.1f}s ({total/60:.2f} mnt)", flush=True)

lst = "/tmp/imglist_b16_fix.txt"
with open(lst, "w") as f:
    for img, d, _ in segs:
        f.write(f"file '{img}'\n")
        f.write(f"duration {d}\n")
    f.write(f"file '{segs[-1][0]}'\n")

def dt(text, s, e, fs=58, y="h-150", color="white"):
    return (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize={fs}:"
            f"fontcolor={color}:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y={y}:enable='between(t,{s:.2f},{e:.2f})'")

# ---------- PASS 1: intermediate CFR ----------
inter = "/tmp/b16_intermediate.mp4"
if not os.path.exists(inter):
    r = subprocess.run([Q, "-y", "-c:v", "webp", "-f", "concat", "-safe", "0",
                        "-i", lst,
                        "-vf", "fps=30,scale=1280:720:force_original_aspect_ratio=decrease,"
                               "pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                        inter], capture_output=True, text=True)
    if r.returncode != 0:
        print("PASS1 ERR:", r.stderr[-800:]); sys.exit(1)
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                         "stream=codec_type,duration", "-of", "csv=p=0", inter],
                        capture_output=True, text=True)
    vdur = float([l for l in pr.stdout.strip().split("\n") if l.startswith("video")][0].split(",")[1])
    print(f"pass1 video duration: {vdur:.2f}s (expected {total:.2f})", flush=True)
    if abs(vdur - total) > 2:
        print("PASS1 DURASI GAGAL"); sys.exit(2)
    print("PASS1 OK", flush=True)
else:
    print("pass1 intermediate sudah ada, dilewati", flush=True)

# ---------- PASS 2: overlays + audio ----------
vf = dt("7 FOODS THAT SHOULD NOT EXIST", 0, TC, fs=84, y="230")
vf += "," + dt("RANKED BY WEIRDNESS", 0, TC, fs=52, y="380", color="yellow")
vf += "," + dt("Weird World Daily", 0, TC, fs=44, y="510")
for beat in sorted(ov_by_beat):
    s = starts[f"b16-beat-{beat:03d}"]
    e = s + float(dj[f"b16-beat-{beat:03d}"])
    vf += "," + dt(ov_by_beat[beat], s, e, fs=56)
mid = total / 2
vf += "," + dt("SUBSCRIBE!", mid, mid + 3.0, fs=72)
vf += "," + dt("SUBSCRIBE!", total - 3.0, total, fs=72)
bs = starts["b16-bumper"]
vf += "," + dt("WEIRD WORLD DAILY", bs, bs + 3.0, fs=64, y="h-110")
vf += ",noise=alls=6:allf=t,vignette=PI/5,format=yuv420p"

tmp_out = os.path.join(W, "video", "2026-10-18-final-TEMP.mp4")
final_out = os.path.join(W, "video", "2026-10-18-final.mp4")
r = subprocess.run([Q, "-y", "-i", inter, "-i", "audio/gabungan-2026-10-18.mp3",
                    "-filter_complex", f"[0:v]{vf}[v];[1:a]adelay=2500|2500,apad[a]",
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                    "-c:a", "aac", "-b:a", "128k",
                    "-t", str(total), "-movflags", "+faststart", tmp_out],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("PASS2 ERR:", r.stderr[-800:]); sys.exit(1)

# verifikasi PER STREAM
pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                     "stream=codec_type,duration", "-of", "csv=p=0", tmp_out],
                    capture_output=True, text=True)
durs = {}
for l in pr.stdout.strip().split("\n"):
    c, d = l.split(",")
    durs[c] = float(d)
print("stream durations:", durs, flush=True)
ok = all(abs(d - total) < 5 for d in durs.values())
if not ok:
    print(f"DURASI STREAM GAGAL: {durs} vs expected {total:.1f} — final TIDAK ditimpa")
    sys.exit(2)
os.rename(tmp_out, final_out)
print(f"OK twopass: {final_out}", flush=True)
