#!/usr/bin/env python3
"""Render part5: mata kartun besar, tangan animasi, ekspresi dinamis, 3 suara mudiwa pitch-shift."""
import sys, math, json, subprocess, os
sys.path.insert(0, "/home/hatch/workspace/fakta-bola-dunia/work")
from faces_v2 import face_image_v2, get_hand
from PIL import Image, ImageDraw, ImageFont

WORK = "/home/hatch/workspace/fakta-bola-dunia/work"
OUT = "/home/hatch/workspace/fakta-bola-dunia/output/angka-seram-part5.mp4"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FPS = 24
BG = (134, 212, 254)
BS = 400  # ukuran bola

POS = {'id': (140, 350), 'cn': (540, 350), 'jp': (340, 1000)}
LABEL = {'id': 'INDONESIA', 'cn': 'CHINA', 'jp': 'JEPANG'}

# Ekspresi per beat: (eye_style, hand_pose atau None)
EXPR = {
    1: ('senang', 'wave'),    # id: excited sharing
    2: ('bingung', None),     # cn: confused
    3: ('bingung', None),     # jp: confused
    4: ('normal', 'point'),    # id: explaining 666
    5: ('takut', 'cheek'),     # jp: scared
    6: ('takut', None),        # cn: scared
    7: ('normal', 'point'),    # id: explaining 13
    8: ('kaget', 'cheek'),     # cn: surprised
    9: ('takut', 'cheek'),     # jp: scared
    10: ('normal', 'point'),    # id: explaining
    11: ('kaget', None),       # jp: curious
    12: ('normal', 'point'),    # id: explaining 4
    13: ('kaget', 'cheek'),    # jp: surprised
    14: ('normal', 'point'),    # cn: explaining serious
    15: ('kaget', 'cheek'),    # jp: surprised
    16: ('senang', 'wave'),    # id: happy
    17: ('normal', None),      # cn: thinking
    18: ('senang', 'wave'),    # id: CTA happy
}
NUM = {4:'666',5:'666',6:'666',7:'13',8:'13',9:'13',10:'13',
       12:'4',13:'4',14:'4',15:'4'}
MOUTH_MAP = {0:'tutup', 1:'buka_kecil', 2:'buka_lebar'}

sync = json.load(open(f"{WORK}/mouth_sync_p5.json"))
beats = []
for line in open(f"{WORK}/script_p4.txt"):
    n, spk, text = line.strip().split("|", 2)
    beats.append((int(n), spk))

print("Pre-render wajah...", flush=True)
BALL = {}
for c in ('id','cn','jp'):
    for es in ('normal','kaget','senang','bingung','takut'):
        for ms in ('tutup','buka_kecil','buka_lebar','senyum','o'):
            BALL[(c,es,ms)] = face_image_v2(c, es, ms, BS)

name_font = ImageFont.truetype(FONT, 48)
num_font = ImageFont.truetype(FONT, 220)
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

# tangan (pre-scale ke ~160px)
HANDS = {}
for pose in ('point','wave','cheek'):
    for side in ('right','left'):
        h = get_hand(side, pose)
        HANDS[(pose,side)] = h.resize((160,160), Image.LANCZOS)

TAIL = 0.30
audio_files = []
total_frames = 0
beat_frames = {}
for n, spk in beats:
    dur = sync[str(n)]["dur"]
    vdur = dur + TAIL
    nf = int(vdur*FPS)
    beat_frames[n] = (nf, dur)
    total_frames += nf
    audio_files.append((f"{WORK}/p5audio/b{n:02d}.wav", dur, vdur))

print(f"Total {total_frames} frame (~{total_frames/FPS:.1f}s)", flush=True)

