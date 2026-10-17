#!/usr/bin/env python3
"""Rakit LONG Kisah Dharma 2026-10-17: Jembatan Rama (Rama Setu) — gotong royong wanara.
Footage: pool 2026-10-13 (kd-01..21) + 2026-10-15 (kd-f01..f08) + segar kd-n01.. (2026-10-17).
VO: mudiwa id. Assembly HANYA via ffmpeg-queue.sh. Playlist absolute path.
Tanpa '%' di drawtext. ':' di-escape jadi '\\:'. Tanpa apostrof di teks overlay.
Durasi slide dari gap timeline audio (starts[k+1]-starts[k]).
CTA verbal tengah+akhir, overlay 50%+akhir."""
import subprocess, os, sys, json
from PIL import Image, ImageDraw, ImageFont

D = "/home/hatch/workspace/kisah-dharma/2026-10-17"
FT13 = "/home/hatch/workspace/kisah-dharma/2026-10-13/footage"
FT15 = "/home/hatch/workspace/kisah-dharma/2026-10-15/footage"
FTN = os.path.join(D, "footage")  # klip segar kd-n01..
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-kisahdharma.wav"
VO = os.path.join(D, "vo.mp3")
BUMPER_D = 5.366
TITLE_D = 6.0

def run(cmd, desc):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"GAGAL {desc}:\n{r.stderr[-1500:]}"); sys.exit(1)

def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", p],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

# --- durasi beat dari file TTS ---
B = []
i = 0
while True:
    p = os.path.join(D, f"_beat{i:02d}.mp3")
    if not os.path.exists(p):
        break
    B.append(dur(p)); i += 1
assert len(B) == 8, f"beat files: {len(B)}"
print("B =", [round(x, 2) for x in B], flush=True)
T_VO = sum(B)

# --- alokasi klip per beat dibaca dari _plan.json (dibuat solver) ---
# format: [ [ [clip, offset, dur], ... ], ... ] per beat; clip tanpa prefix dir:
#   kd-n* -> footage/10-17, kd-f* -> pool 10-15. Tiap klip maks 2x per video.
import json as _json
PLAN = _json.load(open(os.path.join(D, "_plan.json")))
assert len(PLAN) == 8, f"plan beats: {len(PLAN)}"

def src_of(clip):
    if clip.startswith("kd-n"):
        return os.path.join(FTN, clip + ".mp4")
    return os.path.join(FT15, clip + ".mp4")

def grab_frame(clip_path, t, out):
    run([FQ, "-y", "-ss", str(t), "-i", clip_path,
         "-frames:v", "1", "-q:v", "2", out], f"frame {clip_path}")

