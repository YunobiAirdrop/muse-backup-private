#!/usr/bin/env python3
"""Batch rakit mystery-en: 6 gambar per 1 panggilan ffmpeg-queue (hemat slot antrean).
Penggunaan: python3 batch_rakit.py <dir_gambar> <file_audio> <output> <durasi_json>
Menghasilkan batch-*.mp4 di <outdir>/_tmp_batch (resume: batch valid dilewati),
lalu concat + mux audio jadi output final (base, tanpa subtitle/overlay)."""
import subprocess, os, glob, sys, json, shutil

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BATCH = int(os.environ.get("BATCHN","6"))

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def zp_expr(idx, frames):
    mode = idx % 4
    if mode == 0:
        return f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    if mode == 1:
        return f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='(iw-iw/zoom)*on/{frames}':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    if mode == 2:
        return f"zoompan=z='max(1.15-0.0012*on,1.0)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    return f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{frames}':s=1280x720:fps=30"

def render_batch(imgs, durs, start_idx, out):
    args = [FFQ, "-y"]
    for img, d in zip(imgs, durs):
        args += ["-loop", "1", "-t", str(d), "-i", img]
    fc = []
    for j, (img, d) in enumerate(zip(imgs, durs)):
        frames = int(d * 30)
        fc.append(f"[{j}:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
                  f"{zp_expr(start_idx + j, frames)},trim=end_frame={frames},setpts=PTS-STARTPTS[v{j}]")
    fc.append("".join(f"[v{j}]" for j in range(len(imgs))) +
              f"concat=n={len(imgs)}:v=1:a=0,eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
              "noise=alls=6:allf=t,vignette=PI/5,format=yuv420p[out]")
    args += ["-filter_complex", ";".join(fc), "-map", "[out]",
             "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", out]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:]); return False
    return True

def main():
    gdir, audio, out, dur_json = sys.argv[1:5]
    imgs = sorted(glob.glob(os.path.join(gdir, "*.webp")))
    dj = json.load(open(dur_json))
    seg_durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(len(imgs))]
    print(f"{len(imgs)} gambar, target {sum(seg_durs)/60:.1f} mnt", flush=True)
    tmpd = os.path.join(os.path.dirname(out), "_tmp_batch")
    os.makedirs(tmpd, exist_ok=True)
    batches = []
    for b in range(0, len(imgs), BATCH):
        bpath = os.path.join(tmpd, f"batch-{b//BATCH:02d}.mp4")
        bdurs = seg_durs[b:b+BATCH]
        if os.path.exists(bpath) and dur(bpath) >= sum(bdurs) * 0.9:
            print(f"  batch {b//BATCH}: skip (sudah ada)", flush=True)
        else:
            if os.path.exists(bpath): os.remove(bpath)
            print(f"  batch {b//BATCH}: render {len(bdurs)} gambar ({sum(bdurs):.0f}s)...", flush=True)
            if not render_batch(imgs[b:b+BATCH], bdurs, b, bpath):
                print(f"GAGAL batch {b//BATCH}"); sys.exit(1)
            print(f"  batch {b//BATCH}: OK ({dur(bpath):.0f}s)", flush=True)
        batches.append(bpath)
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for s in batches: f.write(f"file '{os.path.abspath(s)}'\n")
    concat = os.path.join(tmpd, "concat.mp4")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", concat],
                   capture_output=True, check=True)
    subprocess.run([FFQ, "-y", "-i", concat, "-i", audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", out],
                   capture_output=True, check=True)
    print(f"OK: {out} ({dur(out)/60:.1f} menit)", flush=True)
    shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
