#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari video long history-en 2026-10-13.
Offset title card 3.0 dtk; bumper 4.29 dtk setelah beat-036 (berlaku beat-037+).
CTA 'Subscribe!' di 3 detik terakhir (aturan wajib channel). Tanpa karakter
persen/apostrof di drawtext. Semua ffmpeg via ffmpeg-queue.sh.
Penggunaan: python3 potong_shorts_2026-10-13.py
"""
import subprocess, json, os

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
VIDEO = os.path.join(BASE, "video", "2026-10-13.mp4")
DUR_JSON = os.path.join(BASE, "audio", "2026-10-13", "durasi-beat-2026-10-13.json")
PLAN_JSON = os.path.join(BASE, "shorts", "shorts-plan-2026-10-13.json")
OUTDIR = os.path.join(BASE, "shorts")
TITLE_CARD = 3.0
BUMPER = 4.29  # setelah beat-036, berlaku untuk beat-037 ke atas
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (id, beat_start, beat_end) — durasi dihitung: 58.653 / 59.175 / 57.837 dtk
SHORTS = [("s1", 1, 7), ("s2", 33, 39), ("s3", 53, 59)]

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
    start = {}
    t = TITLE_CARD
    for i in range(1, 73):
        if i == 37:
            t += BUMPER
        start[i] = t
        t += float(d[f"beat-{i:03d}"])
    results = {}
    for sid, b0, b1 in SHORTS:
        ss = start[b0]
        dur_s = (start[b1] + float(d[f"beat-{b1:03d}"])) - start[b0]
        out = os.path.join(OUTDIR, f"2026-10-13-{sid}.mp4")
        cta_file = "/tmp/short-he13-cta.txt"
        open(cta_file, "w").write("Subscribe!")
        cta_start = max(0.0, dur_s - 3.0)
        vf = ("crop=406:720:(in_w-406)/2:0,scale=720:1280:flags=lanczos,"
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
        results[sid] = (dur_s, dur(out))
        print(f"OK {sid}: beats {b0}-{b1} = {dur_s:.2f}s -> {out} (final {dur(out):.2f}s)", flush=True)
    json.dump(results, open(PLAN_JSON + ".tmp", "w"), indent=1)

if __name__ == "__main__":
    main()
