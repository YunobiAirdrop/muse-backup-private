#!/usr/bin/env python3
"""Single-pass assembly b12 (kontingensi antrean ffmpeg padat; pola build_singlepass b10).
Satu akuisisi antrean: title card 2.5s (frame solid + drawtext) + slideshow 73 gambar
dengan durasi per beat + drawtext overlay terjadwal + grain + vignette + mux VO (adelay 2.5s).
Output: video/2026-10-12-singlepass.mp4 (TIDAK menimpa -final; lihat laporan).
ffmpeg HANYA via ffmpeg-queue.sh."""
import json, os, subprocess, sys

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
N = 73

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

os.chdir(W)
dj = json.load(open("data/durasi-beat-2026-10-12.json"))
batches = json.load(open("data/batches-b12.json"))
overlays = {}
for b in batches.values():
    for e in b:
        if e.get("overlay"):
            overlays[int(e["num"])] = e["overlay"]
overlays[36] = "11-METER CRYSTALS"          # koreksi brief
overlays[68] = "THE WINNER: SALAR DE UYUNI"  # overlay verdict
overlays[55] = "THE WORLDS LARGEST MIRROR"  # apostrof dibuang: parser filtergraph

# title card frame: PNG solid gelap via PIL
tc_png = "/tmp/titlecard_b12.webp"
if not os.path.exists(tc_png):
    from PIL import Image
    Image.new("RGB", (1280, 720), (10, 22, 40)).save(tc_png, "WEBP", quality=92)

# daftar gambar + durasi (title card dulu 2.5s)
starts = {}
cum = 2.5
with open("/tmp/imglist_b12_sp.txt", "w") as f:
    f.write(f"file '{tc_png}'\n")
    f.write("duration 2.5\n")
    for i in range(1, N + 1):
        k = f"b12-beat-{i:03d}"
        starts[i] = cum
        f.write(f"file '{W}/gambar/{k}.webp'\n")
        f.write(f"duration {dj[k]}\n")
        cum += float(dj[k])
    f.write(f"file '{W}/gambar/b12-beat-{N:03d}.webp'\n")
total = cum
print(f"total video: {total:.1f}s", flush=True)

def dt(text, s, e, fs=58, y="h-150", color="white"):
    return (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize={fs}:"
            f"fontcolor={color}:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y={y}:enable='between(t,{s:.2f},{e:.2f})'")

vf = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=black"
# title card texts (0 - 2.5s)
vf += "," + dt("PLACES THAT LOOK FAKE", 0, 2.5, fs=92, y="230")
vf += "," + dt("7 PLACES ON EARTH", 0, 2.5, fs=64, y="360", color="yellow")
vf += "," + dt("Weird World Daily", 0, 2.5, fs=44, y="500")
# overlays per beat
for beat, text in sorted(overlays.items()):
    s = starts[beat]
    e = s + (3.0 if beat == 37 else float(dj[f"b12-beat-{beat:03d}"]))
    vf += "," + dt(text, s, e)
vf += ",noise=alls=6:allf=t,vignette=PI/5,format=yuv420p"

out = os.path.join(W, "video", sys.argv[1] if len(sys.argv) > 1 else "2026-10-12-singlepass.mp4")
r = subprocess.run([Q, "-y", "-f", "concat", "-safe", "0", "-i", "/tmp/imglist_b12_sp.txt",
                    "-i", "audio/gabungan-2026-10-12.mp3",
                    "-filter_complex", f"[0:v]{vf}[v];[1:a]adelay=2500|2500,apad[a]",
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                    "-c:a", "aac", "-b:a", "128k",
                    "-t", str(total), "-movflags", "+faststart", out],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("FFMPEG ERR:", r.stderr[-800:]); sys.exit(1)
print("OK singlepass:", out)
