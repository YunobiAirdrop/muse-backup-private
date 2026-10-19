#!/usr/bin/env python3
"""Rakit POV 2026-10-19 (phinisi) gaya chunk + two-pass (aturan AGENTS.md 2026-10-19):
Pass 1: chunk (input langsung + filter_complex, tanpa concat demuxer) -> concat copy -> intermediate CFR.
Pass 2: intermediate + audio final -> drawtext overlay (5 momen) -> mux, verifikasi PER STREAM.
Output: TEMP dulu -> verifikasi -> pindah ke final."""
import subprocess, os, sys, json, shutil, glob

BASE = "/home/hatch/workspace/youtube-otomatis"
FFQ = os.path.join(BASE, "ffmpeg-queue.sh")
GDIR = os.path.join(BASE, "gambar/2026-10-19")
AUDIO = os.path.join(BASE, "audio/gabungan-2026-10-19-fast.mp3")
DJ = os.path.join(BASE, "audio/durasi-beat-2026-10-19.json")
TMPD = os.path.join(BASE, "video/_tmp_segs_2026-10-19")
OUT_FINAL = os.path.join(BASE, "video/2026-10-19-final.mp4")
OUT_TMP = os.path.join(BASE, "video/_tmp_2026-10-19.mp4")
INTER = os.path.join(TMPD, "intermediate.mp4")
CHUNK = 22
TITLE_DUR = 3.0
TITLE_L1 = "POV: PRAJURIT AZTEC"
TITLE_L2 = "Tenochtitlan, 1519-1521"
TITLE_L3 = "@ceritarakyat862"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
# overlay: (beat, teks, durasi_detik_atau_None=sepanjang_beat)
OVERLAYS = [(1, "LAYAR PUTIH DI CAKRAWALA", None), (28, "PEMBANTAIAN TOXCATL", None),
            (40, "NOCHE TRISTE - MALAM BERDUKA", None), (64, "TENOCHTITLAN JATUH 1521", None), (80, "SUBSCRIBE", 3.0)]
