#!/usr/bin/env python3
"""Rakit LONG Kisah Dharma 2026-10-15: Hanuman Melompat ke Alengka.
Footage: klip Wikimedia Commons pool 2026-10-13 (kd-01..kd-21), frame/klip DIVERIFIKASI.
VO: mudiwa id. Assembly HANYA via ffmpeg-queue.sh. Playlist absolute path.
Tanpa '%' di drawtext. ':' di-escape. CTA verbal tengah+akhir, overlay 50%+akhir."""
import subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont

D = "/home/hatch/workspace/kisah-dharma/2026-10-15"
FT = "/home/hatch/workspace/kisah-dharma/2026-10-13/footage"
FTF = os.path.join(D, "footage")  # klip segar kd-f01..f08 (samudra)
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-kisahdharma.wav"
VO = os.path.join(D, "vo.mp3")
BUMPER_D = 5.366
TITLE_D = 6.0

# Durasi beat (detik) dari TTS
B = [50.760, 72.048, 75.168, 81.912, 34.872, 73.800, 61.128, 72.792]
# (clip, offset_dtk, dur_dtk) — jumlah per beat == durasi beat
SEGS = [
    ("title", None, TITLE_D),
    # b0 hook: samudra luas (klip segar)
    ("f:kd-f02", 0, 18.00),
    ("f:kd-f01", 5, 32.76),
    # b1 awal kisah: perjalanan ke selatan
    ("kd-08", 10, 36.00),
    ("kd-06", 5, 36.05),
    # b2 Jambavan membangunkan Hanuman
    ("kd-18", 1, 20.00),
    ("kd-19", 1, 22.00),
    ("kd-04", 30, 33.17),
    # b3 lompatan melintasi samudra (klip segar)
    ("f:kd-f03", 0, 15.00),
    ("f:kd-f04", 0, 15.00),
    ("f:kd-f05", 0, 16.00),
    ("f:kd-f01", 30, 20.00),
    ("f:kd-f08", 0, 15.91),
    # bumper tengah (setelah b3)
    ("bumper", None, BUMPER_D),
    # b4 refleksi narator
    ("kd-02", 2, 20.00),
    ("kd-09", 1, 14.87),
    # b5 tiba di Alengka malam hari
    ("kd-17", 10, 30.00),
    ("kd-20", 20, 28.00),
    ("kd-10", 1, 15.80),
    # b6 api keadilan + kabar gembira
    ("f:kd-f06", 0, 20.00),
    ("kd-14", 1, 25.00),
    ("kd-21", 10, 16.13),
    # b7 hikmah + penutup
    ("f:kd-f08", 10, 20.00),
    ("kd-05", 10, 26.00),
    ("kd-04", 90, 26.79),
]

def run(cmd, desc):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"GAGAL {desc}:\n{r.stderr[-1500:]}"); sys.exit(1)

def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", p],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def grab_frame(clip, t, out):
    run([FQ, "-y", "-ss", str(t), "-i", os.path.join(FT, clip + ".mp4"),
         "-frames:v", "1", "-q:v", "2", out], f"frame {clip}")

def title_card():
    fr = os.path.join(D, "_title_frame.jpg")
    grab_frame("kd-12", 20, fr)  # ombak dramatis
    im = Image.open(fr).convert("RGB").resize((1280, 720))
    dark = Image.new("RGB", (1280, 720), (0, 0, 0))
    im = Image.blend(im, dark, 0.45)
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(FONT, 110)
    f2 = ImageFont.truetype(FONT, 40)
    t1 = "HANUMAN"
    t2 = "Kesetiaan Tanpa Batas Melintasi Samudra"
    b1 = d.textbbox((0, 0), t1, font=f1); b2 = d.textbbox((0, 0), t2, font=f2)
    d.text(((1280 - (b1[2]-b1[0]))/2, 240), t1, font=f1, fill=(255, 205, 90),
           stroke_width=3, stroke_fill=(60, 30, 0))
    d.text(((1280 - (b2[2]-b2[0]))/2, 400), t2, font=f2, fill=(255, 255, 255),
           stroke_width=2, stroke_fill=(0, 0, 0))
    card = os.path.join(D, "_titlecard.png")
    im.save(card)
    out = os.path.join(D, "_seg_title.mp4")
    tf = int(TITLE_D * 30)
    vf = (f"zoompan=z='1.0+0.0008*on':d={tf}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
          f"s=1280x720:fps=30,noise=alls=8:allf=t,format=yuv420p")
    run([FQ, "-y", "-loop", "1", "-i", card, "-vf", vf, "-t", str(TITLE_D),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-r", "30",
         "-an", out], "render title card")
    return out

def bumper_seg():
    fr = os.path.join(D, "_bumper_frame.jpg")
    grab_frame("kd-01", 40, fr)
    out = os.path.join(D, "_seg_bumper.mp4")
    tf = int(BUMPER_D * 30)
    vf = (f"zoompan=z='1.0+0.0012*on':d={tf}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
          f"s=1280x720:fps=30,"
          f"eq=contrast=1.05:saturation=1.02,noise=alls=8:allf=t,"
          f"drawtext=fontfile={FONT}:text='KISAH DHARMA':fontsize=44:fontcolor=white:"
          f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-120,"
          f"format=yuv420p")
    run([FQ, "-y", "-loop", "1", "-i", fr, "-vf", vf, "-t", str(BUMPER_D),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-r", "30",
         "-an", out], "render bumper seg")
    return out

