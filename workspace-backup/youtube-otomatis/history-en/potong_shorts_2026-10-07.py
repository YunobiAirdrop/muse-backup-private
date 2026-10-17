#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari video long 2026-10-07 (offset title card 3s).
Penggunaan: python3 potong_shorts_2026-10-07.py <video_long> <durasi_json> <shorts_plan_json> <outdir>
"""
import subprocess, json, sys, os

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
OFFSET = 3.0  # title card pembuka

def ts(sec):
    return f"{int(sec//3600):02d}:{int((sec%3600)//60):02d}:{sec%60:06.3f}"

def main():
    video, dur_json, plan_json, outdir = sys.argv[1:5]
    os.makedirs(outdir, exist_ok=True)
    dur = json.load(open(dur_json))
    plan = json.load(open(plan_json))
    start = {}
    t = 0.0
    keys = sorted(dur.keys())
    n = len(keys)
    for i, k in enumerate(keys):
        start[i + 1] = t
        t += float(dur[k])
    for s in plan:
        b0 = int(str(s["beat_start"]).split("-")[-1])
        b1 = int(str(s["beat_end"]).split("-")[-1])
        ss = OFFSET + start[b0]
        dur_s = sum(float(dur[f"beat-{i:03d}"]) for i in range(b0, b1 + 1))
        out = os.path.join(outdir, f"2026-10-07-{s['id']}.mp4")
        vf = "crop=406:720:(in_w-406)/2:0,scale=720:1280:flags=lanczos"
        subprocess.run([FFQ, "-y", "-ss", ts(ss), "-i", video,
                        "-t", str(round(dur_s, 2)),
                        "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-r", "30", "-c:a", "aac", "-b:a", "128k",
                        "-movflags", "+faststart", out],
                       capture_output=True, check=True)
        print(f"OK {s['id']}: beats {b0}-{b1} = {dur_s:.1f}s -> {out}", flush=True)

if __name__ == "__main__":
    main()
