#!/usr/bin/env python3
"""Rakit video history-en 2026-10-20 (Cuban Missile Crisis 1962).
36 beats x 2 segmen gambar (a/b) = 72 segmen. Ringan: 1280x720, preset
ultrafast, film grain, semua ffmpeg via ffmpeg-queue.sh.
Title card 3s + bumper voice-clone di TENGAH (setelah beat-018) + CTA teks
'SUBSCRIBE for more untold history!' di akhir segmen beat-018 & 2 segmen terakhir.
Audio: 3s hening + beats 1-18 + bumper + beats 19-36 (44100 Hz).
Aturan anti-macet: gambar a/b hilang -> pakai huruf lain / beat tetangga.
Concat aman: 6 chunk demuxer-copy, lalu concat-FILTER, lalu mux, lalu
burn-in subtitle SRT (style terbukti jalan di VM ini).
Hasil: video/2026-10-20.mp4 + script/chapters-ts-2026-10-20.txt +
script/deskripsi-final-2026-10-20.txt + script/subs-2026-10-20.srt
"""
import subprocess, os, sys, json, shutil

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
DATE = "2026-10-20"
N_BEATS = 36
ADIR = os.path.join(BASE, "audio", DATE)
GDIR = os.path.join(BASE, "gambar", DATE, "final")
OUT = os.path.join(BASE, "video", f"{DATE}.mp4")
OUT_MUX = os.path.join(BASE, "video", f"_tmp_mux_{DATE}.mp4")
OUT_TMP = os.path.join(BASE, "video", f"_tmp_final_{DATE}.mp4")
TXTDIR = os.path.join(BASE, "video", f"_tmp_txt_{DATE}")
os.makedirs(TXTDIR, exist_ok=True)
SRT = os.path.join(BASE, "script", f"subs-{DATE}.srt")
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-history-en.wav"
TITLE_DUR = 3.0
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BUMPER_AFTER_BEAT = 18        # bumper disisipkan setelah beat-018
N_CHUNK = 6
CTA_TEXT = "SUBSCRIBE for more untold history!"
IMG_SUB = {}   # diisi saat run bila ada beat tanpa gambar (aturan anti-macet)

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
    assert len(bj) == N_BEATS, f"beats: {len(bj)} != {N_BEATS}"
    return bj

def load_overlays(bj):
    ov, ch = {}, []
    for x in bj:
        idx = int(x["beat"].split("-")[1]) - 1
        if x.get("overlay"):
            assert "%" not in x["overlay"] and ":" not in x["overlay"], \
                f"overlay berbahaya: {x['overlay']}"
            ov[idx] = x["overlay"]
        if x.get("chapter"):
            ch.append((idx, x["chapter"]))
    return ov, ch

BEATS = load_beats()
OVERLAYS, CHAPTERS = load_overlays(BEATS)
assert len(OVERLAYS) == 4, f"overlay: {len(OVERLAYS)} != 4"

def img_for(beat_no, letter):
    cand = []
    src = IMG_SUB.get(beat_no, beat_no)
    cand.append(os.path.join(GDIR, f"beat-{src:03d}{letter}.jpg"))
    cand.append(os.path.join(GDIR, f"beat-{src:03d}-{letter}.jpg"))
    other = "b" if letter == "a" else "a"
    cand.append(os.path.join(GDIR, f"beat-{src:03d}{other}.jpg"))
    cand.append(os.path.join(GDIR, f"beat-{src:03d}-{other}.jpg"))
    for nb in (src - 1, src + 1, src - 2, src + 2):
        if 1 <= nb <= N_BEATS:
            cand.append(os.path.join(GDIR, f"beat-{nb:03d}a.jpg"))
            cand.append(os.path.join(GDIR, f"beat-{nb:03d}-a.jpg"))
    for p in cand:
        if os.path.exists(p):
            return p
    raise RuntimeError(f"tidak ada gambar untuk beat-{beat_no:03d}")

