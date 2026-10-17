#!/usr/bin/env python3
"""Orkestrator Greenbrier 2026-10-14: tunggu base -> final assembly (temp+verifikasi)
-> move -> potong 3 shorts -> verifikasi. Log tiap langkah. Resume-safe."""
import subprocess, os, sys, time, shutil

BASE = "/home/hatch/workspace/youtube-otomatis/mystery-en"
LOG = "/tmp/mystery-final-20261015.log"
TGL = "2026-10-14"
EXPECTED = 622.0  # durasi audio voiceover (detik)

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def main():
    os.chdir(BASE)
    base = f"video/{TGL}-base.mp4"
    tmp = f"video/{TGL}-tmp.mp4"
    final = f"video/{TGL}.mp4"

    # 1. tunggu base (maks 3 jam)
    log("menunggu base video...")
    for _ in range(360):
        if os.path.exists(base) and dur(base) > 600:
            break
        time.sleep(30)
    else:
        log("GAGAL: base tidak muncul 3 jam"); sys.exit(1)
    db = dur(base)
    log(f"base OK: {db:.1f}s")

    # 2. final assembly ke TEMP (patuh aturan: tidak timpa final sebelum verifikasi)
    if not (os.path.exists(final) and abs(dur(final) - EXPECTED) < 10):
        log("final assembly -> temp...")
        r = subprocess.run(["python3", f"final_assembly_{TGL}.py", base, tmp],
                           capture_output=True, text=True)
        log(r.stdout[-500:] if r.stdout else "")
        if r.returncode != 0:
            log(f"GAGAL final assembly: {r.stderr[-1500:]}"); sys.exit(1)
        dt = dur(tmp)
        log(f"temp durasi {dt:.1f}s (expected ~{EXPECTED:.0f}s)")
        if abs(dt - EXPECTED) >= 10:
            log(f"GAGAL verifikasi durasi temp (|{dt:.1f}-{EXPECTED:.0f}|>=10) — final TIDAK ditimpa")
            sys.exit(1)
        shutil.move(tmp, final)
        log(f"OK: {final} ({dt:.1f}s)")
    else:
        log(f"final sudah ada & valid, lewati")

    # 3. potong 3 shorts (beat 22/29/42) bila belum ada
    shorts = [(22, "s1"), (29, "s2"), (42, "s3")]
    need = [s for _, s in shorts if not (os.path.exists(f"shorts/{TGL}-{s}.mp4")
                                         and 40 <= dur(f"shorts/{TGL}-{s}.mp4") <= 50)]
    if need:
        log(f"potong shorts {need}...")
        r = subprocess.run(["python3", "potong_shorts_today.py", final,
                            f"audio/{TGL}.durations.txt", "shorts", TGL, "22", "29", "42"],
                           capture_output=True, text=True)
        log(r.stdout[-800:] if r.stdout else "")
        if r.returncode != 0:
            log(f"GAGAL potong shorts: {r.stderr[-1500:]}"); sys.exit(1)
    for _, s in shorts:
        p = f"shorts/{TGL}-{s}.mp4"
        d = dur(p)
        log(f"{p}: {d:.1f}s {'OK' if 40 <= d <= 50 else 'SALAH DURASI!'}")
    log("SELESAI SEMUA")

if __name__ == "__main__":
    main()
