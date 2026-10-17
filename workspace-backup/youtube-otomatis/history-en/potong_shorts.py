#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari video long berdasarkan rentang beat.
Penggunaan: python3 potong_shorts.py <video_long> <durasi_json> <shorts_plan_json> <outdir>
"""
import subprocess, json, sys, os

def ts(sec):
    return f"{int(sec//3600):02d}:{int((sec%3600)//60):02d}:{sec%60:06.3f}"

def main():
    video, dur_json, plan_json, outdir = sys.argv[1:5]
    os.makedirs(outdir, exist_ok=True)
    dur = json.load(open(dur_json))
    plan = json.load(open(plan_json))
    # start kumulatif per beat (1-indexed)
    start = {}
    t = 0.0
    for i in range(1, 76):
        start[i] = t
        t += float(dur[f"beat-{i:03d}"])
    for s in plan:
        b0 = int(str(s["beat_start"]).split("-")[-1])
        b1 = int(str(s["beat_end"]).split("-")[-1])
        ss = start[b0]
        dur_s = sum(float(dur[f"beat-{i:03d}"]) for i in range(b0, b1 + 1))
        out = os.path.join(outdir, f"2026-10-05-{s['id']}.mp4")
        vf = "crop=406:720:(in_w-406)/2:0,scale=720:1280:flags=lanczos"
        subprocess.run(["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-ss", ts(ss), "-i", video,
                        "-t", str(round(dur_s, 2)),
                        "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-r", "30", "-c:a", "aac", "-b:a", "128k",
                        "-movflags", "+faststart", out],
                       capture_output=True, check=True)
        print(f"OK {s['id']}: beats {b0}-{b1} = {dur_s:.1f}s -> {out}")

if __name__ == "__main__":
    main()
