#!/usr/bin/env python3
"""Sintesis SFX untuk mini-pompa-air-v2.mp4 — 160 detik, sinkron per klip."""
import numpy as np

SR = 44100
DUR = 160.0
N = int(SR * DUR)
mix = np.zeros(N)
rng = np.random.default_rng(7)

def add(sig, start):
    i0 = int(start * SR)
    if i0 >= N: return
    i1 = min(N, i0 + len(sig))
    mix[i0:i1] += sig[:i1 - i0]

def t(dur):
    return np.arange(int(dur * SR)) / SR

def lowpass(x, fc):
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y

def decay_env(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))

# ---------- building blocks ----------
def cluck(start):
    """Ayam: 3 pulsa pitch turun."""
    for k in range(3):
        d = 0.10
        tt = t(d)
        f = np.linspace(620, 430, len(tt))
        ph = 2 * np.pi * np.cumsum(f) / SR
        sig = np.sin(ph) * decay_env(len(tt), 0.05) * 0.5
        add(sig, start + k * 0.16)

def moo(start):
    """Sapi: glide 170->115Hz + vibrato 5Hz, ~1 dtk."""
    d = 1.0
    tt = t(d)
    f = np.linspace(170, 115, len(tt)) + 8 * np.sin(2 * np.pi * 5 * tt)
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.minimum(1, tt / 0.15) * np.minimum(1, (d - tt) / 0.25)
    sig = (np.sin(ph) + 0.4 * np.sin(2 * ph)) * env * 0.45
    add(sig, start)

def caw(start):
    """Gagak: squawk turun 850->420Hz, 0.45 dtk."""
    d = 0.45
    tt = t(d)
    f = np.linspace(850, 420, len(tt))
    ph = 2 * np.pi * np.cumsum(f) / SR
    am = 0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 28 * tt))
    sig = np.sin(ph) * am * decay_env(len(tt), 0.25) * 0.4
    add(sig, start)

def chug(start, dur, f0=45, trem=6.0, vol=0.5, ramp=0.0):
    """Mesin diesel: fundamental + harmonik + tremolo."""
    tt = t(dur)
    tremolo = 1 - 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * trem * tt))
    sig = (np.sin(2*np.pi*f0*tt) + 0.5*np.sin(2*np.pi*2*f0*tt) + 0.25*np.sin(2*np.pi*3*f0*tt)) * tremolo * vol
    if ramp > 0:
        sig *= np.minimum(1, tt / ramp)
    add(sig, start)

def thud(start, fc=400, dur=0.28, vol=0.5):
    n = int(dur * SR)
    sig = lowpass(rng.standard_normal(n), fc) * decay_env(n, dur * 0.5) * vol
    add(sig, start)

def click_hi(start, f=1500, dur=0.07, vol=0.35):
    tt = t(dur)
    sig = np.sin(2 * np.pi * f * tt) * decay_env(len(tt), 0.02) * vol
    add(sig, start)

def metal_click(start, vol=0.3):
    tt = t(0.05)
    sig = (np.sin(2*np.pi*2500*tt) + 0.5*np.sin(2*np.pi*3600*tt)) * decay_env(len(tt), 0.015) * vol
    add(sig, start)

def plastic_click(start, vol=0.35):
    tt = t(0.06)
    sig = np.sin(2*np.pi*900*tt) * decay_env(len(tt), 0.02) * vol
    n = int(0.03*SR)
    tick = lowpass(rng.standard_normal(n), 3000) * decay_env(n, 0.01) * vol * 0.5
    add(sig, start); add(tick, start)

def wrench(start, vol=0.25):
    d = 0.55
    tt = t(d)
    f = 800 + 400 * np.sin(2 * np.pi * 1.2 * tt)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) * np.sin(np.pi * tt / d) * vol
    add(sig, start)

def brush(start, vol=0.2):
    d = 0.6
    n = int(d * SR)
    tt = t(d)
    sig = lowpass(rng.standard_normal(n), 2500) * np.sin(np.pi * tt / d) * vol
    add(sig, start)

def water_heavy(start, dur, vol=0.4):
    n = int(dur * SR)
    tt = t(dur)
    base = lowpass(rng.standard_normal(n), 900)
    trem = 1 - 0.3 * (0.5 + 0.5 * np.sin(2 * np.pi * 2 * tt))
    add(base * trem * vol, start)

