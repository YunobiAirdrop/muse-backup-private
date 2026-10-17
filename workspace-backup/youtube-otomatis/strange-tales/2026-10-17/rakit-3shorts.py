#!/usr/bin/env python3
"""Rakit 3 Shorts Strange Tales 2026-10-17 — pola 2026-10-15 + Ken Burns utk foto.
MAKS 2 chain decode per operasi ffmpeg -> 3 operasi per short:
  op1: seg0+seg1 -> partA.mp4 ; op2: seg2+seg3 -> partB.mp4
  op3: concat partA+partB + VO -> tmp.mp4, verifikasi durasi, pindah ke final.
SEMUA ffmpeg WAJIB lewat ffmpeg-queue.sh. setsar=1 setelah crop.
Teks drawtext: TANPA '%', TANPA apostrof, ':' di-escape.
Foto: tidak ada video Lake Hillier di Commons -> Ken Burns di foto asli (CC BY-SA).
"""
import subprocess, os, shutil, glob

D = "/home/hatch/workspace/youtube-otomatis/strange-tales/2026-10-17"
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

def zoompan(motion, dframes):
    n = dframes - 1
    if motion == "zin":
        zp = f"z='1+0.0012*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif motion == "zout":
        zp = f"z='1.32-0.0012*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    else:  # pan
        zp = f"z='1.25':x='(iw-iw/zoom)*on/{n}':y='ih/2-(ih/zoom/2)'"
    return f"zoompan={zp}:d={dframes}:s=1080x1920:fps={FPS}"

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
    # s = (kind, src, ss, dur, cap, motion)
    kind, src, ss, dur, cap, motion = s
    if kind == "img":
        ia = ["-i", os.path.join(C, src)]
        vf = f"{COVER},{zoompan(motion, int(round(dur*FPS)))}"
    else:
        ia = ["-ss", str(ss), "-t", str(dur), "-i", os.path.join(C, src)]
        vf = COVER
    fc = f"[{i}:v]{vf},{drawtext(cap)},{GRAIN},setpts=PTS-STARTPTS,fps={FPS}[v{i}]"
    return ia, fc

def part_valid(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=sample_aspect_ratio,duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    if r.returncode != 0:
        return False
    return r.stdout.strip().startswith("1:1,")

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

# durasi VO: lake 34.632 / meat 31.464 / jelly 30.600
SHORTS = [
    {"slug": "lake-hillier", "vo": "vo-lake-hillier.mp3", "vo_dur": 34.632,
     "final": "strange-tales-2026-10-17-lake-hillier.mp4",
     "segs": [
        ("img", "lake-hillier2.jpg", 0, 8.66, "A LAKE THAT IS\nBUBBLEGUM PINK", "zin"),
        ("img", "lake-gooseisland.jpg", 0, 8.66, "ALGAE + BACTERIA\nPAINT IT PINK", "pan"),
        ("img", "lake-hillier2.jpg", 0, 8.66, "SAFE TO SWIM\nSTILL UNREAL", "zout"),
        ("img", "lake-gooseisland.jpg", 0, 8.65, "HIT SUBSCRIBE\nFOR MORE STRANGE TALES", "zin"),
     ]},
    {"slug": "kentucky-meat-shower", "vo": "vo-kentucky-meat-shower.mp3", "vo_dur": 31.464,
     "final": "strange-tales-2026-10-17-kentucky-meat-shower.mp4",
     "segs": [
        ("vid", "meat-clouds-1080.webm", 2.0, 7.87, "IN 1876\nMEAT FELL FROM THE SKY", ""),
        ("vid", "meat-wheat-1080.webm", 1.0, 7.87, "FRESH MEAT\nRAINED FOR MINUTES", ""),
        ("vid", "meat-vulture-1080.webm", 2.0, 7.87, "LEADING THEORY\nFLYING VULTURES", ""),
        ("vid", "meat-condor-1080.webm", 1.0, 7.85, "HIT SUBSCRIBE\nFOR MORE STRANGE TALES", ""),
     ]},
    {"slug": "upside-down-jellyfish", "vo": "vo-upside-down-jellyfish.mp3", "vo_dur": 30.600,
     "final": "strange-tales-2026-10-17-upside-down-jellyfish.mp4",
     "segs": [
        ("vid", "jelly-cassiopea-1080.webm", 2.0, 7.65, "UPSIDE DOWN\nJELLYFISH", ""),
        ("vid", "jelly-monterey11-1080.webm", 2.0, 8.70, "IT FARMS\nSUNLIGHT", ""),
        ("vid", "jelly-monterey14-1080.webm", 0.0, 6.45, "ALGAE INSIDE\nMAKE ITS FOOD", ""),
        ("vid", "jelly-monterey15-1080.webm", 2.0, 7.80, "HIT SUBSCRIBE\nFOR MORE STRANGE TALES", ""),
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
