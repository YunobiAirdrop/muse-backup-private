#!/usr/bin/env python3
"""Bangun audio final POV 2026-10-12 dari gabungan narasi (merge polos):
- atempo 1.15x seluruhnya (total ~12,4 mnt -> ~10,8 mnt)
- sisip bumper voice-clone tepat sebelum narasi beat 52 (di dalam segmen beat-052,
  setelah jeda hening 0.8 dtk yang sudah termasuk durasi beat-052)
- tulis ulang durasi-beat-2026-10-12.json terskala (beat-052 += durasi bumper terskala)
Satu kali panggilan ffmpeg via antrean."""
import subprocess, json, os, sys

BASE = "/home/hatch/workspace/youtube-otomatis"
FFQ = os.path.join(BASE, "ffmpeg-queue.sh")
SRC = os.path.join(BASE, "audio/gabungan-2026-10-12.mp3")
ORIG_JSON = os.path.join(BASE, "audio/durasi-beat-2026-10-12-orig.json")
JSON = os.path.join(BASE, "audio/durasi-beat-2026-10-12.json")
BUMPER = os.path.join(BASE, "voice-clone-test/bumper-youtubepov.wav")
OUT = os.path.join(BASE, "audio/gabungan-2026-10-12-fast.mp3")
RATE = 1.15
BUMPER_BEFORE = 52

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    return float(r.stdout.strip())

def main():
    d = json.load(open(ORIG_JSON))
    t52 = sum(float(d[f"beat-{i:03d}"]) for i in range(1, BUMPER_BEFORE))
    bd = dur(BUMPER)
    fc = (f"[0:a]asplit=2[p1][p2];"
          f"[p1]atrim=0:{t52:.3f},asetpts=PTS-STARTPTS,atempo={RATE}[a1];"
          f"[p2]atrim={t52:.3f},asetpts=PTS-STARTPTS,atempo={RATE}[a2];"
          f"[1:a]atempo={RATE}[ab];"
          f"[a1][ab][a2]concat=n=3:v=0:a=1[out]")
    r = subprocess.run([FFQ, "-y", "-i", SRC, "-i", BUMPER, "-filter_complex", fc,
                        "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "128k", OUT],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(1)
    nd = {k: round(v / RATE, 3) for k, v in d.items()}
    nd[f"beat-{BUMPER_BEFORE:03d}"] = round(nd[f"beat-{BUMPER_BEFORE:03d}"] + bd / RATE, 3)
    json.dump(nd, open(JSON, "w"), indent=1)
    print(f"OK {OUT}: total json {sum(nd.values()):.1f}s ({sum(nd.values())/60:.2f} mnt), audio {dur(OUT):.1f}s, bumper@{t52:.1f}s")

if __name__ == "__main__":
    main()
