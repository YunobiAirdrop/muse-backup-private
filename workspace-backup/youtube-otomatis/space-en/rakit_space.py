#!/usr/bin/env python3
"""Rakit video Cosmic Unknown 9-10 menit: 72 gambar (Ken Burns 1920x1080)
+ voiceover gabungan per-beat + film grain + grading.
Penggunaan: python3 rakit_space.py <dir_gambar> <file_audio> <output> <durasi_json>
  durasi_json: {"beat-001-a": 8.2, ...} durasi tiap gambar (wajib).
"""
import subprocess, os, glob, sys, json

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def kenburns(img, seg_dur, idx, out):
    total_frames = max(int(seg_dur * 30), 15)
    mode = idx % 4
    if mode == 0:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
    elif mode == 1:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='(iw-iw/zoom)*on/{total_frames}':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
    elif mode == 2:
        zp = f"zoompan=z='max(1.15-0.0012*on,1.0)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
    else:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{total_frames}':s=1920x1080:fps=30"
    vf = (f"scale=1920:1080,{zp},"
          "eq=contrast=1.06:saturation=1.05:brightness=-0.015,"
          "noise=alls=5:allf=t,"
          "vignette=PI/5")
    subprocess.run(["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-loop", "1", "-i", img,
                    "-vf", vf, "-t", str(seg_dur),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", out],
                   capture_output=True, check=True)

def main():
    if len(sys.argv) != 5:
        print("pakai: rakit_space.py <dir_gambar> <file_audio> <output> <durasi_json>"); sys.exit(1)
    gdir, audio, out, dur_json = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    all_imgs = sorted(glob.glob(os.path.join(gdir, "*.webp")) + glob.glob(os.path.join(gdir, "*.jpg")))
    # pilih tepat 1 gambar per kunci durasi (cocokkan substring "beat-XXX-y"), dedupe
    dj = json.load(open(dur_json))
    imgs, seg_durs, missing = [], [], []
    for key in sorted(dj.keys()):
        cands = sorted([p for p in all_imgs if f"-{key}-" in os.path.basename(p) or os.path.basename(p).startswith(f"media-generation-{key}-")])
        if cands:
            imgs.append(cands[0])
            seg_durs.append(float(dj[key]))
        else:
            missing.append(key)
    if missing:
        print(f"durasi hilang untuk {len(missing)}: {missing[:5]}"); sys.exit(1)
    print(f"{len(imgs)} gambar, total {sum(seg_durs):.0f}s")
    tmpd = os.path.join(os.path.dirname(out), "_tmp_segs")
    os.makedirs(tmpd, exist_ok=True)
    segs = []
    for i, img in enumerate(imgs):
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        if os.path.exists(s) and os.path.getsize(s) > 10000:
            print(f"  skip s{i:03d} (sudah ada)", flush=True)
        else:
            kenburns(img, seg_durs[i], i, s)
        segs.append(s)
        if (i + 1) % 8 == 0: print(f"  {i+1}/{len(imgs)} segmen...", flush=True)
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for s in segs: f.write(f"file '{os.path.abspath(s)}'\n")
    concat = os.path.join(tmpd, "concat.mp4")
    subprocess.run(["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)
    subprocess.run(["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-i", concat, "-i", audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", out],
                   capture_output=True, check=True)
    print(f"OK: {out} ({dur(out)/60:.1f} menit)")
    import shutil; shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
