#!/usr/bin/env python3
"""Batch assembly sisa segmen horor 2026-10-10 (s034-s075).
Render 14 segmen per 1x ffmpeg (filter_complex) -> hemat slot queue.
Lalu concat s000-s033 + batch1-3 + mux audio -> video/2026-10-10.mp4
Lalu overlay teks -> video/2026-10-10-youtube.mp4
"""
import subprocess, os, glob, sys

BASE = "/home/hatch/workspace/horor-otomatis"
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
GDIR = os.path.join(BASE, "gambar/2026-10-10")
AUDIO = os.path.join(BASE, "audio/2026-10-10.mp3")
DURF = os.path.join(BASE, "audio/2026-10-10.durations.txt")
TMPD = os.path.join(BASE, "video/_tmp_segs_20261010")
OUT = os.path.join(BASE, "video/2026-10-10.mp4")
OUTYT = os.path.join(BASE, "video/2026-10-10-youtube.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

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

def zp_filter(seg_dur, idx):
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
    return (f"scale=1280:720,{zp},"
            "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
            "noise=alls=6:allf=t,vignette=PI/5,setsar=1")

def render_batch(idxs, durs, imgs, out):
    """Render beberapa segmen dalam 1x ffmpeg."""
    n = len(idxs)
    # validasi durasi batch
    exp_dur = sum(durs[i] for i in idxs)
    if os.path.exists(out):
        try:
            if abs(probe_dur(out) - exp_dur) < 2.0:
                print(f"  skip {out} (sudah ada)", flush=True)
                return
        except Exception:
            pass
        os.remove(out)
    args = [Q, "-y"]
    for i in idxs:
        args += ["-loop", "1", "-framerate", "30", "-t", str(durs[i]), "-i", imgs[i]]
    filt_parts = []
    for k, i in enumerate(idxs):
        filt_parts.append(f"[{k}:v]{zp_filter(durs[i], i)}[v{k}]")
    concat_in = "".join(f"[v{k}]" for k in range(n))
    filt_parts.append(f"{concat_in}concat=n={n}:v=1:a=0[vout]")
    args += ["-filter_complex", ";".join(filt_parts),
             "-map", "[vout]", "-c:v", "libx264", "-preset", "veryfast",
             "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30", out]
    print(f"  render batch s{idxs[0]:03d}-s{idxs[-1]:03d} ({exp_dur:.0f}s video)...", flush=True)
    run(args, capture_output=True)
    got = probe_dur(out)
    assert abs(got - exp_dur) < 2.0, f"batch durasi salah: {got} vs {exp_dur}"
    print(f"  OK batch s{idxs[0]:03d}-s{idxs[-1]:03d}", flush=True)

def esc_drawtext(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")

def main():
    durs = [float(l.strip()) for l in open(DURF) if l.strip()]
    imgs = sorted(glob.glob(os.path.join(GDIR, "b*.webp")))
    assert len(imgs) == len(durs) == 76
    # segmen yang belum ada
    todo = [i for i in range(76)
            if not (os.path.exists(os.path.join(TMPD, f"s{i:03d}.mp4")))]
    print(f"todo: {len(todo)} segmen: {todo[0]:03d}-{todo[-1]:03d}", flush=True)
    # batch 14
    B = 14
    batch_files = []
    for b in range(0, len(todo), B):
        idxs = todo[b:b+B]
        out = os.path.join(TMPD, f"batch{b//B}.mp4")
        batch_files.append(out)
        render_batch(idxs, durs, imgs, out)
    # concat: segmen satuan + batch
    segs = [os.path.join(TMPD, f"s{i:03d}.mp4") for i in range(76)
            if os.path.exists(os.path.join(TMPD, f"s{i:03d}.mp4"))]
    # urutan: s000..s033 lalu batch0..2 (batch meng-cover s034+)
    parts = sorted(segs) + sorted(batch_files)
    # pastikan urutan benar: batch setelah segmen satuan terakhir
    print(f"concat {len(parts)} parts", flush=True)
    lst = os.path.join(TMPD, "list2.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    concat = os.path.join(TMPD, "concat2.mp4")
    run([Q, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", concat],
        capture_output=True)
    run([Q, "-y", "-i", concat, "-i", AUDIO,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
         "-shortest", "-movflags", "+faststart", OUT],
        capture_output=True)
    print(f"OK: {OUT} ({probe_dur(OUT)/60:.1f} menit)", flush=True)
    # overlay
    cum, t = [], 0.0
    for d in durs:
        cum.append((t, t + d)); t += d
    filters = []
    for teks, beat in OVERLAYS:
        s0, s1 = cum[beat - 1]
        filters.append(
            f"drawtext=fontfile={FONT}:text='{esc_drawtext(teks)}':"
            f"fontsize=64:fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-text_h-80:"
            f"enable='between(t,{s0:.2f},{s1:.2f})'")
    run([Q, "-y", "-i", OUT, "-vf", ",".join(filters),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-c:a", "copy", "-movflags", "+faststart", OUTYT],
        capture_output=True)
    print(f"OK: {OUTYT} ({probe_dur(OUTYT)/60:.1f} menit)", flush=True)

if __name__ == "__main__":
    main()
