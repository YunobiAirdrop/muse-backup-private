#!/usr/bin/env python3
"""Rakit video Dark Mind Files 2026-10-18: 1920x1080, grain halus, vignette, resume segmen.
Segmen: 75 beat + 1 bumper (title card gelap). Urutan & durasi dari
durasi-beat-final-2026-10-18.json. Output ke TEMP, verifikasi durasi via ffprobe
(|aktual-target|<5 dtk) SEBELUM pindah ke video/2026-10-18.mp4.
"""
import subprocess, os, glob, sys, json, shutil

BASE = "/home/hatch/workspace/youtube-otomatis/mind-en"
GDIR = f"{BASE}/gambar-2026-10-18"
TMPD = f"{BASE}/video/_tmp_segs-2026-10-18"
AUDIO = f"{BASE}/audio/voiceover-final-2026-10-18.mp3"
OUT = f"{BASE}/video/2026-10-18.mp4"
DURJ = f"{BASE}/audio/durasi-beat-final-2026-10-18.json"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def bumper_card():
    """Title card gelap sederhana untuk segmen bumper (PIL)."""
    from PIL import Image, ImageDraw, ImageFont
    p = os.path.join(TMPD, "bumper-card.png")
    if os.path.exists(p):
        return p
    img = Image.new("RGB", (1920, 1080), (8, 8, 14))
    d = ImageDraw.Draw(img)
    # garis emas tipis atas-bawah
    d.rectangle([0, 120, 1920, 126], fill=(176, 141, 79))
    d.rectangle([0, 954, 1920, 960], fill=(176, 141, 79))
    fp = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    f1 = ImageFont.truetype(fp, 120)
    f2 = ImageFont.truetype(fp, 44)
    t1 = "DARK MIND FILES"
    t2 = "a quick word from the host"
    b1 = d.textbbox((0, 0), t1, font=f1)
    b2 = d.textbbox((0, 0), t2, font=f2)
    d.text(((1920 - (b1[2] - b1[0])) / 2, 460), t1, font=f1, fill=(232, 220, 190))
    d.text(((1920 - (b2[2] - b2[0])) / 2, 620), t2, font=f2, fill=(150, 150, 150))
    img.save(p)
    return p

def kenburns(img, seg_dur, idx, out):
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
    vf = (f"scale=1920:1080,{zp},"
          "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
          "noise=alls=8:allf=t,"
          "vignette=PI/5")
    r = subprocess.run([FFQ, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True)
    return r.returncode == 0

def main():
    dj = json.load(open(DURJ))
    order = dj["order"]
    durs = dj["durations"]
    # slice opsional: python3 rakit_mind_en_2026-10-18.py <start> <end>
    s0, s1 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, len(order))
    print(f"{len(order)} segmen (slice {s0}-{s1}), target {sum(durs.values())/60:.2f} mnt", flush=True)
    os.makedirs(TMPD, exist_ok=True)
    bcard = bumper_card()
    for i in range(s0, min(s1, len(order))):
        sid = order[i]
        img = bcard if sid == "bumper" else os.path.join(GDIR, f"{sid}.webp")
        assert os.path.exists(img), f"gambar hilang: {img}"
        sd = float(durs[sid])
        s = os.path.join(TMPD, f"s{i:03d}.mp4")
        if os.path.exists(s) and dur(s) >= sd * 0.9:
            continue
        if os.path.exists(s):
            os.remove(s)
        if (i + 1) % 10 == 0:
            print(f"  render s{i:03d} ({sd:.1f}s) [{i+1}/{len(order)}]...", flush=True)
        for attempt in range(2):
            if kenburns(img, sd, i, s) and dur(s) >= sd * 0.9:
                break
            print(f"    retry s{i:03d} (attempt {attempt+2})", flush=True)
        else:
            print(f"GAGAL: s{i:03d}"); sys.exit(1)
    if not (s0 == 0 and s1 >= len(order)):
        print(f"slice {s0}-{s1} selesai (tanpa finalisasi)")
        return
    segs = [os.path.join(TMPD, f"s{i:03d}.mp4") for i in range(len(order))]
    assert all(os.path.exists(s) for s in segs), "masih ada segmen hilang"
    lst = os.path.join(TMPD, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    concat = os.path.join(TMPD, "concat.mp4")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)
    tmp_out = os.path.join(TMPD, "_video-tmp.mp4")
    subprocess.run([FFQ, "-y", "-i", concat, "-i", AUDIO,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", tmp_out],
                   capture_output=True, check=True)
    target = sum(durs.values())
    got = dur(tmp_out)
    print(f"verifikasi durasi: target={target:.1f}s aktual={got:.1f}s", flush=True)
    if abs(got - target) >= 5:
        print(f"GAGAL verifikasi durasi (|{got:.1f}-{target:.1f}|>=5). File final TIDAK ditimpa: {tmp_out}")
        sys.exit(2)
    shutil.move(tmp_out, OUT)
    print(f"OK: {OUT} ({dur(OUT)/60:.2f} menit)")

if __name__ == "__main__":
    main()
