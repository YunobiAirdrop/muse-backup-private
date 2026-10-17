#!/usr/bin/env python3
"""Single-pass assembly b13 (pola build_singlepass_b12.py, preseden 10 Okt).
Title card 2.5s + 74 gambar per durasi beat + segmen bumper (setelah beat 59)
+ drawtext overlay momen kunci + CTA overlay di 50% durasi + grain + vignette + mux VO.
ffmpeg HANYA via ffmpeg-queue.sh. TANPA '%' di teks drawtext."""
import json, os, subprocess, sys

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
N = 74
BUMPER_AFTER = 59

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

os.chdir(W)
dj = json.load(open("data/durasi-beat-2026-10-13.json"))

# overlay momen kunci: beat -> (teks, durasi khusus detik | None=sepanjang beat)
OV = {
    1: ("A WAVE OF MOLASSES KILLED 21 PEOPLE", 4.0),
    17: ("MEAT FELL FROM A CLEAR SKY", None),
    26: ("A 15-FOOT WAVE OF BEER", None),
    36: ("25 FEET TALL, 35 MILES AN HOUR", None),
    39: ("SUBSCRIBE!", 3.0),
    53: ("80 MILLION TREES FLATTENED", None),
    70: ("THE CHAMPION: MOLASSES FLOOD", None),
    74: ("STAY WEIRD!", None),
}

tc_png = "/tmp/titlecard_b13.webp"
if not os.path.exists(tc_png):
    from PIL import Image
    Image.new("RGB", (1280, 720), (10, 22, 40)).save(tc_png, "WEBP", quality=92)

segs = [(tc_png, 2.5, "titlecard")]
for i in range(1, N + 1):
    k = f"b13-beat-{i:03d}"
    img = os.path.join(W, "gambar", f"{k}.webp")
    assert os.path.exists(img), f"gambar hilang: {img}"
    segs.append((img, float(dj[k]), k))
    if i == BUMPER_AFTER:
        bimg = os.path.join(W, "gambar", "b13-bumper.webp")
        assert os.path.exists(bimg), "gambar bumper hilang"
        segs.append((bimg, float(dj["b13-bumper"]), "b13-bumper"))

starts, cum = {}, 2.5
for img, d, key in segs[1:]:
    starts[key] = cum
    cum += d
total = cum + 2.5 - 2.5  # segs sudah termasuk offset titlecard
total = sum(d for _, d, _ in segs)
print(f"total video: {total:.1f}s ({total/60:.2f} mnt)", flush=True)

lst = "/tmp/imglist_b13_sp.txt"
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
vf += "," + dt("THE WEIRDNESS FACE-OFF", 0, 2.5, fs=84, y="230")
vf += "," + dt("7 TIMES HISTORY WENT BONKERS", 0, 2.5, fs=56, y="370", color="yellow")
vf += "," + dt("Weird World Daily", 0, 2.5, fs=44, y="500")
for beat, (text, od) in sorted(OV.items()):
    s = starts[f"b13-beat-{beat:03d}"]
    e = s + (od if od else float(dj[f"b13-beat-{beat:03d}"]))
    vf += "," + dt(text, s, e, fs=64 if beat in (39,) else 56)
# CTA overlay tepat di 50% durasi (verbal CTA ada di beat 39, ~di titik ini)
mid = total / 2
vf += "," + dt("SUBSCRIBE!", mid, mid + 3.0, fs=72)
# overlay bumper: nama channel lower-third 3 detik pertama segmen bumper
bs = starts["b13-bumper"]
vf += "," + dt("WEIRD WORLD DAILY", bs, bs + 3.0, fs=64, y="h-110")
vf += ",noise=alls=6:allf=t,vignette=PI/5,format=yuv420p"

out = os.path.join(W, "video", sys.argv[1] if len(sys.argv) > 1 else "2026-10-13-final.mp4")
r = subprocess.run([Q, "-y", "-c:v", "webp", "-f", "concat", "-safe", "0", "-i", lst,
                    "-i", "audio/gabungan-2026-10-13.mp3",
                    "-filter_complex", f"[0:v]{vf}[v];[1:a]adelay=2500|2500,apad[a]",
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                    "-c:a", "aac", "-b:a", "128k",
                    "-t", str(total), "-movflags", "+faststart", out],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("FFMPEG ERR:", r.stderr[-800:]); sys.exit(1)
print("OK singlepass:", out, flush=True)
