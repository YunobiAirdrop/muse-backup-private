#!/usr/bin/env python3
"""Finisher Pompeii 2026-10-12: tunggu rakit_pompeii selesai (file final muncul
& durasi >= 480s), potong 3 shorts, lalu upload LONG via API (upload_pompeii_2026-10-12.py).
- Sukses: update upload-terakhir.txt -> long:2026-10-12, catat hasil di upload-2026-10-12.json.
- Gagal upload: tulis antrean retry-queue empires-en-2026-10-12.json (anti-mogok).
AI disclosure TIDAK bisa via API/script ini -> tetap pending, dicatat eksplisit.
"""
import json, os, subprocess, sys, time

BASE = "/home/hatch/workspace/youtube-otomatis/empires-en"
VID = os.path.join(BASE, "video", "pompeii-2026-10-11-upload.mp4")
LOG = os.path.join(BASE, "finisher-pompeii-2026-10-12.log")

def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
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
    # 1. tunggu video final (maks ~8 jam, cek tiap 120 dtk; file harus stabil)
    deadline = time.time() + 8 * 3600
    last_size = -1
    while time.time() < deadline:
        if os.path.exists(VID):
            sz = os.path.getsize(VID)
            if sz == last_size and sz > 10_000_000 and dur(VID) >= 480:
                log(f"Video final OK: {sz} bytes, {dur(VID):.0f}s")
                break
            last_size = sz
        time.sleep(120)
    else:
        log("TIMEOUT: video final tidak kunjung lengkap; finisher berhenti. Rakit mungkin masih jalan — cek /tmp/empires-build.log")
        sys.exit(2)

    # 2. potong 3 shorts (kegagalan shorts tidak menggagalkan upload long)
    env = dict(os.environ)
    env["SHORTS_SPECS"] = "2026-10-12-s1.mp4|4|37,2026-10-12-s2.mp4|226|31,2026-10-12-s3.mp4|318|44"
    r = subprocess.run([sys.executable, os.path.join(BASE, "potong_shorts_pompeii.py")],
                       capture_output=True, text=True, env=env)
    log("Shorts: " + (r.stdout.strip().replace("\n", "; ") or r.stderr[-300:]))

    # 3. upload long via API (2 percobaan, jeda 10 mnt)
    out = ""
    for attempt in (1, 2):
        r = subprocess.run([sys.executable, os.path.join(BASE, "upload_pompeii_2026-10-12.py")],
                           capture_output=True, text=True)
        out = r.stdout + r.stderr
        log(f"Upload percobaan {attempt} rc={r.returncode}: " + out.strip().replace("\n", " | ")[-400:])
        if r.returncode == 0 and "UPLOAD SELESAI" in out:
            break
        time.sleep(600)

    meta_path = os.path.join(BASE, "upload-2026-10-12.json")
    meta = json.load(open(meta_path))
    if "UPLOAD SELESAI" in out:
        vid_id = out.split("UPLOAD SELESAI:")[1].split()[0].strip()
        meta["long"]["status"] = "uploaded & scheduled via API (finisher)"
        meta["long"]["video_id"] = vid_id
        meta["long"]["url"] = f"https://youtu.be/{vid_id}"
        meta["long"]["ai_disclosure"] = "PENDING — wajib centang Altered content via Studio (tidak didukung API)"
        json.dump(meta, open(meta_path, "w"), indent=1, ensure_ascii=False)
        open(os.path.join(BASE, "upload-terakhir.txt"), "w").write("long:2026-10-12")
        log(f"SUKSES upload long: {vid_id} — terjadwal 2026-10-13 07:00 WIB. AI disclosure MASIH PENDING via Studio.")
    else:
        # anti-mogok: antrean watchdog
        queue = {
            "channel": "empires-en",
            "video_path": VID,
            "instruksi_path": os.path.join(BASE, "instruksi-upload-pompeii-2026-10-12.txt"),
            "slot_target": "2026-10-13 07:00 WIB",
            "gagal_pada": time.strftime("%Y-%m-%dT%H:%M:%S+07:00"),
            "sebab": "Upload API finisher gagal 2x: " + out.strip().replace("\n", " ")[-300:],
        }
        qp = "/home/hatch/workspace/youtube-otomatis/retry-queue/empires-en-2026-10-12.json"
        json.dump(queue, open(qp, "w"), indent=1, ensure_ascii=False)
        meta["long"]["status"] = "GAGAL upload via finisher — masuk antrean watchdog " + qp
        json.dump(meta, open(meta_path, "w"), indent=1, ensure_ascii=False)
        log("GAGAL upload long — antrean retry ditulis: " + qp)

if __name__ == "__main__":
    main()
