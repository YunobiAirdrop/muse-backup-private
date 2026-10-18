#!/usr/bin/env python3
"""Single-pass assembly b16 (pola build_singlepass_b13.py).
Title card 2.5s + 74 gambar per durasi beat + segmen bumper (setelah beat 42)
+ drawtext overlay momen kunci (dari batches-b16.json) + CTA overlay di 50%
durasi + grain + vignette + mux VO. ffmpeg HANYA via ffmpeg-queue.sh.
Tulis ke TEMP dulu, verifikasi durasi, baru pindah ke final."""
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
if not os.path.exists(tc_png):
    from PIL import Image
    Image.new("RGB", (1280, 720), (10, 22, 40)).save(tc_png, "WEBP", quality=92)

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
print(f"total video: {total:.1f}s ({total/60:.2f} mnt)", flush=True)

lst = "/tmp/imglist_b16_sp.txt"
with open(lst, "w") as f:
    for img, d, _ in segs:
        f.write(f"file '{img}'\n")
        f.write(f"duration {d}\n")
    f.write(f"file '{segs[-1][0]}'\n")

def dt(text, s, e, fs=58, y="h-150", color="white"):
    return (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize={fs}:"
            f"fontcolor={color}:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y={y}:enable='between(t,{s:.2f},{e:.2f})'")

vf = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=black"
vf += "," + dt("7 FOODS THAT SHOULD NOT EXIST", 0, TC, fs=84, y="230")
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
assert not os.path.exists(final_out), "final sudah ada — jangan timpa tanpa backup!"
r = subprocess.run([Q, "-y", "-c:v", "webp", "-f", "concat", "-safe", "0", "-i", lst,
                    "-i", "audio/gabungan-2026-10-18.mp3",
                    "-filter_complex", f"[0:v]{vf}[v];[1:a]adelay=2500|2500,apad[a]",
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                    "-c:a", "aac", "-b:a", "128k",
                    "-t", str(total), "-movflags", "+faststart", tmp_out],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("FFMPEG ERR:", r.stderr[-800:]); sys.exit(1)
# verifikasi durasi sebelum pindah ke final
pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "csv=p=0", tmp_out], capture_output=True, text=True)
actual = float(pr.stdout.strip())
if abs(actual - total) > 5:
    print(f"DURASI GAGAL: expected {total:.1f}, got {actual:.1f} — final TIDAK ditimpa")
    sys.exit(2)
os.rename(tmp_out, final_out)
print(f"OK singlepass: {final_out} ({actual:.1f}s)", flush=True)
