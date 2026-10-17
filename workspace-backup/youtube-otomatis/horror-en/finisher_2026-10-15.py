#!/usr/bin/env python3
"""Finisher rantai produksi horror-en 2026-10-15 (bank long 'The Dashcam on Route 17').
Menunggu rakit_2026-10-14.py selesai (video/2026-10-14.mp4), lalu:
sisip_bumper -> potong_shorts -> verifikasi -> update riwayat-topik + memory log.
Semua handoff via FILE (tahan kalau run sudah selesai saat ini rampung).
Jalankan di background: nohup python3 finisher_2026-10-15.py >> finisher-2026-10-15.log 2>&1 &
"""
import os, sys, time, json, subprocess

WS = "/home/hatch/workspace/youtube-otomatis/horror-en"
VIDEO = f"{WS}/video/2026-10-14.mp4"
TIMEOUT = 7 * 3600
POLL = 120
t0 = time.time()

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def memolog(msg):
    with open(os.path.expanduser("~/memory/2026-10-15.md"), "a") as f:
        f.write(msg + "\n")

log("finisher mulai — menunggu video/2026-10-14.mp4")
video_ok = False
while time.time() - t0 < TIMEOUT:
    if os.path.exists(VIDEO) and dur(VIDEO) > 400:
        video_ok = True
        break
    time.sleep(POLL)

if not video_ok:
    msg = ("## horror-en finisher 2026-10-15: GAGAL — video/2026-10-14.mp4 tidak jadi dalam 7 jam "
           "(antrean ffmpeg-queue). Rakit mungkin masih jalan; run besok lanjutkan manual.")
    log(msg); memolog(msg)
    sys.exit(2)

d = dur(VIDEO)
log(f"video OK: {d:.1f} dtk — sisip bumper...")
r = subprocess.run([sys.executable, f"{WS}/sisip_bumper_2026-10-14.py"],
                   capture_output=True, text=True, cwd=WS)
log("sisip_bumper rc=%d %s" % (r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""))
if r.returncode != 0:
    msg = f"## horror-en finisher: sisip_bumper GAGAL rc={r.returncode}: {r.stderr[-300:]}"
    log(msg); memolog(msg); sys.exit(3)

log("potong 3 shorts...")
r = subprocess.run([sys.executable, f"{WS}/potong_shorts_2026-10-14.py"],
                   capture_output=True, text=True, cwd=WS)
log("potong_shorts rc=%d" % r.returncode)
if r.returncode != 0:
    msg = f"## horror-en finisher: potong_shorts GAGAL rc={r.returncode}: {r.stderr[-300:]}"
    log(msg); memolog(msg); sys.exit(4)

shorts = []
for s in ("s1", "s2", "s3"):
    p = f"{WS}/shorts/2026-10-14-{s}.mp4"
    shorts.append((s, round(dur(p), 1) if os.path.exists(p) else 0))
log(f"shorts: {shorts}")

rp = f"{WS}/riwayat-topik.json"
riw = json.load(open(rp))
for e in riw:
    if e.get("judul") == "The Dashcam on Route 17":
        e["status"] = (f"produksi-selesai {time.strftime('%Y-%m-%d %H:%M')} — video {d:.0f} dtk "
                       f"(bumper tengah), shorts {shorts}, thumbnail-2026-10-14.jpg; "
                       f"bank slot 2026-10-17 07:00 WIB")
json.dump(riw, open(rp, "w"), ensure_ascii=False, indent=1)

thumb = os.path.exists(f"{WS}/thumbnail-2026-10-14.jpg")
msg = (f"## horror-en finisher 2026-10-15: SELESAI — 'The Dashcam on Route 17' {d:.0f} dtk "
       f"(bumper tersisip), 3 shorts {shorts}, thumbnail={'OK' if thumb else 'BELUM'}. "
       f"Bank slot 2026-10-17 07:00 WIB; run besok (hari LONG) tinggal upload.")
log(msg); memolog(msg)
log("FINISHER DONE")
