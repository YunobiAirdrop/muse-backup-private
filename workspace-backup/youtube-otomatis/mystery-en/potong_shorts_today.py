#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari video long mystery-en.
Penggunaan: python3 potong_shorts_today.py <video_long> <durations.txt> <outdir> <tgl> <b1> <b2> <b3>
  b1..b3 = nomor beat (1-based) pusat tiap jendela 45 detik.
"""
import subprocess, sys, os

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def potong(src, start, durasi, out):
    vf = "crop=405:720:437:0,scale=720:1280:flags=lanczos,unsharp=5:5:0.6:5:5:0.0"
    subprocess.run([FFQ, "-y", "-ss", str(start), "-t", str(durasi), "-i", src,
                    "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
                   capture_output=True, check=True)
    print(f"OK: {out} ({dur(out):.0f}s)")

def main():
    src, durfile, outdir, tgl, b1, b2, b3 = sys.argv[1:8]
    beats = [int(b1), int(b2), int(b3)]
    os.makedirs(outdir, exist_ok=True)
    durs = [float(x) for x in open(durfile).read().split()]
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    total = cum[-1]
    print(f"total {total:.0f}s, {len(durs)} beats")
    for i, b in enumerate(beats, 1):
        center = (cum[b - 1] + cum[b]) / 2
        start = max(0.0, center - 22.5)
        if start + 45 > total:
            start = total - 45
        potong(src, round(start, 2), 45, os.path.join(outdir, f"{tgl}-s{i}.mp4"))

if __name__ == "__main__":
    main()
