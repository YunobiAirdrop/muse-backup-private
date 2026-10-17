#!/usr/bin/env python3
"""Overlay teks momen kunci video POV 2026-10-15 via drawtext ffmpeg.
Penggunaan: python3 overlay_pov_2026-10-15.py <video_in> <durasi_json> <video_out>
Overlay 4 momen penuh 1 beat + 1 overlay SUBSCRIBE! 3 detik di beat 44.
drawtext aman: tanpa %, tanpa apostrof, tanpa colon di teks."""
import json, subprocess, sys

OVERLAYS = [
    (2, "ACEH 1873", None),
    (24, "BANDA ACEH JATUH", None),
    (48, "MARECHAUSSEE DATANG", None),
    (65, "GERILYA TERAKHIR", None),
    (44, "SUBSCRIBE!", 3.0),  # CTA tengah video, 3 detik saja
]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
TOFF = 3.0  # offset title card pembuka di video final

def dur(p):
    import subprocess
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", p],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def main():
    vin, djur, vout = sys.argv[1:4]
    d = json.load(open(djur))
    durs = [float(d[f"beat-{i+1:03d}"]) for i in range(len(d))]
    # skala sama seperti rakit: slide selaras audio aktual (3 dtk pad di awal)
    aud = "/home/hatch/workspace/youtube-otomatis/audio/gabungan-2026-10-15-final.mp3"
    scale = (dur(aud) - TOFF) / sum(durs) if dur(aud) > TOFF else 1.0
    durs = [x * scale for x in durs]
    cum = [TOFF]
    for x in durs:
        cum.append(cum[-1] + x)
    filters = []
    for beat, teks, fixed in OVERLAYS:
        s = cum[beat - 1]
        e = s + fixed if fixed else cum[beat]
        filters.append(
            f"drawtext=fontfile={FONT}:text='{teks}':fontsize=60:fontcolor=white:"
            f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.80:"
            f"enable='between(t,{s:.2f},{e:.2f})'"
        )
    vf = ",".join(filters)
    r = subprocess.run([FFQ, "-y", "-i", vin, "-vf", vf,
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", vout],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(1)
    print(f"OK: {vout}")

if __name__ == "__main__":
    main()
