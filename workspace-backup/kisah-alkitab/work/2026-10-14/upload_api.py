#!/usr/bin/env python3
"""Upload Kisah Alkitab 2026-10-14 via API yt-growth (slug kisahalkitab).
Mode: 'long' (Musa long 2026-10-14, publishAt 2026-10-15 19:00 WIB)
Anti-mogok: gagal limit harian -> tulis antrean retry-queue JSON; gagal lain -> laporkan.
"""
import json, os, sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth/hidden_files")
from auth import api_session, YT_BASE
import importlib.util
spec = importlib.util.spec_from_file_location(
    "bu", "/home/hatch/workspace/youtube-otomatis/yt-growth/hidden_files/batch_upload_2026-10-13.py")
bu = importlib.util.module_from_spec(spec); spec.loader.exec_module(bu)

WIB = timezone(timedelta(hours=7))
SLUG = "kisahalkitab"
W14 = os.path.expanduser("~/workspace/kisah-alkitab/work/2026-10-14")
QDIR = os.path.expanduser("~/workspace/youtube-otomatis/retry-queue")

LONG_TITLE = "Terjepit di Tepi Laut, Lalu Air Berdiri Seperti Tembok \u2014 Kisah Musa"
LONG_DESC = """Terjepit di depan laut, dikejar kereta perang Firaun di belakang \u2014 lebih dari satu juta orang Israel tidak punya jalan keluar. Lalu Musa mengangkat tongkatnya, dan laut terbelah: air berdiri seperti tembok di kanan dan kiri. Kisah Keluaran 14, mukjizat terbesar dalam perjalanan bangsa Israel keluar dari Mesir.

Yang membuat saya takjub, Musa berani berkata "janganlah takut" justru di saat yang paling tidak masuk akal untuk tenang. Tidak ada rencana cadangan, tidak ada jalan memutar \u2014 hanya laut di depan dan pedang di belakang.

Pelajaran yang saya ambil: Tuhan tidak selalu menyingkirkan laut dari hadapan kita \u2014 kadang Ia justru membelahnya tepat di depan mata kita, di saat kita sudah tidak bisa berbuat apa-apa lagi. Bangsa Israel tidak membelah laut itu dengan kekuatan mereka; mereka hanya diminta satu hal: berangkat dan berjalan maju dengan berani.

00:00 Terjepit: Laut di Depan, Firaun di Belakang
00:57 Dari Perbudakan Menuju Kebebasan
02:23 Jangan Takut \u2014 Tuhan Akan Berperang Untukmu
04:27 Laut Terbelah & Air Kembali Menelan Mesir
06:13 Hikmah: Saat Tidak Ada Jalan, Tuhan Membuka Jalan

Menurut kamu, "laut" apa yang sedang kamu hadapi hari ini? Tulis di komentar \u2014 siapa tahu kisah ini menguatkan seseorang yang membacanya.

Kalau kisah ini menguatkanmu, subscribe channel Kisah Alkitab dan bagikan video ini. Tonton juga kisah Daniel di gua singa di channel ini \u2014 kisah tentang kesetiaan yang tenang di tengah jebakan.

#kisahalkitab #musa #lautmerah #keluaran14 #ceritaalkitab #renungankristen #alkitab #rohanikristen #firmantuhan #mukjizat #foryou

Referensi: Keluaran 14 (juga Keluaran 15:1-21).
Footage: Wikimedia Commons, lisensi bebas komersial \u2014 atribusi:
- "Waves crashing on rocks off Beach 4, Kalaloch Beach, Washington" \u00a9 Joe Mabel, CC BY-SA 4.0, via Wikimedia Commons
- "Huge waves-VarnaPort-Bulgaria" \u00a9 Chiro J, CC BY 3.0, via Wikimedia Commons
- "USVI Sequence 01 2 - Palm trees sway gently" \u2014 Public Domain (Government of the U.S. Virgin Islands), via Wikimedia Commons"""
LONG_TAGS = ["kisah alkitab", "musa membelah laut merah", "keluaran 14", "cerita alkitab",
             "renungan kristen", "firman tuhan", "rohani kristen", "mukjizat musa",
             "tokoh alkitab", "perjanjian lama", "laut merah terbelah", "iman kristen",
             "renungan harian", "kristen indonesia", "bible story indonesia", "firaun",
             "sepuluh tulah"]
