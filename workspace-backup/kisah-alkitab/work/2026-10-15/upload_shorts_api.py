#!/usr/bin/env python3
"""Upload 3 shorts Kisah Alkitab (dipotong dari long Musa 2026-10-14) via API yt-growth (slug kisahalkitab).
publishAt 2026-10-16 19:00 WIB. Anti-mogok: gagal limit -> antrean retry-queue JSON."""
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
W15 = os.path.expanduser("~/workspace/kisah-alkitab/work/2026-10-15")
QDIR = os.path.expanduser("~/workspace/youtube-otomatis/retry-queue")
PUB = "2026-10-16T12:00:00.000Z"  # BESOK 2026-10-16 19:00 WIB

SHORTS = [
    {
        "file": f"{W15}/shorts/2026-10-15-s1.mp4",
        "title": "TERJEPIT! Laut di Depan, 600 Kereta Firaun di Belakang #shorts #alkitab #musa #foryou",
        "desc": ("Fajar di tepi laut. Di depan: air tanpa ujung. Di belakang: 600 kereta perang Firaun. "
                 "Lebih dari satu juta orang Israel terjepit — dan justru di titik tanpa jalan inilah "
                 "mukjizat terbesar terjadi.\n\n"
                 "Yang membuat saya takjub, Musa berani berkata \"janganlah takut\" justru di saat yang "
                 "paling tidak masuk akal untuk tenang.\n\n"
                 "Menurut kamu, \"laut\" apa yang sedang kamu hadapi hari ini? Tulis di komentar.\n"
                 "Kalau kisah ini menguatkanmu, subscribe channel Kisah Alkitab.\n\n"
                 "Referensi: Keluaran 14. Tonton versi lengkapnya di channel ini."),
    },
    {
        "file": f"{W15}/shorts/2026-10-15-s2.mp4",
        "title": "Laut Berdiri Seperti Tembok di Kanan dan Kiri! #shorts #alkitab #musa #foryou",
        "desc": ("Musa mengulurkan tangannya ke atas laut — dan sepanjang malam Tuhan menguakkan air lewat "
                 "angin timur yang keras. Air laut yang dalam berdiri tegak seperti tembok di kanan dan di kiri. "
                 "Bangsa Israel berjalan di tanah kering di tengah-tengah laut.\n\n"
                 "Yang membuat saya takjub, mukjizat ini terjadi perlahan, semalaman — bukan selalu dalam sekejap. "
                 "Kadang pertolongan Tuhan bekerja diam-diam saat kita sedang gelisah.\n\n"
                 "Menurut kamu, \"laut\" apa yang sedang kamu hadapi hari ini? Tulis di komentar.\n"
                 "Kalau kisah ini menguatkanmu, subscribe channel Kisah Alkitab.\n\n"
                 "Referensi: Keluaran 14. Tonton versi lengkapnya di channel ini."),
    },
    {
        "file": f"{W15}/shorts/2026-10-15-s3.mp4",
        "title": "Saat Tidak Ada Jalan, Tuhan Justru Membelah Laut #shorts #alkitab #renungan #foryou",
        "desc": ("Pelajaran yang saya ambil dari kisah Musa sederhana tetapi dalam: Tuhan tidak selalu "
                 "menyingkirkan laut dari hadapan kita — kadang Ia justru membelahnya tepat di depan mata kita, "
                 "di saat kita sudah tidak bisa berbuat apa-apa lagi.\n\n"
                 "Bangsa Israel tidak membelah laut itu dengan kekuatan mereka; mereka hanya diminta satu hal: "
                 "berangkat dan berjalan maju dengan berani.\n\n"
                 "Menurut kamu, \"laut\" apa yang sedang kamu hadapi hari ini? Tulis di komentar — siapa tahu "
                 "kisah ini menguatkan seseorang yang membacanya.\n"
                 "Kalau kisah ini menyentuh hatimu, subscribe channel Kisah Alkitab dan bagikan video ini.\n\n"
                 "Referensi: Keluaran 14. Tonton versi lengkapnya di channel ini."),
    },
]
TAGS = ["kisah alkitab", "musa", "laut merah", "keluaran 14", "cerita alkitab",
        "renungan kristen", "firman tuhan", "rohani kristen", "mukjizat musa",
        "tokoh alkitab", "perjanjian lama", "iman kristen", "kristen indonesia",
        "bible story indonesia", "shorts", "alkitab"]


def log(msg):
    print(f"[{datetime.now(WIB).strftime('%H:%M:%S')}] {msg}", flush=True)


def queue_retry(video_path, instruksi_path, slot_target, sebab):
    os.makedirs(QDIR, exist_ok=True)
    base = os.path.basename(video_path).replace(".mp4", "")
    qpath = os.path.join(QDIR, f"kisah-alkitab-{base}-2026-10-15.json")
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
    ipath = f"{W15}/upload-instruksi-shorts-2026-10-15.md"
    slot = "2026-10-16 19:00 WIB"
    out = []
    for sh in SHORTS:
        if not os.path.exists(sh["file"]):
            log(f"BATAL: file belum ada: {sh['file']}"); return 2
        log(f"UPLOAD: {sh['title'][:60]}")
        dup = bu.is_duplicate(s, uploads_id, sh["title"])
        if bu.STOP_ALL["stop"]:
            log("STOP: quotaExceeded saat cek duplikat"); return 1
        if dup:
            log("DUP: judul sudah ada — tidak upload dobel")
            out.append({"title": sh["title"][:60], "status": "DUP"}); continue
        meta = {"title": sh["title"], "description": sh["desc"],
                "tags": TAGS, "made_for_kids": False}
        res = bu.upload_video(s, sh["file"], meta, "private", PUB)
        if res == "STOP_QUOTA":
            queue_retry(sh["file"], ipath, slot, "403 quotaExceeded"); return 1
        if res == "SKIP_CHANNEL":
            queue_retry(sh["file"], ipath, slot, "uploadLimitExceeded"); return 1
        if isinstance(res, tuple) and res[0] == "OK":
            vid = res[1]
            log(f"SUKSES: {vid} https://youtu.be/{vid}")
            out.append({"title": sh["title"][:60], "status": "OK", "video_id": vid})
            continue
        log(f"FAIL: {str(res)[:200]}")
        out.append({"title": sh["title"][:60], "status": "FAIL", "info": str(res)[:120]})
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
