#!/usr/bin/env python3
"""Gabung 75 beat mp3 -> audio/gabungan-2026-10-06.mp3, sisip 1 detik hening
dramatis SEBELUM beat-beat reveal besar. Tulis durasi-beat-2026-10-06.json
(durasi per segmen = hening + voiceover) untuk sinkronisasi gambar."""
import subprocess, os, json, tempfile

BASE = "/home/hatch/workspace/youtube-otomatis/truecrime-en"
ADIR = os.path.join(BASE, "audio/2026-10-06")
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"

# beat reveal besar -> hening 1 detik sebelumnya
REVEAL = {"beat-018", "beat-033", "beat-054"}

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of",
                        "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def main():
    tmpd = tempfile.mkdtemp(prefix="merge-aud-")
    silence = os.path.join(tmpd, "sil1.mp3")
    subprocess.run([FFQ, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-t", "1", "-c:a", "libmp3lame", "-b:a", "128k",
                    silence], capture_output=True, check=True)
    halfsil = os.path.join(tmpd, "sil05.mp3")
    subprocess.run([FFQ, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-t", "0.5", "-c:a", "libmp3lame", "-b:a", "128k",
                    halfsil], capture_output=True, check=True)
    seg_durs = {}
    parts = []
    for i in range(1, 76):
        bid = f"beat-{i:03d}"
        mp3 = os.path.join(ADIR, f"{bid}.mp3")
        if not os.path.exists(mp3) or os.path.getsize(mp3) == 0:
            raise SystemExit(f"HILANG/RUSAK: {mp3}")
        d = dur(mp3)
        total = d
        seg = [mp3]
        if bid in REVEAL:
            total += 1.0
            seg = [silence, mp3]
        # re-encode tiap segmen ke wav seragam lalu concat demuxer butuh format sama;
        # pakai concat filter via daftar file mp3 langsung (semua mp3 128k stereo)
        seg_durs[bid] = round(total, 3)
        parts.extend(seg)
        if i < 75:  # jeda napas 0.5 dtk antar beat (kecuali setelah beat terakhir)
            parts.append(halfsil)
            seg_durs[bid] = round(total + 0.5, 3)
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    out = os.path.join(BASE, "audio/gabungan-2026-10-06.mp3")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", out], capture_output=True, check=True)
    with open(os.path.join(BASE, "audio/durasi-beat-2026-10-06.json"), "w") as f:
        json.dump(seg_durs, f, indent=1)
    total = sum(seg_durs.values())
    print(f"OK: {out} total {total:.1f}s ({total/60:.1f} mnt)")
    import shutil; shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
