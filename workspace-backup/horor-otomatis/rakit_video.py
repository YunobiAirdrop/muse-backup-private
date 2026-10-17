#!/usr/bin/env python3
"""Rakit video POV 15 menit: N gambar (Ken Burns) + voiceover gabungan + film grain + grading.
Penggunaan: python3 rakit_video.py <dir_gambar> <file_audio> <output> [durations.txt]
  dir_gambar: direktori berisi *.webp/*.jpg (satu per adegan)
  file_audio: mp3 voiceover gabungan
  output: mp4 final
  durations.txt (opsional): satu durasi detik per baris, urutan sama dengan gambar terurut.
    Kalau diberikan, tiap gambar memakai durasi beat-nya sendiri (sinkron voiceover);
    kalau tidak, durasi audio dibagi rata ke semua gambar.
"""
import subprocess, os, glob, sys

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def kenburns(img, seg_dur, idx, out):
    total_frames = int(seg_dur * 30)
    mode = idx % 4
    if mode == 0:
        zp = f"zoompan=z='min(zoom+0.0012,1.25)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode == 1:
        zp = f"zoompan=z='min(zoom+0.0012,1.25)':d={total_frames}:x='(iw-iw/zoom)*on/{total_frames}':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode == 2:
        zp = f"zoompan=z='max(1.25-0.0012*on,1.0)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    else:
        zp = f"zoompan=z='min(zoom+0.0012,1.25)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{total_frames}':s=1280x720:fps=30"
    vf = (f"scale=1600:900,{zp},"
          "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
          "noise=alls=6:allf=t,"
          "vignette=PI/5")
    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", img,
                    "-vf", vf, "-t", str(seg_dur),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", out],
                   capture_output=True, check=True)

def main():
    if len(sys.argv) not in (4, 5):
        print("pakai: rakit_video.py <dir_gambar> <file_audio> <output> [durations.txt]"); sys.exit(1)
    gdir, audio, out = sys.argv[1], sys.argv[2], sys.argv[3]
    imgs = sorted(glob.glob(os.path.join(gdir, "*.webp")) + glob.glob(os.path.join(gdir, "*.jpg")))
    if not imgs:
        print("tidak ada gambar"); sys.exit(1)
    audio_dur = dur(audio)
    durs = None
    if len(sys.argv) == 5:
        durs = [float(x.strip()) for x in open(sys.argv[4]) if x.strip()]
        if len(durs) != len(imgs):
            print(f"durations {len(durs)} != gambar {len(imgs)}"); sys.exit(1)
        print(f"{len(imgs)} gambar, audio {audio_dur:.0f}s, durasi per beat (total {sum(durs):.0f}s)")
    else:
        seg_dur = audio_dur / len(imgs)
        durs = [seg_dur] * len(imgs)
        print(f"{len(imgs)} gambar, audio {audio_dur:.0f}s, per segmen {seg_dur:.1f}s (rata)")
    tmpd = os.path.join(os.path.dirname(out), "_tmp_segs")
    os.makedirs(tmpd, exist_ok=True)
    segs = []
    for i, (img, seg_dur) in enumerate(zip(imgs, durs)):
        s = os.path.join(tmpd, f"s{i:02d}.mp4")
        kenburns(img, seg_dur, i, s)
        segs.append(s)
        if (i + 1) % 10 == 0: print(f"  {i+1}/{len(imgs)} segmen...")
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for s in segs: f.write(f"file '{s}'\n")
    concat = os.path.join(tmpd, "concat.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)
    subprocess.run(["ffmpeg", "-y", "-i", concat, "-i", audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", out],
                   capture_output=True, check=True)
    print(f"OK: {out} ({dur(out)/60:.1f} menit)")
    import shutil; shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
