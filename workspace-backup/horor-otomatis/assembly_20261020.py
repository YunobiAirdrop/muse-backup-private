#!/usr/bin/env python3
"""Assembly video horor 2026-10-20 (Lift yang Berhenti di Lantai yang Tak Ada) — 75 beat.
gambar/2026-10-20/beat-NNN.* + audio/2026-10-20.mp3 -> video/2026-10-20.mp4
+ 3 shorts vertikal -> shorts/2026-10-20-sN.mp4 (diupload BESOK)

- Pelajaran AGENTS.md: still-image -> preset ULTRAFAST; slide dari TIMELINE audio;
  semua ffmpeg via ffmpeg-queue.sh; drawtext tanpa %, tanpa :, tanpa apostrof+between;
  playlist concat ABSOLUTE path; tulis TEMP -> verifikasi durasi PER STREAM -> move final.
"""
import subprocess, os, glob, sys, shutil

BASE = "/home/hatch/workspace/horor-otomatis"
FF = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
GDIR = os.path.join(BASE, "gambar/2026-10-20")
AUDIO = os.path.join(BASE, "audio/2026-10-20.mp3")
DURS = os.path.join(BASE, "audio/2026-10-20.durations.txt")
OUT_FINAL = os.path.join(BASE, "video/2026-10-20.mp4")
OUT_TMP = os.path.join(BASE, "video/2026-10-20-TEMP.mp4")
OUT_TMP2 = os.path.join(BASE, "video/2026-10-20-TEMP2.mp4")
TMPD = os.path.join(BASE, "video/_tmp_segs_20261020")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (teks, beat_mulai) — tanpa %, tanpa :, tanpa apostrof. Waktu dihitung dari timeline audio.
OVERLAY_BEATS = [
    ("GEDUNG INI CUMA 12 LANTAI", 2),
    ("LIFT B SUDAH MATI 10 TAHUN", 23),
    ("AKU SUDAH 28 TAHUN DI SINI", 39),
    ("JANGAN NAIK SENDIRIAN", 74),
]
OVERLAY_DUR = 8
# shorts: (nama, beat_mulai, durasi)
SHORTS_BEATS = [("s1", 1, 45), ("s2", 37, 50), ("s3", 67, 45)]

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def dur(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path])
    return float(r.stdout.strip())

def stream_durs(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration",
             "-of", "csv=p=0", path])
    out = {}
    for line in r.stdout.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) == 2:
            out[parts[0]] = float(parts[1])
    return out

def seg_ok(path, expect):
    if not os.path.exists(path) or os.path.getsize(path) < 30000:
        return False
    try:
        return abs(dur(path) - expect) < 0.6
    except Exception:
        return False

def kenburns(img, seg_dur, idx, out):
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
    r = run([FF, "-y", "-loop", "1", "-i", img,
             "-vf", vf, "-t", str(seg_dur),
             "-c:v", "libx264", "-preset", "ultrafast",
             "-pix_fmt", "yuv420p", "-r", "30", out])
    return r.returncode == 0

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

def img_for_beat(b):
    cands = glob.glob(os.path.join(GDIR, f"beat-{b:03d}.*"))
    cands = [c for c in cands if not c.endswith(".json")]
    assert len(cands) == 1, (b, cands)
    return os.path.abspath(cands[0])

def main():
    durs = [float(x.strip()) for x in open(DURS) if x.strip()]
    assert len(durs) == 75, f"durations {len(durs)} != 75"
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
            ok = kenburns(img, sd, i, s)
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
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", concat], check=True)
    run([FF, "-y", "-i", concat, "-i", AUDIO,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
         "-shortest", "-movflags", "+faststart", OUT_TMP], check=True)
    d = dur(OUT_TMP)
    print(f"RAKIT OK: {OUT_TMP} ({d:.1f}s)", flush=True)
    assert abs(d - audio_dur) < 5, f"durasi rakit {d} != audio {audio_dur}"

    # text overlay -> TEMP2
    parts = []
    for teks, beat in OVERLAY_BEATS:
        t1 = int(starts[beat-1] + 1)
        t2 = t1 + OVERLAY_DUR
        parts.append(
            f"drawtext=fontfile={FONT}:text='{esc(teks)}':fontsize=64:"
            f"fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-170:enable='between(t,{t1},{t2})'"
        )
    vf = ",".join(parts)
    r = run([FF, "-y", "-i", OUT_TMP, "-vf", vf,
             "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
             "-c:a", "copy", "-movflags", "+faststart", OUT_TMP2])
    if r.returncode != 0:
        print("OVERLAY GAGAL:", r.stderr[-1500:], flush=True); sys.exit(3)
    dy = dur(OUT_TMP2)
    print(f"OVERLAY OK: {OUT_TMP2} ({dy:.1f}s)", flush=True)
    assert abs(dy - d) < 5, f"durasi overlay {dy} != rakit {d}"

    # verifikasi PER STREAM sebelum move ke final
    sd = stream_durs(OUT_TMP2)
    print("stream durations:", sd, flush=True)
    for ctype, dd in sd.items():
        assert abs(dd - audio_dur) < 5, f"stream {ctype} durasi {dd} != audio {audio_dur}"
    print("QC PER-STREAM LOLOS", flush=True)

    shutil.move(OUT_TMP2, OUT_FINAL)
    os.remove(OUT_TMP)
    print(f"FINAL: {OUT_FINAL} ({dy:.1f}s)", flush=True)

    # 3 shorts vertikal dari final
    for nama, beat, t in SHORTS_BEATS:
        ss = starts[beat-1]
        sp = os.path.join(BASE, f"shorts/2026-10-20-{nama}.mp4")
        r = run([FF, "-y", "-ss", str(int(ss)), "-i", OUT_FINAL, "-t", str(t),
                 "-vf", "crop=ih*9/16:ih",
                 "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
                 "-c:a", "aac", "-b:a", "128k",
                 "-movflags", "+faststart", sp])
        if r.returncode != 0:
            print(f"SHORT {nama} GAGAL:", r.stderr[-800:], flush=True); sys.exit(4)
        ds = dur(sp)
        print(f"SHORT OK: {sp} ({ds:.1f}s)", flush=True)

    shutil.rmtree(TMPD)
    print("SELESAI SEMUA", flush=True)

if __name__ == "__main__":
    main()