def title_card():
    fr = os.path.join(D, "_title_frame.jpg")
    grab_frame(src_of("kd-n01"), 5, fr)
    im = Image.open(fr).convert("RGB").resize((1280, 720))
    dark = Image.new("RGB", (1280, 720), (0, 0, 0))
    im = Image.blend(im, dark, 0.45)
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(FONT, 110)
    f2 = ImageFont.truetype(FONT, 38)
    t1 = "JEMBATAN RAMA"
    t2 = "Gotong Royong Menaklukkan Samudra"
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
    grab_frame(src_of("kd-f08"), 15, fr)
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
    seg_files = [title_card()]
    print("seg title ok", flush=True)
    # timeline video: title(0-6), lalu tiap beat; bumper setelah b3
    v_starts = []  # (beat_idx, start_t)
    t = TITLE_D
    seg_idx = 1
    for bi, clips in enumerate(PLAN):
        v_starts.append((bi, t))
        for (clip, off, durv) in clips:
            srcp = src_of(clip)
            assert os.path.exists(srcp), f"missing {clip}"
            sd = dur(srcp)
            assert off + durv <= sd + 0.6, f"{clip}: butuh {off+durv:.1f}s > {sd:.1f}s"
            out = os.path.join(D, f"_seg{seg_idx:02d}.mp4")
            vf = ("scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
                  "fps=30,eq=contrast=1.05:saturation=1.02,"
                  "noise=alls=8:allf=t,format=yuv420p")
            run([FQ, "-y", "-ss", str(off), "-i", srcp, "-t", f"{durv:.2f}",
                 "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                 "-r", "30", "-an", out], f"seg b{bi} {clip}")
            seg_files.append(out)
            seg_idx += 1
            t += durv
            print(f"seg b{bi} [{clip}]: {durv:.2f}s ok", flush=True)
        if bi == 3:
            seg_files.append(bumper_seg())
            print("seg bumper ok", flush=True)
            t += BUMPER_D

    lst = os.path.join(D, "_segs.txt")
    with open(lst, "w") as f:
        for p in seg_files:
            f.write(f"file '{p}'\n")
    vconcat = os.path.join(D, "_vconcat.mp4")
    run([FQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vconcat],
        "concat video")
    vd = dur(vconcat)
    print(f"_vconcat: {vd:.2f}s", flush=True)

    # audio: 6s hening + vo[0:T_B] + bumper + vo[T_B:end] ; T_B = akhir b3
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

    # text overlay momen kunci (timeline video; title 0-6)
    s = {bi: st for bi, st in v_starts}
    def win(bi, a, b):
        return f"between(t,{s[bi]+a:.1f},{s[bi]+b:.1f})"
    mid50 = vd * 0.5
    dt = (
        f"drawtext=fontfile={FONT}:text='YUDDHA KANDA':fontsize=64:fontcolor=white:"
        f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=120:enable='{win(1,4,12)}',"
        f"drawtext=fontfile={FONT}:text='Kitab Keenam Ramayana':fontsize=40:fontcolor=white:"
        f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=200:enable='{win(1,4,12)}',"
        f"drawtext=fontfile={FONT}:text='RAMA SETU':fontsize=64:fontcolor=white:"
        f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=120:enable='{win(3,4,12)}',"
        f"drawtext=fontfile={FONT}:text='Jembatan 100 Yojana - 5 Hari':fontsize=40:fontcolor=white:"
        f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=200:enable='{win(3,4,12)}',"
        f"drawtext=fontfile={FONT}:text='SUBSCRIBE - KISAH DHARMA':fontsize=52:fontcolor=white:"
        f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{mid50:.1f},{mid50+8:.1f})',"
        f"drawtext=fontfile={FONT}:text='GOTONG ROYONG':fontsize=64:fontcolor=white:"
        f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=120:enable='{win(6,4,12)}',"
        f"drawtext=fontfile={FONT}:text='Kekuatan Kebersamaan':fontsize=40:fontcolor=white:"
        f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=200:enable='{win(6,4,12)}',"
        f"drawtext=fontfile={FONT}:text='Om Shanti\\, Shanti\\, Shanti\\, Om':fontsize=48:"
        f"fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-140:"
        f"enable='{win(7,max(0,B[7]-8),B[7]-0.2)}'"
    )
    tmp_master = os.path.join(D, "_master_tmp.mp4")
    run([FQ, "-y", "-i", vconcat, "-i", afull, "-vf", dt,
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-c:a", "copy", "-movflags", "+faststart", "-shortest", tmp_master],
        "final mux")
    md = dur(tmp_master)
    print(f"MASTER tmp: {md:.2f}s", flush=True)
    assert abs(md - vd) < 5, f"durasi master menyimpang: {md:.2f} vs {vd:.2f}"
    master = os.path.join(D, "kisah-dharma-2026-10-17-long.mp4")
    os.replace(tmp_master, master)

    small = os.path.join(D, "kisah-dharma-2026-10-17-long-small.mp4")
    run([FQ, "-y", "-i", master, "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "26", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart",
         small], "versi small")
    sz = os.path.getsize(small) / 1e6
    print(f"SMALL: {dur(small):.2f}s, {sz:.1f}MB", flush=True)
    assert sz < 100, "small > 100MB!"

    # simpan timeline untuk chapters + thumbnail
    tl = {"beats": [{"beat": bi, "start": round(st, 1), "dur": round(B[bi], 1)}
                    for bi, st in v_starts],
          "bumper_at": round(TITLE_D + sum(B[:4]), 1),
          "total": round(vd, 1)}
    json.dump(tl, open(os.path.join(D, "_timeline.json"), "w"), indent=1)
    print("SELESAI:", master, flush=True)

if __name__ == "__main__":
    main()
