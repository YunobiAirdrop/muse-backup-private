#!/usr/bin/env python3
"""Rakit video history-en 2026-10-11 (The Black Death 1347-1353).
Ringan: 1280x720, preset veryfast, film grain, semua ffmpeg via ffmpeg-queue.sh.
Title card 3s + bumper voice-clone di TENGAH (setelah beat-035, jeda natural antar chapter)
+ CTA teks 'Subscribe!' di segmen bumper (sekitar 50%) dan segmen terakhir.
Audio: 3s hening + beats 1-35 + bumper + beats 36-70.
Penggunaan: python3 rakit_2026-10-11.py
Menghasilkan: video/2026-10-11.mp4 + audio/2026-10-11/durasi-beat-2026-10-11.json
"""
import subprocess, os, glob, sys, json, shutil

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
ADIR = os.path.join(BASE, "audio", "2026-10-11")
GDIR = os.path.join(BASE, "gambar", "2026-10-11", "final")
OUT = os.path.join(BASE, "video", "2026-10-11.mp4")
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-history-en.wav"
TITLE_DUR = 3.0
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BUMPER_AFTER = 35  # setelah beat-035 (akhir chapter The Death Ships / Year of Terror)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def load_overlays():
    bj = json.load(open(os.path.join(BASE, "beats", "beats-2026-10-11.json")))
    ov = {}
    for x in bj:
        if x.get("overlay"):
            idx = int(x["beat"].split("-")[1]) - 1
            ov[idx] = x["overlay"]
    return ov
OVERLAYS = load_overlays()

