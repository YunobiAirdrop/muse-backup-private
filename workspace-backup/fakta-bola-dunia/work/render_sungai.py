#!/usr/bin/env python3
"""Render sungai-terpanjang: background sungai (riverbg.py) 100% PIL,
karakter id/eg/br, CTA tengah (beat 16) + CTA akhir (beat 15)."""
import sys, math, json, subprocess, os
sys.path.insert(0, "/home/hatch/workspace/fakta-bola-dunia/work")
from faces_v2 import face_image_v2, get_hand
from emoticons import EMOTICONS
from riverbg import draw_background, paste_ball_shadow
from PIL import Image, ImageDraw, ImageFont

WORK = "/home/hatch/workspace/fakta-bola-dunia/work"
ADIR = f"{WORK}/sungai-audio"
TEMP = f"{WORK}/sungai_silent_tmp.mp4"
FINAL = "/home/hatch/workspace/fakta-bola-dunia/output/sungai-terpanjang.mp4"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FPS = 30
BS = 400
HAND_SIZE = 150

POS = {'id': (140, 350), 'eg': (540, 350), 'br': (340, 1000)}
LABEL = {'id': 'INDONESIA', 'eg': 'MESIR', 'br': 'BRASIL'}

EXPR = {
    1: ('senang', 'wave'),
    2: ('senang', 'open_palm'),
    3: ('bingung', 'cheek'),
    4: ('normal', 'open_palm'),
    5: ('kaget', None),
    6: ('senang', 'thumbs_up'),
    7: ('senang', 'fist'),
    8: ('kaget', 'cheek'),
    9: ('senang', 'open_palm'),
    10: ('kaget', None),
    16: ('senang', 'wave'),   # CTA TENGAH
    11: ('normal', 'open_palm'),
    12: ('kaget', 'cheek'),
    13: ('senang', 'fist'),
    14: ('senang', 'peace'),
    15: ('senang', 'wave'),   # CTA AKHIR (verbal + visual)
}
MOUTH_MAP = {0: 'tutup', 1: 'buka_kecil', 2: 'buka_lebar'}

EMO = {
    2: 'notes',
    3: 'question',
    5: 'interrobang',
    7: 'exclaim',
    8: 'interrobang',
    12: 'interrobang',
    14: 'notes',
}
EMO_SIZE = 95

# overlay kata kunci per beat
KEY_TXT = {2: 'SUNGAI NIL', 6: 'TERDERAS SEDUNIA', 9: 'SUNGAI KAPUAS',
           12: 'PIRAMIDA!', 14: 'PIRANHA!'}

sync = json.load(open(f"{WORK}/mouth_sync_sungai.json"))
ORDER = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 11, 12, 13, 14, 15]
beats = []
for line in open(f"{WORK}/script_sungai.txt"):
    n, spk, text = line.strip().split("|", 2)
    beats.append((int(n), spk))
bmap = dict(beats)
beats = [(n, bmap[n]) for n in ORDER]
print("Urutan beat:", [n for n, _ in beats], flush=True)

print("Pre-render wajah...", flush=True)
BALL = {}
for c in ('id', 'eg', 'br'):
    for es in ('normal', 'kaget', 'senang', 'bingung', 'takut'):
        for ms in ('tutup', 'buka_kecil', 'buka_lebar', 'senyum', 'o'):
            BALL[(c, es, ms)] = face_image_v2(c, es, ms, BS)

name_font = ImageFont.truetype(FONT, 48)
key_font = ImageFont.truetype(FONT, 130)
cta_font = ImageFont.truetype(FONT, 110)

def text_img(text, font, fill, stroke_w=4):
    bb = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
        (0, 0), text, font=font, stroke_width=stroke_w)
    w, h = bb[2]-bb[0]+20, bb[3]-bb[1]+20
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((10-bb[0], 10-bb[1]), text, font=font, fill=fill,
           stroke_width=stroke_w, stroke_fill="black")
    return im

labels = {c: text_img(LABEL[c], name_font, "white") for c in LABEL}
keytxt = {k: text_img(v, key_font, (255, 215, 0), stroke_w=6)
          for k, v in KEY_TXT.items()}
for k, im in keytxt.items():
    if im.width > 860:
        _sc = 860 / im.width
        keytxt[k] = im.resize((860, int(im.height*_sc)), Image.LANCZOS)
