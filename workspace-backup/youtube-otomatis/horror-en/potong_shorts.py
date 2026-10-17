#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari video longform + JSON durasi per-beat.
Penggunaan: python3 potong_shorts.py <video_long> <durasi_json> <rencana_jsonl> <outdir>
  rencana_jsonl: satu JSON per baris {"beats":[a,b], "judul":..., ...} (1-indexed, inklusif)
Output: <outdir>/2026-10-05-s1.mp4 dst (1080x1920, blur-fill background).
"""
import subprocess, os, sys, json

def run(cmd):
    subprocess.run(cmd, capture_output=True, check=True)

def main():
    video, dur_json, rencana, outdir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    os.makedirs(outdir, exist_ok=True)
    dj = json.load(open(dur_json))
    n = len(dj)
    # cumulative start times
    cum = [0.0]
    for i in range(1, n + 1):
        cum.append(cum[-1] + float(dj[f"beat-{i:03d}"]))
    for idx, line in enumerate(open(rencana)):
        r = json.loads(line)
        a, b = r["beats"]
        start, dur = cum[a - 1], cum[b] - cum[a - 1]
        out = os.path.join(outdir, f"2026-10-05-s{idx+1}.mp4")
        vf = ("split[a][b];"
              "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.35[bg];"
              "[b]scale=1080:-2[fg];"
              "[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p")
        run(["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-ss", str(start), "-t", str(dur), "-i", video,
             "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-c:a", "aac", "-b:a", "128k", "-r", "30",
             "-movflags", "+faststart", out])
        print(f"OK s{idx+1}: {r['judul'][:50]} ({dur:.0f}s) -> {out}")

if __name__ == "__main__":
    main()
