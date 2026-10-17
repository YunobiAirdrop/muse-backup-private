#!/usr/bin/env python3
"""Rakit video history-en 2026-10-13 (Titanic 1912).
Ringan: 1280x720, preset veryfast, film grain, semua ffmpeg via ffmpeg-queue.sh.
Title card 3s + bumper voice-clone di TENGAH (setelah beat-036) + CTA teks
'SUBSCRIBE for more untold history!' di beat-036 & 2 beat terakhir.
Audio: 3s hening + beats 1-36 + bumper + beats 37-72 (44100 Hz).
Gambar hilang (038/042/054) diganti tetangga (039/041/053) - aturan anti-macet.
Concat aman: 6 chunk demuxer-copy, lalu concat-FILTER (video 6 input, audio 6 input).
Hasil: video/2026-10-13.mp4 + script/chapters-ts-2026-10-13.txt + script/deskripsi-final-2026-10-13.txt
"""
import subprocess, os, sys, json, shutil

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
DATE = "2026-10-13"
ADIR = os.path.join(BASE, "audio", DATE)
GDIR = os.path.join(BASE, "gambar", DATE, "final")
OUT = os.path.join(BASE, "video", f"{DATE}.mp4")
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-history-en.wav"
TITLE_DUR = 3.0
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BUMPER_AFTER_IDX = 35          # setelah beat-036 (idx 35)
N_CHUNK = 6
CTA_TEXT = "SUBSCRIBE for more untold history!"
IMG_SUB = {38: 39, 42: 41, 54: 53}   # beat hilang -> gambar tetangga

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def load_overlays():
    bj = json.load(open(os.path.join(BASE, "beats", f"beats-{DATE}.json")))
    ov, ch = {}, []
    for x in bj:
        idx = int(x["beat"].split("-")[1]) - 1
        if x.get("overlay"):
            ov[idx] = x["overlay"]
        if x.get("chapter"):
            ch.append((idx, x["chapter"]))
    return ov, ch
OVERLAYS, CHAPTERS = load_overlays()
assert len(OVERLAYS) == 4, f"overlay: {len(OVERLAYS)} != 4"

def img_for(beat_no):
    src = IMG_SUB.get(beat_no, beat_no)
    p = os.path.join(GDIR, f"beat-{src:03d}.jpg")
    assert os.path.exists(p), f"gambar hilang: {p}"
    return p

def render_titlecard(out):
    if os.path.exists(out) and dur(out) >= TITLE_DUR * 0.9:
        return True
    meta = json.load(open(os.path.join(BASE, "script", f"meta-{DATE}.json")))
    t1 = f"/tmp/title-he13-1.txt"; t2 = f"/tmp/title-he13-2.txt"
    open(t1, "w").write(meta["title_card_l1"])
    open(t2, "w").write(meta["title_card_l2"])
    assert "%" not in meta["title_card_l1"] + meta["title_card_l2"]
    vf = (f"drawtext=fontfile={FONT}:textfile={t1}:fontsize=110:fontcolor=white:"
          f"x=(w-text_w)/2:y=h/2-140,"
          f"drawtext=fontfile={FONT}:textfile={t2}:fontsize=46:fontcolor=#ffd97a:"
          f"x=(w-text_w)/2:y=h/2+10,"
          f"setsar=1")
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
    vf = (f"scale=1280:720,{zp},setsar=1,"
          "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
          "noise=alls=6:allf=t,"
          "vignette=PI/5")
    if idx in OVERLAYS:
        assert "%" not in OVERLAYS[idx]
        tfile = f"/tmp/overlay-he13-{idx}.txt"
        open(tfile, "w", encoding="utf-8").write(OVERLAYS[idx])
        vf += (f",drawtext=fontfile={FONT}:textfile={tfile}:fontsize=46:"
               "fontcolor=white:borderw=2:bordercolor=black@0.8:"
               "x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.55:boxborderw=24")
    if extra_text:
        assert "%" not in extra_text
        tfile = f"/tmp/cta-he13-{idx}.txt"
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

def write_list(paths, dst):
    with open(dst, "w") as f:
        for s in paths:
            f.write(f"file '{os.path.abspath(s)}'\n")

