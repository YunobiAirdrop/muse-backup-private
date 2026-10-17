#!/usr/bin/env python3
"""Overlay teks momen kunci video POV 2026-10-08 via drawtext ffmpeg.
Penggunaan: python3 overlay_pov_2026-10-08.py <video_in> <durasi_json> <video_out>
"""
import json, subprocess, sys

OVERLAYS = [
    (2, "MALAM BENTENG JATUH"),
    (31, "DUURSTEDE DIREBUT"),
    (58, "HARGA SEBUAH KEMENANGAN"),
    (79, "16 DESEMBER 1817"),
]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"

def main():
    vin, djur, vout = sys.argv[1:4]
    d = json.load(open(djur))
    durs = [float(d[f"beat-{i+1:03d}"]) for i in range(len(d))]
    cum = [0.0]
    for x in durs:
        cum.append(cum[-1] + x)
    filters = []
    for beat, teks in OVERLAYS:
        s, e = cum[beat - 1], cum[beat]
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
