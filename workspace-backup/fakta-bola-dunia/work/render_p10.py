#!/usr/bin/env python3
"""Render part10: background diganti animasi gaya gameplay (gamebg.py),
100% digambar via PIL. Sisanya sama seperti part9."""
import sys, math, json, subprocess, os
sys.path.insert(0, "/home/hatch/workspace/fakta-bola-dunia/work")
from faces_v2 import face_image_v2, get_hand
from emoticons import EMOTICONS
from gamebg import draw_background, paste_ball_shadow
from PIL import Image, ImageDraw, ImageFont

WORK = "/home/hatch/workspace/fakta-bola-dunia/work"
OUT = "/home/hatch/workspace/fakta-bola-dunia/output/angka-seram-part10.mp4"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FPS = 24
BG = (134, 212, 254)
BS = 400  # ukuran bola
HAND_SIZE = 150

POS = {'id': (140, 350), 'cn': (540, 350), 'jp': (340, 1000)}
LABEL = {'id': 'INDONESIA', 'cn': 'CHINA', 'jp': 'JEPANG'}

# Ekspresi per beat: (eye_style, hand_pose atau None)
# Mapping pose tangan mengikuti konteks dialog (tidak ada 2 beat berurutan dgn pose sama):
#  1 wave       : pembuka, melambai ("Eh eh, kalian tau nggak?")
#  2 open_palm  : bingung mempresentasikan ("Hah? Angka kok seram?")
#  3 None       : bingung saja (variasi, hindari duplikat pose)
#  4 open_palm  : mempresentasikan fakta ("Dengerin dulu! ...666")
#  5 cheek      : kaget takut ("Hih?! ...Angka setan!")
#  6 fist       : tegang ("Waduh... film horor")
#  7 thumbs_up  : setuju ("Betul! Lanjut...")
#  8 cheek      : kaget ("Serius?! Friday the thirteenth?")
#  9 fist       : takut tegang ("Katanya hari sial ya?")
# 10 open_palm  : menjelaskan ("Gedung-gedung aja nggak ada lantai 13")
# 11 None       : penasaran bertanya (variasi, hindari duplikat pose)
# 12 fist       : penekanan dramatis ("Nah, yang paling seram... angka empat!")
# 13 cheek      : kaget ("Hah?! Kok empat?")
# 14 open_palm  : menjelaskan ("Di China, angka empat bunyinya mirip kata mati")
# 15 clap       : kagum menyadari ("Ya ampun! Bener juga!")
# 16 peace      : fun ("Tuh kan! Kalian baru tau kan?")
# 17 thumbs_up  : setuju ("Serem juga ya...")
# 18 wave       : CTA (tetap)
EXPR = {
    1: ('senang', 'wave'),
    2: ('bingung', 'open_palm'),
    3: ('bingung', None),
    4: ('normal', 'open_palm'),
    5: ('takut', 'cheek'),
    6: ('takut', 'fist'),
    7: ('normal', 'thumbs_up'),
    8: ('kaget', 'cheek'),
    9: ('takut', 'fist'),
    10: ('normal', 'open_palm'),
    11: ('kaget', None),
    12: ('normal', 'fist'),
    13: ('kaget', 'cheek'),
    14: ('normal', 'open_palm'),
    15: ('kaget', 'clap'),
    16: ('senang', 'peace'),
    17: ('normal', 'thumbs_up'),
    18: ('senang', 'wave'),
    19: ('senang', 'wave'),   # CTA TENGAH (setelah beat 10)
}
NUM = {4:'666',5:'666',6:'666',7:'13',8:'13',9:'13',10:'13',
       12:'4',13:'4',14:'4',15:'4'}
MOUTH_MAP = {0:'tutup', 1:'buka_kecil', 2:'buka_lebar'}

