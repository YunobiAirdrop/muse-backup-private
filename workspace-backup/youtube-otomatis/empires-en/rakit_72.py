#!/usr/bin/env python3
"""Rakit video long 72 gambar (ringan: 1280x720 langsung, via ffmpeg-queue.sh).
Penggunaan: python3 rakit_72.py <dir_gambar> <file_audio> <output> <durasi_json_72>
  dir_gambar: berisi 72 *.jpg ter-sortir (beat-001-a ... beat-024-c)
  durasi_json_72: JSON {"beat-001": d, ..., "beat-072": d} durasi tiap segmen
"""
import subprocess, os, glob, sys, json, shutil

QUEUE = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
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
    r = subprocess.run([QUEUE, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True)
    return r.returncode == 0

def main():
    gdir, audio, out, dur_json = sys.argv[1:5]
    imgs = sorted(glob.glob(os.path.join(gdir, "*.jpg")))
    if len(imgs) != 72:
        print(f"PERINGATAN: {len(imgs)} gambar (harusnya 72)")
    dj = json.load(open(dur_json))
    seg_durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(len(imgs))]
    print(f"{len(imgs)} gambar, target {sum(seg_durs)/60:.1f} mnt", flush=True)
    tmpd = os.path.join(os.path.dirname(out), "_tmp_segs")
    os.makedirs(tmpd, exist_ok=True)
    from concurrent.futures import ThreadPoolExecutor
    def _kb(arg):
        i, img = arg
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        ok = os.path.exists(s) and dur(s) >= seg_durs[i] * 0.9
        if ok:
            return True
        if os.path.exists(s):
            os.remove(s)
        for _ in range(2):
            if kenburns_light(img, seg_durs[i], i, s) and dur(s) >= seg_durs[i] * 0.9:
                break
        else:
            print(f"GAGAL: s{i:03d}", flush=True)
            return False
        if (i + 1) % 6 == 0:
            print(f"  {i+1}/{len(imgs)} segmen...", flush=True)
        return True
    with ThreadPoolExecutor(max_workers=2) as ex:
        results = list(ex.map(_kb, enumerate(imgs)))
    if not all(results):
        print("ADA SEGMEN GAGAL"); sys.exit(1)
    segs = [os.path.join(tmpd, f"s{i:03d}.mp4") for i in range(len(imgs))]
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    concat = os.path.join(tmpd, "concat.mp4")
    subprocess.run([QUEUE, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)
    subprocess.run([QUEUE, "-y", "-i", concat, "-i", audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", out],
                   capture_output=True, check=True)
    print(f"OK: {out} ({dur(out)/60:.1f} menit)")
    shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
