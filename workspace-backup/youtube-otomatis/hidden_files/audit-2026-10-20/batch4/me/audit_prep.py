#!/usr/bin/env python3
"""Audit video prep: download full video, frames every 10s, contact sheets,
key frames, subs, audio analysis, thumbnail. Input: lines 'slug vid dur views'."""
import os, re, subprocess, sys, glob, shutil
from PIL import Image, ImageDraw

WORK = os.path.dirname(os.path.abspath(__file__))
YTDLP = os.path.expanduser("~/.local/bin/yt-dlp")

def run(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return p

def download(slug, vid):
    out = f"{WORK}/{slug}__{vid}.mp4"
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        return out
    url = f"https://www.youtube.com/watch?v={vid}"
    for attempt in (1, 2):
        r = run([YTDLP, "-q", "--no-warnings",
                 "--extractor-args", "youtube:player_client=android",
                 "--no-playlist", "-f", "b[height<=480]/b",
                 "--merge-output-format", "mp4",
                 "-o", out, url], cwd=WORK)
        if os.path.exists(out) and os.path.getsize(out) > 10000:
            return out
    print(f"GAGAL download {vid} (2x)", flush=True)
    return None

def frames(vid, path):
    d = f"{WORK}/fr_{vid}"
    if glob.glob(f"{d}/f*.jpg") and len(glob.glob(f"{d}/f*.jpg")) > 0:
        return sorted(glob.glob(f"{d}/f*.jpg"))
    os.makedirs(d, exist_ok=True)
    r = run(["ffmpeg", "-y", "-v", "error", "-i", path,
             "-vf", "fps=1/10,scale=320:-1", f"{d}/f%04d.jpg"])
    return sorted(glob.glob(f"{d}/f*.jpg"))

def contact_sheets(vid, files):
    outs = []
    for si in range(0, len(files), 12):
        chunk = files[si:si+12]
        cols, rows = 4, 3
        imgs = [Image.open(f) for f in chunk]
        w, h = imgs[0].size
        sheet = Image.new("RGB", (cols*w, rows*h), (20, 20, 20))
        for i, im in enumerate(imgs):
            sheet.paste(im, ((i % cols)*w, (i//cols)*h))
            ImageDraw.Draw(sheet).text((5+(i%cols)*w, 5+(i//cols)*h),
                                       f"{i*10}s", fill=(255,255,0))
        out = f"{WORK}/sheet_{vid}_{si//12:02d}.jpg"
        sheet.save(out, quality=80)
        outs.append(out)
        for im in imgs: im.close()
    return outs

def keyframes(slug, vid, path, dur):
    for name, ss in (("k1", 1), ("km", max(1, dur//2)), ("ke", max(1, dur-3))):
        out = f"{WORK}/key_{vid}_{name}.jpg"
        if not os.path.exists(out):
            run(["ffmpeg", "-y", "-v", "error", "-ss", str(ss), "-i", path,
                 "-frames:v", "1", "-q:v", "3", out])

def subs(slug, vid):
    url = f"https://www.youtube.com/watch?v={vid}"
    run([YTDLP, "-q", "--no-warnings", "--skip-download",
         "--write-auto-subs", "--write-subs",
         "--sub-langs", "en,id", "--sub-format", "vtt",
         "-o", f"{slug}__{vid}.%(ext)s", url], cwd=WORK)

def audio(path, vid):
    out = f"{WORK}/audio_{vid}.txt"
    if os.path.exists(out): return out
    r = run(["ffmpeg", "-y", "-v", "info", "-i", path,
             "-af", "volumedetect,silencedetect=noise=-35dB:d=2",
             "-vn", "-f", "null", "-"], cwd=WORK)
    info = r.stderr
    lines = [l for l in info.splitlines()
             if ("max_volume" in l or "mean_volume" in l or "silence_start" in l
                 or "silence_end" in l)]
    # also duration
    r2 = run(["ffprobe", "-v", "error", "-show_entries",
              "format=duration", "-of", "csv=p=0", path])
    with open(out, "w") as f:
        f.write("DURATION_S: " + r2.stdout.strip() + "\n")
        f.write("\n".join(lines) + "\n")
    return out

def thumb(vid):
    out = f"{WORK}/th_{vid}.jpg"
    if not os.path.exists(out):
        run(["curl", "-sL", f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", "-o", out], cwd=WORK)
    return out

def main():
    daftar = sys.argv[1] if len(sys.argv) > 1 else f"{WORK}/daftar.txt"
    for line in open(daftar):
        line = line.strip()
        if not line: continue
        slug, vid, dur, views = line.split()
        dur = int(dur)
        print(f"== {slug} {vid} ==", flush=True)
        mp4 = download(slug, vid)
        if not mp4:
            open(f"{WORK}/gagal_{vid}.txt", "w").write("tidak_terdownload\n")
            continue
        fs = frames(vid, mp4)
        print(f"   frames: {len(fs)}", flush=True)
        contact_sheets(vid, fs)
        keyframes(slug, vid, mp4, dur)
        subs(slug, vid)
        audio(mp4, vid)
        thumb(vid)
    print("PREP SELESAI", flush=True)

if __name__ == "__main__":
    main()
