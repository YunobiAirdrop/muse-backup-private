#!/usr/bin/env python3
"""Potong 3 shorts 45 detik vertikal 9:16 dari video long POV 2026-10-14.
s1: beat 1-6 (cold open) | s2: beat 48-56 (serangan fajar) | s3: beat 65-72 (benteng runtuh).
Output: shorts/2026-10-14-s1/s2/s3.mp4"""
import json, subprocess, sys, os

BASE = "/home/hatch/workspace/youtube-otomatis"
FFQ = os.path.join(BASE, "ffmpeg-queue.sh")
VIN = os.path.join(BASE, "video/2026-10-14-final.mp4")
DJ = os.path.join(BASE, "audio/durasi-beat-2026-10-14.json")
OUTD = os.path.join(BASE, "shorts")
CUTS = {"s1": (1, 45.0), "s2": (48, 45.0), "s3": (65, 45.0)}

def main():
    d = json.load(open(DJ))
    durs = [float(d[f"beat-{i+1:03d}"]) for i in range(len(d))]
    cum = [0.0]
    for x in durs:
        cum.append(cum[-1] + x)
    os.makedirs(OUTD, exist_ok=True)
    for name, (beat, durasi) in CUTS.items():
        ss = cum[beat - 1]
        out = os.path.join(OUTD, f"2026-10-14-{name}.mp4")
        vf = ("crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=720:1280,"
              "eq=contrast=1.08:saturation=0.92,noise=alls=6:allf=t")
        r = subprocess.run([FFQ, "-y", "-ss", f"{ss:.2f}", "-i", VIN, "-t", str(durasi),
                            "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                            "-pix_fmt", "yuv420p", "-r", "30",
                            "-c:a", "aac", "-b:a", "128k", out],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-1500:]); sys.exit(1)
        print(f"OK: {out} (mulai {ss:.1f}s)")

if __name__ == "__main__":
    main()