# Emoticon per beat mengikuti ekspresi (maks 1 per beat, beat 18/CTA: tidak pakai)
# kaget -> interrobang/exclaim | bingung -> question | takut -> sweat_drop | senang -> notes
EMO = {
    1: 'notes',        # senang (pembuka)
    2: 'question',     # bingung
    3: 'question',     # bingung
    5: 'sweat_drop',   # takut
    6: 'sweat_drop',   # takut
    8: 'interrobang',  # kaget
    9: 'sweat_drop',   # takut
    11: 'exclaim',     # kaget
    13: 'interrobang', # kaget
    15: 'exclaim',     # kaget
    16: 'notes',       # senang
}
EMO_SIZE = 95

sync = json.load(open(f"{WORK}/mouth_sync_p5.json"))
beats = []
for line in open(f"{WORK}/script_p4.txt"):
    n, spk, text = line.strip().split("|", 2)
    beats.append((int(n), spk))
# Sisipkan CTA TENGAH (beat 19, suara Indonesia) setelah beat 10 (selesai bahas 13)
beats2 = []
for n, spk in beats:
    beats2.append((n, spk))
    if n == 10:
        beats2.append((19, 'id'))
beats = beats2
print("Urutan beat:", [n for n, _ in beats], flush=True)

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

# ---- TOMBOL CTA TENGAH (gaya referensi: LIKE + Subscribe + "DONG!") ----
YT_RED = (230, 33, 23)
def _rounded_rect(d, box, r, fill):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=r, fill=fill)

