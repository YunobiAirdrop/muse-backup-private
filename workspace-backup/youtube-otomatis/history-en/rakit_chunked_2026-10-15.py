#!/usr/bin/env python3
"""Rakit CHUNKED history-en 2026-10-15 (D-Day 1944).
Menggantikan render per-segmen (72 antrean) dengan 6 chunk multi-input
(1 antrean per chunk) karena antrean ffmpeg-queue padat.
Pakai ulang: title.mp4, s000.mp4, s001.mp4 dari _tmp_segs_2026-10-15.
Chunk: A=idx2-13, B=idx14-25, C=idx26-35+bumper+idx36-37, D=idx38-49,
       E=idx50-61, F=idx62-71. Semua ffmpeg via ffmpeg-queue.sh.
Urutan final: title + s000 + s001 + A + B + C + D + E + F.
Audio: silence3 + beat-001..036 + bumper + beat-037..072 (44100 Hz).
Output: tulis ke TEMP, verifikasi durasi +-5 dtk, baru move ke video/2026-10-15.mp4.
"""
import subprocess, os, sys, json, shutil

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
DATE = "2026-10-15"
ADIR = os.path.join(BASE, "audio", DATE)
GDIR = os.path.join(BASE, "gambar", DATE, "final")
SEGDIR = os.path.join(BASE, "video", "_tmp_segs_2026-10-15")
CHKDIR = os.path.join(BASE, "video", "_tmp_chunks_2026-10-15")
OUT = os.path.join(BASE, "video", f"{DATE}.mp4")
OUT_TMP = os.path.join(BASE, "video", f"_tmp_final_{DATE}.mp4")
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-history-en.wav"
TITLE_DUR = 3.0
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CTA_TEXT = "SUBSCRIBE for more untold history!"
CTA_IDX = {35, 70, 71}          # idx beat (0-based)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def load_beats():
    bj = json.load(open(os.path.join(BASE, "beats", f"beats-{DATE}.json")))
    durs = json.load(open(os.path.join(ADIR, f"durasi-beat-{DATE}.json")))
    ov, ch = {}, {}
    for x in bj:
        idx = int(x["beat"].split("-")[1]) - 1
        if x.get("overlay"):
            assert "%" not in x["overlay"], f"persen di overlay {x['beat']}"
            ov[idx] = x["overlay"]
        if x.get("chapter"):
            ch[idx] = x["chapter"]
    seg_durs = [durs[f"beat-{i+1:03d}"] for i in range(72)]
    return ov, ch, seg_durs

OVERLAYS, CHAPTERS, SEG_DURS = load_beats()
BUMPER_DUR = dur(BUMPER)
assert BUMPER_DUR > 0.5
TOTAL = TITLE_DUR + sum(SEG_DURS) + BUMPER_DUR
print(f"target total {TOTAL:.1f}s", flush=True)

def img_for(beat_no):
    p = os.path.join(GDIR, f"beat-{beat_no:03d}.jpg")
    assert os.path.exists(p), f"gambar hilang: {p}"
    return p

def pan_filter(idx, frames, dur):
    # Ken Burns murah: scale 1440x810 sekali, lalu crop 1280x720 dengan
    # offset animasi pakai t (pola terbukti dari lima-misteri).
    mode = idx % 4
    dd = max(0.1, dur)
    if mode == 0:
        xy = f"x='(in_w-out_w)*t/{dd}':y='(in_h-out_h)/2'"
    elif mode == 1:
        xy = f"x='(in_w-out_w)*(1-t/{dd})':y='(in_h-out_h)/2'"
    elif mode == 2:
        xy = f"x='(in_w-out_w)/2':y='(in_h-out_h)*t/{dd}'"
    else:
        xy = f"x='(in_w-out_w)/2':y='(in_h-out_h)*(1-t/{dd})'"
    return (f"scale=1440:810,crop=1280:720:{xy},setsar=1,"
            "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
            "noise=alls=6:allf=t,vignette=PI/5")

def zp_filter(idx, frames, dur=8.0):
    return pan_filter(idx, frames, dur)

