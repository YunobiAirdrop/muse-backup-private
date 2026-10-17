#!/usr/bin/env python3
"""Tambah text overlay di momen kunci ke video horor via ffmpeg drawtext.
Penggunaan: python3 overlay_teks.py video/2026-10-06.mp4 video/2026-10-06-youtube.mp4
Jalankan dengan PATH=/home/hatch/workspace/youtube-otomatis:$PATH agar ffmpeg=ffmpeg-queue.sh
"""
import subprocess, sys

SRC, DST = sys.argv[1], sys.argv[2]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (teks, mulai_detik, selesai_detik) — momen kunci 2026-10-06
OVERLAYS = [
    ("GIGINYA... BUKAN GIGI MANUSIA", 7, 20),        # hook awal
    ("UANGNYA BERUBAH JADI DAUN KERING", 313, 326),  # twist 1
    ("ISINYA... GIGI MANUSIA", 464, 478),            # twist 2
    ("DIA ADA DI DALAM CERMIN", 570, 584),           # klimaks
    ("JANGAN MAMPIR \u2014 LARI!", 678, 699),        # ending
]

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

parts = []
for teks, t1, t2 in OVERLAYS:
    parts.append(
        f"drawtext=fontfile={FONT}:text='{esc(teks)}':fontsize=64:"
        f"fontcolor=white:borderw=3:bordercolor=black:"
        f"x=(w-text_w)/2:y=h-170:enable='between(t,{t1},{t2})'"
    )
vf = ",".join(parts)
r = subprocess.run(["ffmpeg", "-y", "-i", SRC, "-vf", vf,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-c:a", "copy", "-movflags", "+faststart", DST],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("GAGAL:", r.stderr[-2000:]); sys.exit(1)
print("OK:", DST)
