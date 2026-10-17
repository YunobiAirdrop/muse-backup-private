#!/usr/bin/env python3
"""Rakit video final promo 2026-10-08: seg1+voice, seg2+voice, concat, encode WA-friendly.
Pakai ffmpeg-queue.sh (bukan ffmpeg mentah) sesuai AGENTS.md.
Fallback: kalau segmen media-generation tidak ada, pakai video Ken Burns fallback.
Normalisasi 540x960 sebelum concat agar aman bila sumber campur AI + Ken Burns."""
import json, os, subprocess, glob

FFQ = os.path.expanduser("~/workspace/youtube-otomatis/ffmpeg-queue.sh")
OUT = os.path.expanduser("~/workspace/blog-otomatis/promo_out")

def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(r.stdout.strip())

def run(cmd):
    # timeout 3600: antrean ffmpeg-queue bisa padat saat cron YouTube 16:11 render
    # bareng; tiap op cepat (<60 dtk) begitu dapat slot.
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-500:])
    return r

def seg_mp4(slug, seg, fallback):
    cands = sorted(glob.glob(os.path.join(OUT, f"media-generation-{seg}-{slug}-*.mp4")))
    if cands:
        return cands[0], "AI"
    return fallback, "KenBurns"

manifest = json.load(open(os.path.join(OUT, "manifest_2026-10-08.json")))
hasil = {}
for prod in manifest["produk"]:
    slug = prod["file_gambar"].replace(".jpg", "")
    nama = prod["nama"]
    print(f">> {slug} ({nama})", flush=True)
    fb = prod["video_fallback"]
    v1, src1 = seg_mp4(slug, "seg1", fb)
    v2, src2 = seg_mp4(slug, "seg2", fb)
    print(f"   seg1={src1} seg2={src2}", flush=True)
    a1 = os.path.join(OUT, f"voice_seg1_{slug}.mp3")
    a2 = os.path.join(OUT, f"voice_seg2_{slug}.mp3")
    d1, d2 = dur(a1), dur(a2)
    s1v = os.path.join(OUT, f"seg1v_{slug}.mp4")
    s2v = os.path.join(OUT, f"seg2v_{slug}.mp4")
    pad1 = max(0.0, d1 - 10.0)
    pad2 = max(0.0, d2 - 10.0)
    norm = "scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2"
    run([FFQ, "-y", "-i", v1, "-i", a1,
         "-filter_complex", f"[0:v]{norm},tpad=stop_mode=clone:stop_duration={pad1:.2f}[v]",
         "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", s1v])
    run([FFQ, "-y", "-i", v2, "-i", a2,
         "-filter_complex", f"[0:v]{norm},tpad=stop_mode=clone:stop_duration={pad2:.2f}[v]",
         "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", s2v])
    lst = os.path.join(OUT, f"concat_{slug}.txt")
    open(lst, "w").write(f"file '{s1v}'\nfile '{s2v}'\n")
    final = os.path.join(OUT, f"video_final_{slug}.mp4")
    run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final])
    wa = os.path.join(OUT, f"video_final_{slug}_wa.mp4")
    run([FFQ, "-y", "-i", final, "-vf", "scale=540:-2", "-c:v", "libx264",
         "-profile:v", "baseline", "-level", "3.0", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-movflags", "+faststart", wa])
    df = dur(final)
    print(f"   final={df:.1f}s wa={os.path.getsize(wa)//1024}KB", flush=True)
    hasil[slug] = {"final": final, "wa": wa, "durasi": round(df, 1),
                   "seg1": src1, "seg2": src2}

json.dump(hasil, open(os.path.join(OUT, "rakit_2026-10-08.json"), "w"), indent=1)
print("RAKIT SELESAI", flush=True)
