#!/usr/bin/env python3
"""Rakit final Lima Misteri 2026-10-13:
1) concat 78 segmen + mux audio -> video-2026-10-13-base.mp4 (BERSIH, tanpa overlay; dipakai untuk potong shorts)
2) base + drawtext overlay momen kunci -> video-2026-10-13-final.mp4
Penggunaan: python3 rakit_final_2026-10-13.py  (cek dulu semua segmen valid)
"""
import json, subprocess, sys, os

BASE = "/home/hatch/workspace/lima-misteri"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SEGDIR = os.path.join(BASE, "video", "_tmp_segs_2026-10-13")
AUDIO = os.path.join(BASE, "audio", "2026-10-13.mp3")
DJUR = os.path.join(BASE, "audio", "2026-10-13-durations.json")
BASEV = os.path.join(BASE, "video", "video-2026-10-13-base.mp4")
OUT = os.path.join(BASE, "video", "video-2026-10-13-final.mp4")

OVERLAYS = [
    (7, "BELL WITCH"),
    (23, "PULAU BONEKA"),
    (36, "CHUPACABRA"),
    (41, "SUBSCRIBE!"),
    (49, "RENDLESHAM 1980"),
    (62, "HUJAN DARAH KERALA"),
    (74, "SUBSCRIBE!"),
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

def run(args, label):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"GAGAL {label}:", r.stderr[-2000:]); sys.exit(1)

def main():
    dj = json.load(open(DJUR))
    assert len(dj) == 78, f"durations: {len(dj)} (harap 78)"
    durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(78)]
    segs = [os.path.join(SEGDIR, f"s{i:03d}.mp4") for i in range(78)]
    bad = [i for i, s in enumerate(segs) if not (os.path.exists(s) and dur(s) >= durs[i] * 0.9)]
    if bad:
        print("SEGMEN BELUM VALID:", bad); sys.exit(1)
    lst = os.path.join(SEGDIR, "list-final.txt")
    with open(lst, "w") as f:  # absolute path (aturan AGENTS.md)
        for s in segs:
            f.write(f"file '{s}'\n")
    # 1) base: concat + mux audio
    run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", AUDIO,
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", BASEV],
        "base concat+mux")
    da, dv = dur(AUDIO), dur(BASEV)
    print(f"base OK: audio {da:.1f}s vs video {dv:.1f}s (selisih {abs(da-dv):.1f}s)")
    # 2) overlay momen kunci
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
    run([FFQ, "-y", "-i", BASEV, "-vf", vf,
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-c:a", "copy", "-movflags", "+faststart", OUT], "final overlay")
    print(f"OK: {OUT} ({dur(OUT)/60:.1f} menit)")

if __name__ == "__main__":
    main()
