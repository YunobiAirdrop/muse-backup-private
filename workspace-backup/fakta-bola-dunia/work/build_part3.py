#!/usr/bin/env python3
"""Rakit part3: 3 countryball PERSISTEN, suara beda/karakter, mulut animasi buka-tutup."""
import subprocess, math

WORK = "/home/hatch/workspace/fakta-bola-dunia/work"
OUT = "/home/hatch/workspace/fakta-bola-dunia/output/angka-seram-part3.mp4"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BG = "0x86D4FE"
FPS = 30

POS = {'id': (150, 400), 'cn': (630, 400), 'jp': (390, 950)}  # top-left, 300px
LABEL = {'id': 'INDONESIA', 'cn': 'CHINA', 'jp': 'JEPANG'}
LABEL_X = {'id': 300, 'cn': 780, 'jp': 540}   # center x
LABEL_Y = {'id': 350, 'cn': 350, 'jp': 900}
TALK = {c: f'{WORK}/talk-{c}.mov' for c in ('id', 'cn', 'jp')}
CLOSED = {c: f'{WORK}/ball-{c}-closed.png' for c in ('id', 'cn', 'jp')}

SPEAK = {1:'id',2:'cn',3:'jp',4:'id',5:'jp',6:'cn',7:'id',8:'jp',9:'cn',
         10:'id',11:'jp',12:'id',13:'cn',14:'jp',15:'id'}
NUM = {4:'666',5:'666',6:'666',7:'13',8:'13',9:'13',
       10:'4',11:'4',12:'4',13:'4',14:'4'}

