#!/usr/bin/env python3
"""Finishing: concat s000-s033 + batchA + batchB, mux audio, overlay teks."""
import subprocess, os, glob

BASE = "/home/hatch/workspace/horor-otomatis"
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
AUDIO = os.path.join(BASE, "audio/2026-10-10.mp3")
DURF = os.path.join(BASE, "audio/2026-10-10.durations.txt")
TMPD = os.path.join(BASE, "video/_tmp_segs_20261010")
OUT = os.path.join(BASE, "video/2026-10-10.mp4")
OUTYT = os.path.join(BASE, "video/2026-10-10-youtube.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OVERLAYS = [
    ("NAMA SENDIRI DI DAFTAR KORBAN", 1),
    ("SUSTER TANPA KAKI", 14),
    ("DIA MENYELAMATKAN PASIEN", 27),
    ("AKU MENINGGAL 2004?", 45),
    ("GANTIAN JAGA SHIFT", 62),
]

def run(a, **kw):
    return subprocess.run(a, check=True, **kw)

def probe(p):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", p],
            capture_output=True, text=True)
    return float(r.stdout.strip())

def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")

def main():
    parts = [os.path.join(TMPD, f"s{i:03d}.mp4") for i in range(34)]
    parts += [os.path.join(TMPD, "batchA.mp4"), os.path.join(TMPD, "batchB.mp4")]
    for p in parts:
        assert os.path.exists(p), f"hilang: {p}"
    print(f"concat {len(parts)} parts", flush=True)
    lst = os.path.join(TMPD, "list3.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    concat = os.path.join(TMPD, "concat3.mp4")
    run([Q, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", concat],
        capture_output=True)
    run([Q, "-y", "-i", concat, "-i", AUDIO, "-c:v", "copy",
         "-c:a", "aac", "-b:a", "128k", "-shortest",
         "-movflags", "+faststart", OUT], capture_output=True)
    print(f"OK: {OUT} ({probe(OUT)/60:.1f} mnt)", flush=True)
    durs = [float(l.strip()) for l in open(DURF) if l.strip()]
    cum, t = [], 0.0
    for d in durs:
        cum.append((t, t + d)); t += d
    flt = []
    for teks, beat in OVERLAYS:
        s0, s1 = cum[beat - 1]
        flt.append(f"drawtext=fontfile={FONT}:text='{esc(teks)}':"
                   f"fontsize=64:fontcolor=white:borderw=3:bordercolor=black:"
                   f"x=(w-text_w)/2:y=h-text_h-80:enable='between(t,{s0:.2f},{s1:.2f})'")
    run([Q, "-y", "-i", OUT, "-vf", ",".join(flt), "-c:v", "libx264",
         "-preset", "veryfast", "-crf", "20", "-c:a", "copy",
         "-movflags", "+faststart", OUTYT], capture_output=True)
    print(f"OK: {OUTYT} ({probe(OUTYT)/60:.1f} mnt)", flush=True)

if __name__ == "__main__":
    main()
