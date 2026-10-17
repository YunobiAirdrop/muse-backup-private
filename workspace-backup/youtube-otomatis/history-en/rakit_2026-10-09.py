#!/usr/bin/env python3
"""Rakit video history-en 2026-10-09 (Mount Tambora 1815).
Ringan: 1280x720 langsung, preset veryfast, film grain, semua via ffmpeg-queue.sh.
Title card pembuka 3 detik (teks via drawtext) + 3 detik hening di awal audio.
Penggunaan: python3 rakit_2026-10-09.py <dir_gambar> <durasi_json> <out>
"""
import subprocess, os, glob, sys, json, shutil

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
TITLE_DUR = 3.0

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

# indeks segmen gambar 0-based -> teks overlay (HURUF KAPITAL)
# dibaca dari beats JSON (field "overlay"), bukan hardcoded — tahan terhadap reindex
def load_overlays():
    bj = json.load(open(os.path.join(BASE, "beats", "beats-2026-10-09.json")))
    ov = {}
    for x in bj:
        if x.get("overlay"):
            idx = int(x["beat"].split("-")[1]) - 1
            ov[idx] = x["overlay"]
    return ov
OVERLAYS = load_overlays()
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def render_titlecard(out):
    if os.path.exists(out) and dur(out) >= TITLE_DUR * 0.9:
        return True
    t1 = "/tmp/title-he-1.txt"; t2 = "/tmp/title-he-2.txt"
    open(t1, "w").write("1521:")
    open(t2, "w").write("THE FALL OF TENOCHTITLAN")
    vf = (f"drawtext=fontfile={FONT}:textfile={t1}:fontsize=110:fontcolor=white:"
          f"x=(w-text_w)/2:y=h/2-140,"
          f"drawtext=fontfile={FONT}:textfile={t2}:fontsize=52:fontcolor=#ffd97a:"
          f"x=(w-text_w)/2:y=h/2+10")
    r = subprocess.run([FFQ, "-y", "-f", "lavfi",
                        f"-i", f"color=c=black:s=1280x720:r=30:d={TITLE_DUR}",
                        "-vf", vf, "-t", str(TITLE_DUR),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True)
    return r.returncode == 0

def kenburns_light(img, seg_dur, idx, out):
    total_frames = int(seg_dur * 30)
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
    if idx in OVERLAYS:
        tfile = f"/tmp/overlay-he-{idx}.txt"
        open(tfile, "w").write(OVERLAYS[idx])
        vf += (f",drawtext=fontfile={FONT}:textfile={tfile}:fontsize=46:"
               "fontcolor=white:borderw=2:bordercolor=black@0.8:"
               "x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.55:boxborderw=24")
    r = subprocess.run([FFQ, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True)
    return r.returncode == 0

def main():
    gdir, dur_json, out = sys.argv[1:4]
    imgs = sorted(glob.glob(os.path.join(gdir, "scene-*.jpg")))
    dj = json.load(open(dur_json))
    n = len(imgs)
    seg_durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(n)]
    print(f"{n} gambar, target {(sum(seg_durs)+TITLE_DUR)/60:.1f} mnt", flush=True)
    tmpd = os.path.join(os.path.dirname(out), "_tmp_segs")
    os.makedirs(tmpd, exist_ok=True)
    # title card
    tcard = os.path.join(tmpd, "title.mp4")
    print("  render title card...", flush=True)
    if not render_titlecard(tcard):
        print("GAGAL: title card"); sys.exit(1)
    # segmen gambar
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
            print(f"  {i+1}/{n} segmen...", flush=True)
    segs = [tcard] + [os.path.join(tmpd, f"s{i:03d}.mp4") for i in range(n)]
    assert all(os.path.exists(s) for s in segs), "masih ada segmen hilang"
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    concat = os.path.join(tmpd, "concat.mp4")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)
    # audio: 3s hening + gabungan beats
    adir = os.path.join(BASE, "audio", "2026-10-09", "final")
    silence3 = os.path.join(adir, "_silence3s.mp3")
    if not (os.path.exists(silence3) and dur(silence3) >= 2.9):
        subprocess.run([FFQ, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                        "-t", str(TITLE_DUR), "-c:a", "libmp3lame", silence3],
                       capture_output=True, check=True)
    beats_lst = os.path.join(tmpd, "beats_list.txt")
    with open(beats_lst, "w") as f:
        for i in range(n):
            f.write(f"file '{os.path.join(adir, f'beat-{i+1:03d}.mp3')}'\n")
    beats_mp3 = os.path.join(adir, "_beats_only.mp3")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", beats_lst,
                    "-c:a", "libmp3lame", "-b:a", "128k", beats_mp3],
                   capture_output=True, check=True)
    gabungan = os.path.join(adir, "gabungan-2026-10-09.mp3")
    full_lst = os.path.join(tmpd, "full_list.txt")
    with open(full_lst, "w") as f:
        f.write(f"file '{silence3}'\nfile '{beats_mp3}'\n")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", full_lst,
                    "-c:a", "libmp3lame", "-b:a", "128k", gabungan],
                   capture_output=True, check=True)
    subprocess.run([FFQ, "-y", "-i", concat, "-i", gabungan,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", out],
                   capture_output=True, check=True)
    print(f"OK: {out} ({dur(out)/60:.1f} menit)", flush=True)
    shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
