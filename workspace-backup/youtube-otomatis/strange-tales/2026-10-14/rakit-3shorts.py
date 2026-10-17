#!/usr/bin/env python3
"""Rakit 3 Shorts Strange Tales 2026-10-14 — v3.
v2 (4 chain decode paralel dalam 1 ffmpeg) kena OOM-kill di VM 8GB yang padat
(mati di frame 512/918 tanpa pesan error, RAM tersisa ~200MB).
v3: MAKS 2 chain decode per operasi ffmpeg -> 3 operasi per short:
  op1: seg0+seg1 -> partA.mp4 (video saja)
  op2: seg2+seg3 -> partB.mp4 (video saja)
  op3: concat partA+partB + VO -> tmp.mp4, verifikasi durasi, pindah ke final.
Total 9 operasi antrean. SEMUA ffmpeg WAJIB lewat ffmpeg-queue.sh.
Aturan AGENTS.md 2026-10-14: tulis ke TEMP, verifikasi durasi via ffprobe
(|durasi-expected| < 5 dtk), BARU pindahkan ke path final.
Teks drawtext: TANPA '%' dan TANPA apostrof.
Footage: Wikimedia Commons, lisensi terverifikasi per file (lihat run-state).
dragons-blood: 4 foto (tidak ada video Dracaena di Commons) + gerak Ken Burns.
"""
import subprocess, os, shutil, glob

D = "/home/hatch/workspace/youtube-otomatis/strange-tales/2026-10-14"
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
    """Return (input_args, filter_chain) untuk satu segmen."""
    if s[0] == "v":
        _, src, ss, dur, cap = s
        ia = ["-ss", str(ss), "-t", str(dur), "-i", os.path.join(C, src)]
        fc = f"[{i}:v]{COVER},{drawtext(cap)},{GRAIN},setpts=PTS-STARTPTS,fps={FPS}[v{i}]"
    else:
        _, src, dur, cap, zin = s
        n = int(round(dur * FPS))
        z = f"min(1+0.15*on/{n},1.15)" if zin else f"max(1.15-0.15*on/{n},1.0)"
        zp = (f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
              f"d={n}:s=1080x1920:fps={FPS}")
        ia = ["-i", os.path.join(C, src)]
        fc = f"[{i}:v]{COVER},{zp},{drawtext(cap)},{GRAIN},setpts=PTS-STARTPTS[v{i}]"
    return ia, fc

def part_valid(path):
    """Valid hanya jika ffprobe OK dan SAR 1:1 (syarat concat)."""
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
    {"slug": "movile-cave", "vo": "vo-movile-cave.mp3", "vo_dur": 30.600,
     "final": "strange-tales-2026-10-14-movile-cave.mp4",
     "segs": [
        ("v", "black-chasm-1080.webm", 2.0, 7.7, "A CAVE SEALED\nFOR 5.5 MILLION YEARS"),
        ("v", "black-chasm-1080.webm", 25.0, 7.7, "NO SUNLIGHT\nYET FULL OF LIFE"),
        ("v", "black-chasm-1080.webm", 50.0, 7.7, "48 SPECIES FOUND\nNOWHERE ELSE ON EARTH"),
        ("v", "black-chasm-1080.webm", 70.0, 7.5, "HIT SUBSCRIBE\nFOR MORE STRANGE TALES"),
     ]},
    {"slug": "dragons-blood", "vo": "vo-dragons-blood.mp3", "vo_dur": 30.792,
     "final": "strange-tales-2026-10-14-dragons-blood.mp4",
     "segs": [
        ("p", "dragon-tree-2.jpg", 7.7, "TREES THAT BLEED\nRED ON SOCOTRA", True),
        ("p", "dragon-tree-1.jpg", 7.7, "UMBRELLAS LIKE\nLANDED UFOs", False),
        ("p", "dragon-tree-3.jpg", 7.7, "ISOLATED FOR\n6 MILLION YEARS", True),
        ("p", "dragon-tree-4.jpg", 7.69, "HIT SUBSCRIBE\nFOR MORE STRANGE TALES", False),
     ]},
    {"slug": "green-flash", "vo": "vo-green-flash.mp3", "vo_dur": 29.712,
     "final": "strange-tales-2026-10-14-green-flash.mp4",
     "segs": [
        ("v", "pacific-01-1080.webm", 0.0, 7.5, "THE SUN CAN FLASH\nGREEN AT SUNSET"),
        ("v", "pacific-01-1080.webm", 12.0, 7.5, "ONE OR TWO SECONDS\nOF EMERALD FIRE"),
        ("v", "zeitraffer-1080.webm", 0.0, 7.4, "THE ATMOSPHERE SPLITS\nSUNLIGHT LIKE A PRISM"),
        ("v", "zeitraffer-1080.webm", 8.0, 7.31, "HIT SUBSCRIBE\nFOR MORE STRANGE TALES"),
     ]},
]

# bersihkan sisa tmp gagal v2
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
