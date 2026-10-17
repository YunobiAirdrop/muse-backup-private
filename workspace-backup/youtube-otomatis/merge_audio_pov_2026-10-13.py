#!/usr/bin/env python3
"""Gabung 88 beat mp3 -> audio/gabungan-2026-10-13.mp3 + sisip bumper voice-clone
sebelum narasi beat 52 (tengah video, jeda natural). Durasi beat-052 di
durasi-beat-2026-10-13.json diperpanjang sebesar durasi bumper agar sinkron.
JEDA beats: sisip 0.8 dtk hening SEBELUM beat. Antar beat: 0.5 dtk hening."""
import subprocess, os, json, tempfile, sys

BASE = "/home/hatch/workspace/youtube-otomatis"
ADIR = os.path.join(BASE, "audio/2026-10-13")
FFQ = os.path.join(BASE, "ffmpeg-queue.sh")
BUMPER_WAV = os.path.join(BASE, "voice-clone-test/bumper-youtubepov.wav")
BUMPER_BEFORE = 52
JEDA = {"beat-003", "beat-014", "beat-021", "beat-030", "beat-034", "beat-051", "beat-055", "beat-062", "beat-068", "beat-073", "beat-084"}
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
    # Pakai ulang silence yang sudah dibuat via antrean oleh percobaan merge pertama
    import shutil as _sh
    _prev = "/tmp/merge-aud-iq92f7rw"
    if os.path.exists(os.path.join(_prev, "sil08.mp3")) and os.path.exists(os.path.join(_prev, "sil05.mp3")):
        sil08 = os.path.join(tmpd, "sil08.mp3"); _sh.copy(os.path.join(_prev, "sil08.mp3"), sil08)
        sil05 = os.path.join(tmpd, "sil05.mp3"); _sh.copy(os.path.join(_prev, "sil05.mp3"), sil05)
        print("silence: pakai ulang", flush=True)
    else:
        sil08 = mksil("sil08.mp3", 0.8)
        sil05 = mksil("sil05.mp3", 0.5)
    bd = 0.0  # bumper disisipkan di langkah atempo rantai (build_fast_audio.py), bukan di merge ini
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
    out = os.path.join(BASE, "audio/gabungan-2026-10-13.mp3")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], capture_output=True, check=True)
    dj = os.path.join(BASE, "audio/durasi-beat-2026-10-13.json")
    json.dump(seg_durs, open(dj, "w"), indent=1)
    total = sum(seg_durs.values())
    print(f"OK: {out} total {total:.1f}s ({total/60:.1f} mnt), {len(seg_durs)} beat")
    import shutil
    shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
