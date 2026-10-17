#!/usr/bin/env python3
"""Burn text overlay momen kunci video Lima Misteri 2026-10-12.
Penggunaan: python3 overlay_2026-10-12.py <video_in> <durations.json> <video_out>
Tidak memakai karakter persen (aturan drawtext VM).
"""
import json, subprocess, sys

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

OVERLAYS = [
    (6, "DENGUNG TAOS"),
    (20, "SINYAL WOW! 1977"),
    (34, "HUTAN HOIA BACIU"),
    (40, "SUBSCRIBE!"),
    (48, "SEGITIGA BERMUDA"),
    (61, "DYATLOV PASS 1959"),
    (76, "JAWABANNYA TETAP RETAK"),
    (79, "SUBSCRIBE!"),
]
TAMPIL = 6.0

def main():
    vin, djur, vout = sys.argv[1:4]
    dj = json.load(open(djur))
    n = len(dj)
    durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(n)]
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    filters = []
    def add_overlay(beat, teks, tampil):
        t0 = cum[beat - 1] + 0.8
        t1 = min(t0 + tampil, cum[beat] - 0.3)
        if t1 <= t0:
            return
        teks_esc = teks.replace(":", "\\:").replace("'", "")
        filters.append(
            f"drawtext=fontfile={FONT}:text='{teks_esc}':fontsize=58:"
            f"fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-170:enable='between(t\\,{t0:.2f}\\,{t1:.2f})'"
        )
    for beat, teks in OVERLAYS:
        add_overlay(beat, teks, TAMPIL)
    vf = ",".join(filters)
    r = subprocess.run([FFQ, "-y", "-i", vin, "-vf", vf,
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", vout],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("GAGAL overlay:", r.stderr[-1500:]); sys.exit(1)
    print(f"OK: {vout} ({len(filters)} overlay)")

if __name__ == "__main__":
    main()