def render_titlecard(out):
    if os.path.exists(out) and dur(out) >= TITLE_DUR * 0.9:
        return True
    meta = json.load(open(os.path.join(BASE, "script", f"meta-{DATE}.json")))
    l1, l2 = meta["title_card_l1"], meta["title_card_l2"]
    assert "%" not in l1 + l2 and ":" not in l1 + l2
    t1 = os.path.join(TXTDIR, "title-1.txt"); t2 = os.path.join(TXTDIR, "title-2.txt")
    open(t1, "w").write(l1); open(t2, "w").write(l2)
    vf = (f"drawtext=fontfile={FONT}:textfile={t1}:fontsize=110:fontcolor=white:"
          f"x=(w-text_w)/2:y=h/2-140,"
          f"drawtext=fontfile={FONT}:textfile={t2}:fontsize=46:fontcolor=#ffd97a:"
          f"x=(w-text_w)/2:y=h/2+10,"
          f"setsar=1")
    r = subprocess.run([FFQ, "-y", "-f", "lavfi",
                        "-i", f"color=c=black:s=1280x720:r=30:d={TITLE_DUR}",
                        "-vf", vf, "-t", str(TITLE_DUR),
                        "-c:v", "libx264", "-preset", "ultrafast",
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
    vf = (f"scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
          f"{zp},setsar=1,"
          "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
          "noise=alls=6:allf=t,"
          "vignette=PI/5")
    beat_idx = idx // 2
    if idx % 2 == 0 and beat_idx in OVERLAYS:
        tfile = os.path.join(TXTDIR, f"overlay-{idx}.txt")
        open(tfile, "w", encoding="utf-8").write(OVERLAYS[beat_idx])
        vf += (f",drawtext=fontfile={FONT}:textfile={tfile}:fontsize=46:"
               "fontcolor=white:borderw=2:bordercolor=black@0.8:"
               "x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.55:boxborderw=24")
    if extra_text:
        assert "%" not in extra_text
        tfile = os.path.join(TXTDIR, f"cta-{idx}.txt")
        open(tfile, "w").write(extra_text)
        vf += (f",drawtext=fontfile={FONT}:textfile={tfile}:fontsize=54:"
               "fontcolor=#ffd97a:borderw=2:bordercolor=black@0.8:"
               "x=(w-text_w)/2:y=60:box=1:boxcolor=black@0.55:boxborderw=20")
    r = subprocess.run([FFQ, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "ultrafast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True)
    return r.returncode == 0

def write_list(paths, dst):
    with open(dst, "w") as f:
        for s in paths:
            f.write(f"file '{os.path.abspath(s)}'\n")

def srt_ts(sec):
    ms = int(round((sec - int(sec)) * 1000))
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = int(sec % 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def wrap(text, width=42):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return "\n".join(lines[:2])

def main():
    # --- durasi audio per beat (slide dihitung dari timeline audio) ---
    durs = {}
    for i in range(1, N_BEATS + 1):
        p = os.path.join(ADIR, f"beat-{i:03d}.mp3")
        d = dur(p)
        assert d > 0.5, f"audio tidak valid: {p} ({d})"
        durs[f"beat-{i:03d}"] = round(d, 3)
    json.dump(durs, open(os.path.join(ADIR, f"durasi-beat-{DATE}.json"), "w"), indent=1)

    # --- 2 segmen per beat: split 55/45 dari durasi audio beat ---
    segs = []          # (img_path, seg_dur, seg_global_idx)
    for i in range(1, N_BEATS + 1):
        d = durs[f"beat-{i:03d}"]
        da = round(d * 0.55, 3)
        db = round(d - da, 3)
        segs.append((img_for(i, "a"), da))
        segs.append((img_for(i, "b"), db))
    seg_durs = [s[1] for s in segs]
    bumper_dur = dur(BUMPER)
    assert bumper_dur > 0.5, "bumper tidak valid"
    total = TITLE_DUR + sum(seg_durs) + bumper_dur
    print(f"72 segmen, total target {total:.1f}s = {total/60:.2f} mnt "
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
    CTA_IDX = {2 * BUMPER_AFTER_BEAT - 1, 70, 71}   # seg akhir beat-18, 2 seg terakhir
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
            if seg_video(segs[i][0], seg_durs[i], i, s, extra_text=extra) \
               and dur(s) >= seg_durs[i] * 0.9:
                with lock:
                    n_done[0] += 1
                    print(f"  [{n_done[0]}/72] s{i:03d} OK ({seg_durs[i]:.1f}s)", flush=True)
                return
            print(f"    retry s{i:03d}", flush=True)
        raise RuntimeError(f"GAGAL: s{i:03d}")
    with ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(render_one, range(len(segs))))
    print("  72 segmen selesai", flush=True)

    # --- segmen bumper: gambar beat-018-a, tanpa CTA ---
    bseg = os.path.join(tmpd, "bumper.mp4")
    if not (os.path.exists(bseg) and dur(bseg) >= bumper_dur * 0.9):
        if os.path.exists(bseg):
            os.remove(bseg)
        print(f"  render bumper ({bumper_dur:.1f}s)...", flush=True)
        if not (seg_video(img_for(BUMPER_AFTER_BEAT, "a"), bumper_dur,
                          2 * BUMPER_AFTER_BEAT - 2, bseg)
                and dur(bseg) >= bumper_dur * 0.9):
            print("GAGAL: segmen bumper"); sys.exit(1)

    # --- urutan final: title + segs beat 1-18 + bumper + segs beat 19-36 ---
    mid = 2 * BUMPER_AFTER_BEAT
    vsegs = [tcard] + [os.path.join(tmpd, f"s{i:03d}.mp4") for i in range(mid)] \
            + [bseg] + [os.path.join(tmpd, f"s{i:03d}.mp4") for i in range(mid, len(segs))]
    vdurs = [TITLE_DUR] + seg_durs[:mid] + [bumper_dur] + seg_durs[mid:]
    assert len(vsegs) == 74 == len(vdurs)
    silence3 = os.path.join(ADIR, "_silence3s.mp3")
    if not (os.path.exists(silence3) and dur(silence3) >= 2.9):
        subprocess.run([FFQ, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                        "-t", str(TITLE_DUR), "-ar", "44100", "-ac", "2",
                        "-c:a", "libmp3lame", silence3], capture_output=True, check=True)
    asegs = [silence3] + [os.path.join(ADIR, f"beat-{i:03d}.mp3") for i in range(1, BUMPER_AFTER_BEAT + 1)] \
            + [BUMPER] + [os.path.join(ADIR, f"beat-{i:03d}.mp3") for i in range(BUMPER_AFTER_BEAT + 1, N_BEATS + 1)]
    assert len(asegs) == 1 + N_BEATS + 1

    # --- 6 chunk: concat demuxer -c copy, verifikasi ffprobe per chunk ---
    idxs = [0]
    per = len(vsegs) // N_CHUNK
    for c in range(1, N_CHUNK):
        idxs.append(c * per)
    idxs.append(len(vsegs))
    print(f"  chunk boundaries: {idxs}", flush=True)
    # batas chunk audio dihitung TERPISAH (asegs 38 item, bukan 74 seperti video)
    n_a = len(asegs)
    aidxs = [0]
    per_a = n_a // N_CHUNK
    for c in range(1, N_CHUNK):
        aidxs.append(c * per_a)
    aidxs.append(n_a)
    print(f"  audio chunk boundaries: {aidxs}", flush=True)
    vchunks, achunks = [], []
    for c in range(N_CHUNK):
        a, b = idxs[c], idxs[c + 1]
        aa, ab = aidxs[c], aidxs[c + 1]
        assert ab - aa > 0, f"chunk audio {c} kosong"
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
            lst = os.path.join(tmpd, f"listA{c}.txt"); write_list(asegs[aa:ab], lst)
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
        fc = "".join(f"[{i}:v]setsar=1[v{i}];" for i in range(N_CHUNK))
        fc += "".join(f"[v{i}]" for i in range(N_CHUNK)) + f"concat=n={N_CHUNK}:v=1:a=0"
        cmd += ["-filter_complex", fc,
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
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

    # --- mux ---
    subprocess.run([FFQ, "-y", "-i", vconcat, "-i", aconcat,
                    "-c:v", "copy", "-c:a", "copy",
                    "-shortest", "-movflags", "+faststart", OUT_MUX],
                   capture_output=True, check=True)
    dtmp = dur(OUT_MUX)
    print(f"  mux: {dtmp:.1f}s vs target {total:.1f}s", flush=True)
    assert abs(dtmp - total) < 5.0, f"DURASI MUX SALAH: {dtmp:.1f}s vs {total:.1f}s"
    vinfo = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=p=0", OUT_MUX],
        capture_output=True, text=True).stdout.strip()
    assert vinfo == "1280,720", f"RESOLUSI SALAH: {vinfo}"
    assert os.path.getsize(OUT_MUX) > 10 * 1024 * 1024, "FILE TERLALU KECIL"

    # --- subtitle SRT dari timeline audio (beats 1-36) ---
    starts = {}
    t = TITLE_DUR
    for i in range(1, N_BEATS + 1):
        if i == BUMPER_AFTER_BEAT + 1:
            t += bumper_dur
        starts[i] = t
        t += durs[f"beat-{i:03d}"]
    with open(SRT, "w", encoding="utf-8") as f:
        n = 1
        for i in range(1, N_BEATS + 1):
            txt = BEATS[i - 1]["text"].replace("[JEDA]", " ").strip()
            while "  " in txt:
                txt = txt.replace("  ", " ")
            f.write(f"{n}\n{srt_ts(starts[i])} --> {srt_ts(starts[i] + durs[f'beat-{i:03d}'])}\n{wrap(txt)}\n\n")
            n += 1
    print(f"  SRT: {SRT}", flush=True)

    # --- burn-in subtitle (style terbukti jalan di VM ini) ---
    subprocess.run([FFQ, "-y", "-i", OUT_MUX,
                    "-vf", f"subtitles={SRT}:force_style='FontName=DejaVu Sans,FontSize=22,BorderStyle=1,Outline=2,Alignment=2,MarginV=45'",
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                    "-r", "30", "-c:a", "copy", "-movflags", "+faststart", OUT_TMP],
                   capture_output=True, check=True)
    dtmp = dur(OUT_TMP)
    print(f"  final (subtitle): {dtmp:.1f}s vs target {total:.1f}s", flush=True)
    assert abs(dtmp - total) < 5.0, f"DURASI FINAL SALAH: {dtmp:.1f}s vs {total:.1f}s"
    # verifikasi PER STREAM (pelajaran 2026-10-18: durasi format != durasi stream)
    sv = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        OUT_TMP], capture_output=True, text=True).stdout.strip()
    sa = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        OUT_TMP], capture_output=True, text=True).stdout.strip()
    dv, da = float(sv), float(sa)
    print(f"  stream video: {dv:.1f}s | stream audio: {da:.1f}s", flush=True)
    assert abs(dv - da) < 5.0, f"VIDEO/AUDIO TIDAK SINKRON: v={dv:.1f}s a={da:.1f}s"
    assert abs(dv - total) < 5.0 and abs(da - total) < 5.0, "durasi stream vs target > 5 dtk"
    shutil.move(OUT_TMP, OUT)
    print(f"OK: {OUT} ({dur(OUT)/60:.2f} menit, terverifikasi)", flush=True)

    # --- chapters + deskripsi ---
    def fmt(s):
        h = int(s // 3600); m = int((s % 3600) // 60); sec = int(s % 60)
        return f"{h}:{m:02d}:{sec:02d}"
    chmap = dict(CHAPTERS)
    lines = []
    for i in sorted(chmap):
        ts = starts[i + 1]
        lines.append(f"{fmt(ts)} — {chmap[i]}")
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