def make_like_button(w=440, h=100):
    """Tombol LIKE merah + icon jempol putih."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    _rounded_rect(d, [0, 0, w, h], h // 2, YT_RED)
    # icon jempol sederhana: lingkaran + jempol
    cx, cy, r = 62, h // 2, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="white")
    # jempol: batang vertikal + ujung
    d.rounded_rectangle([cx - 8, cy - 22, cx + 8, cy + 14], radius=8, fill=YT_RED)
    d.ellipse([cx - 12, cy - 30, cx + 12, cy - 8], fill=YT_RED)
    # 4 jari: garis horizontal
    for i in range(3):
        yy = cy + 2 + i * 9
        d.rounded_rectangle([cx - 2, yy, cx + 26, yy + 6], radius=3, fill=YT_RED)
    fnt = ImageFont.truetype(FONT, 52)
    d.text((110, h // 2), "LIKE", font=fnt, fill="white", anchor="lm")
    return im

def make_subscribe_button(w=560, h=100):
    """Tombol Subscribe merah + icon play putih."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    _rounded_rect(d, [0, 0, w, h], h // 2, YT_RED)
    # icon play: segitiga putih
    cx, cy, s = 62, h // 2, 26
    d.polygon([(cx - 14, cy - s), (cx - 14, cy + s), (cx + 20, cy)], fill="white")
    fnt = ImageFont.truetype(FONT, 52)
    d.text((110, h // 2), "Subscribe", font=fnt, fill="white", anchor="lm")
    return im

btn_like = make_like_button()
btn_sub = make_subscribe_button()
dong_font = ImageFont.truetype(FONT, 120)
dong_img = text_img("DONG!", dong_font, (255, 215, 0), stroke_w=8)
print("Tombol CTA tengah OK", flush=True)

# ---- TANGAN: siapkan aset ----
# point: putar 90° CCW agar jari menunjuk ke ATAS (untuk posisi bawah bola)
_hand_point_src = get_hand("right", "point").rotate(90, expand=True, resample=Image.BICUBIC)
HAND_POINT_UP = _hand_point_src.resize((HAND_SIZE, HAND_SIZE), Image.LANCZOS)
HAND_WAVE_L = get_hand("left", "wave").resize((HAND_SIZE, HAND_SIZE), Image.LANCZOS)
HAND_WAVE_R = get_hand("right", "wave").resize((HAND_SIZE, HAND_SIZE), Image.LANCZOS)
# cheek: ukuran seperti part5 (160)
HAND_CHEEK = {}
for side in ('left', 'right'):
    HAND_CHEEK[side] = get_hand(side, "cheek").resize((160, 160), Image.LANCZOS)
# 5 pose baru (ukuran HAND_SIZE agar konsisten)
HAND_NEW = {}
for pose in ('thumbs_up', 'open_palm', 'fist', 'peace', 'clap'):
    for side in ('left', 'right'):
        HAND_NEW[(side, pose)] = get_hand(side, pose).resize((HAND_SIZE, HAND_SIZE), Image.LANCZOS)

# ---- EMOTICON: pre-render ----
EMO_IMG = {name: fn(EMO_SIZE) for name, fn in EMOTICONS.items()}
print("Emoticon OK:", list(EMO_IMG.keys()), flush=True)

def paste_emoticon(fr, emo_name, bx, by, t):
    """Emoticon di kanan atas kepala: pop-in 0.2s + bounce ringan.
    bx,by = posisi kiri-atas bola (sudah termasuk yoff bounce)."""
    img = EMO_IMG[emo_name]
    # posisi: kanan atas kepala (offset dari center bola)
    cx = bx + BS // 2 + 150
    cy = by + BS // 2 - 80
    # pop-in scale 0->1 dalam 0.2 detik
    pop = min(1.0, t / 0.2)
    # overshoot sedikit biar terasa pop
    s = pop * (1 + 0.25 * math.sin(pop * math.pi)) if pop < 1.0 else 1.0
    # bounce ringan setelah muncul
    bob = int(6 * math.sin(2 * math.pi * 2.5 * t)) if pop >= 1.0 else 0
    w = int(img.width * s)
    h = int(img.height * s)
    if w < 4 or h < 4:
        return
    im2 = img.resize((w, h), Image.LANCZOS)
    fr.paste(im2, (int(cx - w // 2), int(cy - h // 2 + bob)), im2)

def paste_hands_bottom(fr, pose, bx, by, t):
    """Dua tangan di BAWAH bola, seolah memegangi tepi bawah (referensi h32.png)."""
    base_y = by + BS - 20          # overlap sedikit dengan bola
    lx = bx - 60                    # tangan kiri
    rx = bx + BS - 40               # tangan kanan
    if pose == "point":
        # naik-turun bergantian, seolah menunjuk ke atas
        ly = base_y + int(18*math.sin(2*math.pi*2*t))
        ry = base_y + int(18*math.sin(2*math.pi*2*t + math.pi))
        fr.paste(HAND_POINT_UP, (lx, ly), HAND_POINT_UP)
        fr.paste(HAND_POINT_UP, (rx, ry), HAND_POINT_UP)
    elif pose == "wave":
        # goyang kiri-kanan berlawanan arah
        loff = int(22*math.sin(2*math.pi*3*t))
        fr.paste(HAND_WAVE_L, (lx + loff, base_y), HAND_WAVE_L)
        fr.paste(HAND_WAVE_R, (rx - loff, base_y), HAND_WAVE_R)
    elif pose == "thumbs_up":
        # hentakan ke atas bergantian (semangat)
        ly = base_y + int(20*abs(math.sin(2*math.pi*2.5*t)))
        ry = base_y + int(20*abs(math.sin(2*math.pi*2.5*t + math.pi)))
        fr.paste(HAND_NEW[('left','thumbs_up')], (lx, ly), HAND_NEW[('left','thumbs_up')])
        fr.paste(HAND_NEW[('right','thumbs_up')], (rx, ry), HAND_NEW[('right','thumbs_up')])
    elif pose == "open_palm":
        # ayun lembut naik-turun (mempresentasikan)
        loff = int(14*math.sin(2*math.pi*1.8*t))
        fr.paste(HAND_NEW[('left','open_palm')], (lx, base_y+loff), HAND_NEW[('left','open_palm')])
        fr.paste(HAND_NEW[('right','open_palm')], (rx, base_y-loff), HAND_NEW[('right','open_palm')])
    elif pose == "fist":
        # getar cepat kecil (tegang)
        loff = int(8*math.sin(2*math.pi*8*t))
        fr.paste(HAND_NEW[('left','fist')], (lx+loff, base_y), HAND_NEW[('left','fist')])
        fr.paste(HAND_NEW[('right','fist')], (rx-loff, base_y), HAND_NEW[('right','fist')])
    elif pose == "peace":
        # goyang santai kiri-kanan
        loff = int(18*math.sin(2*math.pi*2*t))
        fr.paste(HAND_NEW[('left','peace')], (lx+loff, base_y), HAND_NEW[('left','peace')])
        fr.paste(HAND_NEW[('right','peace')], (rx+loff, base_y), HAND_NEW[('right','peace')])
    elif pose == "clap":
        # kedua tangan mendekat-menjauh (tepuk tangan)
        gap = int(55*abs(math.sin(2*math.pi*3*t)))  # 0=rapat, 55=renggang
        fr.paste(HAND_NEW[('left','clap')], (lx+110-gap, base_y), HAND_NEW[('left','clap')])
        fr.paste(HAND_NEW[('right','clap')], (rx-110+gap, base_y), HAND_NEW[('right','clap')])

def paste_cheek(fr, bx, by, t):
    """Tangan di pipi (tetap seperti part5)."""
    for side in ('left', 'right'):
        h = HAND_CHEEK[side]
        hx = bx - 110 if side == "left" else bx + BS - 50
        hy = by + 120
        if t < 0.25:
            s = t/0.25
            nw, nh = int(160*s), int(160*s)
            if nw > 4:
                h2 = h.resize((nw, nh), Image.LANCZOS)
                fr.paste(h2, (hx+80-nw//2, hy+80-nh//2), h2)
                continue
        fr.paste(h, (hx, hy), h)

TAIL = 0.30
# sumber audio per beat (beat 19 = file khusus CTA tengah)
AUDIO_SRC = {n: f"{WORK}/p5audio/b{n:02d}.wav" for n, _ in beats}
AUDIO_SRC[19] = f"{WORK}/p5audio/b19_midcta.wav"
audio_files = []
total_frames = 0
beat_frames = {}
for n, spk in beats:
    dur = sync[str(n)]["dur"]
    vdur = dur + TAIL
    nf = int(vdur*FPS)
    beat_frames[n] = (nf, dur)
    total_frames += nf
    audio_files.append((AUDIO_SRC[n], dur, vdur))

print(f"Total {total_frames} frame (~{total_frames/FPS:.1f}s)", flush=True)
print("Background: animasi gameplay via gamebg.py", flush=True)

fi10 = 0  # counter frame global untuk background
p = subprocess.Popen(
    [FFQ,"-y","-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920",
     "-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast",
     "-crf","23","-pix_fmt","yuv420p", f"{WORK}/p10_silent.mp4"],
    stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
assert p.stdin

for n, spk in beats:
    nf, adur = beat_frames[n]
    states = sync[str(n)]["mouth"]
    eye_spk, hand_pose = EXPR.get(n, ("normal", None))
    is_cta = (n == 18)
    is_midcta = (n == 19)
    for i in range(nf):
        t = i / FPS
        fr = draw_background(fi10)
        fi10 += 1
        # bayangan lembut di belakang tiap bola agar terbaca jelas
        for bc in ('id', 'cn', 'jp'):
            _bx0, _by0 = POS[bc]
            paste_ball_shadow(fr, _bx0, _by0, BS)
        spk_yoff = 0
        for c in ('id','cn','jp'):
            x0, y0 = POS[c]
            if is_midcta:
                # CTA TENGAH: semua karakter senang menatap kamera
                if c == spk:
                    st = states[min(i, len(states)-1)]
                    ms = MOUTH_MAP[st]
                    if ms == 'tutup':
                        ms = 'senyum'
                    img = BALL[(c, 'senang', ms)]
                    yoff = -abs(math.sin(2*math.pi*1.5*t))*25
                    spk_yoff = yoff
                else:
                    img = BALL[(c, 'senang', 'senyum')]
                    yoff = -abs(math.sin(2*math.pi*1.5*t + 1.0))*15
            elif c == spk:
                st = states[min(i, len(states)-1)]
                ms = MOUTH_MAP[st]
                if ms == 'tutup' and eye_spk in ('kaget','takut') and t < 0.8:
                    ms = 'o'
                if ms == 'tutup' and eye_spk == 'senang':
                    ms = 'senyum'
                img = BALL[(c, eye_spk, ms)]
                yoff = -abs(math.sin(2*math.pi*1.5*t))*25
                spk_yoff = yoff
            else:
                img = BALL[(c, 'normal', 'tutup')]
                yoff = 0
            fr.paste(img, (x0, int(y0+yoff)), img)
            lb = labels[c]
            fr.paste(lb, (x0+BS//2-lb.width//2, y0-60), lb)
        # tangan digambar SETELAH semua bola
        if is_midcta:
            # CTA TENGAH: ketiga karakter wave (meriah)
            for c in ('id','cn','jp'):
                x0, y0 = POS[c]
                paste_hands_bottom(fr, 'wave', x0, int(y0), t)
        elif hand_pose and not is_cta:
            x0, y0 = POS[spk]
            by_eff = int(y0 + spk_yoff)
            if hand_pose == "cheek":
                paste_cheek(fr, x0, by_eff, t)
            else:
                # point & wave -> dua tangan di BAWAH bola
                paste_hands_bottom(fr, hand_pose, x0, by_eff, t)
        # emoticon digambar TERAKHIR (di atas semua), di kanan atas kepala pembicara
        if n in EMO and not is_cta and not is_midcta:
            x0, y0 = POS[spk]
            paste_emoticon(fr, EMO[n], x0, int(y0 + spk_yoff), t)
        if n in NUM and not is_cta and not is_midcta:
            nm = nums[NUM[n]]
            fr.paste(nm, (540-nm.width//2, 1480), nm)
        if is_midcta:
            # CTA TENGAH: tombol LIKE + Subscribe + "DONG!" (gaya referensi)
            pop = min(1.0, t/0.3)
            s = pop * (1 + 0.15*math.sin(pop*math.pi)) if pop < 1.0 else 1.0
            for btn, by in ((btn_like, 90), (btn_sub, 210)):
                bw, bh = int(btn.width*s), int(btn.height*s)
                if bw > 4 and bh > 4:
                    b2 = btn.resize((bw, bh), Image.LANCZOS)
                    fr.paste(b2, (540-bw//2, by), b2)
            dw, dh = int(dong_img.width*s), int(dong_img.height*s)
            if dw > 4 and dh > 4:
                d2 = dong_img.resize((dw, dh), Image.LANCZOS)
                fr.paste(d2, (540-dw//2, 1450-dh//2), d2)
        if is_cta:
            pop = min(1.0, t/0.35)
            s = pop*(1+0.08*math.sin(2*math.pi*1.5*t))
            cw, ch = int(cta_base.width*s), int(cta_base.height*s)
            if cw > 4 and ch > 4:
                ct = cta_base.resize((cw,ch), Image.LANCZOS)
                fr.paste(ct, (540-cw//2, 1500-ch//2), ct)
        p.stdin.write(fr.tobytes())
    print(f"  beat {n:02d} ({spk},{EXPR.get(n,('?','?'))[0]},{EXPR.get(n,('?','?'))[1]}) {nf}f", flush=True)
p.stdin.close(); p.wait()
assert p.returncode == 0, "render gagal"
print("Video silent OK", flush=True)

# audio: REUSE p9_full.wav langsung (tidak regenerate)
import shutil
shutil.copy(f"{WORK}/p9_full.wav", f"{WORK}/p10_full.wav")
print("Audio OK (reuse p9_full.wav)", flush=True)

subprocess.run([FFQ,"-y","-v","error","-i",f"{WORK}/p10_silent.mp4",
                "-i",f"{WORK}/p10_full.wav",
                "-c:v","copy","-c:a","aac","-b:a","128k","-ar","44100",
                "-shortest", OUT],
               check=True, capture_output=True)
r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
            "-of","csv=p=0",OUT], capture_output=True, text=True)
print(f"SELESAI: {OUT} ({float(r.stdout.strip()):.1f}s)")