LONG_THUMB = f"{W14}/out/thumbnail.jpg"
LONG_VIDEO = f"{W14}/out/kisah-alkitab-2026-10-14-long.mp4"
LONG_PUB = "2026-10-15T12:00:00.000Z"  # 19:00 WIB 2026-10-15


def log(msg):
    print(f"[{datetime.now(WIB).strftime('%H:%M:%S')}] {msg}", flush=True)


def set_thumbnail(s, video_id, thumb_path):
    try:
        with open(thumb_path, "rb") as f:
            r = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                       params={"videoId": video_id},
                       files={"media": ("thumb.jpg", f, "image/jpeg")}, timeout=120)
        if r.status_code == 200:
            return True
        log(f"thumbnail ditolak ({r.status_code}): {r.text[:120]}")
        return False
    except Exception as e:
        log(f"thumbnail error: {e}")
        return False


def queue_retry(video_path, instruksi_path, slot_target, sebab):
    os.makedirs(QDIR, exist_ok=True)
    base = os.path.basename(video_path).replace(".mp4", "")
    qpath = os.path.join(QDIR, f"kisah-alkitab-{base}-2026-10-14.json")
    q = {"channel": "kisah-alkitab", "video_path": video_path,
         "instruksi_path": instruksi_path,
         "slot_target": slot_target,
         "gagal_pada": datetime.now(WIB).strftime("%Y-%m-%dT%H:%M:%S+07:00"),
         "sebab": sebab}
    json.dump(q, open(qpath, "w"), ensure_ascii=False, indent=1)
    log(f"antrean retry ditulis: {qpath}")
    return qpath


def main():
    ch = bu.get_channel(SLUG)
    if bu.STOP_ALL["stop"]:
        log("STOP: quota habis saat verifikasi channel"); return 2
    if ch is None:
        log("BATAL: verifikasi channel gagal"); return 2
    s, uploads_id = ch

    vpath, title, desc = LONG_VIDEO, LONG_TITLE, LONG_DESC
    ipath = f"{W14}/upload-instruksi-2026-10-14.md"
    slot = "2026-10-15 19:00 WIB"

    if not os.path.exists(vpath):
        log(f"BATAL: video belum ada: {vpath}"); return 2
    log(f"UPLOAD: {title[:60]} (publishAt {LONG_PUB})")
    dup = bu.is_duplicate(s, uploads_id, title)
    if bu.STOP_ALL["stop"]:
        log("STOP: quotaExceeded saat cek duplikat"); return 2
    if dup:
        log("DUP: judul sudah ada di channel — tidak upload dobel")
        print(json.dumps([{"title": title[:60], "status": "DUP", "info": "judul sudah ada"}], ensure_ascii=False))
        return 0
    meta = {"title": title, "description": desc, "tags": LONG_TAGS, "made_for_kids": False}
    res = bu.upload_video(s, vpath, meta, "private", LONG_PUB)
    if res == "STOP_QUOTA":
        queue_retry(vpath, ipath, slot, "403 quotaExceeded"); return 1
    if res == "SKIP_CHANNEL":
        queue_retry(vpath, ipath, slot, "uploadLimitExceeded"); return 1
    if isinstance(res, tuple) and res[0] == "OK":
        vid = res[1]
        log(f"SUKSES: {vid} https://youtu.be/{vid}")
        if os.path.exists(LONG_THUMB):
            set_thumbnail(s, vid, LONG_THUMB)
        print(json.dumps([{"title": title[:60], "status": "OK", "info": vid}],
                         ensure_ascii=False, indent=1))
        return 0
    log(f"FAIL: {str(res)[:200]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
