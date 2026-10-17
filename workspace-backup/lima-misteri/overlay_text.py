#!/usr/bin/env python3
"""Burn text overlay di 5 momen kunci video Lima Misteri.
Penggunaan: python3 overlay_text.py <video_in> <durations.json> <video_out>
"""
import json, subprocess, sys

BASE = "/home/hatch/workspace/lima-misteri"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (nomor beat 1-based, teks overlay) — 2026-10-10: kereta hantu Manggarai
OVERLAYS = [
    (1, "KERETA YANG TAK ADA DI JADWAL"),
    (17, "KERETA PENJEMPUT?!"),
    (27, "BERANI NAIK NGGAK?!"),
    (36, "WAJAH KEDUA DI KACA"),
    (46, "HILANG 3 HARI, NGAKU 5 MENIT"),
]
TAMPIL = 7.0  # detik per overlay
# overlay CTA tengah (beat, teks, durasi detik) — 2026-10-10
SUB_OVERLAY = (59, "SUBSCRIBE!", 3.0)

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
            f"drawtext=fontfile={FONT}:text='{teks_esc}':fontsize=62:"
            f"fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-170:enable='between(t\\,{t0:.2f}\\,{t1:.2f})'"
        )
    for beat, teks in OVERLAYS:
        add_overlay(beat, teks, TAMPIL)
    if SUB_OVERLAY:
        add_overlay(*SUB_OVERLAY)
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
