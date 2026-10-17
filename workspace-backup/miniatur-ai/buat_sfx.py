#!/usr/bin/env python3
"""SFX track untuk mini-pompa-air-drama.mp4 — 190 detik, sinkron per scene.
Scene: tiap klip 10 detik. 0-10 A intro | 10-20 B masalah | 20-30 traktor |
30-40 gali | 40-50 semen | 50-70 bata | 70-90 rakit | 90-110 pompa+pipa |
110-120 cat | 120-130 tanam | 130-140 KLIMAKS diesel | 140-160 air deras |
160-180 happy ending | 180-190 penutup golden hour."""
import numpy as np
import wave

SR = 44100
DUR = 190.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
track = np.zeros(N, dtype=np.float64)
t_all = np.arange(N) / SR


def fft_filter(x, cutoff, ftype="lowpass"):
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = 1e-9
    if ftype == "lowpass":
        H = 1 / (1 + (f / cutoff) ** 4)
    elif ftype == "highpass":
        H = (f / cutoff) ** 4 / (1 + (f / cutoff) ** 4)
    else:  # bandpass, cutoff = (f1, f2)
        f1, f2 = cutoff
        H = (1 / (1 + (f / f2) ** 4)) * ((f / f1) ** 4 / (1 + (f / f1) ** 4))
    return np.fft.irfft(X * H, n)


def pink_noise(n):
    w = rng.standard_normal(n)
    W = np.fft.rfft(w)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = 1.0
    x = np.fft.irfft(W / np.sqrt(f), n)
    return x / (np.max(np.abs(x)) + 1e-9)


def add_at(sound, start):
    i0 = int(start * SR)
    i1 = min(N, i0 + len(sound))
    if i1 > i0:
        track[i0:i1] += sound[: i1 - i0]


def env_ad(n, a=0.005, d=0.05):
    e = np.ones(n)
    na = max(1, int(a * SR))
    nd = max(1, int(d * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nd:] = np.linspace(1, 0, nd)
    return e


def tone(freq, dur, decay=0.05, f1=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    fr = np.linspace(freq, f1 if f1 else freq, n)
    ph = np.cumsum(2 * np.pi * fr / SR)
    s = np.sin(ph) * np.exp(-t / decay)
    return s * env_ad(n)


# ---- 1. Angin dasar sepanjang video (pink noise lowpass, pelan) ----
wind = fft_filter(pink_noise(N), 350) * 0.10
lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t_all)
track += wind * lfo

# ---- 2. Kicau burung (scene 1-2 dan 13-14) ----
def bird_chirp():
    dur = rng.uniform(0.2, 0.4)
    f0 = rng.uniform(2400, 3000)
    return tone(f0, dur, decay=dur / 2.5, f1=f0 + rng.uniform(800, 1500)) * 0.16

for span in [(1.0, 19.0), (161.0, 188.0)]:
    tt = span[0]
    while tt < span[1]:
        add_at(bird_chirp(), tt)
        tt += rng.uniform(4.0, 8.0)

# ---- 3. Traktor (20-30): dengung mesin rendah ----
n = int(10 * SR)
t = np.arange(n) / SR
hum = (np.sin(2 * np.pi * 60 * t) + 0.5 * np.sin(2 * np.pi * 120 * t))
hum *= 0.6 + 0.4 * np.sin(2 * np.pi * 8 * t)
hum *= np.minimum(1, t / 1.5) * np.minimum(1, (10 - t) / 1.5)
add_at(hum * 0.28, 20.0)

# ---- 4. Gali (30-40): hentakan sekop tiap ~1 dtk ----
for k in range(9):
    burst = fft_filter(rng.standard_normal(int(0.18 * SR)), 500) * np.exp(
        -np.arange(int(0.18 * SR)) / SR / 0.05
    )
    add_at(burst * 0.55 * env_ad(len(burst)), 30.3 + k * 1.0)

# ---- 5. Aduk semen (40-50): noise bandpass termodulasi ----
n = int(10 * SR)
t = np.arange(n) / SR
mix = fft_filter(pink_noise(n), (300, 600), "bandpass")
mix *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.9 * t)
mix *= np.minimum(1, t / 1.0) * np.minimum(1, (10 - t) / 1.0)
add_at(mix * 0.30, 40.0)

