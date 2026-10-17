#!/usr/bin/env python3
"""Build 3 shorts weird-en 2026-10-09 (SHORTS day).
s1: REBUILD dari gambar beat-001..005.webp (sudah benar, hasil regenerasi 8 Okt)
    + audio beats 1-10 — video 2026-10-07.mp4 di range ini masih gambar Emu War basi.
s2/s3: potong dari video/2026-10-07.mp4 (range terverifikasi bersih via cek frame).
Semua vertikal 9:16, 30fps, film grain anti-AI look.
"""
import os, subprocess, sys

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
VID = os.path.join(W, "video", "2026-10-07.mp4")
OUTD = os.path.join(W, "shorts")
TMPD = os.path.join(W, "video", "_tmp_segs")
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
os.makedirs(OUTD, exist_ok=True)

def run(args, label):
    print(f"[{label}] start", flush=True)
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[{label}] GAGAL:\n{r.stderr[-600:]}", flush=True)
        return False
    print(f"[{label}] OK", flush=True)
    return True

ok = True

# ---- s2 & s3: potong dari video (range bersih) ----
cuts = {
    "2026-10-07-s2.mp4": (414.4, 44.5),   # pistol shrimp
    "2026-10-07-s3.mp4": (190.6, 40.3),   # mantis shrimp punch
}
for out, (start, dur) in cuts.items():
    ok &= run([Q, "-y", "-ss", str(start), "-t", str(dur), "-i", VID,
        "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-r", "30", "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", os.path.join(OUTD, out)], "cut-" + out)

# ---- s1: rebuild dari gambar + audio ----
# audio: concat beats 1-10
lst = os.path.join(TMPD, "s1-concat.txt")
with open(lst, "w") as f:
    for i in range(1, 11):
        f.write(f"file '{os.path.join(W, 'audio', f'w7-beat-{i:03d}.mp3')}'\n")
s1a = os.path.join(TMPD, "s1-audio.mp3")
r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c:a", "libmp3lame", "-b:a", "128k", s1a],
                   capture_output=True, text=True)
if r.returncode != 0 or not os.path.exists(s1a):
    print("[s1-audio] GAGAL:\n" + r.stderr[-400:], flush=True); ok = False
else:
    print("[s1-audio] OK", flush=True)

# video: 5 gambar loop sesuai durasi grup + overlay + grain
segs = [("beat-001.webp", 10.05), ("beat-002.webp", 9.66), ("beat-003.webp", 5.90),
        ("beat-004.webp", 8.30), ("beat-005.webp", 8.85)]
if ok:
    args = [Q, "-y"]
    for img, dur in segs:
        args += ["-framerate", "30", "-loop", "1", "-t", str(dur),
                 "-i", os.path.join(W, "gambar", img)]
    args += ["-i", s1a]
    n = len(segs)
    vcat = "".join(f"[{i}:v]" for i in range(n)) + f"concat=n={n}:v=1:a=0"
    dt = (f"drawtext=fontfile={FONT}:text='SURVIVED OUTER SPACE':fontsize=64:"
          f"fontcolor=white:borderw=3:bordercolor=black@0.9:"
          f"x=(w-text_w)/2:y=200:box=1:boxcolor=black@0.5:boxborderw=20:"
          f"enable='between(t,10.05,12.25)'")
    vf = (f"{vcat},scale=720:1280:force_original_aspect_ratio=increase,"
          f"crop=720:1280,{dt},noise=alls=6:allf=t,format=yuv420p[v]")
    args += ["-filter_complex", vf, "-map", "[v]", f"-map", f"{n}:a",
             "-c:v", "libx264", "-preset", "veryfast", "-r", "30",
             "-c:a", "aac", "-b:a", "128k", "-shortest",
             "-movflags", "+faststart", os.path.join(OUTD, "2026-10-07-s1.mp4")]
    ok &= run(args, "build-s1")

# ---- verifikasi akhir ----
for f in ["2026-10-07-s1.mp4", "2026-10-07-s2.mp4", "2026-10-07-s3.mp4"]:
    p = os.path.join(OUTD, f)
    if os.path.exists(p):
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip().replace("\n", " ")
        print(f"VERIFY {f}: {d} size={os.path.getsize(p)}", flush=True)
    else:
        print(f"VERIFY {f}: HILANG!", flush=True); ok = False

sys.exit(0 if ok else 1)
