#!/usr/bin/env python3
"""Rakit video Cosmic Unknown 2026-10-09: 72 gambar Ken Burns 1280x720
+ voiceover + film grain + grading natural + text overlay momen kunci.
Penggunaan: python3 rakit_space_720.py
"""
import subprocess, os, glob, json, shutil

BASE = "/home/hatch/workspace/youtube-otomatis/space-en"
GDIR = os.path.join(BASE, "gambar/2026-10-09")
AUDIO = os.path.join(BASE, "audio/2026-10-09/voiceover-full.mp3")
DUR_JSON = os.path.join(BASE, "script/durasi-segmen-2026-10-09.json")
OUT = os.path.join(BASE, "video/2026-10-09.mp4")
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (beat narasi, teks overlay) — tampil selama beat tsb
OVERLAYS = [
    (2, "500 MILLION SUNS... IN A MILLISECOND"),
    (5, "THOUSANDS SCREAM EVERY DAY"),
    (7, "A MAGNET 1 QUADRILLION TIMES EARTH"),
    (9, "CAUGHT RED-HANDED IN OUR GALAXY"),
    (13, "WEIGHING THE INVISIBLE UNIVERSE"),
]

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def kenburns(img, seg_dur, idx, out):
    total_frames = max(int(seg_dur * 30), 15)
    mode = idx % 4
    if mode == 0:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode == 1:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='(iw-iw/zoom)*on/{total_frames}':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode == 2:
        zp = f"zoompan=z='max(1.15-0.0012*on,1.0)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    else:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{total_frames}':s=1280x720:fps=30"
    vf = (f"scale=1280:720,{zp},"
          "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
          "noise=alls=6:allf=t,"
          "vignette=PI/5")
    r = subprocess.run([FFQ, "-y", "-loop", "1", "-i", img, "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True)
    return r.returncode == 0

def main():
    dj = json.load(open(DUR_JSON))
    n = len(dj)
    imgs = []
    for k in range(1, n + 1):
        narration_beat = (k - 1) // 4 + 1
        variant = "abcd"[(k - 1) % 4]
        name = f"beat-{narration_beat:03d}-{variant}.webp"
        p = os.path.join(GDIR, name)
        if not os.path.exists(p):
            print(f"GAMBAR HILANG: {name}"); return
        imgs.append(p)
    seg_durs = [float(dj[f"beat-{k:03d}"]) for k in range(1, n + 1)]
    print(f"{len(imgs)} gambar, total {sum(seg_durs):.0f}s", flush=True)

    tmpd = os.path.join(BASE, "video", "_tmp_segs_2026-10-09")
    os.makedirs(tmpd, exist_ok=True)
    segs = []
    for i, img in enumerate(imgs):
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        ok = os.path.exists(s) and dur(s) >= seg_durs[i] * 0.9
        if not ok:
            if os.path.exists(s): os.remove(s)
            for attempt in range(2):
                if kenburns(img, seg_durs[i], i, s) and dur(s) >= seg_durs[i] * 0.9:
                    break
                print(f"  retry s{i:03d}", flush=True)
        segs.append(s)
        if (i + 1) % 12 == 0: print(f"  {i+1}/{len(imgs)} segmen...", flush=True)

    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for s in segs: f.write(f"file '{s}'\n")
    concat = os.path.join(tmpd, "concat.mp4")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", concat],
                   capture_output=True, check=True)
    raw = os.path.join(BASE, "video", "2026-10-09-raw.mp4")
    subprocess.run([FFQ, "-y", "-i", concat, "-i", AUDIO, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "128k", "-shortest", "-movflags", "+faststart", raw],
                   capture_output=True, check=True)
    print("mux OK:", raw, flush=True)

    # text overlay pass (timestamp absolut per beat narasi)
    cum = [0.0]
    for k in range(1, n + 1):
        cum.append(cum[-1] + seg_durs[k - 1])
    filters = []
    for beat, teks in OVERLAYS:
        s = cum[(beat - 1) * 4]
        e = cum[beat * 4]
        filters.append(
            f"drawtext=fontfile={FONT}:text='{teks}':fontsize=54:fontcolor=white:"
            f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.78:"
            f"enable='between(t,{s:.2f},{e:.2f})'"
        )
    vf = ",".join(filters)
    r = subprocess.run([FFQ, "-y", "-i", raw, "-vf", vf, "-c:v", "libx264",
                        "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                        "-c:a", "copy", OUT], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:]); return
    print(f"OK: {OUT} ({dur(OUT)/60:.1f} menit)")
    shutil.rmtree(tmpd, ignore_errors=True)
    if os.path.exists(raw): os.remove(raw)

if __name__ == "__main__":
    main()
