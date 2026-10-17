#!/usr/bin/env python3
"""Analisis volume per beat -> urutan state mulut per frame (24fps).
State: 0=tutup, 1=buka_kecil, 2=buka_lebar. Threshold dari RMS per 120ms."""
import wave, struct
import numpy as np
import json

WORK = "/home/hatch/workspace/fakta-bola-dunia/work"
FPS = 24
WIN = 0.120  # 120ms

def analyze(path):
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        n = w.getnframes()
        raw = w.readframes(n)
    samp = np.array(struct.unpack(f"<{n}h", raw), dtype=float) / 32768.0
    dur = n / sr
    # RMS per 120ms window, hop 20ms (smooth)
    hop = int(sr * 0.020)
    win_samp = int(sr * WIN)
    rms = []
    for i in range(0, n - win_samp, hop):
        seg = samp[i:i+win_samp]
        rms.append(float(np.sqrt((seg**2).mean())))
    rms = np.array(rms)
    mx = rms.max() if rms.max() > 0 else 1.0
    # map ke frame 24fps: tiap frame ambil RMS window terdekat
    nframes = int(dur * FPS) + 1
    states = []
    for f in range(nframes):
        t = f / FPS
        idx = int(t / 0.020)
        r = rms[min(idx, len(rms)-1)] / mx if len(rms) else 0
        if r > 0.40:
            states.append(2)
        elif r > 0.15:
            states.append(1)
        else:
            states.append(0)
    return dur, states

result = {}
for n in range(1, 19):
    dur, states = analyze(f"{WORK}/p4audio/b{n:02d}.wav")
    result[str(n)] = {"dur": round(dur, 3), "mouth": states}
    o = sum(1 for s in states if s > 0)
    print(f"b{n:02d}: {dur:.2f}s, frames={len(states)}, mulut_buka={o} ({100*o//max(1,len(states))}%)")

with open(f"{WORK}/mouth_sync.json", "w") as f:
    json.dump(result, f)
print("mouth_sync.json OK")