def render_titlecard(out):
    if os.path.exists(out) and dur(out) >= TITLE_DUR * 0.9:
        return True
    t1 = "/tmp/title-he11-1.txt"; t2 = "/tmp/title-he11-2.txt"
    open(t1, "w").write("1347:")
    open(t2, "w").write("THE BLACK DEATH CAME ON SHIPS")
    vf = (f"drawtext=fontfile={FONT}:textfile={t1}:fontsize=110:fontcolor=white:"
          f"x=(w-text_w)/2:y=h/2-140,"
          f"drawtext=fontfile={FONT}:textfile={t2}:fontsize=46:fontcolor=#ffd97a:"
          f"x=(w-text_w)/2:y=h/2+10")
    r = subprocess.run([FFQ, "-y", "-f", "lavfi",
                        "-i", f"color=c=black:s=1280x720:r=30:d={TITLE_DUR}",
                        "-vf", vf, "-t", str(TITLE_DUR),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True)
    return r.returncode == 0

def seg_video(img, seg_dur, idx, out, extra_text=None):
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
    if idx in OVERLAYS:
        tfile = f"/tmp/overlay-he11-{idx}.txt"
        open(tfile, "w").write(OVERLAYS[idx])
        vf += (f",drawtext=fontfile={FONT}:textfile={tfile}:fontsize=46:"
               "fontcolor=white:borderw=2:bordercolor=black@0.8:"
               "x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.55:boxborderw=24")
    if extra_text:
        tfile = f"/tmp/cta-he11-{idx}.txt"
        open(tfile, "w").write(extra_text)
        vf += (f",drawtext=fontfile={FONT}:textfile={tfile}:fontsize=54:"
               "fontcolor=#ffd97a:borderw=2:bordercolor=black@0.8:"
               "x=(w-text_w)/2:y=60:box=1:boxcolor=black@0.55:boxborderw=20")
    r = subprocess.run([FFQ, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True)
    return r.returncode == 0

def main():
    imgs = sorted(glob.glob(os.path.join(GDIR, "scene-*.jpg")))
    assert len(imgs) == 70, f"gambar final: {len(imgs)} != 70"
    # durasi per beat dari file audio final
    durs = {}
    for i in range(1, 71):
        p = os.path.join(ADIR, f"beat-{i:03d}.mp3")
        d = dur(p)
        assert d > 0.5, f"audio tidak valid: {p} ({d})"
        durs[f"beat-{i:03d}"] = round(d, 3)
    json.dump(durs, open(os.path.join(ADIR, "durasi-beat-2026-10-11.json"), "w"), indent=1)
    seg_durs = [durs[f"beat-{i+1:03d}"] for i in range(70)]
    bumper_dur = dur(BUMPER)
    assert bumper_dur > 0.5, "bumper tidak valid"
    total = TITLE_DUR + sum(seg_durs) + bumper_dur
    print(f"70 gambar, total target {total/60:.2f} mnt (bumper {bumper_dur:.2f}s)", flush=True)

    tmpd = os.path.join(BASE, "video", "_tmp_segs_2026-10-11")
    os.makedirs(tmpd, exist_ok=True)
    tcard = os.path.join(tmpd, "title.mp4")
    print("  render title card...", flush=True)
    if not render_titlecard(tcard):
        print("GAGAL: title card"); sys.exit(1)

    # segmen gambar; segmen terakhir (beat-070) dapat CTA teks
    for i, img in enumerate(imgs):
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        if os.path.exists(s) and dur(s) >= seg_durs[i] * 0.9:
            continue
        if os.path.exists(s):
            os.remove(s)
        extra = "Subscribe!" if i == 69 else None
        print(f"  render s{i:03d} ({seg_durs[i]:.1f}s)...", flush=True)
        for attempt in range(2):
            if seg_video(img, seg_durs[i], i, s, extra_text=extra) and dur(s) >= seg_durs[i] * 0.9:
                break
            print(f"    retry s{i:03d}", flush=True)
        else:
            print(f"GAGAL: s{i:03d}"); sys.exit(1)
    # segmen bumper: pakai gambar beat-036 (scene-036), teks Subscribe! (CTA di ~50%)
    bseg = os.path.join(tmpd, "bumper.mp4")
    if not (os.path.exists(bseg) and dur(bseg) >= bumper_dur * 0.9):
        if os.path.exists(bseg):
            os.remove(bseg)
        if not seg_video(imgs[BUMPER_AFTER], bumper_dur, BUMPER_AFTER, bseg, extra_text="Subscribe!"):
            print("GAGAL: segmen bumper"); sys.exit(1)

    segs = [tcard]
    for i in range(70):
        segs.append(os.path.join(tmpd, f"s{i:03d}.mp4"))
        if i + 1 == BUMPER_AFTER:
            segs.append(bseg)
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    concat = os.path.join(tmpd, "concat.mp4")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)
    cdur = dur(concat)
    print(f"  concat video: {cdur:.1f}s", flush=True)

    # audio: silence3 + beats1-35 + bumper + beats36-70 (semua path absolut)
    silence3 = os.path.join(ADIR, "_silence3s.mp3")
    if not (os.path.exists(silence3) and dur(silence3) >= 2.9):
        subprocess.run([FFQ, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                        "-t", str(TITLE_DUR), "-c:a", "libmp3lame", silence3],
                       capture_output=True, check=True)
    full = [silence3] + [os.path.join(ADIR, f"beat-{i:03d}.mp3") for i in range(1, BUMPER_AFTER + 1)] \
           + [BUMPER] + [os.path.join(ADIR, f"beat-{i:03d}.mp3") for i in range(BUMPER_AFTER + 1, 71)]
    full_lst = os.path.join(tmpd, "full_list.txt")
    with open(full_lst, "w") as f:
        for s in full:
            f.write(f"file '{os.path.abspath(s)}'\n")
    gabungan = os.path.join(ADIR, "gabungan-2026-10-11.mp3")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", full_lst,
                    "-c:a", "libmp3lame", "-b:a", "128k", gabungan],
                   capture_output=True, check=True)
    adur = dur(gabungan)
    print(f"  audio gabungan: {adur:.1f}s | selisih video-audio: {abs(cdur-adur):.2f}s", flush=True)
    assert abs(cdur - adur) < 2.0, "durasi video & audio tidak sinkron"

    subprocess.run([FFQ, "-y", "-i", concat, "-i", gabungan,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", OUT],
                   capture_output=True, check=True)
    print(f"OK: {OUT} ({dur(OUT)/60:.2f} menit)", flush=True)
    shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
