#!/usr/bin/env python3
"""Potong 3 SHORTS dari LONG 2026-10-13 (Tri Hita Karana — falsafah Hindu Bali).
Sumber: kisah-dharma-2026-10-13-long-small.mp4 (1280x720, 542.8 dtk).
Segmen dipotong TEPAT di batas chapter (batas kalimat), durasi 35-63 dtk.
Output: vertikal 720x1280 crop tengah, hook text 0-5 dtk, CTA overlay 3 dtk terakhir.
Semua ffmpeg via ffmpeg-queue.sh (WAJIB per AGENTS.md). Tanpa '%' & tanpa apostrof di drawtext.
"""
import subprocess, os, sys

D = "/home/hatch/workspace/kisah-dharma/2026-10-14"
SRC = "/home/hatch/workspace/kisah-dharma/2026-10-13/kisah-dharma-2026-10-13-long-small.mp4"
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"

# (nama, start, dur, teks hook) — batas chapter dari upload-instruksi.md 2026-10-13:
#   00:00-00:45 intro | 04:28-05:25 Palemahan (57 dtk) | 05:55-06:30 Refleksi (35 dtk)
SHORTS = [
    ("short1", 0.0, 45.0, "RAHASIA KETENANGAN PULAU BALI"),
    ("short2", 268.0, 57.0, "ALAM BUKAN SEKADAR SUMBER DAYA"),
    ("short3", 355.0, 35.0, "KETENANGAN ITU DIBANGUN"),
]

os.makedirs(D, exist_ok=True)
for name, start, dur, hook in SHORTS:
    out = os.path.join(D, f"kisah-dharma-2026-10-14-{name}.mp4")
    if os.path.exists(out):
        print(f"SKIP exists: {out}", flush=True)
        continue
    cta_start = dur - 3.0
    vf = (
        "crop=ih*9/16:ih,scale=720:1280,setsar=1,"
        f"drawtext=fontfile={FONT}:text='{hook}':fontsize=36:fontcolor=white:"
        "borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=120:"
        "box=1:boxcolor=black@0.45:boxborderw=16:enable='between(t,0,5)',"
        f"drawtext=fontfile={FONT}:text='SUBSCRIBE KISAH DHARMA!':fontsize=40:fontcolor=white:"
        "borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=1080:"
        f"box=1:boxcolor=black@0.45:boxborderw=16:enable='between(t,{cta_start:.1f},{dur:.1f})',"
        "noise=alls=6:allf=t,format=yuv420p"
    )
    r = subprocess.run([FQ, "-y", "-ss", f"{start:.1f}", "-i", SRC, "-t", f"{dur:.1f}",
                        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{name} FAILED:\n{r.stderr[-1500:]}", flush=True)
        sys.exit(1)
    print(f"{name} OK: {out}", flush=True)

print("DONE", flush=True)
