#!/usr/bin/env python3
"""Assembly video horor 2026-10-13 (CCTV Apartemen jam 02.47) — lanjutan run 2026-10-13 yg terputus.
78 gambar + audio 703 dtk -> video/2026-10-13.mp4 -> overlay teks -> video/2026-10-13-youtube.mp4
+ 3 shorts vertikal -> shorts/2026-10-13-sN.mp4

- Pipeline RINGAN (anti-OOM, AGENTS.md 2026-10-05): scale=1280:720 direct, preset veryfast
- Semua ffmpeg via ffmpeg-queue.sh (semaphore max 2, AGENTS.md 2026-10-06)
- Resume: segmen valid (durasi cocok) dilewati
- Playlist concat ABSOLUTE path (AGENTS.md 2026-10-11)
- drawtext: TANPA '%' dan TANPA apostrof (AGENTS.md 2026-10-11/13)
"""
import subprocess, os, glob, sys

BASE = "/home/hatch/workspace/horor-otomatis"
FF = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
GDIR = os.path.join(BASE, "gambar/2026-10-13")
AUDIO = os.path.join(BASE, "audio/2026-10-13.mp3")
DURS = os.path.join(BASE, "audio/2026-10-13.durations.txt")
OUT = os.path.join(BASE, "video/2026-10-13.mp4")
OUT_YT = os.path.join(BASE, "video/2026-10-13-youtube.mp4")
TMPD = os.path.join(BASE, "video/_tmp_segs_20261013")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (teks, mulai, selesai) — 5 momen kunci, tanpa % dan tanpa apostrof
OVERLAYS = [
    ("WAJAHNYA... WAJAHKU", 1, 9),
    ("FOTO ITU... PERSIS WAJAHKU", 300, 307),
    ("KETUKAN PINTU JAM 02.47", 400, 408),
    ("SEMUA... WAJAHKU", 543, 552),
    ("JANGAN BALAS LAMBAIANNYA", 694, 700),
]
# (nama, mulai_detik, durasi) — 3 klip termencekam
SHORTS = [
    ("s1", 0, 45),
    ("s2", 295, 45),
    ("s3", 540, 45),
]

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def seg_ok(path, expect):
    if not os.path.exists(path) or os.path.getsize(path) < 30000:
        return False
    try:
        return abs(dur(path) - expect) < 0.6
    except Exception:
        return False

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
    r = subprocess.run([FF, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True, text=True)
    return r.returncode == 0

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

def main():
    imgs = sorted(glob.glob(os.path.join(GDIR, "b*.webp")))
    durs = [float(x.strip()) for x in open(DURS) if x.strip()]
    assert len(imgs) == len(durs) == 78, (len(imgs), len(durs))
    audio_dur = dur(AUDIO)
    print(f"{len(imgs)} gambar, audio {audio_dur:.0f}s, total beat {sum(durs):.0f}s", flush=True)
    os.makedirs(TMPD, exist_ok=True)

    segs = []
    for i, (img, sd) in enumerate(zip(imgs, durs)):
        s = os.path.join(TMPD, f"s{i:02d}.mp4")
        if seg_ok(s, sd):
            st = "skip"
        else:
            ok = kenburns_light(img, sd, i, s)
            st = "buat" if ok else "GAGAL"
            if not ok:
                print(f"SEGMENT {i} GAGAL, berhenti", flush=True); sys.exit(2)
        segs.append(s)
        if st == "buat" or (i + 1) % 13 == 0:
            print(f"  segmen {i+1}/78 {st}", flush=True)

    lst = os.path.join(TMPD, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    concat = os.path.join(TMPD, "concat.mp4")
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)
    subprocess.run([FF, "-y", "-i", concat, "-i", AUDIO,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", OUT],
                   capture_output=True, check=True)
    d = dur(OUT)
    print(f"RAKIT OK: {OUT} ({d:.0f}s = {d/60:.1f} mnt)", flush=True)
    assert abs(d - audio_dur) < 3, f"durasi rakit {d} != audio {audio_dur}"

    # --- text overlay -> versi youtube ---
    parts = []
    for teks, t1, t2 in OVERLAYS:
        parts.append(
            f"drawtext=fontfile={FONT}:text='{esc(teks)}':fontsize=64:"
            f"fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-170:enable='between(t,{t1},{t2})'"
        )
    vf = ",".join(parts)
    r = subprocess.run([FF, "-y", "-i", OUT, "-vf", vf,
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-c:a", "copy", "-movflags", "+faststart", OUT_YT],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("OVERLAY GAGAL:", r.stderr[-1500:], flush=True); sys.exit(3)
    dy = dur(OUT_YT)
    print(f"OVERLAY OK: {OUT_YT} ({dy:.0f}s)", flush=True)
    assert abs(dy - d) < 3, f"durasi overlay {dy} != rakit {d}"

    # --- 3 shorts vertikal ---
    for nama, ss, t in SHORTS:
        sp = os.path.join(BASE, f"shorts/2026-10-13-{nama}.mp4")
        r = subprocess.run([FF, "-y", "-ss", str(ss), "-i", OUT_YT, "-t", str(t),
                            "-vf", "crop=ih*9/16:ih",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                            "-c:a", "aac", "-b:a", "128k",
                            "-movflags", "+faststart", sp],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"SHORT {nama} GAGAL:", r.stderr[-800:], flush=True); sys.exit(4)
        ds = dur(sp)
        print(f"SHORT OK: {sp} ({ds:.0f}s)", flush=True)

    import shutil
    shutil.rmtree(TMPD)
    print("SELESAI SEMUA", flush=True)

if __name__ == "__main__":
    main()
