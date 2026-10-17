#!/usr/bin/env python3
"""Rakit part2: 2 countryball ngobrol (bounce gantian) + CTA pulse."""
import subprocess, math

WORK = "/home/hatch/workspace/fakta-bola-dunia/work"
OUT = "/home/hatch/workspace/fakta-bola-dunia/output/angka-seram-part2.mp4"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BG = "0x86D4FE"

BALL = {'ID': f'{WORK}/ball-id.png', 'CN': f'{WORK}/ball-cn.png', 'JP': f'{WORK}/ball-jp.png'}
NAME = {'ID': 'INDONESIA', 'CN': 'CHINA', 'JP': 'JEPANG'}
ORDER = {'ID': 0, 'JP': 1, 'CN': 2}

# (beat, speaker, lawan, angka_visual)
BEATS = [
    (1, 'ID', 'CN', None),
    (2, 'CN', 'ID', None),
    (3, 'JP', 'ID', None),
    (4, 'ID', 'JP', '666'),
    (5, 'JP', 'CN', '666'),
    (6, 'CN', 'JP', '666'),
    (7, 'ID', 'CN', '13'),
    (8, 'JP', 'ID', '13'),
    (9, 'CN', 'ID', '13'),
    (10, 'ID', 'JP', '4'),
    (11, 'JP', 'CN', '4'),
    (12, 'ID', 'CN', '4'),
    (13, 'CN', 'ID', '4'),
    (14, 'JP', 'CN', '4'),
]

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def dt(text, x, y, fs):
    return (f"drawtext=fontfile={FONT}:text='{text}':fontsize={fs}:"
            f"fontcolor=white:borderw=3:bordercolor=black:x='{x}':y={y}")

segs = []
prev_pair = None
for n, spk, other, num in BEATS:
    a = dur(f"{WORK}/beat{n:02d}.mp3")
    vdur = a / 1.2 + 0.35
    left = spk if ORDER[spk] < ORDER[other] else other
    right = other if left == spk else spk
    pair = (left, right)
    slide = pair != prev_pair
    prev_pair = pair
    sl = 350 if left == spk else 300
    sr = 350 if right == spk else 300
    k = max(4, round(vdur * 3))  # setengah-siklus bounce (mulai & akhiri di 0)

    def yexp(is_spk):
        base = "800-h/2"
        if is_spk:
            return f"800-h/2-abs(sin(PI*{k}*t/{vdur:.3f}))*30"
        return base

    xl = "270-w/2-(0.4-min(t,0.4))*1400" if slide else "270-w/2"
    xr = "810-w/2+(0.4-min(t,0.4))*1400" if slide else "810-w/2"

    fc = (
        f"[1:v]format=rgba,scale={sl}:{sl}:flags=lanczos[bl];"
        f"[2:v]format=rgba,scale={sr}:{sr}:flags=lanczos[br];"
        f"[0:v][bl]overlay=x='{xl}':y='{yexp(left == spk)}':format=yuv420[e1];"
        f"[e1][br]overlay=x='{xr}':y='{yexp(right == spk)}':format=yuv420[e2];"
        f"[e2]{dt(NAME[left], '270-text_w/2', 540, 44)},"
        f"{dt(NAME[right], '810-text_w/2', 540, 44)}"
    )
    if num:
        fc += (f",drawtext=fontfile={FONT}:text='{num}':fontsize=200:"
               f"fontcolor=0x8B0000:borderw=6:bordercolor=white:"
               f"x=(w-text_w)/2:y=1150")
    fc += ",format=yuv420p[v]"

    seg = f"{WORK}/p2_seg{n:02d}.mp4"
    cmd = [FFQ, "-y",
           "-f", "lavfi", "-i", f"color=c={BG}:s=1080x1920:r=30:d={vdur:.3f}",
           "-i", BALL[left], "-i", BALL[right],
           "-i", f"{WORK}/beat{n:02d}.mp3",
           "-filter_complex", fc + f";[3:a]atempo=1.2,apad,atrim=0:{vdur:.3f}[a]",
           "-map", "[v]", "-map", "[a]",
           "-t", f"{vdur:.3f}", "-r", "30",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-c:a", "aac", "-b:a", "128k", "-ar", "44100", seg]
    print(f"beat{n:02d}: {NAME[spk]} bicara ({left}+{right}) {vdur:.2f}s slide={slide}", flush=True)
    subprocess.run(cmd, check=True, capture_output=True)
    segs.append(seg)

# ---------- CTA (beat 15): render frame via PIL ----------
from PIL import Image, ImageDraw, ImageFont
CTA_DUR = 5.0
FPS = 30
NF = int(CTA_DUR * FPS)
cta_audio = dur(f"{WORK}/beat15_cta.mp3")
print(f"CTA audio {cta_audio:.2f}s -> video {CTA_DUR}s", flush=True)

ball = Image.open(BALL['ID'])
ctatxt = Image.open(f"{WORK}/cta-text.png")
tw, th = ctatxt.size
tscale = 950 / tw
ctatxt = ctatxt.resize((950, int(th * tscale)), Image.LANCZOS)
name_font = ImageFont.truetype(FONT, 44)

cta_silent = f"{WORK}/p2_cta_silent.mp4"
p = subprocess.Popen(
    [FFQ, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920",
     "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast",
     "-crf", "23", "-pix_fmt", "yuv420p", cta_silent],
    stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
for i in range(NF):
    t = i / FPS
    fr = Image.new("RGB", (1080, 1920), (134, 212, 254))
    # bola: bounce
    bs = 380
    b = ball.resize((bs, bs), Image.LANCZOS)
    yoff = -abs(math.sin(2 * math.pi * 1.2 * t)) * 25
    fr.paste(b, (540 - bs // 2, int(720 - bs // 2 + yoff)), b)
    d = ImageDraw.Draw(fr)
    nm = "INDONESIA"
    bb = d.textbbox((0, 0), nm, font=name_font, stroke_width=3)
    d.text((540 - (bb[2] - bb[0]) / 2 - bb[0], 470 - bb[1]), nm, font=name_font,
           fill="white", stroke_width=3, stroke_fill="black")
    # teks CTA: pop-in + pulse
    pop = min(1.0, t / 0.35)
    s = pop * (1 + 0.08 * math.sin(2 * math.pi * 1.5 * t))
    cw, ch = int(950 * s), int(ctatxt.size[1] * s)
    if cw > 4 and ch > 4:
        ct = ctatxt.resize((cw, ch), Image.LANCZOS)
        fr.paste(ct, (540 - cw // 2, 1300 - ch // 2), ct)
    p.stdin.write(fr.tobytes())
p.stdin.close()
p.wait()
assert p.returncode == 0, "render CTA gagal"

seg15 = f"{WORK}/p2_seg15.mp4"
subprocess.run(
    [FFQ, "-y", "-i", cta_silent, "-i", f"{WORK}/beat15_cta.mp3",
     "-filter_complex", f"[1:a]atempo=1.2,apad,atrim=0:{CTA_DUR}[a]",
     "-map", "0:v", "-map", "[a]", "-c:v", "copy",
     "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
     "-t", str(CTA_DUR), seg15],
    check=True, capture_output=True)
segs.append(seg15)
print("CTA selesai", flush=True)

# ---------- concat ----------
lst = f"{WORK}/p2_concat.txt"
with open(lst, "w") as f:
    for s in segs:
        f.write(f"file '{s}'\n")
subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                "-c", "copy", OUT], check=True, capture_output=True)
print(f"SELESAI: {OUT} ({dur(OUT):.1f}s)")