# ---- 6. Susun bata (50-70): klik tiap bata ----
tt = 50.4
while tt < 69.0:
    add_at(tone(1500, 0.09, decay=0.02) * 0.35, tt)
    add_at(tone(900, 0.07, decay=0.03) * 0.15, tt + 0.03)
    tt += rng.uniform(1.2, 1.8)

# ---- 7a. Rakit mesin (70-80): klik logam ----
tt = 70.4
while tt < 79.0:
    add_at(tone(2500, 0.06, decay=0.015) * 0.28, tt)
    tt += rng.uniform(0.9, 1.5)

# ---- 7b. Kunci pas (80-90): derit + klik ----
for k in range(4):
    add_at(tone(1800, 0.18, decay=0.09, f1=2400) * 0.20, 80.5 + k * 2.2)
    add_at(tone(2600, 0.05, decay=0.012) * 0.25, 81.0 + k * 2.2)

# ---- 8a. Pasang pompa (90-100): dentuman rendah ----
for k in range(5):
    add_at(tone(120, 0.25, decay=0.09) * 0.5, 90.5 + k * 2.0)

# ---- 8b. Sambung pipa (100-110): klik plastik ----
tt = 100.4
while tt < 109.0:
    burst = fft_filter(rng.standard_normal(int(0.06 * SR)), 2000) * np.exp(
        -np.arange(int(0.06 * SR)) / SR / 0.015
    )
    add_at(burst * 0.4 * env_ad(len(burst)), tt)
    tt += rng.uniform(1.2, 1.8)

# ---- 9. Cat (110-120): sapuan kuas ----
for k in range(7):
    n = int(0.45 * SR)
    sw = fft_filter(rng.standard_normal(n), 3000) * 0.10
    sw *= np.sin(np.pi * np.arange(n) / n)  # swell
    add_at(sw, 110.4 + k * 1.3)

# ---- 10. Tanam (120-130): tepukan tanah lembut ----
for k in range(6):
    add_at(tone(200, 0.15, decay=0.06) * 0.30, 120.5 + k * 1.6)

# ---- 11. KLIMAKS diesel (130-150): starter crank lalu chug-chug ----
# 130-132: tarikan starter (crank tidak beraturan)
n = int(2.2 * SR)
t = np.arange(n) / SR
crank = np.sin(2 * np.pi * 40 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t))
crank *= np.minimum(1, t / 0.3) * np.linspace(1, 0.3, n)
add_at(crank * 0.35, 130.0)
# 132-150: diesel chug stabil 55Hz + tremolo 7Hz dalam
n = int(18 * SR)
t = np.arange(n) / SR
chug = np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 110 * t)
chug *= 0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t)) ** 2
chug += 0.15 * fft_filter(rng.standard_normal(n), 800)
chug *= np.minimum(1, t / 1.5)  # ramp-up
add_at(chug * 0.42, 132.0)

# ---- 12. Air deras (140-160): pink noise lowpass + tremolo ----
n = int(20 * SR)
t = np.arange(n) / SR
rush = fft_filter(pink_noise(n), 900)
rush *= 0.6 + 0.4 * np.sin(2 * np.pi * 2 * t)
rush *= np.minimum(1, t / 2.0) * np.minimum(1, (20 - t) / 2.0)
add_at(rush * 0.55, 140.0)

# ---- 13. Happy ending (160-180): gemericik lembut + tetesan ----
n = int(20 * SR)
t = np.arange(n) / SR
trickle = fft_filter(pink_noise(n), 1200) * 0.18
trickle *= 0.7 + 0.3 * np.sin(2 * np.pi * 1.3 * t)
trickle *= np.minimum(1, t / 1.5) * np.minimum(1, (20 - t) / 2.0)
add_at(trickle, 160.0)
tt = 161.0
while tt < 179.0:  # tetesan air
    add_at(tone(rng.uniform(2800, 3600), 0.08, decay=0.02) * 0.12, tt)
    tt += rng.uniform(0.8, 2.2)

# ---- Fade-out 2 detik di akhir ----
nf = int(2 * SR)
track[-nf:] *= np.linspace(1, 0, nf)

# ---- Normalisasi & tulis WAV ----
peak = np.max(np.abs(track)) + 1e-9
track = track / peak * 0.89
pcm = (track * 32767).astype(np.int16)
with wave.open("/home/hatch/workspace/miniatur-ai/sfx-drama.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"SFX OK: {DUR}s, peak {peak:.3f} -> dinormalisasi 0.89")
