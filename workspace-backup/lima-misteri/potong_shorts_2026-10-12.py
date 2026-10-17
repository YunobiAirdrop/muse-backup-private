#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 (45 dtk) dari video long Lima Misteri 2026-10-12.
s1=Dyatlov (beat 65), s2=Bermuda (beat 50), s3=Hoia Baciu (beat 36/39).
Penggunaan: python3 potong_shorts_2026-10-12.py <video_long> <durations.json> <outdir> <tgl>
"""
import subprocess, sys, os, json

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def potong(src, start, durasi, out):
    vf = "crop=405:720:437:0,scale=720:1280:flags=lanczos,unsharp=5:5:0.6:5:5:0.0"
    r = subprocess.run([FFQ, "-y", "-ss", str(start), "-t", str(durasi), "-i", src,
                        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("GAGAL potong:", r.stderr[-800:]); sys.exit(1)
    print(f"OK: {out} ({dur(out):.0f}s)")

def main():
    src, djur, outdir, tgl = sys.argv[1:5]
    os.makedirs(outdir, exist_ok=True)
    dj = json.load(open(djur))
    durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(len(dj))]
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    total = cum[-1]
    print(f"total {total:.0f}s, {len(durs)} beats")

    def beat_time(n):
        return (cum[n - 1] + cum[n]) / 2

    windows = [
        ("s1", "dyatlov-tenda-robek", beat_time(65)),
        ("s2", "bermuda-kompas", beat_time(50)),
        ("s3", "hoia-baciu-lingkaran", beat_time(37)),
    ]
    for name, label, center in windows:
        start = max(0.0, center - 22.5)
        if start + 45 > total:
            start = total - 45
        out = os.path.join(outdir, f"{tgl}-{name}.mp4")
        print(f"  {name} ({label}): mulai {start:.1f}s")
        potong(src, round(start, 2), 45, out)

if __name__ == "__main__":
    main()
