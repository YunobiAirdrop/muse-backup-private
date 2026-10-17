#!/usr/bin/env python3
"""Render banyak segmen dalam SATU panggilan ffmpeg-queue (multi-input, multi-output).
TANPA zoompan (deadlock di VM ini bila multi-input) — Ken Burns via crop-pan linear.
Penggunaan: python3 rakit_multi_2026-10-12.py <start_idx> <end_idx>
Segmen yang sudah valid di video/_tmp_segs dilewati. Output ke video/_tmp_segs_multi/.
"""
import subprocess, os, glob, sys, json

BASE = "/home/hatch/workspace/lima-misteri"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
GDIR = os.path.join(BASE, "gambar", "2026-10-12-clean")
DJUR = os.path.join(BASE, "audio", "2026-10-12-durations.json")
SEGDIR = os.path.join(BASE, "video", "_tmp_segs")
OUTDIR = os.path.join(BASE, "video", "_tmp_segs_multi")

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def main():
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    os.makedirs(OUTDIR, exist_ok=True)
    imgs = sorted(glob.glob(os.path.join(GDIR, "*.webp")))
    dj = json.load(open(DJUR))
    durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(len(imgs))]
    todo = []
    for i in range(lo, min(hi, len(imgs))):
        s = os.path.join(SEGDIR, f"s{i:03d}.mp4")
        if os.path.exists(s) and dur(s) >= durs[i] * 0.9:
            continue
        todo.append(i)
    print(f"todo: {todo}", flush=True)
    if not todo:
        print("nothing to do"); return
    args = [FFQ, "-y"]
    for i in todo:
        args += ["-loop", "1", "-t", f"{durs[i]:.2f}", "-i", imgs[i]]
    fc = []
    for k, i in enumerate(todo):
        d = durs[i]
        mode = i % 4
        if mode == 0:
            x, y = f"(in_w-out_w)*t/{d:.2f}", "(in_h-out_h)/2"
        elif mode == 1:
            x, y = f"(in_w-out_w)*(1-t/{d:.2f})", "(in_h-out_h)/2"
        elif mode == 2:
            x, y = "(in_w-out_w)/2", f"(in_h-out_h)*t/{d:.2f}"
        else:
            x, y = "(in_w-out_w)/2", f"(in_h-out_h)*(1-t/{d:.2f})"
        fc.append(f"[{k}:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
                  f"scale=1560:878,crop=1280:720:x='{x}':y='{y}',"
                  f"eq=contrast=1.08:saturation=0.92:brightness=-0.02,noise=alls=6:allf=t,"
                  f"vignette=PI/5,setsar=1,format=yuv420p[v{k}]")
    args += ["-filter_complex", ";".join(fc)]
    for k, i in enumerate(todo):
        out = os.path.join(OUTDIR, f"s{i:03d}.mp4")
        args += ["-map", f"[v{k}]", "-t", f"{durs[i]:.2f}", "-c:v", "libx264",
                 "-preset", "veryfast", "-r", "30", out]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print("GAGAL multi:", r.stderr[-2000:]); sys.exit(1)
    print(f"OK multi: {len(todo)} segmen")

if __name__ == "__main__":
    main()
