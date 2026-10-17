#!/usr/bin/env python3
"""Rakit video truecrime-en 2026-10-06: Ken Burns ringan (1280x720 langsung,
preset veryfast — anti OOM), resume dari _tmp_segs, lalu burn-in text overlay
di 5 beat kunci. Semua ffmpeg via ffmpeg-queue.sh."""
import subprocess, os, glob, sys, json, shutil

BASE = "/home/hatch/workspace/youtube-otomatis/truecrime-en"
GDIR = os.path.join(BASE, "gambar/2026-10-06")
AUDIO = os.path.join(BASE, "audio/gabungan-2026-10-06.mp3")
DJ = os.path.join(BASE, "audio/durasi-beat-2026-10-06.json")
OUT = os.path.join(BASE, "video/2026-10-06.mp4")
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of",
                        "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def kenburns_light(img, seg_dur, idx, out):
    total_frames = max(1, int(seg_dur * 30))
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
    r = subprocess.run([FFQ, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True)
    return r.returncode == 0

def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")

def main():
    imgs = sorted(glob.glob(os.path.join(GDIR, "*.jpg")) +
                  glob.glob(os.path.join(GDIR, "*.webp")))
    assert len(imgs) == 75, f"gambar: {len(imgs)} (butuh 75)"
    dj = json.load(open(DJ))
    seg_durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(75)]
    beats = json.load(open(os.path.join(BASE, "script/beats-2026-10-06.json")))
    print(f"{len(imgs)} gambar, target {sum(seg_durs)/60:.1f} mnt", flush=True)
    tmpd = os.path.join(os.path.dirname(OUT), "_tmp_segs")
    os.makedirs(tmpd, exist_ok=True)
    for i, img in enumerate(imgs):
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        ok = os.path.exists(s) and dur(s) >= seg_durs[i] * 0.9
        if ok:
            continue
        if os.path.exists(s):
            os.remove(s)
        print(f"  render s{i:03d} ({seg_durs[i]:.1f}s)...", flush=True)
        for attempt in range(2):
            if kenburns_light(img, seg_durs[i], i, s) and dur(s) >= seg_durs[i] * 0.9:
                break
            print(f"    retry s{i:03d} (attempt {attempt+2})", flush=True)
        else:
            print(f"GAGAL: s{i:03d}"); sys.exit(1)
        if (i + 1) % 5 == 0:
            print(f"  {i+1}/75 segmen...", flush=True)
    segs = [os.path.join(tmpd, f"s{i:03d}.mp4") for i in range(75)]
    assert all(os.path.exists(s) for s in segs)
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    concat = os.path.join(tmpd, "concat.mp4")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)
    # timestamp kumulatif untuk overlay
    cum, overlays = 0.0, []
    for i, b in enumerate(beats):
        if "overlay" in b:
            overlays.append((b["overlay"], cum, cum + seg_durs[i]))
        cum += seg_durs[i]
    print("overlays:", [(t, round(a, 1), round(c, 1)) for t, a, c in overlays],
          flush=True)
    # mux audio dulu
    muxed = os.path.join(tmpd, "muxed.mp4")
    subprocess.run([FFQ, "-y", "-i", concat, "-i", AUDIO,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", muxed],
                   capture_output=True, check=True)
    # burn-in overlay via drawtext
    dts = []
    for text, a, c in overlays:
        dts.append(
            f"drawtext=fontfile={FONT}:text='{esc(text)}':"
            f"fontsize=44:fontcolor=white:borderw=2:bordercolor=black@0.8:"
            f"box=1:boxcolor=black@0.55:boxborderw=18:"
            f"x=(w-text_w)/2:y=90:enable='between(t\\,{a:.2f}\\,{c:.2f})'")
    vf = ",".join(dts)
    subprocess.run([FFQ, "-y", "-i", muxed, "-vf", vf,
                    "-c:v", "libx264", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", OUT],
                   capture_output=True, check=True)
    print(f"OK: {OUT} ({dur(OUT)/60:.1f} menit)", flush=True)
    shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
