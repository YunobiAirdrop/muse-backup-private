#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari video long 2026-10-11 (offset title card 3s).
Teks on-screen (hook) sepanjang short + CTA 'Subscribe!' di 3 detik terakhir.
Semua ffmpeg via ffmpeg-queue.sh. Tanpa karakter persen di drawtext.
Penggunaan: python3 potong_shorts_2026-10-11.py
"""
import subprocess, json, os

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
VIDEO = os.path.join(BASE, "video", "2026-10-11.mp4")
DUR_JSON = os.path.join(BASE, "audio", "2026-10-11", "durasi-beat-2026-10-11.json")
PLAN_JSON = os.path.join(BASE, "shorts", "shorts-plan-2026-10-11.json")
OUTDIR = os.path.join(BASE, "shorts")
OFFSET = 3.0
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def ts(sec):
    return f"{int(sec//3600):02d}:{int((sec%3600)//60):02d}:{sec%60:06.3f}"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    d = json.load(open(DUR_JSON))
    plan = json.load(open(PLAN_JSON))
    start = {}
    t = 0.0
    for i in range(1, 71):
        start[i] = t
        t += float(d[f"beat-{i:03d}"])
    for s in plan:
        b0 = int(s["beat_start"].split("-")[-1])
        b1 = int(s["beat_end"].split("-")[-1])
        ss = OFFSET + start[b0]
        dur_s = sum(float(d[f"beat-{i:03d}"]) for i in range(b0, b1 + 1))
        out = os.path.join(OUTDIR, f"2026-10-11-{s['id']}.mp4")
        hook_file = f"/tmp/short-he11-{s['id']}.txt"
        open(hook_file, "w").write(s["onscreen_text"])
        cta_file = f"/tmp/short-he11-cta.txt"
        open(cta_file, "w").write("Subscribe!")
        cta_start = max(0.0, dur_s - 3.0)
        vf = ("crop=406:720:(in_w-406)/2:0,scale=720:1280:flags=lanczos,"
              f"drawtext=fontfile={FONT}:textfile={hook_file}:fontsize=40:"
              "fontcolor=white:borderw=2:bordercolor=black@0.8:"
              "x=(w-text_w)/2:y=80:box=1:boxcolor=black@0.55:boxborderw=18,"
              f"drawtext=fontfile={FONT}:textfile={cta_file}:fontsize=52:"
              "fontcolor=#ffd97a:borderw=2:bordercolor=black@0.8:"
              "x=(w-text_w)/2:y=h-220:box=1:boxcolor=black@0.6:boxborderw=20:"
              f"enable='between(t,{cta_start:.2f},{dur_s:.2f})'")
        subprocess.run([FFQ, "-y", "-ss", ts(ss), "-i", VIDEO,
                        "-t", str(round(dur_s, 2)),
                        "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-r", "30", "-c:a", "aac", "-b:a", "128k",
                        "-movflags", "+faststart", out],
                       capture_output=True, check=True)
        print(f"OK {s['id']}: beats {b0}-{b1} = {dur_s:.1f}s -> {out} (final {dur(out):.1f}s)", flush=True)

if __name__ == "__main__":
    main()
