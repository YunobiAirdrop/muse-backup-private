#!/usr/bin/env python3
"""Rakit video horor harian 2026-10-10 (pola resume_rakit_20261006.py).
- 76 gambar b001..b076.webp, durasi dari audio/2026-10-10.durations.txt
- Pipeline RINGAN: scale 1280x720 langsung, veryfast, crf 20, noise grain + vignette
- Semua ffmpeg lewat ffmpeg-queue.sh (maks 2 konkurensi, anti-OOM)
- concat + mux audio -> video/2026-10-10.mp4
- text overlay 5 momen -> video/2026-10-10-youtube.mp4 (audio copy, faststart)
"""
import subprocess, os, glob, shutil, sys

BASE = "/home/hatch/workspace/horor-otomatis"
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
GDIR = os.path.join(BASE, "gambar/2026-10-10")
AUDIO = os.path.join(BASE, "audio/2026-10-10.mp3")
DURF = os.path.join(BASE, "audio/2026-10-10.durations.txt")
TMPD = os.path.join(BASE, "video/_tmp_segs_20261010")
OUT = os.path.join(BASE, "video/2026-10-10.mp4")
OUTYT = os.path.join(BASE, "video/2026-10-10-youtube.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (teks, nomor beat 1-indexed)
OVERLAYS = [
    ("NAMA SENDIRI DI DAFTAR KORBAN", 1),
    ("SUSTER TANPA KAKI", 14),
    ("DIA MENYELAMATKAN PASIEN", 27),
    ("AKU MENINGGAL 2004?", 45),
    ("GANTIAN JAGA SHIFT", 62),
]

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
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", "-r", "30", out],
        capture_output=True)

def esc_drawtext(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")

def main():
    durs = [float(l.strip()) for l in open(DURF) if l.strip()]
    imgs = sorted(glob.glob(os.path.join(GDIR, "b*.webp")))[:76]
    assert len(imgs) == len(durs) == 76, f"gambar={len(imgs)} durasi={len(durs)}"
    print(f"{len(imgs)} gambar, target {sum(durs)/60:.1f} mnt", flush=True)
    os.makedirs(TMPD, exist_ok=True)
    for i, img in enumerate(imgs):
        s = os.path.join(TMPD, f"s{i:03d}.mp4")
        if seg_ok(s, durs[i]):
            continue
        if os.path.exists(s):
            os.remove(s)
        print(f"  render s{i:03d} ({durs[i]:.1f}s)...", flush=True)
        for attempt in range(2):
            kenburns_light(img, durs[i], i, s)
            if seg_ok(s, durs[i]):
                break
            print(f"    retry s{i:03d} (attempt {attempt+2})", flush=True)
        else:
            print(f"GAGAL: s{i:03d}"); sys.exit(1)
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(imgs)} segmen...", flush=True)
    segs = [os.path.join(TMPD, f"s{i:03d}.mp4") for i in range(len(imgs))]
    assert all(os.path.exists(s) for s in segs)
    lst = os.path.join(TMPD, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    concat = os.path.join(TMPD, "concat.mp4")
    run([Q, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", concat],
        capture_output=True)
    run([Q, "-y", "-i", concat, "-i", AUDIO,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
         "-shortest", "-movflags", "+faststart", OUT],
        capture_output=True)
    print(f"OK: {OUT} ({probe_dur(OUT)/60:.1f} menit)", flush=True)
    # overlay timing dari kumulatif
    cum, t = [], 0.0
    for d in durs:
        cum.append((t, t + d)); t += d
    filters = []
    used = []
    for teks, beat in OVERLAYS:
        s0, s1 = cum[beat - 1]
        used.append((teks, s0, s1))
        filters.append(
            f"drawtext=fontfile={FONT}:text='{esc_drawtext(teks)}':"
            f"fontsize=64:fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-text_h-80:"
            f"enable='between(t,{s0:.2f},{s1:.2f})'")
    print("Overlay detik:", [(t_, round(a, 1), round(b, 1)) for t_, a, b in used], flush=True)
    run([Q, "-y", "-i", OUT, "-vf", ",".join(filters),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-c:a", "copy", "-movflags", "+faststart", OUTYT],
        capture_output=True)
    print(f"OK: {OUTYT} ({probe_dur(OUTYT)/60:.1f} menit)", flush=True)

if __name__ == "__main__":
    main()
