#!/usr/bin/env python3
"""Rakit video weird-en 2026-10-07: title card + 132 segmen + overlay teks.
Ringkas: 1280x720 langsung, zoompan Ken Burns, eq, film grain, vignette,
preset veryfast. ffmpeg HANYA via ffmpeg-queue.sh (semaphore max 2).
"""
import subprocess, os, glob, sys, json, shutil, re

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TITLE = "7 Real Animals With ACTUAL Superpowers (You Won't Believe #3)"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

def drawtext_overlay(text):
    return (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize=58:"
            f"fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-150")

def kenburns(img, seg_dur, idx, out, overlay=None):
    total_frames = max(int(seg_dur * 30), 30)
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
    if overlay:
        vf += "," + drawtext_overlay(overlay)
    r = subprocess.run([Q, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("ffmpeg err:", r.stderr[-500:], flush=True)
    return r.returncode == 0

def title_card(out):
    vf = (f"drawtext=fontfile={FONT}:text='{esc('REAL ANIMALS')}':fontsize=110:"
          f"fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=230,"
          f"drawtext=fontfile={FONT}:text='{esc('WITH ACTUAL SUPERPOWERS')}':fontsize=72:"
          f"fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=360,"
          f"drawtext=fontfile={FONT}:text='{esc('Weird World Daily')}':fontsize=44:"
          f"fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=500,"
          "format=yuv420p")
    r = subprocess.run([Q, "-y", "-f", "lavfi", "-i", "color=c=0x0a1628:s=1280x720:d=2.5:r=30",
                        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("title card err:", r.stderr[-500:], flush=True)
    return r.returncode == 0

def main():
    gdir = os.path.join(W, "gambar")
    audio = os.path.join(W, "audio", "gabungan-2026-10-07.mp3")
    dur_json = os.path.join(W, "data", "durasi-beat-2026-10-07.json")
    out = os.path.join(W, "video", "2026-10-07.mp4")
    batches = json.load(open(os.path.join(W, "data", "batches-w7.json")))
    overlay = {}
    for b in batches.values():
        for e in b:
            if e["overlay"]:
                overlay[f"w7-beat-{e['num']}"] = e["overlay"]

    imgs = sorted(glob.glob(os.path.join(gdir, "w7-beat-*.webp")))
    dj = json.load(open(dur_json))
    keys = [f"w7-beat-{i+1:03d}" for i in range(len(imgs))]
    seg_durs = [float(dj[k]) for k in keys]
    print(f"{len(imgs)} gambar, target {sum(seg_durs)/60:.1f} mnt", flush=True)

    tmpd = os.path.join(os.path.dirname(out), "_tmp_segs")
    os.makedirs(tmpd, exist_ok=True)

    # 0. title card
    tc = os.path.join(tmpd, "titlecard.mp4")
    if not (os.path.exists(tc) and dur(tc) >= 2.2):
        if os.path.exists(tc):
            os.remove(tc)
        print("render title card...", flush=True)
        assert title_card(tc) and dur(tc) >= 2.2, "title card gagal"

    # 1. segmen
    for i, img in enumerate(imgs):
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        ok = os.path.exists(s) and dur(s) >= seg_durs[i] * 0.9
        if ok:
            continue
        if os.path.exists(s):
            os.remove(s)
        ov = overlay.get(keys[i])
        print(f"  render s{i:03d} ({seg_durs[i]:.1f}s){' +overlay '+ov if ov else ''}...", flush=True)
        for attempt in range(2):
            if kenburns(img, seg_durs[i], i, s, ov) and dur(s) >= seg_durs[i] * 0.9:
                break
            print(f"    retry s{i:03d} (attempt {attempt+2})", flush=True)
        else:
            print(f"GAGAL: s{i:03d}"); sys.exit(1)
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(imgs)} segmen...", flush=True)

    # 2. concat title + segmen
    segs = [tc] + [os.path.join(tmpd, f"s{i:03d}.mp4") for i in range(len(imgs))]
    assert all(os.path.exists(s) for s in segs), "masih ada segmen hilang"
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    concat = os.path.join(tmpd, "concat.mp4")
    subprocess.run([Q, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)

    # 3. mux audio dengan delay 2.5s (title card)
    vdur = dur(concat)
    subprocess.run([Q, "-y", "-i", concat, "-i", audio,
                    "-filter_complex", "[1:a]adelay=2500|2500,apad[a]",
                    "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-t", str(vdur), "-movflags", "+faststart", out],
                   capture_output=True, check=True)
    print(f"OK: {out} ({dur(out)/60:.1f} menit)")
    shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
