#!/usr/bin/env python3
"""Resume perakitan video horor 2026-10-06 (lanjutan run 16:11 yang gagal).
- Validasi 11 segmen yang sudah ada (lewati yang valid), bangun yang hilang
- Pipeline RINGAN (scale 1280x720 langsung + preset veryfast) anti-OOM
- Semua ffmpeg lewat ffmpeg-queue.sh (maks 2 konkurensi)
- concat + mux audio -> video/2026-10-06.mp4
- overlay_teks.py -> video/2026-10-06-youtube.mp4
- potong 3 shorts (5s, 305s, 455s) -> shorts/2026-10-06-sN.mp4
"""
import subprocess, os, glob, shutil, sys

BASE = "/home/hatch/workspace/horor-otomatis"
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
GDIR = os.path.join(BASE, "gambar/2026-10-06")
AUDIO = os.path.join(BASE, "audio/2026-10-06.mp3")
DURS = os.path.join(BASE, "audio/2026-10-06.durations.txt")
TMPD = os.path.join(BASE, "video/_tmp_segs")
OUT = os.path.join(BASE, "video/2026-10-06.mp4")
OUTYT = os.path.join(BASE, "video/2026-10-06-youtube.mp4")
SHORTCUTS = [5, 305, 455]

def run(args, check=True, **kw):
    return subprocess.run(args, check=check, **kw)

def probe_dur(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True)
    return float(r.stdout.strip())

def seg_ok(path, expect_dur):
    if not os.path.exists(path) or os.path.getsize(path) < 50000:
        return False
    try:
        return abs(probe_dur(path) - expect_dur) < 0.5
    except Exception:
        return False

def kenburns_light(img, seg_dur, idx, out):
    """Pipeline ringan anti-OOM: scale 1280:720 langsung, preset veryfast."""
    total_frames = int(seg_dur * 30)
    mode = idx % 4
    if mode == 0:
        zp = f"zoompan=z='min(zoom+0.0012,1.25)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode == 1:
        zp = f"zoompan=z='min(zoom+0.0012,1.25)':d={total_frames}:x='(iw-iw/zoom)*on/{total_frames}':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode == 2:
        zp = f"zoompan=z='max(1.25-0.0012*on,1.0)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    else:
        zp = f"zoompan=z='min(zoom+0.0012,1.25)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{total_frames}':s=1280x720:fps=30"
    vf = (f"scale=1280:720,{zp},"
          "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
          "noise=alls=6:allf=t,"
          "vignette=PI/5")
    run([Q, "-y", "-loop", "1", "-i", img,
         "-vf", vf, "-t", str(seg_dur),
         "-c:v", "libx264", "-preset", "veryfast",
         "-pix_fmt", "yuv420p", "-r", "30", out],
        capture_output=True)

imgs = sorted(glob.glob(os.path.join(GDIR, "*.webp")))
durs = [float(x.strip()) for x in open(DURS) if x.strip()]
assert len(imgs) == len(durs) == 76, (len(imgs), len(durs))
os.makedirs(TMPD, exist_ok=True)
print(f"76 gambar, 76 beat, total {sum(durs):.0f}s", flush=True)

segs, dibuat = [], 0
for i, (img, seg_dur) in enumerate(zip(imgs, durs)):
    s = os.path.join(TMPD, f"s{i:02d}.mp4")
    if seg_ok(s, seg_dur):
        status = "skip"
    else:
        kenburns_light(img, seg_dur, i, s)
        if not seg_ok(s, seg_dur):
            print(f"GAGAL bangun segmen {i}", flush=True); sys.exit(1)
        status = "buat"; dibuat += 1
    segs.append(s)
    if status == "buat" or (i + 1) % 10 == 0:
        print(f"  {i+1}/76 {status}", flush=True)
print(f"Segmen selesai: {dibuat} baru, {76-dibuat} reuse", flush=True)

lst = os.path.join(TMPD, "list.txt")
with open(lst, "w") as f:
    for s in segs: f.write(f"file '{s}'\n")
concat = os.path.join(TMPD, "concat.mp4")
run([Q, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", concat],
    capture_output=True)
run([Q, "-y", "-i", concat, "-i", AUDIO,
     "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
     "-shortest", "-movflags", "+faststart", OUT], capture_output=True)
print(f"OK rakit: {OUT} ({probe_dur(OUT)/60:.1f} menit)", flush=True)

# Text overlay 5 momen kunci
env = dict(os.environ, PATH="/home/hatch/workspace/youtube-otomatis:" + os.environ["PATH"])
run([sys.executable, os.path.join(BASE, "overlay_teks.py"), OUT, OUTYT],
    check=True, env=env, capture_output=True)
print(f"OK overlay: {OUTYT} ({probe_dur(OUTYT)/60:.1f} menit)", flush=True)

# 3 shorts vertikal
for n, ss in enumerate(SHORTCUTS, 1):
    sout = os.path.join(BASE, f"shorts/2026-10-06-s{n}.mp4")
    run([Q, "-y", "-ss", str(ss), "-i", OUTYT, "-t", "45",
         "-vf", "crop=ih*9/16:ih,scale=720:1280",
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", sout], capture_output=True)
    print(f"OK shorts {n}: {sout} ({probe_dur(sout):.0f}s)", flush=True)

shutil.rmtree(TMPD)
print("SELESAI SEMUA", flush=True)
