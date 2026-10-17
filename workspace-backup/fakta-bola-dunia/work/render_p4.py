#!/usr/bin/env python3
"""Render part4: PIL frame-by-frame, mulut sinkron volume, 3 suara pitch-shift."""
import sys, math, json, subprocess
sys.path.insert(0, "/home/hatch/workspace/fakta-bola-dunia/work")
from faces import face_image
from PIL import Image, ImageDraw, ImageFont

WORK = "/home/hatch/workspace/fakta-bola-dunia/work"
OUT = "/home/hatch/workspace/fakta-bola-dunia/output/angka-seram-part4.mp4"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FPS = 24
BG = (134, 212, 254)

POS = {'id': (150, 400), 'cn': (630, 400), 'jp': (390, 950)}
LABEL = {'id': 'INDONESIA', 'cn': 'CHINA', 'jp': 'JEPANG'}
LABEL_X = {'id': 300, 'cn': 780, 'jp': 540}
LABEL_Y = {'id': 350, 'cn': 350, 'jp': 900}

sync = json.load(open(f"{WORK}/mouth_sync.json"))
beats = []
for line in open(f"{WORK}/script_p4.txt"):
    n, spk, text = line.strip().split("|", 2)
    beats.append((int(n), spk))

SPEAK = {n: spk for n, spk in beats}
NUM = {4:'666',5:'666',6:'666',7:'13',8:'13',9:'13',10:'13',
       12:'4',13:'4',14:'4',15:'4'}
EYE = {5:'kaget',8:'kaget',9:'kaget',11:'kaget',13:'kaget',15:'kaget',16:'senang'}
MOUTH_MAP = {0:'tutup', 1:'buka_kecil', 2:'buka_lebar'}

# pre-render bola
print("Pre-render wajah...", flush=True)
BALL = {}
for c in ('id','cn','jp'):
    for es in ('normal','kaget','senang'):
        for ms in ('tutup','buka_kecil','buka_lebar','senyum','o'):
            BALL[(c,es,ms)] = face_image(c, es, ms, 300)

name_font = ImageFont.truetype(FONT, 44)
num_font = ImageFont.truetype(FONT, 200)
cta_font = ImageFont.truetype(FONT, 110)

def text_img(text, font, fill, stroke_w=4):
    bb = ImageDraw.Draw(Image.new("RGB",(1,1))).textbbox((0,0), text, font=font, stroke_width=stroke_w)
    w, h = bb[2]-bb[0]+20, bb[3]-bb[1]+20
    im = Image.new("RGBA",(w,h),(0,0,0,0))
    d = ImageDraw.Draw(im)
    d.text((10-bb[0],10-bb[1]), text, font=font, fill=fill, stroke_width=stroke_w, stroke_fill="black")
    return im

labels = {c: text_img(LABEL[c], name_font, "white") for c in LABEL}
nums = {k: text_img(v, num_font, (139,0,0), stroke_w=8) for k,v in
        {'666':'666','13':'13','4':'4'}.items()}
cta_base = text_img("LIKE & SUBSCRIBE!", cta_font, (255,215,0), stroke_w=6)
if cta_base.width > 860:
    _sc = 860 / cta_base.width
    cta_base = cta_base.resize((860, int(cta_base.height*_sc)), Image.LANCZOS)

TAIL = 0.30
# hitung total frame & tulis audio list
import wave
audio_files = []
total_frames = 0
beat_frames = {}
for n, spk in beats:
    dur = sync[str(n)]["dur"]
    vdur = dur + TAIL
    nf = int(vdur*FPS)
    beat_frames[n] = (nf, dur)
    total_frames += nf
    audio_files.append((f"{WORK}/p4audio/b{n:02d}.wav", dur, vdur))

print(f"Total {total_frames} frame (~{total_frames/FPS:.1f}s)", flush=True)

# ---------- render ----------
p = subprocess.Popen(
    [FFQ,"-y","-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920",
     "-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast",
     "-crf","23","-pix_fmt","yuv420p", f"{WORK}/p4_silent.mp4"],
    stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
assert p.stdin

fi = 0
for n, spk in beats:
    nf, adur = beat_frames[n]
    states = sync[str(n)]["mouth"]
    eye_spk = EYE.get(n, "normal")
    is_cta = (n == 18)
    for i in range(nf):
        t = i / FPS
        fr = Image.new("RGB", (1080,1920), BG)
        for c in ('id','cn','jp'):
            x0, y0 = POS[c]
            if c == spk:
                # mulut dari analisis volume
                st = states[min(i, len(states)-1)]
                ms = MOUTH_MAP[st]
                # kejutan: kalau tutup di beat kaget -> mulut 'o'
                if ms == 'tutup' and eye_spk == 'kaget' and t < 0.6:
                    ms = 'o'
                img = BALL[(c, eye_spk, ms)]
                yoff = -abs(math.sin(2*math.pi*1.5*t))*25
            else:
                img = BALL[(c, 'normal', 'tutup')]
                yoff = 0
            fr.paste(img, (x0, int(y0+yoff)), img)
            lb = labels[c]
            fr.paste(lb, (LABEL_X[c]-lb.width//2, LABEL_Y[c]), lb)
        if n in NUM and not is_cta:
            nm = nums[NUM[n]]
            fr.paste(nm, (540-nm.width//2, 1400), nm)
        if is_cta:
            pop = min(1.0, t/0.35)
            s = pop*(1+0.08*math.sin(2*math.pi*1.5*t))
            cw, ch = int(cta_base.width*s), int(cta_base.height*s)
            if cw > 4 and ch > 4:
                ct = cta_base.resize((cw,ch), Image.LANCZOS)
                fr.paste(ct, (540-cw//2, 1450-ch//2), ct)
        p.stdin.write(fr.convert("RGB").tobytes())
        fi += 1
    print(f"  beat {n:02d} ({spk}) {nf} frame", flush=True)
p.stdin.close(); p.wait()
assert p.returncode == 0, "render gagal"
print("Video silent OK", flush=True)

# ---------- audio: pad tiap wav dengan TAIL silence, lalu concat ----------
afiles = []
for wav_path, dur, vdur in audio_files:
    padded = wav_path.replace(".wav", "_pad.wav")
    subprocess.run([FFQ,"-y","-v","error","-i",wav_path,"-af",
                    f"apad,atrim=0:{vdur:.3f}", padded],
                   check=True, capture_output=True)
    afiles.append(padded)
lst = f"{WORK}/p4_audio.txt"
with open(lst,"w") as f:
    for a in afiles: f.write(f"file '{a}'\n")
subprocess.run([FFQ,"-y","-v","error","-f","concat","-safe","0","-i",lst,
                "-c:a","pcm_s16le","-ar","44100",f"{WORK}/p4_full.wav"],
               check=True, capture_output=True)
print("Audio OK", flush=True)

# ---------- mux ----------
subprocess.run([FFQ,"-y","-v","error","-i",f"{WORK}/p4_silent.mp4",
                "-i",f"{WORK}/p4_full.wav",
                "-c:v","copy","-c:a","aac","-b:a","128k","-ar","44100",
                "-shortest", OUT],
               check=True, capture_output=True)
import subprocess as sp
r = sp.run(["ffprobe","-v","error","-show_entries","format=duration",
            "-of","csv=p=0",OUT], capture_output=True, text=True)
print(f"SELESAI: {OUT} ({float(r.stdout.strip()):.1f}s)")