PANEL_BEATS = {34, 42, 58}  # efek bingkai panel komik

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def stream_durs(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    out = {}
    for line in r.stdout.strip().splitlines():
        parts = line.split(",")
        if len(parts) == 2:
            try:
                out[parts[0]] = float(parts[1])
            except ValueError:
                pass
    return out

def zp(idx, frames):
    mode = idx % 4
    if mode == 0:
        return f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    if mode == 1:
        return f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='(iw-iw/zoom)*on/{frames}':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    if mode == 2:
        return f"zoompan=z='max(1.15-0.0012*on,1.0)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    return f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='(iw-iw/zoom)*on/{frames}':y='(ih-ih/zoom)*on/{frames}':s=1280x720:fps=30"

def make_titlecard(out):
    from PIL import Image, ImageDraw, ImageFont
    if os.path.exists(out) and dur(out) >= TITLE_DUR * 0.9:
        print(f"  title card ada: {out}", flush=True); return
    W, H = 1280, 720
    bg = Image.new("RGB", (W, H), (14, 20, 24))
    d = ImageDraw.Draw(bg)
    d.rectangle([30, 30, W-30, H-30], outline=(212, 175, 55), width=4)
    f1 = ImageFont.truetype(FONT, 92); f2 = ImageFont.truetype(FONT, 52); f3 = ImageFont.truetype(FONT, 38)
    def center(txt, font, y, fill):
        bb = d.textbbox((0, 0), txt, font=font)
        d.text(((W-(bb[2]-bb[0]))//2, y), txt, font=font, fill=fill)
    center(TITLE_L1, f1, 220, (212, 175, 55))
    center(TITLE_L2, f2, 380, (245, 240, 230))
    center(TITLE_L3, f3, 560, (160, 150, 140))
    png = os.path.join(TMPD, "titlecard.png")
    os.makedirs(TMPD, exist_ok=True)
    bg.save(png)
    vf = ("scale=1280:720,eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
          "noise=alls=6:allf=t,vignette=PI/5")
    r = subprocess.run([FFQ, "-y", "-loop", "1", "-i", png, "-vf", vf,
                        "-t", str(TITLE_DUR), "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:]); sys.exit(1)
    print(f"  OK title card -> {out}", flush=True)

def render_chunk(idxs, seg_durs, out):
    if os.path.exists(out):
        exp = sum(seg_durs[i] for i in idxs)
        if abs(dur(out) - exp) < 3:
            print(f"  chunk ada: {out}", flush=True); return
        os.remove(out)
    cmd = [FFQ, "-y"]
    for i in idxs:
        cmd += ["-i", os.path.join(GDIR, f"img-{i+1:03d}.jpg")]
    parts, vlabels = [], []
    for k, i in enumerate(idxs):
        frames = int(seg_durs[i] * 30)
        filt = (f"[{k}:v]scale=1280:720,{zp(i, frames)},"
                f"eq=contrast=1.08:saturation=0.92:brightness=-0.02,")
        if (i + 1) in PANEL_BEATS:
            filt += "drawbox=x=18:y=18:w=iw-36:h=ih-36:c=black:t=14,drawbox=x=36:y=36:w=iw-72:h=ih-72:c=white:t=4,"
        filt += ("noise=alls=6:allf=t,vignette=PI/5,setsar=1,"
                 f"trim=duration={seg_durs[i]:.3f},setpts=PTS-STARTPTS[v{k}]")
        parts.append(filt)
        vlabels.append(f"[v{k}]")
    fc = ";".join(parts) + ";" + "".join(vlabels) + f"concat=n={len(idxs)}:v=1:a=0[vout]"
    cmd += ["-filter_complex", fc, "-map", "[vout]",
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(1)
    print(f"  OK chunk -> {out} ({dur(out):.1f}s)", flush=True)

def main():
    dj = json.load(open(DJ))
    n = len(dj)
    seg_durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(n)]
    audio_dur = dur(AUDIO)
    scale = audio_dur / sum(seg_durs)
    seg_durs = [d * scale for d in seg_durs]
    print(f"skala segmen {scale:.4f} (narasi {audio_dur:.1f}s -> slide total {sum(seg_durs):.1f}s)", flush=True)
    os.makedirs(TMPD, exist_ok=True)
    have = sorted(glob.glob(os.path.join(TMPD, "s[0-9][0-9][0-9].mp4")))
    have_idx = set()
    for s in have:
        i = int(os.path.basename(s)[1:4])
        if dur(s) >= seg_durs[i] * 0.9:
            have_idx.add(i)
        else:
            os.remove(s)
    todo = [i for i in range(n) if i not in have_idx]
    chunks = [todo[i:i+CHUNK] for i in range(0, len(todo), CHUNK)]
    for c, idxs in enumerate(chunks):
        out = os.path.join(TMPD, f"chunk{c}.mp4")
        print(f"render chunk{c}: beat {idxs[0]+1}-{idxs[-1]+1} ...", flush=True)
        render_chunk(idxs, seg_durs, out)
    segs = {}
    for s in glob.glob(os.path.join(TMPD, "s[0-9][0-9][0-9].mp4")):
        segs[int(os.path.basename(s)[1:4])] = s
    chunk_map = {}
    for c, idxs in enumerate(chunks):
        for j in idxs:
            chunk_map[j] = c
    ordered, used_chunks = [], set()
    for i in range(n):
        if i in segs:
            ordered.append(segs[i])
        else:
            c = chunk_map[i]
            if c not in used_chunks:
                ordered.append(os.path.join(TMPD, f"chunk{c}.mp4"))
                used_chunks.add(c)
    tcard = os.path.join(TMPD, "titlecard.mp4")
    make_titlecard(tcard)
    ordered = [tcard] + ordered
    lst = os.path.join(TMPD, "list.txt")
    with open(lst, "w") as f:
        for p in ordered:
            f.write(f"file '{os.path.abspath(p)}'\n")
    # PASS 1: concat copy -> intermediate CFR (tanpa filter+audio digabung)
    r = subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", INTER], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(1)
    exp_v = TITLE_DUR + sum(seg_durs)
    sd = stream_durs(INTER)
    print(f"pass1: expected {exp_v:.1f}s, got video {sd.get('video', 0):.1f}s", flush=True)
    assert abs(sd.get("video", 0) - exp_v) < 5, "PASS1 DURASI VIDEO NGAWUR"
    # PASS 2: drawtext overlay + mux audio (delay 3 dtk selaras title card)
    starts = []
    acc = TITLE_DUR
    for d in seg_durs:
        starts.append(acc); acc += d
    dts = []
    for beat, teks, od in OVERLAYS:
        s = starts[beat - 1]
        e = s + (od if od else seg_durs[beat - 1])
        dts.append(f"drawtext=fontfile={FONT}:text='{teks}':fontsize=64:fontcolor=white:"
                   f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-150:"
                   f"enable='between(t\\,{s:.2f}\\,{e:.2f})'")
    vf = ",".join(dts)
    exp_total = exp_v
    r = subprocess.run([FFQ, "-y", "-i", INTER, "-i", AUDIO,
                        "-filter_complex", f"[0:v]{vf}[v];[1:a]adelay=3000|3000,apad[a]",
                        "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30",
                        "-c:a", "aac", "-b:a", "128k", "-t", f"{exp_total:.2f}",
                        "-movflags", "+faststart", OUT_TMP],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(1)
    sd = stream_durs(OUT_TMP)
    print(f"pass2 per-stream: {sd}, expected {exp_total:.1f}s", flush=True)
    assert abs(sd.get("video", 0) - exp_total) < 5, "PASS2 VIDEO NGAWUR"
    assert abs(sd.get("audio", 0) - exp_total) < 5, "PASS2 AUDIO NGAWUR"
    shutil.move(OUT_TMP, OUT_FINAL)
    print(f"OK: {OUT_FINAL} ({sd.get('video', 0)/60:.1f} menit)")
    shutil.rmtree(TMPD)

if __name__ == "__main__":
    main()
