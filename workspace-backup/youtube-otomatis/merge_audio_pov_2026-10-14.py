#!/usr/bin/env python3
"""Gabung 88 beat mp3 -> audio/gabungan-2026-10-14.mp3 + catat durasi per beat.
JEDA beats: sisip 0.8 dtk hening SEBELUM beat. Antar beat: 0.5 dtk hening.
Bumper voice-clone disisipkan di langkah atempo (build_fast_audio_2026-10-14.py)."""
import subprocess, os, json, tempfile, sys

BASE = "/home/hatch/workspace/youtube-otomatis"
ADIR = os.path.join(BASE, "audio/2026-10-14")
FFQ = os.path.join(BASE, "ffmpeg-queue.sh")
JEDA = {"beat-003", "beat-014", "beat-020", "beat-030", "beat-040",
        "beat-047", "beat-054", "beat-062", "beat-072", "beat-084"}
N = 88

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    return float(r.stdout.strip())

def main():
    tmpd = tempfile.mkdtemp(prefix="merge-aud-")
    def mksil(name, secs):
        p = os.path.join(tmpd, name)
        subprocess.run([FFQ, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", str(secs), "-c:a", "libmp3lame", "-b:a", "128k", p], capture_output=True, check=True)
        return p
    sil08 = mksil("sil08.mp3", 0.8)
    sil05 = mksil("sil05.mp3", 0.5)
    seg_durs, parts = {}, []
    for i in range(1, N + 1):
        bid = f"beat-{i:03d}"
        mp3 = os.path.join(ADIR, f"{bid}.mp3")
        if not os.path.exists(mp3) or os.path.getsize(mp3) == 0:
            raise SystemExit(f"HILANG/RUSAK: {mp3}")
        d = dur(mp3)
        total, seg = d, []
        if bid in JEDA:
            total += 0.8
            seg.append(sil08)
        seg.append(mp3)
        parts.extend(seg)
        if i < N:
            parts.append(sil05)
            total += 0.5
        seg_durs[bid] = round(total, 3)
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    out = os.path.join(BASE, "audio/gabungan-2026-10-14.mp3")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], capture_output=True, check=True)
    dj = os.path.join(BASE, "audio/durasi-beat-2026-10-14-orig.json")
    json.dump(seg_durs, open(dj, "w"), indent=1)
    total = sum(seg_durs.values())
    print(f"OK: {out} total {total:.1f}s ({total/60:.1f} mnt), {len(seg_durs)} beat")
    import shutil
    shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