def dt_text(idx, text, fontsize, y, tag):
    tfile = f"/tmp/dt-he15-{tag}-{idx}.txt"
    open(tfile, "w", encoding="utf-8").write(text)
    color = "#ffd97a" if tag == "cta" else "white"
    return (f"drawtext=fontfile={FONT}:textfile={tfile}:fontsize={fontsize}:"
            f"fontcolor={color}:borderw=2:bordercolor=black@0.8:"
            f"x=(w-text_w)/2:y={y}:box=1:boxcolor=black@0.55:boxborderw=20")

# chunk: list of ("beat", idx) atau ("bumper", None)
CHUNKS = {
    "A": [("beat", i) for i in range(2, 14)],
    "B": [("beat", i) for i in range(14, 26)],
    "C": [("beat", i) for i in range(26, 36)] + [("bumper", None)] + [("beat", i) for i in range(36, 38)],
    "D": [("beat", i) for i in range(38, 50)],
    "E": [("beat", i) for i in range(50, 62)],
    "F": [("beat", i) for i in range(62, 72)],
}

def render_chunk(name, items):
    out = os.path.join(CHKDIR, f"chunk-{name}.mp4")
    exp = sum(SEG_DURS[i] if k == "beat" else BUMPER_DUR for k, i in items)
    if os.path.exists(out) and abs(dur(out) - exp) < 2.0:
        print(f"  chunk {name} sudah ada ({dur(out):.1f}s)", flush=True)
        return out
    if os.path.exists(out):
        os.remove(out)
    cmd = [FFQ, "-y"]
    fc_parts = []
    for n, (kind, idx) in enumerate(items):
        if kind == "beat":
            d = SEG_DURS[idx]
            img = img_for(idx + 1)
            vf = zp_filter(idx, max(1, int(d * 30)), d)
            if idx in OVERLAYS:
                vf += "," + dt_text(idx, OVERLAYS[idx], 46, "h-150", "ov")
            if idx in CTA_IDX:
                vf += "," + dt_text(idx, CTA_TEXT, 54, "60", "cta")
        else:
            d = BUMPER_DUR
            img = img_for(36)
            vf = zp_filter(1, max(1, int(d * 30)), d)
        vf += ",format=yuv420p"
        fc_parts.append(f"[{n}:v]{vf}[v{n}]")
        cmd += ["-loop", "1", "-t", str(d), "-i", img]
    fc_parts.append("".join(f"[v{i}]" for i in range(len(items))) +
                    f"concat=n={len(items)}:v=1:a=0[vout]")
    cmd += ["-filter_complex", ";".join(fc_parts),
            "-map", "[vout]", "-c:v", "libx264", "-preset", "veryfast",
            "-pix_fmt", "yuv420p", "-r", "30", out]
    print(f"  render chunk {name} ({len(items)} input, {exp:.1f}s)...", flush=True)
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or abs(dur(out) - exp) > 2.0:
        print(f"GAGAL chunk {name}: rc={r.returncode} dur={dur(out):.1f} vs {exp:.1f}")
        print(r.stderr.decode()[-2000:] if r.stderr else "")
        sys.exit(1)
    print(f"  chunk {name} OK ({dur(out):.1f}s)", flush=True)
    return out

def write_list(paths, dst):
    with open(dst, "w") as f:
        for s in paths:
            f.write(f"file '{os.path.abspath(s)}'\n")

