#!/usr/bin/env python3
"""Rakit SATU panggilan ffmpeg-queue: 80 gambar -> zoompan per segmen -> concat filter -> mux audio.
Cadangan bila antrean per-segmen terlalu lambat. Output: video/video-2026-10-12-oneshot.mp4
Perlakuan visual sama dengan rakit_light.py (scale 1280:720, zoompan 4 mode bergilir,
eq, noise grain, vignette).
"""
import subprocess, os, glob, sys, json

BASE = "/home/hatch/workspace/lima-misteri"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
GDIR = os.path.join(BASE, "gambar", "2026-10-12-clean")
AUDIO = os.path.join(BASE, "audio", "2026-10-12.mp3")
DJUR = os.path.join(BASE, "audio", "2026-10-12-durations.json")
OUT = os.path.join(BASE, "video", "video-2026-10-12-oneshot.mp4")

def main():
    imgs = sorted(glob.glob(os.path.join(GDIR, "*.webp")))
    dj = json.load(open(DJUR))
    durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(len(imgs))]
    print(f"{len(imgs)} gambar, total {sum(durs):.0f}s", flush=True)
    args = [FFQ, "-y"]
    for img in imgs:
        args += ["-i", img]
    args += ["-i", AUDIO]
    fc = []
    for i, d in enumerate(durs):
        frames = int(d * 30)
        mode = i % 4
        if mode == 0:
            zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
        elif mode == 1:
            zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='(iw-iw/zoom)*on/{frames}':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
        elif mode == 2:
            zp = f"zoompan=z='max(1.15-0.0012*on,1.0)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
        else:
            zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{frames}':s=1280x720:fps=30"
        fc.append(f"[{i}:v]scale=1280:720,{zp},eq=contrast=1.08:saturation=0.92:brightness=-0.02,noise=alls=6:allf=t,vignette=PI/5,setsar=1[v{i}]")
    fc.append("".join(f"[v{i}]" for i in range(len(imgs))) + f"concat=n={len(imgs)}:v=1:a=0[vout]")
    args += ["-filter_complex", ";".join(fc),
             "-map", "[vout]", "-map", f"{len(imgs)}:a",
             "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30",
             "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", OUT]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print("GAGAL oneshot:", r.stderr[-2000:]); sys.exit(1)
    print(f"OK: {OUT}")

if __name__ == "__main__":
    main()
