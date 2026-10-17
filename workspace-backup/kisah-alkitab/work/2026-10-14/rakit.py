#!/usr/bin/env python3
"""Rakit LONG Kisah Alkitab 2026-10-14 (Musa, Keluaran 14).
Segmen per klip via ffmpeg-queue.sh (RAM aman), overlay dibakar per segmen,
grain halus anti-AI-look. Lalu concat + mux voiceover.
Manifest: manifest.json -> [{"clip": abs_path, "ss": detik_mulai, "dur": detik, "overlay": teks|null}]
"""
import json, os, subprocess, sys

D = "/home/hatch/workspace/kisah-alkitab/work/2026-10-14"
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
    fs = 44 if n <= 24 else (36 if n <= 32 else 30)
    dt = (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize={fs}:fontcolor=white:"
          "borderw=3:bordercolor=black@0.85:x=(w-text_w)/2:y=h-140:"
          "box=1:boxcolor=black@0.5:boxborderw=20")
    return dt + ","

def build_seg(i, m):
    out = os.path.join(SEG, f"s{i:02d}.mp4")
    if os.path.exists(out) and os.path.getsize(out) > 100000:
        print(f"SKIP s{i:02d} (ada)", flush=True); return out
    vf = ("scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
          "setsar=1,fps=30," + overlay_filter(m.get("overlay")) +
          "noise=alls=6:allf=t,format=yuv420p")
    cmd = [FFQ, "-y", "-loglevel", "error",
           "-ss", str(m.get("ss", 0)), "-t", str(m["dur"]), "-i", m["clip"],
           "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-an", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out):
        print(f"GAGAL s{i:02d}: {r.stderr[-500:]}", flush=True); sys.exit(1)
    print(f"OK s{i:02d} ({m['dur']}s) {os.path.basename(m['clip'])}", flush=True)
    return out

def main():
    man = json.load(open(os.path.join(D, "manifest.json")))
    total = sum(m["dur"] for m in man)
    print(f"Segmen: {len(man)}, total {total:.1f}s (VO 451.7s)")
    segs = [build_seg(i, m) for i, m in enumerate(man)]
    lst = os.path.join(SEG, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")  # absolute path
    vcat = os.path.join(D, "out/vconcat.mp4")
    r = subprocess.run([FFQ, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", lst, "-c", "copy", vcat], capture_output=True, text=True)
    if r.returncode != 0: print("GAGAL concat:", r.stderr[-500:]); sys.exit(1)
    vd = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                               "-of", "csv=p=0", vcat], capture_output=True, text=True).stdout.strip())
    if abs(vd - total) > 8:
        print(f"GAGAL VERIFIKASI CONCAT: {vd:.1f}s vs {total:.1f}s — berhenti sebelum mux")
        sys.exit(1)
    print(f"OK concat ({vd:.1f}s)", flush=True)
    final = os.path.join(D, "out/kisah-alkitab-2026-10-14-long.mp4")
    tmp = final + ".tmp.mp4"
    r = subprocess.run([FFQ, "-y", "-loglevel", "error", "-i", vcat, "-i", VO,
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
                        "-c:a", "aac", "-b:a", "128k", "-shortest", tmp],
                       capture_output=True, text=True)
    if r.returncode != 0: print("GAGAL mux:", r.stderr[-500:]); sys.exit(1)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", tmp], capture_output=True, text=True).stdout.strip())
    # ATURAN AGENTS.md 2026-10-14: verifikasi durasi SEBELUM timpa final
    if abs(dur - total) > 8:
        print(f"GAGAL VERIFIKASI DURASI: {dur:.1f}s vs ekspektasi {total:.1f}s — final TIDAK ditimpa, temp disimpan: {tmp}")
        sys.exit(1)
    os.replace(tmp, final)
    print(f"SELESAI: {final} ({dur:.1f}s, {os.path.getsize(final)//1024//1024}MB)")

if __name__ == "__main__":
    main()