def paste_hand(fr, pose, bx, by, t, side="right"):
    """Tempel tangan dengan animasi keyframe sederhana."""
    h = HANDS[(pose, side)]
    if pose == "point":
        # di samping bola, gerak menunjuk (x oscillate kecil)
        if side == "right":
            hx = bx + BS + 10 + int(15*math.sin(2*math.pi*2*t))
        else:
            hx = bx - 150 - int(15*math.sin(2*math.pi*2*t))
        hy = by + 100
    elif pose == "wave":
        # di samping atas, melambai cepat
        if side == "right":
            hx = bx + BS - 20 + int(30*math.sin(2*math.pi*4*t))
        else:
            hx = bx - 140 + int(30*math.sin(2*math.pi*4*t))
        hy = by - 40
    elif pose == "cheek":
        # dua tangan di pipi — panggil 2x dengan side berbeda
        hx = bx - 110 if side=="left" else bx + BS - 50
        hy = by + 120
        # pop-in cepat di awal
        if t < 0.25:
            s = t/0.25
            nw, nh = int(160*s), int(160*s)
            if nw > 4:
                h2 = h.resize((nw,nh), Image.LANCZOS)
                fr.paste(h2, (hx+80-nw//2, hy+80-nh//2), h2)
                return
    fr.paste(h, (hx, hy), h)

p = subprocess.Popen(
    [FFQ,"-y","-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920",
     "-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast",
     "-crf","23","-pix_fmt","yuv420p", f"{WORK}/p5_silent.mp4"],
    stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
assert p.stdin

for n, spk in beats:
    nf, adur = beat_frames[n]
    states = sync[str(n)]["mouth"]
    eye_spk, hand_pose = EXPR.get(n, ("normal", None))
    is_cta = (n == 18)
    for i in range(nf):
        t = i / FPS
        fr = Image.new("RGB", (1080,1920), BG)
        spk_yoff = 0
        for c in ('id','cn','jp'):
            x0, y0 = POS[c]
            if c == spk:
                st = states[min(i, len(states)-1)]
                ms = MOUTH_MAP[st]
                # ekspresi kaget/takut + mulut tutup di awal -> 'o'
                if ms == 'tutup' and eye_spk in ('kaget','takut') and t < 0.8:
                    ms = 'o'
                # senang + tutup -> senyum
                if ms == 'tutup' and eye_spk == 'senang':
                    ms = 'senyum'
                img = BALL[(c, eye_spk, ms)]
                yoff = -abs(math.sin(2*math.pi*1.5*t))*25
                spk_yoff = yoff
            else:
                # yang diam: ekspresi netral, mulut tutup
                img = BALL[(c, 'normal', 'tutup')]
                yoff = 0
            fr.paste(img, (x0, int(y0+yoff)), img)
            lb = labels[c]
            fr.paste(lb, (x0+BS//2-lb.width//2, y0-60), lb)
        # tangan digambar SETELAH semua bola (tidak ketutupan)
        if hand_pose and not is_cta:
            x0, y0 = POS[spk]
            # sisi tangan: id -> kiri (kanan ketutup china), lainnya -> kanan
            hside = "left" if spk == 'id' else "right"
            if hand_pose == "cheek":
                paste_hand(fr, "cheek", x0, int(y0+spk_yoff), t, "left")
                paste_hand(fr, "cheek", x0, int(y0+spk_yoff), t, "right")
            else:
                paste_hand(fr, hand_pose, x0, int(y0+spk_yoff), t, hside)
        if n in NUM and not is_cta:
            nm = nums[NUM[n]]
            fr.paste(nm, (540-nm.width//2, 1480), nm)
        if is_cta:
            pop = min(1.0, t/0.35)
            s = pop*(1+0.08*math.sin(2*math.pi*1.5*t))
            cw, ch = int(cta_base.width*s), int(cta_base.height*s)
            if cw > 4 and ch > 4:
                ct = cta_base.resize((cw,ch), Image.LANCZOS)
                fr.paste(ct, (540-cw//2, 1500-ch//2), ct)
        p.stdin.write(fr.tobytes())
    print(f"  beat {n:02d} ({spk},{EXPR.get(n,('?','?'))[0]}) {nf}f", flush=True)
p.stdin.close(); p.wait()
assert p.returncode == 0, "render gagal"
print("Video silent OK", flush=True)

# audio: pad + concat
afiles = []
for wav_path, dur, vdur in audio_files:
    padded = wav_path.replace(".wav", "_pad.wav")
    subprocess.run([FFQ,"-y","-v","error","-i",wav_path,"-af",
                    f"apad,atrim=0:{vdur:.3f}", padded],
                   check=True, capture_output=True)
    afiles.append(padded)
lst = f"{WORK}/p5_audio.txt"
with open(lst,"w") as f:
    for a in afiles: f.write(f"file '{a}'\n")
subprocess.run([FFQ,"-y","-v","error","-f","concat","-safe","0","-i",lst,
                "-c:a","pcm_s16le","-ar","44100",f"{WORK}/p5_full.wav"],
               check=True, capture_output=True)
print("Audio OK", flush=True)

subprocess.run([FFQ,"-y","-v","error","-i",f"{WORK}/p5_silent.mp4",
                "-i",f"{WORK}/p5_full.wav",
                "-c:v","copy","-c:a","aac","-b:a","128k","-ar","44100",
                "-shortest", OUT],
               check=True, capture_output=True)
r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
            "-of","csv=p=0",OUT], capture_output=True, text=True)
print(f"SELESAI: {OUT} ({float(r.stdout.strip()):.1f}s)")