cta_base = text_img("LIKE & SUBSCRIBE!", cta_font, (255, 215, 0), stroke_w=6)
if cta_base.width > 860:
    _sc = 860 / cta_base.width
    cta_base = cta_base.resize((860, int(cta_base.height*_sc)), Image.LANCZOS)

YT_RED = (230, 33, 23)
def make_like_button(w=440, h=100):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], radius=h//2, fill=YT_RED)
    cx, cy, r = 62, h//2, 30
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill="white")
    d.rounded_rectangle([cx-8, cy-22, cx+8, cy+14], radius=8, fill=YT_RED)
    d.ellipse([cx-12, cy-30, cx+12, cy-8], fill=YT_RED)
    for i in range(3):
        yy = cy + 2 + i*9
        d.rounded_rectangle([cx-2, yy, cx+26, yy+6], radius=3, fill=YT_RED)
    fnt = ImageFont.truetype(FONT, 52)
    d.text((110, h//2), "LIKE", font=fnt, fill="white", anchor="lm")
    return im

def make_subscribe_button(w=560, h=100):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], radius=h//2, fill=YT_RED)
    cx, cy, s = 62, h//2, 26
    d.polygon([(cx-14, cy-s), (cx-14, cy+s), (cx+20, cy)], fill="white")
    fnt = ImageFont.truetype(FONT, 52)
    d.text((110, h//2), "Subscribe", font=fnt, fill="white", anchor="lm")
    return im

btn_like = make_like_button()
btn_sub = make_subscribe_button()
dong_font = ImageFont.truetype(FONT, 120)
dong_img = text_img("DONG!", dong_font, (255, 215, 0), stroke_w=8)

_hand_point_src = get_hand("right", "point").rotate(90, expand=True, resample=Image.BICUBIC)
HAND_POINT_UP = _hand_point_src.resize((HAND_SIZE, HAND_SIZE), Image.LANCZOS)
HAND_WAVE_L = get_hand("left", "wave").resize((HAND_SIZE, HAND_SIZE), Image.LANCZOS)
HAND_WAVE_R = get_hand("right", "wave").resize((HAND_SIZE, HAND_SIZE), Image.LANCZOS)
HAND_CHEEK = {s: get_hand(s, "cheek").resize((160, 160), Image.LANCZOS)
              for s in ('left', 'right')}
HAND_NEW = {}
for pose in ('thumbs_up', 'open_palm', 'fist', 'peace', 'clap'):
    for side in ('left', 'right'):
        HAND_NEW[(side, pose)] = get_hand(side, pose).resize((HAND_SIZE, HAND_SIZE), Image.LANCZOS)
EMO_IMG = {name: fn(EMO_SIZE) for name, fn in EMOTICONS.items()}

def paste_emoticon(fr, emo_name, bx, by, t):
    img = EMO_IMG[emo_name]
    cx = bx + BS//2 + 150
    cy = by + BS//2 - 80
    pop = min(1.0, t/0.2)
    s = pop*(1+0.25*math.sin(pop*math.pi)) if pop < 1.0 else 1.0
    bob = int(6*math.sin(2*math.pi*2.5*t)) if pop >= 1.0 else 0
    w, h = int(img.width*s), int(img.height*s)
    if w < 4 or h < 4: return
    im2 = img.resize((w, h), Image.LANCZOS)
    fr.paste(im2, (int(cx-w//2), int(cy-h//2+bob)), im2)

def paste_hands_bottom(fr, pose, bx, by, t):
    base_y = by + BS - 20
    lx, rx = bx - 60, bx + BS - 40
    if pose == "point":
        ly = base_y + int(18*math.sin(2*math.pi*2*t))
        ry = base_y + int(18*math.sin(2*math.pi*2*t + math.pi))
        fr.paste(HAND_POINT_UP, (lx, ly), HAND_POINT_UP)
        fr.paste(HAND_POINT_UP, (rx, ry), HAND_POINT_UP)
    elif pose == "wave":
        loff = int(22*math.sin(2*math.pi*3*t))
        fr.paste(HAND_WAVE_L, (lx+loff, base_y), HAND_WAVE_L)
        fr.paste(HAND_WAVE_R, (rx-loff, base_y), HAND_WAVE_R)
    elif pose == "thumbs_up":
        ly = base_y + int(20*abs(math.sin(2*math.pi*2.5*t)))
        ry = base_y + int(20*abs(math.sin(2*math.pi*2.5*t + math.pi)))
        fr.paste(HAND_NEW[('left','thumbs_up')], (lx, ly), HAND_NEW[('left','thumbs_up')])
        fr.paste(HAND_NEW[('right','thumbs_up')], (rx, ry), HAND_NEW[('right','thumbs_up')])
    elif pose == "open_palm":
        loff = int(14*math.sin(2*math.pi*1.8*t))
        fr.paste(HAND_NEW[('left','open_palm')], (lx, base_y+loff), HAND_NEW[('left','open_palm')])
        fr.paste(HAND_NEW[('right','open_palm')], (rx, base_y-loff), HAND_NEW[('right','open_palm')])
    elif pose == "fist":
        loff = int(8*math.sin(2*math.pi*8*t))
        fr.paste(HAND_NEW[('left','fist')], (lx+loff, base_y), HAND_NEW[('left','fist')])
        fr.paste(HAND_NEW[('right','fist')], (rx-loff, base_y), HAND_NEW[('right','fist')])
    elif pose == "peace":
        loff = int(18*math.sin(2*math.pi*2*t))
        fr.paste(HAND_NEW[('left','peace')], (lx+loff, base_y), HAND_NEW[('left','peace')])
        fr.paste(HAND_NEW[('right','peace')], (rx+loff, base_y), HAND_NEW[('right','peace')])
    elif pose == "clap":
        gap = int(55*abs(math.sin(2*math.pi*3*t)))
        fr.paste(HAND_NEW[('left','clap')], (lx+110-gap, base_y), HAND_NEW[('left','clap')])
        fr.paste(HAND_NEW[('right','clap')], (rx-110+gap, base_y), HAND_NEW[('right','clap')])

def paste_cheek(fr, bx, by, t):
    for side in ('left', 'right'):
        h = HAND_CHEEK[side]
        hx = bx-110 if side == "left" else bx+BS-50
        hy = by+120
        if t < 0.25:
            s = t/0.25
            nw, nh = int(160*s), int(160*s)
            if nw > 4:
                h2 = h.resize((nw, nh), Image.LANCZOS)
                fr.paste(h2, (hx+80-nw//2, hy+80-nh//2), h2)
                continue
        fr.paste(h, (hx, hy), h)

TAIL = 0.30
AUDIO_SRC = {n: f"{ADIR}/b{n:02d}.wav" for n, _ in beats}
total_frames = 0
beat_frames = {}
for n, spk in beats:
    dur = sync[str(n)]["dur"]
    nf = int((dur + TAIL)*FPS)
    beat_frames[n] = (nf, dur)
    total_frames += nf

print(f"Total {total_frames} frame (~{total_frames/FPS:.1f}s)", flush=True)
print("Background: sungai via riverbg.py", flush=True)

fi = 0
p = subprocess.Popen(
    [FFQ, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920",
     "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast",
     "-crf", "23", "-pix_fmt", "yuv420p", TEMP],
    stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
assert p.stdin

for n, spk in beats:
    nf, adur = beat_frames[n]
    states = sync[str(n)]["mouth"]
    eye_spk, hand_pose = EXPR.get(n, ("normal", None))
    is_final_cta = (n == 15)
    is_midcta = (n == 16)
    for i in range(nf):
        t = i / FPS
        fr = draw_background(fi)
        fi += 1
        for bc in ('id', 'eg', 'br'):
            _bx0, _by0 = POS[bc]
            paste_ball_shadow(fr, _bx0, _by0, BS)
        spk_yoff = 0
        for c in ('id', 'eg', 'br'):
            x0, y0 = POS[c]
            if is_midcta:
                if c == spk:
                    st = states[min(i, len(states)-1)]
                    ms = MOUTH_MAP[st]
                    if ms == 'tutup': ms = 'senyum'
                    img = BALL[(c, 'senang', ms)]
                    yoff = -abs(math.sin(2*math.pi*1.5*t))*25
                    spk_yoff = yoff
                else:
                    img = BALL[(c, 'senang', 'senyum')]
                    yoff = -abs(math.sin(2*math.pi*1.5*t + 1.0))*15
            elif c == spk:
                st = states[min(i, len(states)-1)]
                ms = MOUTH_MAP[st]
                if ms == 'tutup' and eye_spk in ('kaget', 'takut') and t < 0.8:
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
        if is_midcta:
            for c in ('id', 'eg', 'br'):
                x0, y0 = POS[c]
                paste_hands_bottom(fr, 'wave', x0, int(y0), t)
        elif hand_pose:
            x0, y0 = POS[spk]
            by_eff = int(y0 + spk_yoff)
            if hand_pose == "cheek":
                paste_cheek(fr, x0, by_eff, t)
            else:
                paste_hands_bottom(fr, hand_pose, x0, by_eff, t)
        if n in EMO and not is_midcta:
            x0, y0 = POS[spk]
            paste_emoticon(fr, EMO[n], x0, int(y0 + spk_yoff), t)
        if n in KEY_TXT and not is_midcta:
            ft = keytxt[n]
            fr.paste(ft, (540-ft.width//2, 1480), ft)
        if is_midcta:
            pop = min(1.0, t/0.3)
            s = pop*(1+0.15*math.sin(pop*math.pi)) if pop < 1.0 else 1.0
            for btn, by in ((btn_like, 90), (btn_sub, 210)):
                bw, bh = int(btn.width*s), int(btn.height*s)
                if bw > 4 and bh > 4:
                    b2 = btn.resize((bw, bh), Image.LANCZOS)
                    fr.paste(b2, (540-bw//2, by), b2)
            dw, dh = int(dong_img.width*s), int(dong_img.height*s)
            if dw > 4 and dh > 4:
                d2 = dong_img.resize((dw, dh), Image.LANCZOS)
                fr.paste(d2, (540-dw//2, 1450-dh//2), d2)
        if is_final_cta:
            pop = min(1.0, t/0.35)
            s = pop*(1+0.08*math.sin(2*math.pi*1.5*t))
            cw, ch = int(cta_base.width*s), int(cta_base.height*s)
            if cw > 4 and ch > 4:
                ct = cta_base.resize((cw, ch), Image.LANCZOS)
                fr.paste(ct, (540-cw//2, 1500-ch//2), ct)
        p.stdin.write(fr.tobytes())
    print(f"  beat {n:02d} ({spk},{EXPR.get(n, ('?','?'))[0]},{EXPR.get(n, ('?','?'))[1]}) {nf}f", flush=True)
p.stdin.close(); p.wait()
assert p.returncode == 0, "render gagal"
print("Video silent OK", flush=True)

# ---- audio: gabung beat + tail silence, absolute paths ----
print("Gabung audio...", flush=True)
import shutil
alist = f"{WORK}/sungai_alist.txt"
durs = {}
for n, spk in beats:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0",
                        AUDIO_SRC[n]], capture_output=True, text=True)
    durs[n] = float(r.stdout.strip())
with open(alist, "w") as f:
    for n, spk in beats:
        f.write(f"file '{AUDIO_SRC[n]}'\n")
tmp_full = f"{WORK}/sungai_full_tmp.wav"
inputs, fc, amaps = [], [], []
for idx, (n, spk) in enumerate(beats):
    inputs += ["-i", AUDIO_SRC[n]]
    whole = durs[n] + TAIL
    fc.append(f"[{idx}:a]apad=whole_dur={whole:.3f}[a{idx}]")
    amaps.append(f"[a{idx}]")
fc.append("".join(amaps) + f"concat=n={len(beats)}:v=0:a=1[aout]")
subprocess.run([FFQ, "-y", "-v", "error"] + inputs +
               ["-filter_complex", ";".join(fc), "-map", "[aout]",
                "-ar", "44100", "-ac", "1", tmp_full],
               check=True, capture_output=True, timeout=3600)
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration", "-of", "csv=p=0", tmp_full],
                   capture_output=True, text=True)
aud_dur = float(r.stdout.strip())
print(f"Audio full: {aud_dur:.2f}s", flush=True)

# ---- mux + verifikasi durasi SEBELUM move ----
tmp_mux = f"{WORK}/sungai_mux_tmp.mp4"
subprocess.run([FFQ, "-y", "-v", "error", "-i", TEMP, "-i", tmp_full,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                "-shortest", tmp_mux], check=True, capture_output=True, timeout=3600)
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration", "-of", "csv=p=0", tmp_mux],
                   capture_output=True, text=True)
vid_dur = float(r.stdout.strip())
print(f"Video final (tmp): {vid_dur:.2f}s", flush=True)
assert abs(vid_dur - aud_dur) < 1.5, f"durasi mismatch: {vid_dur} vs {aud_dur}"
assert 25 <= vid_dur <= 70, f"durasi di luar 25-70: {vid_dur}"
shutil.move(tmp_mux, FINAL)
print(f"SELESAI: {FINAL} ({vid_dur:.1f}s)")
