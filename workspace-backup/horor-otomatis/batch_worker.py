#!/usr/bin/env python3
"""Worker: render SATU batch segmen (filter_complex) lalu keluar.
Pakai: python3 batch_worker.py <start_idx> <end_idx> <output>
"""
import subprocess, os, glob, sys

BASE = "/home/hatch/workspace/horor-otomatis"
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
GDIR = os.path.join(BASE, "gambar/2026-10-10")
DURF = os.path.join(BASE, "audio/2026-10-10.durations.txt")

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
        zp = f"zoompan=z='min(zoom+0.0012,1.25)':d={total_frames}:x='iw/2-(iw/zoom)*on/{total_frames}':y='(ih-ih/zoom)*on/{total_frames}':s=1280x720:fps=30"
    return (f"scale=1280:720,{zp},"
            "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
            "noise=alls=6:allf=t,vignette=PI/5,setsar=1")

def main():
    s0, s1, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    idxs = list(range(s0, s1 + 1))
    durs = [float(l.strip()) for l in open(DURF) if l.strip()]
    imgs = sorted(glob.glob(os.path.join(GDIR, "b*.webp")))
    exp_dur = sum(durs[i] for i in idxs)
    if os.path.exists(out):
        try:
            if abs(probe_dur(out) - exp_dur) < 2.0:
                print(f"skip {out} (ada)", flush=True); return
        except Exception:
            pass
        os.remove(out)
    args = [Q, "-y"]
    for i in idxs:
        # SATU frame per input; zoompan d= yang meng-expand (JANGAN -loop/-t di input!)
        args += ["-i", imgs[i]]
    parts = []
    for k, i in enumerate(idxs):
        parts.append(f"[{k}:v]{zp_filter(durs[i], i)}[v{k}]")
    parts.append("".join(f"[v{k}]" for k in range(len(idxs))) +
                f"concat=n={len(idxs)}:v=1:a=0[vout]")
    args += ["-filter_complex", ";".join(parts), "-map", "[vout]",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-pix_fmt", "yuv420p", "-r", "30", out]
    print(f"render s{s0:03d}-s{s1:03d} ({exp_dur:.0f}s)...", flush=True)
    run(args, capture_output=True)
    got = probe_dur(out)
    assert abs(got - exp_dur) < 2.0, f"salah durasi: {got} vs {exp_dur}"
    print(f"OK s{s0:03d}-s{s1:03d}", flush=True)

if __name__ == "__main__":
    main()
