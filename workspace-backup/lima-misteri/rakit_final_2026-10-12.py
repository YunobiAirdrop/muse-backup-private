#!/usr/bin/env python3
"""Rakit final Lima Misteri 2026-10-12 dalam SATU panggilan ffmpeg-queue:
concat 80 segmen + drawtext overlay momen kunci + mux audio -> video-2026-10-12-final.mp4
Penggunaan: python3 rakit_final_2026-10-12.py  (cek dulu semua segmen valid)
"""
import json, subprocess, sys, os

BASE = "/home/hatch/workspace/lima-misteri"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SEGDIR = os.path.join(BASE, "video", "_tmp_segs")
AUDIO = os.path.join(BASE, "audio", "2026-10-12.mp3")
DJUR = os.path.join(BASE, "audio", "2026-10-12-durations.json")
OUT = os.path.join(BASE, "video", "video-2026-10-12-final.mp4")

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

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def main():
    dj = json.load(open(DJUR))
    durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(len(dj))]
    segs = [os.path.join(SEGDIR, f"s{i:03d}.mp4") for i in range(len(durs))]
    bad = [i for i, s in enumerate(segs) if not (os.path.exists(s) and dur(s) >= durs[i] * 0.9)]
    if bad:
        print("SEGMEN BELUM VALID:", bad); sys.exit(1)
    lst = os.path.join(SEGDIR, "list-final.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    filters = []
    for beat, teks in OVERLAYS:
        t0 = cum[beat - 1] + 0.8
        t1 = min(t0 + TAMPIL, cum[beat] - 0.3)
        if t1 <= t0:
            continue
        teks_esc = teks.replace(":", "\\:").replace("'", "")
        filters.append(
            f"drawtext=fontfile={FONT}:text='{teks_esc}':fontsize=58:"
            f"fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-170:enable='between(t\\,{t0:.2f}\\,{t1:.2f})'")
    vf = ",".join(filters)
    r = subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", AUDIO,
                        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                        "-shortest", "-movflags", "+faststart", OUT],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("GAGAL final:", r.stderr[-2000:]); sys.exit(1)
    print(f"OK: {OUT} ({dur(OUT)/60:.1f} menit)")

if __name__ == "__main__":
    main()