def main():
    os.makedirs(CHKDIR, exist_ok=True)
    # pastikan segmen lama ada
    for f in ["title.mp4", "s000.mp4", "s001.mp4"]:
        p = os.path.join(SEGDIR, f)
        assert os.path.exists(p) and dur(p) > 0.5, f"segmen hilang: {p}"
    chunk_files = {}
    for name in ["A", "B", "C", "D", "E", "F"]:
        chunk_files[name] = render_chunk(name, CHUNKS[name])

    vorder = ([os.path.join(SEGDIR, "title.mp4"),
               os.path.join(SEGDIR, "s000.mp4"),
               os.path.join(SEGDIR, "s001.mp4")] +
              [chunk_files[n] for n in ["A", "B", "C", "D", "E", "F"]])
    # --- video concat (demuxer copy) ---
    vconcat = os.path.join(CHKDIR, "vconcat.mp4")
    if not (os.path.exists(vconcat) and abs(dur(vconcat) - TOTAL) < 2.0):
        if os.path.exists(vconcat):
            os.remove(vconcat)
        lst = os.path.join(CHKDIR, "listV.txt"); write_list(vorder, lst)
        subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", vconcat], capture_output=True, check=True)
        assert abs(dur(vconcat) - TOTAL) < 2.0, f"vconcat {dur(vconcat):.1f}s vs {TOTAL:.1f}s"
    print(f"  vconcat: {dur(vconcat):.1f}s", flush=True)

    # --- audio concat ---
    silence3 = os.path.join(ADIR, "_silence3s.mp3")
    if not (os.path.exists(silence3) and dur(silence3) >= 2.9):
        subprocess.run([FFQ, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                        "-t", str(TITLE_DUR), "-ar", "44100", "-ac", "2",
                        "-c:a", "libmp3lame", silence3], capture_output=True, check=True)
    aorder = ([silence3] + [os.path.join(ADIR, f"beat-{i:03d}.mp3") for i in range(1, 37)] +
              [BUMPER] + [os.path.join(ADIR, f"beat-{i:03d}.mp3") for i in range(37, 73)])
    aconcat = os.path.join(CHKDIR, "aconcat.m4a")
    if not (os.path.exists(aconcat) and dur(aconcat) > 0.5):
        lst = os.path.join(CHKDIR, "listA.txt"); write_list(aorder, lst)
        subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", aconcat],
                       capture_output=True, check=True)
    print(f"  aconcat: {dur(aconcat):.1f}s", flush=True)
    assert abs(dur(vconcat) - dur(aconcat)) < 2.0, "video & audio tidak sinkron"

    # --- mux final ke TEMP, verifikasi, baru move ---
    subprocess.run([FFQ, "-y", "-i", vconcat, "-i", aconcat,
                    "-c:v", "copy", "-c:a", "copy",
                    "-shortest", "-movflags", "+faststart", OUT_TMP],
                   capture_output=True, check=True)
    dtmp = dur(OUT_TMP)
    print(f"  final tmp: {dtmp:.1f}s vs target {TOTAL:.1f}s", flush=True)
    assert abs(dtmp - TOTAL) < 5.0, f"DURASI FINAL SALAH: {dtmp:.1f}s vs {TOTAL:.1f}s"
    vinfo = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", OUT_TMP],
                           capture_output=True, text=True).stdout.strip()
    assert vinfo == "1280,720", f"RESOLUSI SALAH: {vinfo}"
    assert os.path.getsize(OUT_TMP) > 10 * 1024 * 1024, "FILE TERLALU KECIL"
    shutil.move(OUT_TMP, OUT)
    print(f"OK: {OUT} ({dur(OUT)/60:.2f} menit, terverifikasi)", flush=True)

    # --- chapters + deskripsi ---
    def fmt(s):
        h = int(s // 3600); m = int((s % 3600) // 60); sec = int(s % 60)
        return f"{h}:{m:02d}:{sec:02d}"
    cum = TITLE_DUR
    lines = []
    for i in range(72):
        if i in CHAPTERS:
            ts = cum + (BUMPER_DUR if i > 35 else 0)
            lines.append(f"{fmt(ts)} — {CHAPTERS[i]}")
        cum += SEG_DURS[i]
    ch_txt = "CHAPTERS\n" + "\n".join(lines)
    open(os.path.join(BASE, "script", f"chapters-ts-{DATE}.txt"), "w").write(ch_txt + "\n")
    meta = json.load(open(os.path.join(BASE, "script", f"meta-{DATE}.json")))
    desc = meta["description"]
    placeholder = "CHAPTERS\n(placeholder — timestamps added during assembly)"
    assert placeholder in desc, "placeholder CHAPTERS tidak ditemukan di meta"
    desc = desc.replace(placeholder, ch_txt)
    open(os.path.join(BASE, "script", f"deskripsi-final-{DATE}.txt"), "w").write(desc + "\n")
    print("  chapters + deskripsi OK", flush=True)

if __name__ == "__main__":
    main()
