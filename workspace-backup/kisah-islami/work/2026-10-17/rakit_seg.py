#!/usr/bin/env python3
"""Assemble Jejak Islami LONG 2026-10-17 — segment-based (robust, resumable).
12 segments x 32.53s -> concat -> overlays + narration -> verify -> final.
"""
import math, os, shutil, subprocess, sys

W = "/home/hatch/workspace/kisah-islami/work/2026-10-17"
FF = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NARR = os.path.join(W, "audio/narration-full.mp3")
CL = os.path.join(W, "clips")
SEGS = os.path.join(W, "segs")
SLOT = 32.53

CLIPS = [
    (f"{CL}/c02.ogv", 0),
    (f"{CL}/c10.webm", 0),
    (f"{CL}/c07.webm", 0),
    (f"{CL}/c09.webm", 0),
    (f"{CL}/c14.webm", 0),
    (f"{CL}/c08.webm", 0),
    (f"{CL}/c02.ogv", 5),
    (f"{CL}/c07.webm", 3),
    (f"{CL}/c10.webm", 40),
    (f"{CL}/c09.webm", 12),
    (f"{CL}/c14.webm", 4),
    (f"{CL}/c08.webm", 2),
]

VF = ("scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
      "setsar=1,fps=25,eq=contrast=1.05:saturation=0.95,"
      "noise=alls=7:allf=t,format=yuv420p")

OVERLAYS = [
    ("BABILONIA - NEGERI PENYEMBAH BERHALA", 31, 36, 44, "#FFD700"),
    ("AKU TIDAK SUKA PADA YANG TENGGELAM", 68, 73, 44, "#FFD700"),
    ("TANYAKAN SAJA PADA BERHALA BESAR ITU", 111, 116, 44, "#FFD700"),
    ("NAMRUDZ - RAJA YANG MENGAKU TUHAN", 154, 159, 44, "#FFD700"),
    ("WAHAI API - JADILAH DINGIN", 231, 237, 48, "#FFD700"),
    ("SUBSCRIBE JEJAK ISLAMI", 195, 198, 54, "white"),
    ("SUBSCRIBE - AKTIFKAN LONCENG", 385, 390, 54, "white"),
]

def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0

def run(cmd, log):
    with open(log, "a") as lf:
        r = subprocess.run(cmd, stderr=lf, stdout=lf)
    return r.returncode

def main():
    os.makedirs(SEGS, exist_ok=True)
    log = os.path.join(W, "rakit-seg.log")
    # 1. segments
    for i, (cf, sso) in enumerate(CLIPS):
        out = os.path.join(SEGS, f"s{i:02d}.mp4")
        if os.path.isfile(out) and probe(out) > SLOT - 2:
            print(f"SKIP s{i:02d}", flush=True); continue
        dur = probe(cf)
        need = SLOT + sso + 1.0
        loops = max(0, math.ceil(need / max(dur, 0.1)) - 1)
        cmd = [FF, "-hide_banner", "-loglevel", "error"]
        if loops > 0:
            cmd += ["-stream_loop", str(loops)]
        cmd += ["-ss", str(sso), "-i", cf, "-t", str(SLOT),
                "-vf", VF, "-c:v", "libx264", "-preset", "ultrafast",
                "-crf", "23", "-an", "-y", out]
        print(f"build s{i:02d} (loop {loops})...", flush=True)
        if run(cmd, log) != 0:
            print(f"GAGAL s{i:02d}"); sys.exit(1)
        print(f"OK s{i:02d}", flush=True)
    # 2. concat
    lst = os.path.join(W, "seg-list.txt")
    with open(lst, "w") as f:
        for i in range(len(CLIPS)):
            f.write(f"file '{os.path.join(SEGS, f's{i:02d}.mp4')}'\n")
    vconcat = os.path.join(W, "vconcat.mp4")
    if not (os.path.isfile(vconcat) and abs(probe(vconcat) - SLOT*len(CLIPS)) < 5):
        print("concat...", flush=True)
        if run([FF, "-hide_banner", "-loglevel", "error", "-f", "concat",
                "-safe", "0", "-i", lst, "-c", "copy", "-y", vconcat], log) != 0:
            print("GAGAL concat"); sys.exit(1)
    print(f"vconcat: {probe(vconcat):.1f}s", flush=True)
    # 3. overlays + audio
    dt = ",".join(
        f"drawtext=fontfile={FONT}:text='{t}':fontsize={fs}:fontcolor={col}:"
        f"borderw=3:bordercolor=black@0.9:x=(w-text_w)/2:y=h-170:"
        f"enable='between(t,{ts},{te})'"
        for t, ts, te, fs, col in OVERLAYS)
    tmp = os.path.join(W, "jejak-islami-2026-10-17-long-TEMP.mp4")
    final = os.path.join(W, "jejak-islami-2026-10-17-long.mp4")
    print("final pass (overlay+audio)...", flush=True)
    if run([FF, "-hide_banner", "-loglevel", "error", "-i", vconcat,
            "-i", NARR, "-vf", dt, "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            "-shortest", "-y", tmp], log) != 0:
        print("GAGAL final"); sys.exit(1)
    vd = probe(tmp)
    nd = probe(NARR)
    print(f"TEMP: {vd:.1f}s vs narasi {nd:.1f}s", flush=True)
    if abs(vd - nd) > 8:
        print("DURASI TIDAK VALID"); sys.exit(1)
    shutil.move(tmp, final)
    print(f"OK FINAL: {final} ({os.path.getsize(final)//1024//1024}MB)")

if __name__ == "__main__":
    main()
