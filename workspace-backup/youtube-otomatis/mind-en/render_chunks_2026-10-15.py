#!/usr/bin/env python3
"""Render chunked Dark Mind Files 2026-10-15: 10 segmen per 1 panggilan ffmpeg.
Mengurangi akuisisi slot ffmpeg-queue dari 76 menjadi 8. Tiap chunk = N input
gambar -> filter_complex (Ken Burns + grain + vignette per input) -> concat.
Resume: chunk yang sudah ada & durasi OK dilewati.
Penggunaan: python3 render_chunks_2026-10-15.py [--finalize]
  tanpa flag: render semua chunk saja. --finalize: gabung chunk + mux VO + verifikasi + pindah final.
"""
import subprocess, os, sys, json, shutil, glob

BASE = "/home/hatch/workspace/youtube-otomatis/mind-en"
GDIR = f"{BASE}/gambar-2026-10-15"
TMPD = f"{BASE}/video/_tmp_segs-2026-10-15"
CHD = f"{BASE}/video/_tmp_chunks-2026-10-15"
AUDIO = f"{BASE}/audio/voiceover-final-2026-10-15.mp3"
OUT = f"{BASE}/video/2026-10-15.mp4"
DURJ = f"{BASE}/audio/durasi-beat-final-2026-10-15.json"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
CHUNK = int(os.environ.get("CHUNK_N", "10"))

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def zp_expr(seg_dur, idx):
    total_frames = max(int(seg_dur * 30), 15)
    mode = idx % 4
    if mode == 0:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
    elif mode == 1:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='(iw-iw/zoom)*on/{total_frames}':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
    elif mode == 2:
        zp = f"zoompan=z='max(1.15-0.0012*on,1.0)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
    else:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{total_frames}':s=1920x1080:fps=30"
    return zp

def bumper_card():
    from PIL import Image, ImageDraw, ImageFont
    p = os.path.join(TMPD, "bumper-card.png")
    if os.path.exists(p):
        return p
    os.makedirs(TMPD, exist_ok=True)
    img = Image.new("RGB", (1920, 1080), (8, 8, 14))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 120, 1920, 126], fill=(176, 141, 79))
    d.rectangle([0, 954, 1920, 960], fill=(176, 141, 79))
    fp = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    f1 = ImageFont.truetype(fp, 120); f2 = ImageFont.truetype(fp, 44)
    t1, t2 = "DARK MIND FILES", "a quick word from the host"
    b1 = d.textbbox((0, 0), t1, font=f1); b2 = d.textbbox((0, 0), t2, font=f2)
    d.text(((1920 - (b1[2] - b1[0])) / 2, 460), t1, font=f1, fill=(232, 220, 190))
    d.text(((1920 - (b2[2] - b2[0])) / 2, 620), t2, font=f2, fill=(150, 150, 150))
    img.save(p)
    return p

def render_chunk(cidx, seg_ids, durs, bcard):
    os.makedirs(CHD, exist_ok=True)
    out = os.path.join(CHD, f"chunk-{cidx:02d}.mp4")
    target = sum(durs)
    if os.path.exists(out) and dur(out) >= target * 0.97:
        print(f"  chunk-{cidx:02d} sudah ada, lewati", flush=True)
        return True
    if os.path.exists(out):
        os.remove(out)
    cmd = [FFQ, "-y"]
    for sid in seg_ids:
        img = bcard if sid == "bumper" else os.path.join(GDIR, f"{sid}.webp")
        cmd += ["-loop", "1", "-i", img]
    fc = []
    for k, (sid, sd) in enumerate(zip(seg_ids, durs)):
        fc.append(
            f"[{k}:v]scale=1920:1080,{zp_expr(sd, k)},"
            "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
            "noise=alls=8:allf=t,vignette=PI/5,format=yuv420p,setpts=PTS-STARTPTS[v{k}]".replace("{k}", str(k))
        )
    ins = "".join(f"[v{k}]" for k in range(len(seg_ids)))
    fc.append(f"{ins}concat=n={len(seg_ids)}:v=1:a=0[vout]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[vout]",
            "-t", f"{target:.3f}", "-c:v", "libx264", "-preset", "veryfast",
            "-pix_fmt", "yuv420p", "-r", "30", out]
    print(f"  render chunk-{cidx:02d} ({len(seg_ids)} segmen, {target:.1f}s)...", flush=True)
    for attempt in range(2):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and dur(out) >= target * 0.97:
            print(f"  chunk-{cidx:02d} OK", flush=True)
            return True
        print(f"    retry chunk-{cidx:02d} (attempt {attempt+2}): {r.stderr[-300:]}", flush=True)
    print(f"GAGAL: chunk-{cidx:02d}")
    return False

def main():
    dj = json.load(open(DURJ))
    order, dd = dj["order"], dj["durations"]
    bcard = bumper_card()
    chunks = [order[i:i + CHUNK] for i in range(0, len(order), CHUNK)]
    # slice chunk opsional: python3 render_chunks_2026-10-15.py <c0> <c1> [--finalize]
    args = [a for a in sys.argv[1:] if a != "--finalize"]
    c0, c1 = (int(args[0]), int(args[1])) if len(args) >= 2 else (0, len(chunks))
    print(f"{len(order)} segmen -> {len(chunks)} chunk (slice {c0}-{c1})", flush=True)
    for cidx in range(c0, min(c1, len(chunks))):
        seg_ids = chunks[cidx]
        durs = [float(dd[s]) for s in seg_ids]
        if not render_chunk(cidx, seg_ids, durs, bcard):
            sys.exit(1)
    if "--finalize" in sys.argv:
        finalize(dj)

def finalize(dj):
    chunks = sorted(glob.glob(os.path.join(CHD, "chunk-*.mp4")))
    assert chunks, "tidak ada chunk"
    lst = os.path.join(CHD, "list.txt")
    with open(lst, "w") as f:
        for c in chunks:
            f.write(f"file '{os.path.abspath(c)}'\n")
    concat = os.path.join(CHD, "concat.mp4")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)
    tmp_out = os.path.join(CHD, "_video-tmp.mp4")
    subprocess.run([FFQ, "-y", "-i", concat, "-i", AUDIO,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", tmp_out],
                   capture_output=True, check=True)
    target = dj["total"]
    got = dur(tmp_out)
    print(f"verifikasi durasi: target={target:.1f}s aktual={got:.1f}s", flush=True)
    if abs(got - target) >= 5:
        print(f"GAGAL verifikasi durasi. Final TIDAK ditimpa: {tmp_out}")
        sys.exit(2)
    shutil.move(tmp_out, OUT)
    print(f"OK: {OUT} ({dur(OUT)/60:.2f} menit)")

if __name__ == "__main__":
    main()
