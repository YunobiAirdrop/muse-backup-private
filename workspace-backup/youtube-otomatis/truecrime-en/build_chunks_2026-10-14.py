#!/usr/bin/env python3
"""Build video/2026-10-14.mp4 dari 72 gambar + gabungan-2026-10-14.mp3.
3 chunk via ffmpeg-queue -> concat -> mux audio. (adaptasi build_chunks_2026-10-12.py)"""
import subprocess, os, json, sys
BASE = "/home/hatch/workspace/youtube-otomatis/truecrime-en"
GDIR = f"{BASE}/gambar/2026-10-14"
AUDIO = f"{BASE}/audio/gabungan-2026-10-14.mp3"
OUT = f"{BASE}/video/2026-10-14.mp4"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TMP = f"{BASE}/video/_chunks14"
os.makedirs(TMP, exist_ok=True)
os.makedirs("/tmp/tc-ov14", exist_ok=True)

N = 88
dj = json.load(open(f"{BASE}/audio/durasi-beat-2026-10-14.json"))
beats = json.load(open(f"{BASE}/script/beats-2026-10-14.json"))
bj = json.load(open(f"{BASE}/audio/bumper-2026-10-14.json"))
durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(N)]
cum = [0.0]
for d in durs:
    cum.append(cum[-1] + d)

def overlays_global():
    ov = []
    c = 0.0
    for i, b in enumerate(beats):
        if "overlay" in b:
            ov.append((b["overlay"], c, c + durs[i]))
        if b["id"] == "beat-053":
            ov.append(("SUBSCRIBE - DARK CASE FILES", c, c + durs[i] - bj["dur"]))
        if i == len(beats) - 1:
            ov.append(("SUBSCRIBE FOR THE NEXT FILE", c, c + durs[i]))
        c += durs[i]
    ov.append(("HI, I'M YUNOBI - DARK CASE FILES", bj["start"], bj["start"] + bj["dur"]))
    return ov

OV = overlays_global()
CHUNKS = [(0, 30), (30, 59), (59, 88)]

def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of",
                        "default=noprint_wrappers=1:nokey=1", p],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 0.0

for ci, (a, b) in enumerate(CHUNKS):
    cout = f"{TMP}/chunk{ci}.mp4"
    want = cum[b] - cum[a]
    if os.path.exists(cout) and abs(dur(cout) - want) < 2.0:
        print(f"chunk{ci} exists ok", flush=True)
        continue
    args = [FFQ, "-y"]
    for i in range(a, b):
        args += ["-i", f"{GDIR}/beat-{i+1:03d}.jpg"]
    fc = []
    for k, i in enumerate(range(a, b)):
        d = durs[i]
        frames = max(1, int(d * 30))
        mode = i % 4
        if mode == 0:
            zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
        elif mode == 1:
            zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='(iw-iw/zoom)*on/{frames}':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
        elif mode == 2:
            zp = f"zoompan=z='max(1.15-0.0012*on,1.0)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
        else:
            zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{frames}':s=1280x720:fps=30"
        fc.append(f"[{k}:v]scale=1280:720,{zp},eq=contrast=1.08:saturation=0.92:brightness=-0.02,noise=alls=6:allf=t,vignette=PI/5,setsar=1,trim=duration={d:.3f},setpts=PTS-STARTPTS[v{k}]")
    fc.append("".join(f"[v{k}]" for k in range(b - a)) + f"concat=n={b-a}:v=1:a=0[vc]")
    cur = "[vc]"
    start = cum[a]
    for j, (text, ga, gc) in enumerate(OV):
        if ga >= start and ga < cum[b]:
            tf = f"/tmp/tc-ov14/c{ci}ov{j}.txt"
            open(tf, "w").write(text)
            fc.append(f"{cur}drawtext=fontfile={FONT}:textfile={tf}:fontsize=44:fontcolor=white:borderw=2:bordercolor=black@0.8:box=1:boxcolor=black@0.55:boxborderw=18:x=(w-text_w)/2:y=90:enable='between(t,{ga-start:.2f},{gc-start:.2f})'[vo{j}]")
            cur = f"[vo{j}]"
    fc.append(f"{cur}null[vout]")
    args += ["-filter_complex", ";".join(fc), "-map", "[vout]",
             "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
             "-r", "30", cout]
    print(f"render chunk{ci} beats {a+1}-{b} ({want:.0f}s)...", flush=True)
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print("CHUNK FAIL:", "".join([l for l in r.stderr.splitlines() if "frame=" not in l])[-1200:])
        sys.exit(1)
    print(f"chunk{ci} ok dur {dur(cout):.1f}", flush=True)

lst = f"{TMP}/list.txt"
with open(lst, "w") as f:
    for ci in range(3):
        f.write(f"file '{TMP}/chunk{ci}.mp4'\n")
merged = f"{TMP}/merged.mp4"
r = subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", merged], capture_output=True, text=True)
if r.returncode != 0:
    print("CONCAT FAIL", r.stderr[-800:]); sys.exit(1)
r = subprocess.run([FFQ, "-y", "-i", merged, "-i", AUDIO,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", OUT],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("MUX FAIL", r.stderr[-800:]); sys.exit(1)
print(f"ALL OK: {OUT} dur {dur(OUT):.1f}s", flush=True)
