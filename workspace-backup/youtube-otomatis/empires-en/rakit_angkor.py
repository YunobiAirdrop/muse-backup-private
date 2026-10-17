#!/usr/bin/env python3
"""Rakit video long Angkor: 73 segmen (title card + 72 gambar), text overlay
5 momen kunci, grain halus, pacing bervariasi, via ffmpeg-queue.sh.
Penggunaan: python3 rakit_angkor.py
"""
import subprocess, os, glob, sys, json, shutil
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/hatch/workspace/youtube-otomatis/empires-en"
QUEUE = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
GDIR = os.path.join(BASE, "gambar", "2026-10-10")
AUDIO = os.path.join(BASE, "audio", "voiceover-angkor-2026-10-10.mp3")
DURJ = os.path.join(BASE, "durasi-73-angkor.json")
OUT = os.path.join(BASE, "video", "angkorwat-2026-10-10-upload.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# segmen idx (0=title) -> teks overlay (ditampilkan 4 detik pertama segmen)
OVERLAYS = {
    4: "ANGKOR WAT, CAMBODIA - TODAY",              # beat 2
    7: "PHNOM KULEN - AD 802 - THE GOD-KING",       # beat 3
    13: "ANGKOR - AD 1200 - A CITY OF ONE MILLION", # beat 5
    31: "ANGKOR - AD 1340s - THE MONSOON FAILS",    # beat 11
    46: "SIEM REAP - 1860 - TOLD TO THE WORLD",     # beat 16
}

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def make_titlecard(bg_path, out):
    bg = Image.open(bg_path).convert("RGB")
    w, h = bg.size
    tr = 1280 / 720
    if w / h > tr:
        nw = int(h * tr); x0 = (w - nw) // 2; bg = bg.crop((x0, 0, x0 + nw, h))
    else:
        nh = int(w / tr); y0 = (h - nh) // 2; bg = bg.crop((0, y0, w, y0 + nh))
    bg = bg.resize((1280, 720), Image.LANCZOS)
    # gelapkan
    ov = Image.new("L", (1, 720))
    for y in range(720):
        ov.putpixel((0, y), int(160))
    ov = ov.resize((1280, 720))
    bg = Image.composite(Image.new("RGB", (1280, 720), (0, 0, 0)), bg, ov)
    d = ImageDraw.Draw(bg)
    def txt(t, size, y, color=(255, 255, 255)):
        f = ImageFont.truetype(FONT, size)
        bb = d.textbbox((0, 0), t, font=f); tw = bb[2] - bb[0]
        x = (1280 - tw) // 2
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                d.text((x + dx, y + dy), t, font=f, fill=(0, 0, 0))
        d.text((x, y), t, font=f, fill=color)
    txt("LOST EMPIRES", 44, 120, (255, 215, 0))
    txt("ANGKOR WAT", 120, 260)
    txt("The Megacity the Jungle Swallowed", 52, 430, (255, 215, 0))
    bg.save(out, format="JPEG", quality=92)
    print("OK title card:", out, flush=True)

def kenburns_light(img, seg_dur, idx, out, ov_file=None):
    total_frames = max(1, int(seg_dur * 30))
    mode = idx % 4
    if mode == 0:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode == 1:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='(iw-iw/zoom)*on/{total_frames}':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode == 2:
        zp = f"zoompan=z='max(1.15-1.15e-3*on,1.0)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    else:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{total_frames}':s=1280x720:fps=30"
    vf = (f"scale=1280:720,{zp},"
          "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
          "noise=alls=6:allf=t,"
          "vignette=PI/5")
    if ov_file:
        vf += (f",drawtext=fontfile={FONT}:textfile='{ov_file}':fontsize=34:"
               "fontcolor=white:borderw=2:bordercolor=black@0.7:"
               "x=(w-text_w)/2:y=h-100:enable='between(t,0,4)'")
    r = subprocess.run([QUEUE, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True)
    return r.returncode == 0

def main():
    imgs = sorted(glob.glob(os.path.join(GDIR, "*.jpg")))
    imgs = [p for p in imgs if not os.path.basename(p).startswith("titlecard")]
    if len(imgs) != 72:
        print(f"PERINGATAN: {len(imgs)} gambar (harusnya 72)")
    tc = os.path.join(GDIR, "titlecard-2026-10-10.jpg")
    make_titlecard(imgs[1] if len(imgs) > 1 else imgs[0], tc)
    segs_imgs = [tc] + imgs
    dj = json.load(open(DURJ))
    seg_durs = [float(dj[f"beat-{i:03d}"]) for i in range(len(segs_imgs))]
    print(f"{len(segs_imgs)} segmen, target {sum(seg_durs)/60:.1f} mnt", flush=True)
    tmpd = os.path.join(os.path.dirname(OUT), "_tmp_angkor")
    os.makedirs(tmpd, exist_ok=True)
    # tulis file teks overlay
    ov_files = {}
    for idx, txt in OVERLAYS.items():
        fp = os.path.join(tmpd, f"ov{idx}.txt")
        open(fp, "w").write(txt)
        ov_files[idx] = fp
    from concurrent.futures import ThreadPoolExecutor
    def _kb(arg):
        i, img = arg
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        ok = os.path.exists(s) and dur(s) >= seg_durs[i] * 0.9
        if ok:
            return True
        if os.path.exists(s):
            os.remove(s)
        for _ in range(2):
            if kenburns_light(img, seg_durs[i], i, s, ov_files.get(i)) and dur(s) >= seg_durs[i] * 0.9:
                break
        else:
            print(f"GAGAL: s{i:03d}", flush=True)
            return False
        if (i + 1) % 8 == 0:
            print(f"  {i+1}/{len(segs_imgs)} segmen...", flush=True)
        return True
    with ThreadPoolExecutor(max_workers=2) as ex:
        results = list(ex.map(_kb, enumerate(segs_imgs)))
    if not all(results):
        print("ADA SEGMEN GAGAL"); sys.exit(1)
    segs = [os.path.join(tmpd, f"s{i:03d}.mp4") for i in range(len(segs_imgs))]
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    concat = os.path.join(tmpd, "concat.mp4")
    subprocess.run([QUEUE, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)
    subprocess.run([QUEUE, "-y", "-i", concat, "-i", AUDIO,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", OUT],
                   capture_output=True, check=True)
    print(f"OK: {OUT} ({dur(OUT)/60:.1f} menit)")
    shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
