#!/usr/bin/env python3
"""Potong 3 shorts 45 detik dari video final POV 2026-10-18 (phinisi).
s1 = beat 1-6 (cold open), s2 = beat 40-48 (puncak badai + perompak), s3 = beat 61-68.
Vertikal 9:16 720x1280 (crop tengah). Via ffmpeg-queue."""
import subprocess, os, json, sys

BASE = "/home/hatch/workspace/youtube-otomatis"
FFQ = os.path.join(BASE, "ffmpeg-queue.sh")
VIDEO = os.path.join(BASE, "video/2026-10-18-final.mp4")
DJ = os.path.join(BASE, "audio/durasi-beat-2026-10-18.json")
AUDIO = os.path.join(BASE, "audio/gabungan-2026-10-18-fast.mp3")
TITLE_DUR = 3.0
DUR = 45.0
CUTS = {"s1": 1, "s2": 40, "s3": 61}

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def main():
    dj = json.load(open(DJ))
    n = len(dj)
    seg = [float(dj[f"beat-{i+1:03d}"]) for i in range(n)]
    scale = dur(AUDIO) / sum(seg)
    seg = [d * scale for d in seg]
    starts, acc = [], TITLE_DUR
    for d in seg:
        starts.append(acc); acc += d
    os.makedirs(os.path.join(BASE, "shorts"), exist_ok=True)
    for name, beat in CUTS.items():
        out = os.path.join(BASE, "shorts", f"2026-10-18-{name}.mp4")
        ss = starts[beat - 1]
        r = subprocess.run([FFQ, "-y", "-ss", f"{ss:.2f}", "-t", str(DUR), "-i", VIDEO,
                            "-vf", "crop=ih*9/16:ih,scale=720:1280",
                            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "128k", out],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-1500:]); sys.exit(1)
        print(f"OK {out} ({dur(out):.1f}s) dari beat {beat} @ {ss:.1f}s", flush=True)

if __name__ == "__main__":
    main()