def trickle(start, dur, vol=0.14):
    n = int(dur * SR)
    add(lowpass(rng.standard_normal(n), 1800) * vol, start)
    # tetesan acak
    tt_end = start + dur
    tt = start + 0.5
    while tt < tt_end - 0.3:
        d = 0.06
        ttt = t(d)
        f = np.linspace(2200, 1200, len(ttt))
        ph = 2 * np.pi * np.cumsum(f) / SR
        add(np.sin(ph) * decay_env(len(ttt), 0.02) * 0.12, tt)
        tt += rng.uniform(0.4, 1.1)

def chirp(start, vol=0.18):
    d = 0.28
    tt = t(d)
    f = np.concatenate([np.linspace(2800, 3900, len(tt)//2), np.linspace(3900, 3000, len(tt)-len(tt)//2)])
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) * np.sin(np.pi * tt / d) * vol
    add(sig, start)

def cement(start, dur, vol=0.16):
    n = int(dur * SR)
    tt = t(dur)
    base = lowpass(rng.standard_normal(n), 550)
    am = 1 - 0.4 * (0.5 + 0.5 * np.sin(2 * np.pi * 1.5 * tt))
    add(base * am * vol, start)

def crank(start, vol=0.4):
    for k in range(8):
        d = 0.12
        tt = t(d)
        sig = np.sign(np.sin(2*np.pi*85*tt)) * decay_env(len(tt), 0.05) * vol * 0.6
        add(sig, start + k * 0.22)

# ---------- timeline ----------
# Ambience: angin lembut sepanjang video
wind = lowpass(rng.standard_normal(N), 280) * 0.045
mix += wind

# Burung di scene tenang outdoor
for bt in [2.0, 7.0, 13.5, 46.0, 112.5, 116.5, 151.5, 155.5]:
    chirp(bt); chirp(bt + 0.4)

# Klip 1 (0-10): intro — ayam + sapi
cluck(3.0); cluck(5.6); moo(7.2)
# Klip 2 (10-20): ladang kering — gagak
caw(14.0)
# Klip 3 (20-30): traktor datang
chug(20.0, 10.0, f0=45, trem=6.0, vol=0.5, ramp=3.0)
# Klip 4 (30-40): traktor idle + bata diturunkan
chug(30.0, 10.0, f0=45, trem=6.0, vol=0.22)
for bt in [31.0, 32.5, 34.0, 35.5, 37.0, 38.5]:
    thud(bt, fc=1200, dur=0.12, vol=0.4)
# Klip 5 (40-50): gali
for st in np.arange(40.5, 49.5, 1.2):
    thud(st, fc=400, dur=0.28, vol=0.5)
# Klip 6 (50-60): aduk semen
cement(50.0, 10.0)
# Klip 7 (60-70): susun bata
for bt in np.arange(60.5, 69.0, 1.5):
    click_hi(bt, f=1500, vol=0.35)
# Klip 8 (70-80): rakit mesin
for mt in np.arange(70.5, 79.0, 1.4):
    metal_click(mt)
# Klip 9 (80-90): pasang pompa + kunci pas
thud(81.0, fc=300, dur=0.3, vol=0.55)
wrench(84.0); wrench(86.5)
# Klip 10 (90-100): sambung pipa
for pt in np.arange(91.0, 98.0, 1.4):
    plastic_click(pt)
# Klip 11 (100-110): cat biru
for bt in [101.0, 103.0, 105.0, 107.0, 108.5]:
    brush(bt)
# Klip 12 (110-120): tanam
for pt in np.arange(111.0, 118.0, 1.4):
    thud(pt, fc=500, dur=0.15, vol=0.25)
# Klip 13 (120-130): KLIMAKS — crank lalu diesel chug kuat
crank(120.0)
chug(122.0, 8.0, f0=55, trem=7.0, vol=0.55, ramp=1.5)
# Klip 14 (130-140): air menyembur + diesel lanjut pelan
chug(130.0, 10.0, f0=55, trem=7.0, vol=0.3)
water_heavy(130.0, 10.0, vol=0.42)
# Klip 15 (140-150): irigasi gemericik
trickle(140.0, 10.0, vol=0.15)
# Klip 16 (150-160): happy ending — gemericik + ayam + sapi + burung
trickle(150.0, 10.0, vol=0.1)
cluck(152.0); moo(154.5); cluck(156.5)

# Fade-out 2 detik terakhir
fade_n = int(2.0 * SR)
fade = np.linspace(1, 0, fade_n)
mix[-fade_n:] *= fade

# Normalisasi & tulis
peak = np.max(np.abs(mix))
mix = mix / peak * 0.85
import wave
with wave.open('/home/hatch/workspace/miniatur-ai/sfx-v2.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print(f"SFX OK: {DUR}s, peak sebelum normalisasi {peak:.2f}")