def main():
    # --- durasi audio (verifikasi ulang + refresh json) ---
    durs = {}
    for i in range(1, 73):
        p = os.path.join(ADIR, f"beat-{i:03d}.mp3")
        d = dur(p)
        assert d > 0.5, f"audio tidak valid: {p} ({d})"
        durs[f"beat-{i:03d}"] = round(d, 3)
    json.dump(durs, open(os.path.join(ADIR, f"durasi-beat-{DATE}.json"), "w"), indent=1)
    seg_durs = [durs[f"beat-{i+1:03d}"] for i in range(72)]
    bumper_dur = dur(BUMPER)
    assert bumper_dur > 0.5, "bumper tidak valid"
    total = TITLE_DUR + sum(seg_durs) + bumper_dur
    print(f"72 gambar (3 diganti tetangga), total target {total:.1f}s = {total/60:.2f} mnt "
          f"(bumper {bumper_dur:.2f}s)", flush=True)

    tmpd = os.path.join(BASE, "video", f"_tmp_segs_{DATE}")
    os.makedirs(tmpd, exist_ok=True)

    # --- title card ---
    tcard = os.path.join(tmpd, "title.mp4")
    print("  render title card...", flush=True)
    if not render_titlecard(tcard):
        print("GAGAL: title card"); sys.exit(1)

    # --- segmen gambar (2 worker paralel, tetap dalam batas 2 slot VM) ---
    from concurrent.futures import ThreadPoolExecutor
    import threading
    CTA_IDX = {BUMPER_AFTER_IDX, 70, 71}
    lock = threading.Lock()
    n_done = [0]
    def render_one(i):
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        if os.path.exists(s) and dur(s) >= seg_durs[i] * 0.9:
            with lock:
                n_done[0] += 1
            return
        if os.path.exists(s):
            os.remove(s)
        extra = CTA_TEXT if i in CTA_IDX else None
        for attempt in range(2):
            if seg_video(img_for(i + 1), seg_durs[i], i, s, extra_text=extra) \
               and dur(s) >= seg_durs[i] * 0.9:
                with lock:
                    n_done[0] += 1
                    print(f"  [{n_done[0]}/72] s{i:03d} OK ({seg_durs[i]:.1f}s)", flush=True)
                return
            print(f"    retry s{i:03d}", flush=True)
        raise RuntimeError(f"GAGAL: s{i:03d}")
    with ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(render_one, range(72)))
    print(f"  72 segmen selesai", flush=True)

    # --- segmen bumper: gambar beat-036, tanpa CTA ---
    bseg = os.path.join(tmpd, "bumper.mp4")
    if not (os.path.exists(bseg) and dur(bseg) >= bumper_dur * 0.9):
        if os.path.exists(bseg):
            os.remove(bseg)
        print(f"  render bumper ({bumper_dur:.1f}s)...", flush=True)
        if not (seg_video(img_for(36), bumper_dur, BUMPER_AFTER_IDX, bseg)
                and dur(bseg) >= bumper_dur * 0.9):
            print("GAGAL: segmen bumper"); sys.exit(1)

    # --- urutan final: title + s000..s035 + bumper + s036..s071 ---
    vsegs = [tcard] + [os.path.join(tmpd, f"s{i:03d}.mp4") for i in range(0, BUMPER_AFTER_IDX + 1)] \
            + [bseg] + [os.path.join(tmpd, f"s{i:03d}.mp4") for i in range(BUMPER_AFTER_IDX + 1, 72)]
    vdurs = [TITLE_DUR] + seg_durs[:BUMPER_AFTER_IDX + 1] + [bumper_dur] + seg_durs[BUMPER_AFTER_IDX + 1:]
    assert len(vsegs) == 74 == len(vdurs)
    silence3 = os.path.join(ADIR, "_silence3s.mp3")
    if not (os.path.exists(silence3) and dur(silence3) >= 2.9):
        subprocess.run([FFQ, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                        "-t", str(TITLE_DUR), "-ar", "44100", "-ac", "2",
                        "-c:a", "libmp3lame", silence3], capture_output=True, check=True)
    asegs = [silence3] + [os.path.join(ADIR, f"beat-{i:03d}.mp3") for i in range(1, 37)] \
            + [BUMPER] + [os.path.join(ADIR, f"beat-{i:03d}.mp3") for i in range(37, 73)]
    assert len(asegs) == 74

    # --- 6 chunk: concat demuxer -c copy, verifikasi ffprobe per chunk ---
    idxs = [0]
    per = len(vsegs) // N_CHUNK
    for c in range(1, N_CHUNK):
        idxs.append(c * per)
    idxs.append(len(vsegs))
    print(f"  chunk boundaries: {idxs}", flush=True)
    vchunks, achunks = [], []
    for c in range(N_CHUNK):
        a, b = idxs[c], idxs[c + 1]
        exp_v = sum(vdurs[a:b])
        vc = os.path.join(tmpd, f"chunkV{c}.mp4")
        if not (os.path.exists(vc) and abs(dur(vc) - exp_v) < 1.0):
            lst = os.path.join(tmpd, f"listV{c}.txt"); write_list(vsegs[a:b], lst)
            subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                            "-c", "copy", vc], capture_output=True, check=True)
            d = dur(vc)
            assert abs(d - exp_v) < 1.0, f"chunkV{c}: {d:.1f}s vs target {exp_v:.1f}s"
        vchunks.append(vc)
        ac = os.path.join(tmpd, f"chunkA{c}.m4a")
        if not (os.path.exists(ac) and dur(ac) > 0.5):
            lst = os.path.join(tmpd, f"listA{c}.txt"); write_list(asegs[a:b], lst)
            subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                            "-ar", "44100", "-ac", "2",
                            "-c:a", "aac", "-b:a", "128k", ac],
                           capture_output=True, check=True)
        achunks.append(ac)
        print(f"  chunk{c}: V {dur(vc):.1f}s / A {dur(ac):.1f}s", flush=True)

    # --- concat-FILTER final: 6 input video, 6 input audio ---
    vconcat = os.path.join(tmpd, "vconcat.mp4")
    if not (os.path.exists(vconcat) and abs(dur(vconcat) - total) < 2.0):
        if os.path.exists(vconcat):
            os.remove(vconcat)
        cmd = [FFQ, "-y"]
        for vc in vchunks:
            cmd += ["-i", vc]
        # setsar per input: segmen zoompan ada yang SAR 27:32/9:8 -> concat filter butuh seragam
        fc = "".join(f"[{i}:v]setsar=1[v{i}];" for i in range(N_CHUNK))
        fc += "".join(f"[v{i}]" for i in range(N_CHUNK)) + f"concat=n={N_CHUNK}:v=1:a=0"
        cmd += ["-filter_complex", fc,
                "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                "-r", "30", vconcat]
        subprocess.run(cmd, capture_output=True, check=True)
        d = dur(vconcat)
        assert abs(d - total) < 2.0, f"vconcat {d:.1f}s vs target {total:.1f}s"
    print(f"  vconcat (filter): {dur(vconcat):.1f}s", flush=True)
    aconcat = os.path.join(tmpd, "aconcat.m4a")
    if not (os.path.exists(aconcat) and dur(aconcat) > 0.5):
        cmd = [FFQ, "-y"]
        for ac in achunks:
            cmd += ["-i", ac]
        cmd += ["-filter_complex", f"concat=n={N_CHUNK}:v=0:a=1",
                "-c:a", "aac", "-b:a", "128k", "-ar", "44100", aconcat]
        subprocess.run(cmd, capture_output=True, check=True)
    adur = dur(aconcat)
    print(f"  aconcat (filter): {adur:.1f}s | selisih: {abs(dur(vconcat)-adur):.2f}s", flush=True)
    assert abs(dur(vconcat) - adur) < 2.0, "video & audio tidak sinkron"

    # --- mux final ---
    subprocess.run([FFQ, "-y", "-i", vconcat, "-i", aconcat,
                    "-c:v", "copy", "-c:a", "copy",
                    "-shortest", "-movflags", "+faststart", OUT],
                   capture_output=True, check=True)
    print(f"OK: {OUT} ({dur(OUT)/60:.2f} menit)", flush=True)

    # --- chapters + deskripsi ---
    def fmt(s):
        h = int(s // 3600); m = int((s % 3600) // 60); sec = int(s % 60)
        return f"{h}:{m:02d}:{sec:02d}"
    cum = TITLE_DUR
    lines = []
    chmap = dict(CHAPTERS)
    for i in range(72):
        if i in chmap:
            ts = cum + (bumper_dur if i > BUMPER_AFTER_IDX else 0)
            lines.append(f"{fmt(ts)} — {chmap[i]}")
        cum += seg_durs[i]
    ch_txt = "CHAPTERS\n" + "\n".join(lines)
    open(os.path.join(BASE, "script", f"chapters-ts-{DATE}.txt"), "w").write(ch_txt + "\n")
    meta = json.load(open(os.path.join(BASE, "script", f"meta-{DATE}.json")))
    desc = meta["description"]
    placeholder = "CHAPTERS\n(placeholder — timestamps added during assembly)"
    assert placeholder in desc, "placeholder CHAPTERS tidak ditemukan di meta"
    desc = desc.replace(placeholder, ch_txt)
    open(os.path.join(BASE, "script", f"deskripsi-final-{DATE}.txt"), "w").write(desc + "\n")
    print("  chapters + deskripsi OK", flush=True)

    shutil.rmtree(tmpd)
    print("  staging dihapus", flush=True)

if __name__ == "__main__":
    main()