def main():
    seg_files = []
    for i, (clip, off, durv) in enumerate(SEGS):
        out = os.path.join(D, f"_seg{i:02d}.mp4")
        if clip == "title":
            seg_files.append(title_card()); print(f"seg {i:02d} [title] ok", flush=True); continue
        if clip == "bumper":
            seg_files.append(bumper_seg()); print(f"seg {i:02d} [bumper] ok", flush=True); continue
        if clip.startswith("f:"):
            src = os.path.join(FTF, clip[2:] + ".mp4")
        else:
            src = os.path.join(FT, clip + ".mp4")
        assert os.path.exists(src), f"missing {clip}"
        vf = ("scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
              "fps=30,eq=contrast=1.05:saturation=1.02,"
              "noise=alls=8:allf=t,format=yuv420p")
        run([FQ, "-y", "-ss", str(off), "-i", src, "-t", f"{durv:.2f}",
             "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
             "-r", "30", "-an", out], f"seg {i} {clip}")
        seg_files.append(out)
        print(f"seg {i:02d} [{clip}]: {durv:.2f}s ok", flush=True)

    lst = os.path.join(D, "_segs.txt")
    with open(lst, "w") as f:
        for p in seg_files:
            f.write(f"file '{p}'\n")
    vconcat = os.path.join(D, "_vconcat.mp4")
    run([FQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vconcat],
        "concat video")
    vd = dur(vconcat)
    print(f"_vconcat: {vd:.2f}s", flush=True)

    # audio: 6s hening + vo[0:T_B] + bumper + vo[T_B:end]
    T_B = sum(B[:4])
    print(f"T_B (bumper split): {T_B:.2f}s", flush=True)
    afull = os.path.join(D, "_afull.m4a")
    fc = (f"anullsrc=r=44100:cl=stereo:d={TITLE_D}[sil];"
          f"[0:a]atrim=0:{T_B:.2f},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo[a0];"
          f"[0:a]atrim={T_B:.2f},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo[a2];"
          f"[1:a]aresample=44100,aformat=channel_layouts=stereo[b];"
          f"[sil][a0][b][a2]concat=n=4:v=0:a=1[outa]")
    run([FQ, "-y", "-i", VO, "-i", BUMPER, "-filter_complex", fc,
         "-map", "[outa]", "-c:a", "aac", "-b:a", "128k", afull], "rakit audio")
    ad = dur(afull)
    print(f"_afull: {ad:.2f}s", flush=True)
    assert abs(vd - ad) < 1.5, f"AV mismatch: {vd:.2f} vs {ad:.2f}"

    # text overlay momen kunci (timeline video, title 0-6)
    # b3 203.98-285.89 | bumper 285.89-291.25 | b6 399.93-461.05 | b7 461.05-533.85
    dt = (f"drawtext=fontfile={FONT}:text='SUNDARA KANDA':fontsize=64:fontcolor=white:"
          f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=120:enable='between(t,60,68)',"
          f"drawtext=fontfile={FONT}:text='Kitab Kelima Ramayana':fontsize=40:fontcolor=white:"
          f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=200:enable='between(t,60,68)',"
          f"drawtext=fontfile={FONT}:text='100 YOJANA':fontsize=64:fontcolor=white:"
          f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=120:enable='between(t,124,132)',"
          f"drawtext=fontfile={FONT}:text='Samudra Menuju Alengka':fontsize=40:fontcolor=white:"
          f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=200:enable='between(t,124,132)',"
          f"drawtext=fontfile={FONT}:text='SUBSCRIBE - KISAH DHARMA':fontsize=52:fontcolor=white:"
          f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,272,280)',"
          f"drawtext=fontfile={FONT}:text='DRISHTA SITA':fontsize=64:fontcolor=white:"
          f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=120:enable='between(t,405,413)',"
          f"drawtext=fontfile={FONT}:text='Shinta Telah Ditemukan':fontsize=40:fontcolor=white:"
          f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=200:enable='between(t,405,413)',"
          f"drawtext=fontfile={FONT}:text='Om Shanti\\, Shanti\\, Shanti\\, Om':fontsize=48:"
          f"fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-140:"
          f"enable='between(t,527,533.8)'")
    tmp_master = os.path.join(D, "_master_tmp.mp4")
    run([FQ, "-y", "-i", vconcat, "-i", afull, "-vf", dt,
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-c:a", "copy", "-movflags", "+faststart", "-shortest", tmp_master],
        "final mux")
    md = dur(tmp_master)
    print(f"MASTER tmp: {md:.2f}s", flush=True)
    # verifikasi durasi sebelum timpa final (aturan 2026-10-14)
    assert abs(md - vd) < 5, f"durasi master menyimpang: {md:.2f} vs {vd:.2f}"
    master = os.path.join(D, "kisah-dharma-2026-10-15-long.mp4")
    os.replace(tmp_master, master)

    small = os.path.join(D, "kisah-dharma-2026-10-15-long-small.mp4")
    run([FQ, "-y", "-i", master, "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "26", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart",
         small], "versi small")
    sz = os.path.getsize(small) / 1e6
    print(f"SMALL: {dur(small):.2f}s, {sz:.1f}MB", flush=True)
    assert sz < 100, "small > 100MB!"
    print("SELESAI:", master, flush=True)

if __name__ == "__main__":
    main()
