#!/usr/bin/env python3
"""Potong 3 shorts vertikal 720x1280 dari video/2026-10-16.mp4.
Rentang beat -> timestamp dari durasi-beat-2026-10-16.json.
Di-upload BESOK oleh run berikutnya (pola selang-seling)."""
import subprocess, os, json

BASE = "/home/hatch/workspace/youtube-otomatis/truecrime-en"
VID = os.path.join(BASE, "video/2026-10-16.mp4")
SOD = os.path.join(BASE, "shorts")
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
N = 85

# (nama, beat_awal_1based, beat_akhir_1based_inklusif)
CLIPS = [
    ("2026-10-16-s1", 1, 6),     # hook: black screen -> masked figure -> "he came back"
    ("2026-10-16-s2", 25, 31),   # the 90 seconds: figure, Pepsi, "Catch the wave"
    ("2026-10-16-s3", 46, 52),   # how they did it: STL override
]

TITLES = {
    "2026-10-16-s1": "Chicago's TV Went Black \u2014 Then HE Appeared #shorts #truecrime #unsolved #foryou",
    "2026-10-16-s2": "He Hijacked Live TV for 90 Seconds (Never Caught) #shorts #truecrime #mystery #foryou",
    "2026-10-16-s3": "How One Man Hacked Every TV in Chicago #shorts #truecrime #1980s #foryou",
}

def main():
    dj = json.load(open(os.path.join(BASE, "audio/durasi-beat-2026-10-16.json")))
    durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(N)]
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    os.makedirs(SOD, exist_ok=True)
    for name, b1, b2 in CLIPS:
        start, end = cum[b1 - 1], cum[b2]
        out = os.path.join(SOD, f"{name}.mp4")
        vf = "crop=405:720:(in_w-405)/2:0,scale=720:1280"
        r = subprocess.run([FFQ, "-y", "-ss", f"{start:.2f}", "-to", f"{end:.2f}",
                            "-i", VID, "-vf", vf,
                            "-c:v", "libx264", "-preset", "veryfast",
                            "-pix_fmt", "yuv420p", "-r", "30",
                            "-c:a", "aac", "-b:a", "128k", out],
                           capture_output=True)
        if r.returncode != 0:
            print(f"GAGAL {name}: {r.stderr.decode()[-500:]}")
            continue
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration", "-of",
                            "default=noprint_wrappers=1:nokey=1", out],
                           capture_output=True, text=True)
        print(f"OK {name}: {float(d.stdout.strip()):.1f}s ({start:.0f}-{end:.0f})")
    with open(os.path.join(SOD, "2026-10-16-titles.json"), "w") as f:
        json.dump(TITLES, f, indent=1)
    print("titles written")

if __name__ == "__main__":
    main()
