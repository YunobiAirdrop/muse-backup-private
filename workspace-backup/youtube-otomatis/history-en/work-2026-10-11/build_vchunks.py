#!/usr/bin/env python3
"""Render video history-en 2026-10-11 per chunk (concat FILTER, sinkron pasti).
6 chunk video -> concat demuxer copy -> mux dengan gabungan-final (619.4s).
Drawtext per chunk memakai jendela waktu lokal (dari windows.json global).
Tanpa karakter persen di teks drawtext. Semua ffmpeg via ffmpeg-queue.sh.
"""
import subprocess, json, os, sys

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
W = os.path.join(BASE, "work-2026-10-11")
ADIR = os.path.join(BASE, "audio", "2026-10-11")
GDIR = os.path.join(BASE, "gambar", "2026-10-11", "final")
GAB = os.path.join(ADIR, "gabungan-final-2026-10-11.mp3")
SILENT2 = os.path.join(BASE, "video", "_silent2-2026-10-11.mp4")
OUT = os.path.join(BASE, "video", "2026-10-11.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DJ = json.load(open(os.path.join(ADIR, "durasi-beat-2026-10-11.json")))
WIN = json.load(open(os.path.join(W, "windows.json")))
WINS = {int(k): v for k, v in WIN["wins"].items()}
OVERLAYS = {int(k): v for k, v in WIN["overlays"].items()}
BUMPER_WIN = WIN["bumper"]
TOTAL = WIN["total"]
BD = 4.29

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def tf(name, text):
    p = os.path.join(W, f"dt-{name}.txt")
    open(p, "w").write(text)
    return p

# segmen global: (label, gambar atau 'BLACK', mulai, durasi)
segs = [("title", "BLACK", 0.0, 3.0)]
t = 3.0
for i in range(1, 36):
    d = DJ[f"beat-{i:03d}"]
    segs.append((f"b{i}", os.path.join(GDIR, f"scene-{i:03d}.jpg"), t, d))
    t += d
segs.append(("bumper", os.path.join(GDIR, "scene-036.jpg"), t, BD)); t += BD
for i in range(36, 71):
    d = DJ[f"beat-{i:03d}"]
    segs.append((f"b{i}", os.path.join(GDIR, f"scene-{i:03d}.jpg"), t, d))
    t += d
assert abs(t - TOTAL) < 0.1, (t, TOTAL)

# chunk: rentang segmen berdasarkan indeks beat
chunk_defs = [(0, 13), (13, 25), (25, 38), (38, 50), (50, 62), (62, 73)]

chunk_files = []
for ci, (a, b) in enumerate(chunk_defs):
    parts = segs[a:b]
    cf = os.path.join(W, f"vchunk-{ci}.mp4")
    chunk_files.append(cf)
    expect = sum(p[3] for p in parts)
    if os.path.exists(cf) and abs(dur(cf) - expect) < 1.0:
        print(f"vchunk-{ci}: sudah OK ({dur(cf):.1f}s)", flush=True)
        continue
    start = parts[0][2]
    inputs = []
    fc = []
    for j, (label, img, st, d) in enumerate(parts):
        if img == "BLACK":
            inputs += ["-f", "lavfi", "-i", f"color=c=black:s=1280x720:r=30:d={d}"]
            fc.append(f"[{j}:v]setsar=1,fps=30,trim=duration={d},setpts=PTS-STARTPTS[v{j}]")
        else:
            inputs += ["-loop", "1", "-i", img]
            fc.append(f"[{j}:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1,fps=30,trim=duration={d},setpts=PTS-STARTPTS[v{j}]")
    fc.append("".join(f"[v{j}]" for j in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0[vc]")
    vf = "eq=contrast=1.08:saturation=0.92:brightness=-0.02,noise=alls=6:allf=t,vignette=PI/5"
    if ci == 0:
        vf += (f",drawtext=fontfile={FONT}:textfile={tf('t1','1347:')}:fontsize=110:fontcolor=white:"
               "x=(w-text_w)/2:y=h/2-140:enable='between(t,0,3)'")
        vf += (f",drawtext=fontfile={FONT}:textfile={tf('t2','THE BLACK DEATH CAME ON SHIPS')}:fontsize=46:fontcolor=#ffd97a:"
               "x=(w-text_w)/2:y=h/2+10:enable='between(t,0,3)'")
    for idx, text in OVERLAYS.items():
        s, e = WINS[idx]
        if start - 0.01 <= s < start + expect:
            vf += (f",drawtext=fontfile={FONT}:textfile={tf(f'ov{idx}', text)}:fontsize=46:"
                   "fontcolor=white:borderw=2:bordercolor=black@0.8:"
                   f"x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.55:boxborderw=24:enable='between(t,{s-start:.2f},{e-start:.2f})'")
    cta = tf('cta', 'Subscribe!')
    for (cs, ce) in (BUMPER_WIN, (TOTAL - 5, TOTAL)):
        if start - 0.01 <= cs < start + expect:
            vf += (f",drawtext=fontfile={FONT}:textfile={cta}:fontsize=54:fontcolor=#ffd97a:"
                   "borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=60:box=1:boxcolor=black@0.55:boxborderw=20:"
                   f"enable='between(t,{cs-start:.2f},{ce-start:.2f})'")
    vf += ",format=yuv420p"
    fc.append(f"[vc]{vf}[vout]")
    cmd = [FFQ, "-y", "-threads", "2"] + inputs + [
        "-filter_complex", ";".join(fc), "-map", "[vout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-pix_fmt", "yuv420p", "-r", "30", "-an", cf]
    print(f"vchunk-{ci}: render (target {expect:.1f}s, {len(parts)} segmen)...", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"vchunk-{ci} GAGAL:\n", (r.stderr or "")[-2000:]); sys.exit(1)
    got = dur(cf)
    print(f"vchunk-{ci}: hasil {got:.1f}s (target {expect:.1f}s)", flush=True)
    if abs(got - expect) > 1.5:
        print(f"PERINGATAN: vchunk-{ci} meleset"); sys.exit(2)

lst = os.path.join(W, "vchunklist.txt")
with open(lst, "w") as f:
    for cf in chunk_files:
        f.write(f"file '{cf}'\n")
r = subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", SILENT2],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("concat video GAGAL:\n", (r.stderr or "")[-2000:]); sys.exit(1)
sd = dur(SILENT2)
print(f"silent2: {sd:.1f}s (target {TOTAL:.1f}s)", flush=True)
assert abs(sd - TOTAL) < 2.0, "silent2 masih meleset"
r = subprocess.run([FFQ, "-y", "-i", SILENT2, "-i", GAB,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", OUT],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("mux GAGAL:\n", (r.stderr or "")[-2000:]); sys.exit(1)
print(f"FINAL: {OUT} ({dur(OUT):.1f}s = {dur(OUT)/60:.2f} menit)", flush=True)
