#!/usr/bin/env python3
"""Rakit LONG Kisah Alkitab 2026-10-16 (Nuh, Kejadian 6-9).
Lanjutan produksi yang terhenti 2026-10-17 (naskah+VO+klip selesai, rakit belum).
Segmen per klip via ffmpeg-queue.sh (RAM aman), overlay dibakar per segmen,
grain halus anti-AI-look. Lalu concat + mux voiceover.
9 klip reuse (Commons, terverifikasi QC) + 1 klip baru (rv01 sungai, PD).
Tiap klip dipakai MAKS 2x, offset beda.
"""
import json, os, subprocess, sys

D = "/home/hatch/workspace/kisah-alkitab/work/2026-10-16"
KLIP = os.path.join(D, "klip")
SEG = os.path.join(D, "_segs"); os.makedirs(SEG, exist_ok=True)
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
VO = os.path.join(D, "audio/voiceover.mp3")

def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019")

def overlay_filter(text):
    if not text:
        return ""
    n = len(text)
    fs = 44 if n <= 24 else (36 if n <= 32 else 28)
    dt = (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize={fs}:fontcolor=white:"
          "borderw=3:bordercolor=black@0.85:x=(w-text_w)/2:y=h-140:"
          "box=1:boxcolor=black@0.5:boxborderw=20")
    return dt + ","

# (clip, ss, dur, overlay)
PLAN = [
    # BEAT 1 — hujan turun (0 - 136.56)
    ("r04.orig", 0,   30.0,   "40 Hari 40 Malam Hujan Tanpa Henti"),
    ("n14.orig", 5,   28.0,   None),
    ("n04.orig", 10,  30.0,   "Kejadian 6:9 \u2014 Nuh bergaul dengan Allah"),
    ("r02.orig", 0,   24.0,   None),
    ("r04.orig", 100, 24.56,  None),
    # BEAT 2 — perintah membangun (136.56 - 235.416)
    ("r01.orig", 0,   28.0,   "Kejadian 6:14 \u2014 Buatlah Bahtera"),
    ("n04.orig", 45,  26.0,   None),
    ("r03.orig", 0,   19.0,   None),
    ("n14.orig", 32,  25.856, None),
    # BEAT 3 — hewan masuk, pintu ditutup (235.416 - 338.976)
    ("n23.orig", 5,   26.0,   None),
    ("cl01.orig", 0,  26.0,   "Kejadian 7:16 \u2014 Tuhan menutup pintu bahtera"),
    ("r01.orig", 10,  26.0,   None),
    ("n23.orig", 33,  25.56,  None),
    # BEAT 4 — air bah & penantian (338.976 - 423.528)
    ("r02.orig", 15,  30.0,   None),
    ("rv01.orig", 0,  27.0,   "Kejadian 8:11 \u2014 Daun zaitun yang segar"),
    ("n27.orig", 8,   27.552, None),
    # BEAT 5 — keluar, pelangi (423.528 - 525.216)
    ("n27.orig", 45,  30.0,   None),
    ("rv01.orig", 0,  26.0,   "Kejadian 9:13 \u2014 Pelangi, tanda perjanjian"),
    ("r03.orig", 0,   19.0,   None),
    ("cl01.orig", 0,  26.688, None),
]
TOTAL = 525.216

def build_seg(i, clip, ss, dur, overlay):
    out = os.path.join(SEG, f"s{i:02d}.mp4")
    if os.path.exists(out) and os.path.getsize(out) > 100000:
        print(f"SKIP s{i:02d} (ada)", flush=True); return out
    vf = ("scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
          "setsar=1,fps=30," + overlay_filter(overlay) +
          "noise=alls=6:allf=t,format=yuv420p")
    cmd = [FFQ, "-y", "-loglevel", "error",
           "-ss", str(ss), "-t", str(dur), "-i", os.path.join(KLIP, clip),
           "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-an", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out):
        print(f"GAGAL s{i:02d}: {r.stderr[-500:]}", flush=True); sys.exit(1)
    print(f"OK s{i:02d} ({dur}s) {clip}@{ss}", flush=True)
    return out

def stream_durs(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type,duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return r.stdout.strip()

def main():
    total = sum(p[2] for p in PLAN)
    assert abs(total - TOTAL) < 0.01, f"plan {total} != {TOTAL}"
    print(f"Segmen: {len(PLAN)}, total {total:.2f}s (VO {TOTAL}s)", flush=True)
    # cek klip cukup panjang utk ss+dur
    for i, (clip, ss, dur, ov) in enumerate(PLAN):
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                  "format=duration", "-of", "csv=p=0",
                                  os.path.join(KLIP, clip)],
                                 capture_output=True, text=True).stdout.strip())
        if ss + dur > d + 0.5:
            print(f"KLIP KURANG: s{i:02d} {clip} butuh {ss+dur:.1f}s, ada {d:.1f}s"); sys.exit(1)
    segs = [build_seg(i, *p) for i, p in enumerate(PLAN)]
    lst = os.path.join(SEG, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")  # absolute path
    vcat = os.path.join(D, "out/vconcat.mp4")
    os.makedirs(os.path.join(D, "out"), exist_ok=True)
    r = subprocess.run([FFQ, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", lst, "-c", "copy", vcat], capture_output=True, text=True)
    if r.returncode != 0: print("GAGAL concat:", r.stderr[-500:]); sys.exit(1)
    print("stream vconcat:\n" + stream_durs(vcat), flush=True)
    final = os.path.join(D, "out/kisah-alkitab-2026-10-16-long.mp4")
    tmp = final + ".tmp.mp4"
    r = subprocess.run([FFQ, "-y", "-loglevel", "error", "-i", vcat, "-i", VO,
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
                        "-c:a", "aac", "-b:a", "128k", "-shortest", tmp],
                       capture_output=True, text=True)
    if r.returncode != 0: print("GAGAL mux:", r.stderr[-500:]); sys.exit(1)
    print("stream final(tmp):\n" + stream_durs(tmp), flush=True)
    vd = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                               "-of", "csv=p=0", tmp], capture_output=True, text=True).stdout.strip())
    if abs(vd - TOTAL) > 8:
        print(f"GAGAL VERIFIKASI DURASI: {vd:.1f}s vs {TOTAL}s — final TIDAK ditimpa: {tmp}")
        sys.exit(1)
    os.replace(tmp, final)
    print(f"SELESAI: {final} ({vd:.1f}s, {os.path.getsize(final)//1024//1024}MB)")

if __name__ == "__main__":
    main()
