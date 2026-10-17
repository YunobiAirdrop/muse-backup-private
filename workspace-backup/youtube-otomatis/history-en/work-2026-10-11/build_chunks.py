#!/usr/bin/env python3
"""Bangun gabungan audio 2026-10-11 per chunk (concat FILTER + aresample seragam).
Menghindari concat demuxer yang terputus di tengah pada daftar campuran.
Output: audio/2026-10-11/gabungan-final-2026-10-11.mp3 (24000 Hz mono, ~619s).
"""
import subprocess, json, os, sys

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
W = os.path.join(BASE, "work-2026-10-11")
ADIR = os.path.join(BASE, "audio", "2026-10-11")
OUT = os.path.join(ADIR, "gabungan-final-2026-10-11.mp3")
DJ = json.load(open(os.path.join(ADIR, "durasi-beat-2026-10-11.json")))
BUMPER_MP3 = os.path.join(W, "bumper.mp3")
BUMPER_DUR = 4.29

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def beat(i):
    return os.path.join(ADIR, f"beat-{i:03d}.mp3")

# chunk: (nama, [(tipe, nilai)], durasi harapan)
chunks = [
    ("c1", [("silence", 3.0)] + [("f", beat(i)) for i in range(1, 12)],
     3.0 + sum(DJ[f"beat-{i:03d}"] for i in range(1, 12))),
    ("c2", [("f", beat(i)) for i in range(12, 24)],
     sum(DJ[f"beat-{i:03d}"] for i in range(12, 24))),
    ("c3", [("f", beat(i)) for i in range(24, 36)] + [("f", BUMPER_MP3)],
     sum(DJ[f"beat-{i:03d}"] for i in range(24, 36)) + BUMPER_DUR),
    ("c4", [("f", beat(i)) for i in range(36, 48)],
     sum(DJ[f"beat-{i:03d}"] for i in range(36, 48))),
    ("c5", [("f", beat(i)) for i in range(48, 60)],
     sum(DJ[f"beat-{i:03d}"] for i in range(48, 60))),
    ("c6", [("f", beat(i)) for i in range(60, 71)],
     sum(DJ[f"beat-{i:03d}"] for i in range(60, 71))),
]

chunk_files = []
for name, parts, expect in chunks:
    cf = os.path.join(W, f"chunk-{name}.mp3")
    chunk_files.append(cf)
    if os.path.exists(cf) and abs(dur(cf) - expect) < 1.5:
        print(f"{name}: sudah OK ({dur(cf):.1f}s)", flush=True)
        continue
    inputs = []
    fc = []
    for j, (kind, val) in enumerate(parts):
        if kind == "silence":
            inputs += ["-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono"]
            fc.append(f"[{j}:a]atrim=0:{val},asetpts=PTS-STARTPTS,aresample=24000,aformat=sample_fmts=fltp:channel_layouts=mono[a{j}]")
        else:
            inputs += ["-i", val]
            fc.append(f"[{j}:a]aresample=24000,aformat=sample_fmts=fltp:channel_layouts=mono[a{j}]")
    fc.append("".join(f"[a{j}]" for j in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[aout]")
    cmd = [FFQ, "-y", "-threads", "2"] + inputs + [
        "-filter_complex", ";".join(fc), "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "128k", cf]
    print(f"{name}: render (target {expect:.1f}s)...", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{name} GAGAL:\n", (r.stderr or "")[-2000:]); sys.exit(1)
    got = dur(cf)
    print(f"{name}: hasil {got:.1f}s (target {expect:.1f}s)", flush=True)
    if abs(got - expect) > 2.0:
        print(f"PERINGATAN: {name} meleset >2s dari target"); sys.exit(2)

lst = os.path.join(W, "chunklist.txt")
with open(lst, "w") as f:
    for cf in chunk_files:
        f.write(f"file '{cf}'\n")
r = subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c:a", "libmp3lame", "-b:a", "128k", OUT],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("final concat GAGAL:\n", (r.stderr or "")[-2000:]); sys.exit(1)
print(f"FINAL AUDIO: {OUT} ({dur(OUT):.1f}s)", flush=True)
