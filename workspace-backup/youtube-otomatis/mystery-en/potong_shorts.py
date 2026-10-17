#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari video panjang.
Penggunaan: python3 potong_shorts.py <video_long> <durations.txt> <outdir>
  Memilih 3 jendela 45 detik di momen paling dramatis berdasarkan beat.
"""
import subprocess, sys, os

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def potong(src, start, durasi, out):
    # crop tengah 405x720 -> scale 720x1280 + sharpen
    vf = "crop=405:720:437:0,scale=720:1280:flags=lanczos,unsharp=5:5:0.6:5:5:0.0"
    subprocess.run(["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-ss", str(start), "-t", str(durasi), "-i", src,
                    "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
                   capture_output=True, check=True)
    print(f"OK: {out} ({dur(out):.0f}s)")

def main():
    src, durfile, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    durs = [float(x) for x in open(durfile).read().split()]
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    total = cum[-1]
    print(f"total {total:.0f}s, {len(durs)} beats")

    def beat_time(n):
        # waktu tengah beat n (1-based)
        return (cum[n - 1] + cum[n]) / 2

    # Jendela dramatis (45 detik), dipusatkan di beat kunci:
    #  S1: tenda disobek dari dalam (beat ~16)
    #  S2: penemuan mayat + detail mengerikan (beat ~30)
    #  S3: bola api / radiasi (beat ~45)
    windows = [
        ("s1", beat_time(16)),
        ("s2", beat_time(30)),
        ("s3", beat_time(45)),
    ]
    for name, center in windows:
        start = max(0.0, center - 22.5)
        if start + 45 > total:
            start = total - 45
        out = os.path.join(outdir, f"2026-10-05-{name}.mp4")
        potong(src, round(start, 2), 45, out)

if __name__ == "__main__":
    main()
