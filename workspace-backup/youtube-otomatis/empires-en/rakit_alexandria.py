#!/usr/bin/env python3
"""Rakit video long Alexandria: 73 segmen (title card + 72 gambar), text overlay
5 momen kunci (4 + CTA 50%), grain halus, pacing bervariasi, subtitle SRT
terbakar (style aman ffmpeg 8.1.2: tanpa kode warna &H), bumper suara owner
~40% durasi (ducking + lower-third), SFX rekaman asli tersinkron.
Tulis ke TEMP dulu, assert |durasi video - durasi audio| < 5 dtk, BARU move final.
Via ffmpeg-queue.sh. Penggunaan: python3 rakit_alexandria.py
"""
import subprocess, os, glob, sys, json, shutil
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/hatch/workspace/youtube-otomatis/empires-en"
QUEUE = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
GDIR = os.path.join(BASE, "gambar", "2026-10-18")
AUDIO = os.path.join(BASE, "audio", "voiceover-alexandria-2026-10-18.mp3")
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-empires-en.wav"
SRT = os.path.join(BASE, "subtitles-alexandria.srt")
DURJ = os.path.join(BASE, "durasi-73-alexandria.json")
DURB = os.path.join(BASE, "durasi-beat-alexandria.json")
OUT = os.path.join(BASE, "video", "alexandria-2026-10-18-upload.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SFXD = "/home/hatch/workspace/miniatur-ai/sfx-real"

# segmen idx (0=title; beat n -> seg (n-1)*3+1..+3) -> teks overlay (4 detik pertama)
OVERLAYS = {
    10: "ALEXANDRIA, EGYPT - 331 BC",                 # beat 4
    16: "EVERY SHIP SEARCHED - THE HARBOR LAW",       # beat 6
    35: "SUBSCRIBE - A NEW LOST WORLD EVERY DAY",     # beat 12, CTA ~50%
    37: "48 BC - CAESAR'S FIRE",                      # beat 13
    64: "2002 - THE LIBRARY RISES AGAIN",             # beat 22
}

# (file sfx, beat_mulai, durasi_s, volume) — waktu mulai dihitung dari timeline beat
SFX = [
    ("birds-ambience.mp3", 2, 70, 0.12),   # Alexandria modern, pembuka
    ("brick-place-1.mp3", 6, 8, 0.45),     # pembangunan
    ("crow-caw.mp3", 13, 5, 0.35),         # malam kebakaran
    ("wind-soft.mp3", 19, 44, 0.12),       # reruntuhan tenggelam
    ("shovel-dig-3.mp3", 20, 48, 0.22),    # penggalian modern
]

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
    txt("ALEXANDRIA", 110, 260)
    txt("The Day Humanity's Memory Burned", 48, 440, (255, 215, 0))
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
    imgs = sorted(glob.glob(os.path.join(GDIR, "img-*.jpg")))
    print(f"Gambar ditemukan: {len(imgs)}", flush=True)
    if len(imgs) < 72:
        print("GAGAL: gambar kurang dari 72"); sys.exit(1)
    imgs = imgs[:72]
    tc = os.path.join(GDIR, "titlecard-2026-10-18.jpg")
    make_titlecard(imgs[6], tc)
    segs_imgs = [tc] + imgs
    dj = json.load(open(DURJ))
    seg_durs = [float(dj[f"beat-{i:03d}"]) for i in range(len(segs_imgs))]
    print(f"{len(segs_imgs)} segmen, target {sum(seg_durs)/60:.1f} mnt", flush=True)

    db = json.load(open(DURB))
    cum, bounds = 0.0, []
    for i in range(25):
        bounds.append(cum)
        cum += float(db[f"beat-{i:03d}"])
    target = sum(seg_durs) * 0.40
    t40 = min([b for b in bounds if b >= target], default=bounds[-1])
    bd = dur(BUMPER)
    print(f"Bumper disisipkan di t={t40:.1f}s (durasi bumper {bd:.1f}s)", flush=True)

    tmpd = os.path.join(os.path.dirname(OUT), "_tmp_alexandria")
    os.makedirs(tmpd, exist_ok=True)
    ov_files = {}
    for idx, txt in OVERLAYS.items():
        fp = os.path.join(tmpd, f"ov{idx}.txt")
        open(fp, "w").write(txt)
        ov_files[idx] = fp
    lt = os.path.join(tmpd, "lowerthird.txt")
    open(lt, "w").write("LOST EMPIRES")

    from concurrent.futures import ThreadPoolExecutor
    def _kb(arg):
        i, img = arg
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        if os.path.exists(s) and dur(s) >= seg_durs[i] * 0.9:
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

    # final: burn subtitle (style aman) + lower-third bumper, mix bumper + SFX
    t0 = round(t40, 2)
    t0ms = int(t40 * 1000)
    dd = round(bd + 0.5, 2)
    vf = ("subtitles='" + SRT + "':force_style='FontName=DejaVu Sans,FontSize=22,"
          "BorderStyle=1,Outline=2,Alignment=2,MarginV=45',"
          f"drawtext=fontfile={FONT}:textfile='{lt}':fontsize=30:"
          "fontcolor=0xFFD700:borderw=2:bordercolor=black@0.7:"
          "x=(w-text_w)/2:y=h-150:"
          f"enable='between(t,{t0},{t0 + 3})'")

    inputs = ["-i", concat, "-i", AUDIO, "-i", BUMPER]
    af_parts = [f"[1:a]volume=volume='if(between(t,{t0},{t0 + dd}),0.25,1)':eval=frame[a0]",
                f"[2:a]adelay={t0ms}|{t0ms},volume=1.3[a1]"]
    mix_ins = ["[a0]", "[a1]"]
    sfx_idx = 3
    for fname, beat_n, sfx_dur, vol in SFX:
        fpath = os.path.join(SFXD, fname)
        if not os.path.exists(fpath):
            print(f"SFX tidak ada, lewati: {fname}", flush=True)
            continue
        start = round(bounds[beat_n], 2)
        start_ms = int(start * 1000)
        inputs += ["-i", fpath]
        af_parts.append(
            f"[{sfx_idx}:a]atrim=0:{sfx_dur},adelay={start_ms}|{start_ms},volume={vol}[s{sfx_idx}]")
        mix_ins.append(f"[s{sfx_idx}]")
        sfx_idx += 1
    af_parts.append("".join(mix_ins) +
                    f"amix=inputs={len(mix_ins)}:duration=first:dropout_transition=0[aout]")
    af = ";".join(af_parts)

    tmp_out = os.path.join(tmpd, "final-tmp.mp4")
    r = subprocess.run([QUEUE, "-y"] + inputs +
                       ["-filter_complex", af, "-map", "0:v", "-map", "[aout]",
                        "-vf", vf,
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-pix_fmt", "yuv420p", "-r", "30",
                        "-c:a", "aac", "-b:a", "128k",
                        "-shortest", "-movflags", "+faststart", tmp_out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("FINAL ENCODE GAGAL:", r.stderr[-2000:], flush=True); sys.exit(1)

    dv, da = dur(tmp_out), dur(AUDIO)
    print(f"Durasi video {dv:.1f}s vs audio {da:.1f}s (selisih {abs(dv-da):.1f}s)", flush=True)
    if abs(dv - da) >= 5:
        print("GAGAL ASSERT: selisih >= 5 dtk, final TIDAK ditimpa"); sys.exit(1)
    shutil.move(tmp_out, OUT)
    print(f"OK: {OUT} ({dv/60:.1f} menit)")
    shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