def dur(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries",
                        "format=duration","-of","csv=p=0",path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def dt(text, cx, y, fs, color="white"):
    return (f"drawtext=fontfile={FONT}:text='{text}':fontsize={fs}:"
            f"fontcolor={color}:borderw=3:bordercolor=black:"
            f"x='{cx}-text_w/2':y={y}")

segs = []
for n in range(1, 16):
    spk = SPEAK[n]
    others = [c for c in ('id','cn','jp') if c != spk]
    a = dur(f"{WORK}/p3audio/b{n:02d}.mp3")
    vdur = a / 1.2 + 0.35
    k = max(4, round(vdur * 3))
    xs, ys = POS[spk]
    xa, ya = POS[others[0]]
    xb, yb = POS[others[1]]

    fc = (
        f"[1:v]scale=300:300:flags=lanczos,format=rgba,"
        f"loop=loop=-1:size=12,setpts=N/{FPS}/TB[talk];"
        f"[2:v]format=rgba,scale=300:300:flags=lanczos[la];"
        f"[3:v]format=rgba,scale=300:300:flags=lanczos[lb];"
        f"[0:v][talk]overlay=x={xs}:y='{ys}-abs(sin(PI*{k}*t/{vdur:.3f}))*30'"
        f":format=yuv420[e1];"
        f"[e1][la]overlay=x={xa}:y={ya}:format=yuv420[e2];"
        f"[e2][lb]overlay=x={xb}:y={yb}:format=yuv420[e3];"
        f"[e3]{dt(LABEL['id'], LABEL_X['id'], LABEL_Y['id'], 44)},"
        f"{dt(LABEL['cn'], LABEL_X['cn'], LABEL_Y['cn'], 44)},"
        f"{dt(LABEL['jp'], LABEL_X['jp'], LABEL_Y['jp'], 44)}"
    )
    if n in NUM:
        fc += (f",drawtext=fontfile={FONT}:text='{NUM[n]}':fontsize=180:"
               f"fontcolor=0x8B0000:borderw=6:bordercolor=white:"
               f"x=(w-text_w)/2:y=1450")
    fc += ",format=yuv420p[v]"

    seg = f"{WORK}/p3_seg{n:02d}.mp4"
    cmd = [FFQ, "-y",
           "-f","lavfi","-i",f"color=c={BG}:s=1080x1920:r={FPS}:d={vdur:.3f}",
           "-i", TALK[spk], "-i", CLOSED[others[0]], "-i", CLOSED[others[1]],
           "-i", f"{WORK}/p3audio/b{n:02d}.mp3",
           "-filter_complex", fc + f";[4:a]atempo=1.2,apad,atrim=0:{vdur:.3f}[a]",
           "-map","[v]","-map","[a]",
           "-t",f"{vdur:.3f}","-r",str(FPS),
           "-c:v","libx264","-preset","veryfast","-crf","23",
           "-c:a","aac","-b:a","128k","-ar","44100", seg]
    print(f"beat{n:02d}: {LABEL[spk]} bicara {vdur:.2f}s", flush=True)
    subprocess.run(cmd, check=True, capture_output=True)
    segs.append(seg)

# ---------- CTA: PIL render, 3 bola, ID ngomong+mulut, teks pulse ----------
from PIL import Image, ImageDraw, ImageFont
CTA_DUR = 5.0
NF = int(CTA_DUR * FPS)
print(f"CTA render {NF} frame...", flush=True)
balls_closed = {c: Image.open(CLOSED[c]) for c in ('id','cn','jp')}
balls_open = {c: Image.open(f'{WORK}/ball-{c}-open.png') for c in ('id','cn','jp')}
ctatxt = Image.open(f"{WORK}/cta-text.png")
tw, th = ctatxt.size
tscale = 950 / tw
ctatxt = ctatxt.resize((950, int(th*tscale)), Image.LANCZOS)
name_font = ImageFont.truetype(FONT, 44)

cta_silent = f"{WORK}/p3_cta_silent.mp4"
p = subprocess.Popen(
    [FFQ,"-y","-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920",
     "-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast",
     "-crf","23","-pix_fmt","yuv420p", cta_silent],
    stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
for i in range(NF):
    t = i / FPS
    fr = Image.new("RGB", (1080,1920), (134,212,254))
    d = ImageDraw.Draw(fr)
    for c in ('id','cn','jp'):
        x0, y0 = POS[c]
        # ID: mulut animasi + bounce ; lainnya: diam mulut tutup
        if c == 'id':
            img = balls_open['id'] if (i // 6) % 2 == 1 else balls_closed['id']
            yoff = -abs(math.sin(2*math.pi*1.5*t))*25
        else:
            img = balls_closed[c]; yoff = 0
        b = img.resize((300,300), Image.LANCZOS)
        fr.paste(b, (x0, int(y0+yoff)), b)
        nm = LABEL[c]
        bb = d.textbbox((0,0), nm, font=name_font, stroke_width=3)
        d.text((LABEL_X[c]-(bb[2]-bb[0])/2-bb[0], LABEL_Y[c]-bb[1]),
               nm, font=name_font, fill="white",
               stroke_width=3, stroke_fill="black")
    # CTA pulse
    pop = min(1.0, t/0.35)
    s = pop*(1+0.08*math.sin(2*math.pi*1.5*t))
    cw, ch = int(950*s), int(ctatxt.size[1]*s)
    if cw > 4 and ch > 4:
        ct = ctatxt.resize((cw,ch), Image.LANCZOS)
        fr.paste(ct, (540-cw//2, 1450-ch//2), ct)
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
assert p.returncode == 0, "render CTA gagal"

seg_cta = f"{WORK}/p3_seg_cta.mp4"
subprocess.run(
    [FFQ,"-y","-i",cta_silent,"-i",f"{WORK}/p3audio/cta.mp3",
     "-filter_complex",f"[1:a]atempo=1.2,apad,atrim=0:{CTA_DUR}[a]",
     "-map","0:v","-map","[a]","-c:v","copy",
     "-c:a","aac","-b:a","128k","-ar","44100",
     "-t",str(CTA_DUR), seg_cta],
    check=True, capture_output=True)
segs.append(seg_cta)
print("CTA selesai", flush=True)

lst = f"{WORK}/p3_concat.txt"
with open(lst,"w") as f:
    for s in segs: f.write(f"file '{s}'\n")
subprocess.run([FFQ,"-y","-f","concat","-safe","0","-i",lst,
                "-c","copy",OUT], check=True, capture_output=True)
print(f"SELESAI: {OUT} ({dur(OUT):.1f}s)")
