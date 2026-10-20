#!/usr/bin/env python3
"""Two-pass assembly w20 (weird-en 2026-10-20) — pola build_twopass_b16.py (2026-10-18):
- Pass 1: imglist -> concat -> scale,pad,format -> intermediate, -preset ultrafast
  (JANGAN veryfast: B-frames+lookahead merusak timestamp input VFR still-image).
- Pass 2: intermediate + audio -> drawtext overlay + CTA + noise(grain) + vignette -> final.
- File kerja di WORKSPACE (bukan /tmp). Tulis TEMP, verifikasi PER STREAM, baru pindah.
- drawtext: TANPA '%', TANPA apostrof, ':' di-escape."""
import json, os, subprocess, sys

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
N = 74
BUMPER_AFTER = 28
TC = 2.5
PRESET = "ultrafast"  # WAJIB ultrafast untuk still-image concat (lihat AGENTS.md)

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

os.chdir(W)
os.makedirs("_tmp_build", exist_ok=True)
dj = json.load(open("data/durasi-beat-2026-10-20.json"))
batches = json.load(open("data/batches-w20.json"))
ov_by_beat = {}
for b in batches.values():
    for e in b:
        if "overlay" in e:
            ov_by_beat[int(e["num"])] = e["overlay"]

tc_png = os.path.join(W, "_tmp_build", "titlecard_w20.webp")
if not os.path.exists(tc_png):
    from PIL import Image
    Image.new("RGB", (1280, 720), (10, 22, 40)).save(tc_png, "WEBP", quality=92)

segs = [(tc_png, TC, "titlecard")]
for i in range(1, N + 1):
    k = f"w20-beat-{i:03d}"
    img = os.path.join(W, "gambar", "w20", f"{k}.webp")
    assert os.path.exists(img), f"gambar hilang: {img}"
    segs.append((img, float(dj[k]), k))
    if i == BUMPER_AFTER:
        segs.append((os.path.join(W, "gambar", "w20", "w20-bumper.webp"),
                     float(dj["w20-bumper"]), "w20-bumper"))

starts, cum = {}, TC
for img, d, key in segs[1:]:
    starts[key] = cum
    cum += d
total = sum(d for _, d, _ in segs)
print(f"total expected: {total:.1f}s ({total/60:.2f} mnt)", flush=True)

lst = os.path.join(W, "_tmp_build", "imglist_w20.txt")
with open(lst, "w") as f:
    for img, d, _ in segs:
        f.write(f"file '{img}'\n")
        f.write(f"duration {d}\n")
    f.write(f"file '{segs[-1][0]}'\n")

def dt(text, s, e, fs=58, y="h-150", color="white"):
    return (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize={fs}:"
            f"fontcolor={color}:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y={y}:enable='between(t,{s:.2f},{e:.2f})'")

def stream_durs(path):
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                         "stream=codec_type,duration", "-of", "csv=p=0", path],
                        capture_output=True, text=True)
    durs = {}
    for l in pr.stdout.strip().split("\n"):
        if "," in l:
            c, d = l.split(",")
            durs[c] = float(d)
    return durs

# ---------- PASS 1: intermediate ----------
inter = os.path.join(W, "_tmp_build", "w20_intermediate.mp4")
if os.path.exists(inter):
    os.remove(inter)
r = subprocess.run([Q, "-y", "-c:v", "webp", "-f", "concat", "-safe", "0",
                    "-i", lst,
                    "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,"
                           "pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p",
                    "-c:v", "libx264", "-preset", PRESET, "-crf", "18",
                    inter], capture_output=True, text=True)
if r.returncode != 0:
    print("PASS1 ERR:", r.stderr[-800:]); sys.exit(1)
durs = stream_durs(inter)
print("pass1 streams:", durs, flush=True)
if abs(durs.get("video", 0) - total) > 2:
    print("PASS1 DURASI GAGAL"); sys.exit(2)
print("PASS1 OK", flush=True)

# ---------- PASS 2: overlays + audio ----------
vf = dt("7 WORLD RECORDS", 0, TC, fs=84, y="230")
vf += "," + dt("TOO WEIRD TO BE LEGAL", 0, TC, fs=52, y="380", color="yellow")
vf += "," + dt("Weird World Daily", 0, TC, fs=44, y="510")
for beat in sorted(ov_by_beat):
    s = starts[f"w20-beat-{beat:03d}"]
    e = s + float(dj[f"w20-beat-{beat:03d}"])
    vf += "," + dt(ov_by_beat[beat], s, e, fs=56)
mid = total / 2
vf += "," + dt("SUBSCRIBE!", mid, mid + 3.0, fs=72)
vf += "," + dt("SUBSCRIBE!", total - 3.0, total, fs=72)
bs = starts["w20-bumper"]
vf += "," + dt("WEIRD WORLD DAILY", bs, bs + 3.0, fs=64, y="h-110")
vf += ",noise=alls=6:allf=t,vignette=PI/5,format=yuv420p"

tmp_out = os.path.join(W, "video", "2026-10-20-final-TEMP.mp4")
final_out = os.path.join(W, "video", "2026-10-20-final.mp4")
r = subprocess.run([Q, "-y", "-i", inter, "-i", "audio/gabungan-2026-10-20.mp3",
                    "-filter_complex", f"[0:v]{vf}[v];[1:a]adelay=2500|2500,apad[a]",
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", PRESET, "-crf", "21",
                    "-c:a", "aac", "-b:a", "128k",
                    "-t", str(total), "-movflags", "+faststart", tmp_out],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("PASS2 ERR:", r.stderr[-800:]); sys.exit(1)

durs = stream_durs(tmp_out)
print("pass2 streams:", durs, flush=True)
if not all(abs(d - total) < 5 for d in durs.values()):
    print(f"DURASI STREAM GAGAL: {durs} vs expected {total:.1f} — final TIDAK ditimpa")
    sys.exit(2)
os.rename(tmp_out, final_out)
print(f"OK twopass: {final_out}", flush=True)
