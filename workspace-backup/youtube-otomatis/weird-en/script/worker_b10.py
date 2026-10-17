#!/usr/bin/env python3
"""Worker paralel render segmen b10: merender rentang indeks segmen.
Usage: worker_b10.py <idx_start> <idx_end>  (0-based, end eksklusif)
Contoh: worker_b10.py 21 46  -> segmen s021..s045 (beat 22..46)
Setiap ffmpeg via ffmpeg-queue.sh. Aman di-restart (skip segmen valid).
"""
import subprocess, os, glob, json, sys

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

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

def kenburns(img, seg_dur, idx, out, overlay=None, overlay_dur=None):
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
        base = (f"drawtext=fontfile={FONT}:text='{esc(overlay)}':fontsize=58:"
                f"fontcolor=white:borderw=3:bordercolor=black:"
                f"x=(w-text_w)/2:y=h-150")
        if overlay_dur:
            base += f":enable='between(t,0,{overlay_dur})'"
        vf += "," + base
    r = subprocess.run([Q, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True, text=True)
    return r.returncode == 0

def main():
    i0, i1 = int(sys.argv[1]), int(sys.argv[2])
    gdir = os.path.join(W, "gambar")
    batches = json.load(open(os.path.join(W, "data", "batches-b10.json")))
    overlays = {}
    for b in batches.values():
        for e in b:
            if e["overlay"]:
                overlays[f"b10-beat-{e['num']}"] = (e["overlay"], 3.0 if e["num"] == "036" else None)
    imgs = sorted(glob.glob(os.path.join(gdir, "b10-beat-*.webp")))
    dj = json.load(open(os.path.join(W, "data", "durasi-beat-2026-10-10.json")))
    tmpd = os.path.join(W, "video", "_tmp_segs_b10")
    os.makedirs(tmpd, exist_ok=True)
    done = 0
    for i in range(i0, i1):
        key = f"b10-beat-{i+1:03d}"
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        if os.path.exists(s) and dur(s) >= float(dj[key]) * 0.9:
            done += 1
            continue
        if os.path.exists(s):
            os.remove(s)
        ov = overlays.get(key)
        ok = False
        for _ in range(2):
            if kenburns(imgs[i], float(dj[key]), i, s,
                         overlay=ov[0] if ov else None,
                         overlay_dur=ov[1] if ov else None):
                ok = True
                break
        if not ok:
            print(f"GAGAL s{i:03d}", flush=True); sys.exit(1)
        done += 1
        if done % 5 == 0:
            print(f"worker[{i0}-{i1}]: {done}/{i1-i0}", flush=True)
    print(f"worker[{i0}-{i1}] SELESAI", flush=True)

if __name__ == "__main__":
    main()
