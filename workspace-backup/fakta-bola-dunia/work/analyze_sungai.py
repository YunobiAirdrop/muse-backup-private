#!/usr/bin/env python3
"""Analisis volume sungai-audio -> mouth_sync_sungai.json (FPS=30)"""
import wave, struct, json
import numpy as np
WORK = "/home/hatch/workspace/fakta-bola-dunia/work"
ADIR = f"{WORK}/sungai-audio"
FPS = 30; WIN = 0.120
ORDER = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 11, 12, 13, 14, 15]
def analyze(path):
    with wave.open(path, "rb") as w:
        sr = w.getframerate(); n = w.getnframes()
        raw = w.readframes(n)
    samp = np.array(struct.unpack(f"<{n}h", raw), dtype=float) / 32768.0
    dur = n / sr
    hop = int(sr * 0.020); win_samp = int(sr * WIN)
    rms = []
    for i in range(0, n - win_samp, hop):
        seg = samp[i:i+win_samp]
        rms.append(float(np.sqrt((seg**2).mean())))
    rms = np.array(rms); mx = rms.max() if rms.max() > 0 else 1.0
    nframes = int(dur * FPS) + 1; states = []
    for f in range(nframes):
        idx = int((f / FPS) / 0.020)
        r = rms[min(idx, len(rms)-1)] / mx if len(rms) else 0
        states.append(2 if r > 0.40 else (1 if r > 0.15 else 0))
    return dur, states
result = {}
for n in ORDER:
    dur, states = analyze(f"{ADIR}/b{n:02d}.wav")
    result[str(n)] = {"dur": round(dur, 3), "mouth": states}
    o = sum(1 for s in states if s > 0)
    print(f"b{n:02d}: {dur:.2f}s, mulut_buka={100*o//max(1,len(states))}%", flush=True)
json.dump(result, open(f"{WORK}/mouth_sync_sungai.json", "w"))
print("mouth_sync_sungai.json OK")
