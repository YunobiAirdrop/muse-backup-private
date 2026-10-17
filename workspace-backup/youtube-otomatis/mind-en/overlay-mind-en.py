#!/usr/bin/env python3
"""Tambah text overlay di momen kunci video Dark Mind Files (English).
Penggunaan: python3 overlay-mind-en.py <video_in> <durasi_json> <video_out>
Overlay ditampilkan selama durasi beat bersangkutan.
"""
import json, subprocess, sys

OVERLAYS = [
    (23, "HIS EYES LEAKED IT"),
    (28, "FEET NEVER LIE"),
    (45, "STACK THE SIGNALS"),
    (66, "THE VOICE BETRAYS"),
    (74, "PROTECT, NEVER TRAP"),
]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"

def main():
    vin, djur, vout = sys.argv[1:4]
    d = json.load(open(djur))
    n = len(d)
    durs = [float(d[f"beat-{i+1:03d}"]) for i in range(n)]
    cum = [0.0]
    for x in durs:
        cum.append(cum[-1] + x)
    filters = []
    for beat, teks in OVERLAYS:
        if beat > n:
            continue
        s, e = cum[beat - 1], cum[beat]
        filters.append(
            f"drawtext=fontfile={FONT}:text='{teks}':fontsize=54:fontcolor=white:"
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
