#!/usr/bin/env python3
"""Render segmen Ken Burns paralel (satu rentang indeks per worker).
Penggunaan: python3 rakit_worker.py <dir_gambar> <durasi_json> <outdir> <idx_awal> <idx_akhir>
Semua ffmpeg lewat ffmpeg-queue.sh (maks 2 konkuren global)."""
import subprocess, os, sys, json

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def kenburns(img, seg_dur, idx, out):
    total_frames = int(seg_dur * 30)
    mode = idx % 4
    if mode == 0:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode == 1:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='(iw-iw/zoom)*on/{total_frames}':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode == 2:
        zp = f"zoompan=z='max(1.15-0.0012*on,1.0)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    else:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{total_frames}':s=1280x720:fps=30"
    vf = (f"scale=1280:720,{zp},"
          "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
          "noise=alls=6:allf=t,"
          "vignette=PI/5")
    r = subprocess.run([FFQ, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True)
    return r.returncode == 0

def main():
    gdir, djur, outdir, a0, a1 = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    os.makedirs(outdir, exist_ok=True)
    imgs = sorted(__import__("glob").glob(os.path.join(gdir, "*.webp")))
    dj = json.load(open(djur))
    for i in range(a0, a1):
        img = imgs[i]
        target = float(dj[f"beat-{i+1:03d}"])
        s = os.path.join(outdir, f"s{i:03d}.mp4")
        if os.path.exists(s) and dur(s) >= target * 0.9:
            continue
        if os.path.exists(s):
            os.remove(s)
        ok = False
        for _ in range(2):
            if kenburns(img, target, i, s) and dur(s) >= target * 0.9:
                ok = True
                break
        if not ok:
            print(f"GAGAL s{i:03d}", flush=True)
            sys.exit(1)
        print(f"worker[{a0}-{a1}] s{i:03d} ok", flush=True)
    print(f"worker[{a0}-{a1}] SELESAI", flush=True)

if __name__ == "__main__":
    main()
