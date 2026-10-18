#!/usr/bin/env python3
"""Assembly video horor 2026-10-17 (Sumur Tua yang Memanggil Nama) — 75 beat.
75 gambar (28 existing + 19 baru + 28 reuse) + audio 574.9 dtk -> video/2026-10-17.mp4
+ 3 shorts vertikal -> shorts/2026-10-17-sN.mp4

- Pipeline RINGAN: scale=1280:720 direct, preset veryfast (anti-OOM)
- Semua ffmpeg via ffmpeg-queue.sh
- Resume: segmen valid dilewati
- Playlist concat ABSOLUTE path
- Tulis ke TEMP, verifikasi durasi, BARU move ke final
- Slide durasi dari TIMELINE audio (starts[k+1]-starts[k])
"""
import subprocess, os, glob, re, sys

BASE = "/home/hatch/workspace/horor-otomatis"
FF = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
GDIR = os.path.join(BASE, "gambar/2026-10-17")
AUDIO = os.path.join(BASE, "audio/2026-10-17.mp3")
DURS = os.path.join(BASE, "audio/2026-10-17.durations.txt")
OUT_FINAL = os.path.join(BASE, "video/2026-10-17.mp4")
OUT_TMP = os.path.join(BASE, "video/2026-10-17-TEMP.mp4")
OUT_TMP2 = os.path.join(BASE, "video/2026-10-17-TEMP2.mp4")
TMPD = os.path.join(BASE, "video/_tmp_segs_20261018")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# beat -> gambar. eNN = existing media-generation-beat-NNN-0-*.webp, nNN = beat-NNN.webp baru
E_REUSE = {
    29: 27, 30: 26, 31: 14, 32: 11, 34: 10, 36: 4, 37: 6, 42: 22, 46: 17,
    50: 25, 53: 21, 54: 23, 55: 24, 57: 18, 62: 3, 64: 28, 65: 10, 66: 7,
    67: 16, 68: 2, 69: 5, 70: 13, 71: 6, 72: 5, 73: 7,
}
N_NEW = {33, 35, 38, 39, 41, 43, 44, 45, 47, 49, 51, 52, 56, 58, 60, 61, 63, 74, 75}
N_REUSE = {40: 39, 48: 47, 59: 58}

# (teks, mulai, selesai) — tanpa %, tanpa :, tanpa apostrof+between
OVERLAYS = [
    ("WAJAHNYA... WAJAHKU", 1, 9),
    ("PAK MARNO SUDAH MENINGGAL", 296, 304),
    ("DIA MENATAP KE KAMERA", 478, 486),
    ("JANGAN JAWAB", 547, 556),
]
SHORTS = [
    ("s1", 0, 45),
    ("s2", 470, 50),
    ("s3", 290, 45),
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
    r = subprocess.run([FF, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True, text=True)
    return r.returncode == 0

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

def img_for_beat(b):
    """kembalikan absolute path gambar untuk beat 1-indexed."""
    if b <= 28:
        cands = glob.glob(os.path.join(GDIR, f"media-generation-beat-{b:03d}-0-*.webp"))
        assert len(cands) == 1, (b, cands)
        return os.path.abspath(cands[0])
    if b in N_NEW or b in N_REUSE:
        src = b if b in N_NEW else N_REUSE[b]
        p = os.path.abspath(os.path.join(GDIR, f"beat-{src:03d}.webp"))
        assert os.path.exists(p), f"gambar baru hilang: {p}"
        return p
    e = E_REUSE[b]
    cands = glob.glob(os.path.join(GDIR, f"media-generation-beat-{e:03d}-0-*.webp"))
    assert len(cands) == 1, (b, e, cands)
    return os.path.abspath(cands[0])

def main():
    durs = [float(x.strip()) for x in open(DURS) if x.strip()]
    assert len(durs) == 75, len(durs)
    audio_dur = dur(AUDIO)
    starts = []
    s = 0.0
    for x in durs:
        starts.append(s); s += x
    slides = [starts[k+1] - starts[k] for k in range(74)] + [audio_dur - starts[74]]
    imgs = [img_for_beat(b) for b in range(1, 76)]
    print(f"75 gambar OK, audio {audio_dur:.1f}s, sum slides {sum(slides):.1f}s", flush=True)
    os.makedirs(TMPD, exist_ok=True)

    segs = []
    for i, (img, sd) in enumerate(zip(imgs, slides)):
        s = os.path.join(TMPD, f"s{i:02d}.mp4")
        if seg_ok(s, sd):
            st = "skip"
        else:
            ok = kenburns_light(img, sd, i, s)
            st = "buat" if ok else "GAGAL"
            if not ok:
                print(f"SEGMENT {i} GAGAL, berhenti", flush=True); sys.exit(2)
        segs.append(s)
        if st == "buat" or (i + 1) % 15 == 0:
            print(f"  segmen {i+1}/75 {st}", flush=True)

    lst = os.path.join(TMPD, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    concat = os.path.join(TMPD, "concat.mp4")
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)
    subprocess.run([FF, "-y", "-i", concat, "-i", AUDIO,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", OUT_TMP],
                   capture_output=True, check=True)
    d = dur(OUT_TMP)
    print(f"RAKIT OK: {OUT_TMP} ({d:.1f}s)", flush=True)
    assert abs(d - audio_dur) < 5, f"durasi rakit {d} != audio {audio_dur}"

    # text overlay -> TEMP2
    parts = []
    for teks, t1, t2 in OVERLAYS:
        parts.append(
            f"drawtext=fontfile={FONT}:text='{esc(teks)}':fontsize=64:"
            f"fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-170:enable='between(t,{t1},{t2})'"
        )
    vf = ",".join(parts)
    r = subprocess.run([FF, "-y", "-i", OUT_TMP, "-vf", vf,
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-c:a", "copy", "-movflags", "+faststart", OUT_TMP2],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("OVERLAY GAGAL:", r.stderr[-1500:], flush=True); sys.exit(3)
    dy = dur(OUT_TMP2)
    print(f"OVERLAY OK: {OUT_TMP2} ({dy:.1f}s)", flush=True)
    assert abs(dy - d) < 5, f"durasi overlay {dy} != rakit {d}"

    import shutil
    shutil.move(OUT_TMP2, OUT_FINAL)
    os.remove(OUT_TMP)
    print(f"FINAL: {OUT_FINAL} ({dy:.1f}s)", flush=True)

    # 3 shorts vertikal dari final
    for nama, ss, t in SHORTS:
        sp = os.path.join(BASE, f"shorts/2026-10-17-{nama}.mp4")
        r = subprocess.run([FF, "-y", "-ss", str(ss), "-i", OUT_FINAL, "-t", str(t),
                            "-vf", "crop=ih*9/16:ih",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                            "-c:a", "aac", "-b:a", "128k",
                            "-movflags", "+faststart", sp],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"SHORT {nama} GAGAL:", r.stderr[-800:], flush=True); sys.exit(4)
        ds = dur(sp)
        print(f"SHORT OK: {sp} ({ds:.1f}s)", flush=True)

    import shutil as _sh
    _sh.rmtree(TMPD)
    print("SELESAI SEMUA", flush=True)

if __name__ == "__main__":
    main()
