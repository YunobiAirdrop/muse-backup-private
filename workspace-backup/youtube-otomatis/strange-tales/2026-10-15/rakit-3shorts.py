#!/usr/bin/env python3
"""Rakit 3 Shorts Strange Tales 2026-10-15 — v3 (salin pola 2026-10-14).
MAKS 2 chain decode per operasi ffmpeg -> 3 operasi per short:
  op1: seg0+seg1 -> partA.mp4 ; op2: seg2+seg3 -> partB.mp4
  op3: concat partA+partB + VO -> tmp.mp4, verifikasi durasi, pindah ke final.
SEMUA ffmpeg WAJIB lewat ffmpeg-queue.sh. setsar=1 setelah crop.
Teks drawtext: TANPA '%', TANPA apostrof, ':' di-escape.
"""
import subprocess, os, shutil, glob

D = "/home/hatch/workspace/youtube-otomatis/strange-tales/2026-10-15"
C = os.path.join(D, "clips")
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
FPS = 30

def esc(t):
    return t.replace(":", "\\:").replace("'", "\u2019")

def drawtext(cap):
    return (f"drawtext=text='{esc(cap)}':fontfile={FONT}:fontsize=54:fontcolor=white:"
            "borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=h-460:"
            "box=1:boxcolor=black@0.45:boxborderw=24")

GRAIN = "noise=alls=8:allf=t,format=yuv420p"
COVER = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"

def run(args, label):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAILED {label}:\n{r.stderr[-2000:]}", flush=True)
        raise SystemExit(1)
    print(f"OK {label}", flush=True)

def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())

def seg_chain(i, s):
    _, src, ss, dur, cap = s
    ia = ["-ss", str(ss), "-t", str(dur), "-i", os.path.join(C, src)]
    fc = f"[{i}:v]{COVER},{drawtext(cap)},{GRAIN},setpts=PTS-STARTPTS,fps={FPS}[v{i}]"
    return ia, fc

def part_valid(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=sample_aspect_ratio,duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    if r.returncode != 0:
        return False
    out = r.stdout.strip()
    return out.startswith("1:1,")

def build_part(slug, part, segs):
    out = os.path.join(D, f"{slug}-{part}.mp4")
    if os.path.exists(out) and part_valid(out):
        print(f"SKIP existing valid {out}", flush=True)
        return out
    if os.path.exists(out):
        print(f"hapus part tidak valid: {out}", flush=True)
        os.remove(out)
    args = [FFQ, "-y"]
    chains = []
    for i, s in enumerate(segs):
        ia, fc = seg_chain(i, s)
        args += ia
        chains.append(fc)
    chains.append("[v0][v1]concat=n=2:v=1:a=0[vv]")
    args += ["-filter_complex", ";".join(chains), "-map", "[vv]",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
             "-r", str(FPS), "-an", out]
    run(args, f"{slug} {part}")
    return out

SHORTS = [
    {"slug": "the-hum", "vo": "vo-the-hum.mp3", "vo_dur": 28.608,
     "final": "strange-tales-2026-10-15-the-hum.mp4",
     "segs": [
        ("v", "hum-city-1080.webm", 2.0, 7.2, "A HUM THAT\nNEVER STOPS"),
        ("v", "hum-ljubljana-1080.webm", 10.0, 7.2, "MILLIONS HEAR IT\nSCIENCE HAS NO ANSWER"),
        ("v", "hum-powerline-1080.webm", 0.0, 7.1, "NOT THE SEA\nNOT MACHINES"),
        ("v", "hum-celltower-480.webm", 5.0, 7.1, "HIT SUBSCRIBE\nFOR MORE STRANGE TALES"),
     ]},
    {"slug": "lluvia-de-peces", "vo": "vo-lluvia-de-peces.mp3", "vo_dur": 34.272,
     "final": "strange-tales-2026-10-15-lluvia-de-peces.mp4",
     "segs": [
        ("v", "pez-rain-1080.webm", 1.0, 8.6, "FISH FALL\nFROM THE SKY"),
        ("v", "pez-fish1-1080.webm", 2.0, 8.6, "THOUSANDS OF FISH\nSTILL ALIVE"),
        ("v", "pez-fish2-1080.webm", 10.0, 8.6, "NO ONE HAS EVER SEEN\nIT HAPPEN"),
        ("v", "pez-river-1080.webm", 20.0, 8.47, "HIT SUBSCRIBE\nFOR MORE STRANGE TALES"),
     ]},
    {"slug": "blob-slime", "vo": "vo-blob-slime.mp3", "vo_dur": 29.712,
     "final": "strange-tales-2026-10-15-blob-slime.mp4",
     "segs": [
        ("v", "blob-physarum-1080.webm", 0.0, 7.43, "NO BRAIN\nYET IT SOLVED A MAZE"),
        ("v", "blob-aus-1080.webm", 2.0, 7.43, "ONE CELL\nFOUND THE SHORTEST PATH"),
        ("v", "blob-intra-1080.webm", 5.0, 7.43, "IT REMEMBERS\nIT LEARNS"),
        ("v", "blob-timelapse-480.webm", 2.0, 7.42, "HIT SUBSCRIBE\nFOR MORE STRANGE TALES"),
     ]},
]

for t in glob.glob(os.path.join(D, "*.tmp.mp4")):
    os.remove(t)
    print(f"hapus sisa gagal: {os.path.basename(t)}", flush=True)

for sh in SHORTS:
    final = os.path.join(D, sh["final"])
    if os.path.exists(final) and os.path.getsize(final) > 10000:
        d = duration(final)
        assert abs(d - sh["vo_dur"]) < 5, f"final rusak {sh['slug']}"
        print(f"SKIP final existing {sh['final']} ({d:.2f}s)", flush=True)
        continue
    a = build_part(sh["slug"], "partA", sh["segs"][:2])
    b = build_part(sh["slug"], "partB", sh["segs"][2:])
    tmp = final + ".tmp.mp4"
    run([FFQ, "-y", "-i", a, "-i", b, "-i", os.path.join(D, sh["vo"]),
         "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[vv]",
         "-map", "[vv]", "-map", "2:a",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
         "-c:a", "aac", "-b:a", "128k",
         "-shortest", "-movflags", "+faststart", tmp],
        f"{sh['slug']} mux")
    d = duration(tmp)
    assert abs(d - sh["vo_dur"]) < 5, f"DURASI SALAH {sh['slug']}: {d} vs VO {sh['vo_dur']}"
    print(f"DURASI OK {sh['slug']}: {d:.2f}s (VO {sh['vo_dur']})", flush=True)
    shutil.move(tmp, final)

print("ALL DONE")
