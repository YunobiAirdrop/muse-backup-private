#!/usr/bin/env python3
"""Rakit Tiny Builders Episode 1: Mini Diesel Water Pump (long 15 mnt + 3 shorts)."""
import os, subprocess, random, wave, math
import numpy as np

FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/miniatur-ai"
KLIP = f"{BASE}/klip/long15"
NORM = f"{BASE}/klip/long15/norm-final"
SFX = f"{BASE}/sfx-real"
WAVDIR = f"{BASE}/sfx-real/wav441"
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
os.makedirs(NORM, exist_ok=True)
os.makedirs(WAVDIR, exist_ok=True)

def run(cmd, tag=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAIL[{tag}]:", r.stderr[-800:])
        raise SystemExit(1)
    return r

def durasi(path):
    r = subprocess.run([FQ, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    hh, mm, ss = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return hh * 3600 + mm * 60 + ss

# ---------- 0. Preflight (OpenMontage: fail fast sebelum produksi) ----------
print("== preflight ==")
assert os.path.isfile(FQ) and os.access(FQ, os.X_OK), f"ffmpeg-queue tidak ada: {FQ}"
assert os.path.isdir(KLIP), f"folder klip tidak ada: {KLIP}"
hilang = [f"{KLIP}/clip-{i:02d}.mp4" for i in range(1, 88)
          if not os.path.isfile(f"{KLIP}/clip-{i:02d}.mp4")]
assert not hilang, f"{len(hilang)} klip hilang, contoh: {hilang[:3]}"
assert os.path.isdir(SFX), f"folder SFX tidak ada: {SFX}"
assert os.path.isfile(FONT), f"font tidak ada: {FONT}"
print(f"  OK: 87 klip + SFX + font + ffmpeg-queue siap")

# ---------- 1. Trim plan (deterministik) ----------
random.seed(7)
trims = {i: round(random.uniform(0, 0.6), 2) for i in range(1, 88)}
dur = {i: round(10.0 - trims[i], 2) for i in range(1, 88)}
starts = {}
t = 4.0  # title card 4 dtk
for i in range(1, 88):
    starts[i] = round(t, 2)
    t += dur[i]
TOTAL = round(t, 2)
print(f"Total durasi video (title+87 klip): {TOTAL:.1f} dtk = {TOTAL/60:.2f} mnt")
assert TOTAL < 900, "MELEBIHI 15 MENIT!"

# ---------- 2. Title card ----------
print("== title card ==")
run([FQ, "-y", "-ss", "3", "-i", f"{KLIP}/clip-01.mp4", "-frames:v", "1",
     "-vf", "scale=1280:720", f"{BASE}/title-bg.png"], "title-bg")
dt1 = f"drawtext=fontfile={FONT}:text='TINY BUILDERS':fontsize=110:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-70"
dt2 = f"drawtext=fontfile={FONT}:text='The Mini Diesel Water Pump':fontsize=46:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2+60"
run([FQ, "-y", "-loop", "1", "-t", "4", "-i", f"{BASE}/title-bg.png",
     "-vf", f"{dt1},{dt2},fade=t=in:st=0:d=0.5,fps=30",
     "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-an",
     f"{BASE}/title.mp4"], "title")

# ---------- 3. Normalisasi klip (trim + 1280x720 + 30fps + no audio) ----------
print("== normalisasi 87 klip ==")
for i in range(1, 88):
    nn = f"{i:02d}"
    out = f"{NORM}/norm-{nn}.mp4"
    if os.path.exists(out):
        continue
    run([FQ, "-y", "-i", f"{KLIP}/clip-{nn}.mp4", "-t", str(dur[i]),
         "-vf", "scale=1280:720,fps=30", "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", out], f"norm-{nn}")
    if i % 15 == 0:
        print(f"  ... {i}/87")

# ---------- 4. Concat ----------
print("== concat ==")
with open(f"{BASE}/concat-ep1.txt", "w") as f:
    f.write(f"file '{BASE}/title.mp4'\n")
    for i in range(1, 88):
        f.write(f"file '{NORM}/norm-{i:02d}.mp4'\n")
run([FQ, "-y", "-f", "concat", "-safe", "0", "-i", f"{BASE}/concat-ep1.txt",
     "-c", "copy", f"{BASE}/ep1-silent.mp4"], "concat")
# gate: durasi concat harus ≈ rencana TOTAL (toleransi 5 dtk)
d_concat = durasi(f"{BASE}/ep1-silent.mp4")
print(f"  concat: {d_concat:.1f}s vs rencana {TOTAL:.1f}s")
assert abs(d_concat - TOTAL) < 5, f"CONCAT MELESET: {d_concat:.1f}s vs {TOTAL:.1f}s"

# ---------- 5. Film grain ----------
print("== film grain ==")
run([FQ, "-y", "-i", f"{BASE}/ep1-silent.mp4",
     "-vf", "noise=alls=6:allf=t",
     "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-an",
     f"{BASE}/ep1-grain.mp4"], "grain")

# ---------- 6. Decode SFX ke WAV 44100 mono ----------
print("== decode SFX ==")
needed = ["wind-soft", "birds-ambience", "rooster-crow", "chicken-cluck-1",
          "chicken-cluck-2", "cow-moo-1", "cow-moo-2", "crow-caw",
          "tractor-engine", "brick-place-1", "brick-place-2", "brick-place-3",
          "shovel-dig-1", "shovel-dig-2", "shovel-dig-3", "cement-mix",
          "trowel-scrape", "paint-brush", "metal-clink", "wrench",
          "valve-squeak", "diesel-engine-start", "diesel-engine-idle",
          "water-gush", "water-trickle", "water-splash-1", "water-splash-2"]
for n in needed:
    out = f"{WAVDIR}/{n}.wav"
    if os.path.exists(out):
        continue
    run([FQ, "-y", "-i", f"{SFX}/{n}.mp3", "-ar", "44100", "-ac", "1",
         "-c:a", "pcm_s16le", out], f"wav-{n}")

def load_wav(name):
    with wave.open(f"{WAVDIR}/{name}.wav", "rb") as w:
        n = w.getnframes()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    return a

S = {n: load_wav(n) for n in needed}
SR = 44100
N = int(TOTAL * SR)
mix = np.zeros(N, dtype=np.float64)

def place(name, start_sec, gain=0.5, dur_sec=None, fade_ms=15):
    a = S[name]
    if dur_sec is not None:
        a = a[:int(dur_sec * SR)]
    n = len(a)
    s0 = int(start_sec * SR)
    if s0 >= N:
        return
    n = min(n, N - s0)
    seg = a[:n] * gain
    f = int(fade_ms * SR / 1000)
    f = min(f, n // 2)
    if f > 0:
        ramp = np.linspace(0, 1, f)
        seg[:f] *= ramp
        seg[-f:] *= ramp[::-1]
    mix[s0:s0 + n] += seg

def loop_bed(name, gain):
    a = S[name]
    pos = 0.0
    while pos < TOTAL:
        place(name, pos, gain)
        pos += len(a) / SR - 0.5  # slight overlap

def clip_end(i):
    return starts[i] + dur[i]

print("== susun SFX ==")
# Bed: angin lembut sepanjang video
loop_bed("wind-soft", 0.06)
# Act 1 (klip 1-12): farm life
place("birds-ambience", starts[1], 0.14, dur_sec=30)
place("chicken-cluck-1", starts[1] + 3, 0.45)
place("rooster-crow", starts[2] + 2, 0.5)
place("chicken-cluck-2", starts[2] + 5, 0.4)
place("cow-moo-1", starts[3] + 2, 0.5)
place("crow-caw", starts[5] + 3, 0.4)
# Act 2 (13-27): persiapan
place("tractor-engine", starts[13], 0.5, dur_sec=clip_end(14) - starts[13])
for k, off in enumerate([2, 5, 8]):
    place("brick-place-1", starts[14] + off, 0.5, dur_sec=2.5)
for i in (17, 18, 19, 20, 21):
    place(f"shovel-dig-{(i % 3) + 1}", starts[i] + 1, 0.5, dur_sec=6)
place("cement-mix", starts[22], 0.45, dur_sec=clip_end(23) - starts[22])
# Act 3 (28-45): bangun tangki
for i in range(28, 36):
    place(f"brick-place-{(i % 3) + 1}", starts[i] + 2, 0.5, dur_sec=4)
place("trowel-scrape", starts[36], 0.45, dur_sec=clip_end(37) - starts[36])
place("paint-brush", starts[39], 0.5, dur_sec=clip_end(41) - starts[39])
# Act 4 (46-60): mesin + pompa
for i in (48, 49, 50):
    place("metal-clink", starts[i] + 2, 0.5)
place("brick-place-2", starts[52] + 2, 0.55)
place("wrench", starts[53] + 2, 0.55)
place("brick-place-3", starts[54] + 2, 0.55)
# Act 5 (61-72): irigasi
place("shovel-dig-1", starts[63] + 1, 0.5, dur_sec=6)
place("water-trickle", starts[67], 0.4, dur_sec=dur[67])
place("valve-squeak", starts[69] + 2, 0.5)
# Act 6 (73-87): klimaks + ending
place("diesel-engine-start", starts[73] + 1, 0.75)
place("diesel-engine-idle", starts[74] + 2, 0.55,
      dur_sec=min(22.8, clip_end(78) - starts[74] - 2))
place("water-gush", starts[78], 0.6, dur_sec=clip_end(80) - starts[78])
place("water-splash-1", starts[78] + 3, 0.5)
place("water-splash-2", starts[79] + 1, 0.5)
place("water-trickle", starts[81], 0.4, dur_sec=clip_end(83) - starts[81])
place("chicken-cluck-1", starts[84] + 2, 0.4)
place("cow-moo-2", starts[86] + 3, 0.5)
place("birds-ambience", starts[85], 0.12, dur_sec=15)

# Normalisasi peak -3dB + fade-out 3 dtk
peak = np.max(np.abs(mix))
print(f"peak sebelum normalisasi: {peak:.3f}")
mix *= (0.7079 / max(peak, 1e-6))
fo = int(3 * SR)
ramp = np.linspace(1, 0, fo)
mix[-fo:] *= ramp
with wave.open(f"{BASE}/sfx-ep1.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print("SFX WAV ditulis.")

# ---------- 7. Mux final ----------
print("== mux final ==")
run([FQ, "-y", "-i", f"{BASE}/ep1-grain.mp4", "-i", f"{BASE}/sfx-ep1.wav",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
     "-movflags", "+faststart", "-shortest",
     f"{BASE}/tiny-builders-ep1-long.mp4"], "mux")

# ---------- 8. Verifikasi ----------
r = run([FQ, "-i", f"{BASE}/tiny-builders-ep1-long.mp4"], "probe")
info = r.stderr
import re
m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
hh, mm, ss = int(m.group(1)), int(m.group(2)), float(m.group(3))
final_dur = hh * 3600 + mm * 60 + ss
has_audio = "Audio:" in info
print(f"FINAL: durasi={final_dur:.1f}s ({final_dur/60:.2f} mnt), audio={'YA' if has_audio else 'TIDAK'}")
assert final_dur < 900, "MELEBIHI 15 MENIT!"
assert has_audio, "TIDAK ADA AUDIO!"

# Simpan timestamp untuk shorts
with open(f"{BASE}/ep1-timestamps.txt", "w") as f:
    f.write(f"total={TOTAL:.2f}\n")
    for i in range(1, 88):
        f.write(f"clip{i:02d}={starts[i]:.2f},{dur[i]:.2f}\n")
print("SELESAI LONG.")

# ---------- 9. Production log (OpenMontage: decision_log append-only) ----------
import datetime, json
log_path = f"{BASE}/production-log.jsonl"
entry = {
    "tanggal": datetime.datetime.now().isoformat(timespec="seconds"),
    "episode": "ep1",
    "judul": "The Mini Diesel Water Pump",
    "seed_trim": 7,
    "n_klip": 87,
    "durasi_rencana_s": TOTAL,
    "durasi_final_s": round(final_dur, 1),
    "audio": has_audio,
    "output": "tiny-builders-ep1-long.mp4",
    "grain": "noise=alls=6:allf=t",
    "sfx_dir": SFX,
}
with open(log_path, "a") as f:
    f.write(json.dumps(entry) + "\n")
print(f"production log → {log_path}")
