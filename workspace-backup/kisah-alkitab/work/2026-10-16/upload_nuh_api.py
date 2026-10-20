#!/usr/bin/env python3
"""Upload Kisah Alkitab 2026-10-20 (Nuh long) via API yt-growth (slug kisahalkitab).
Produksi dimulai 2026-10-16, terhenti di rakit; diselesaikan 2026-10-20.
publishAt: 2026-10-21 19:00 WIB. Anti-mogok: limit harian -> antrean retry-queue.
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
W16 = os.path.expanduser("~/workspace/kisah-alkitab/work/2026-10-16")
QDIR = os.path.expanduser("~/workspace/youtube-otomatis/retry-queue")

meta = json.load(open(f"{W16}/upload-meta.json"))
ATRIBUSI = """
Referensi: Kejadian 6-9.
Footage: Wikimedia Commons, lisensi bebas komersial:
- "Waves crashing on rocks off Beach 4, Kalaloch Beach, Washington" (01 & 02) \u00a9 Joe Mabel, CC BY-SA 4.0, via Wikimedia Commons
- "Huge waves-VarnaPort-Bulgaria" \u00a9 Chiro J, CC BY 3.0, via Wikimedia Commons
- "USVI Sequence 01 2 - Palm trees sway gently" \u2014 Public Domain (Government of the U.S. Virgin Islands), via Wikimedia Commons
- "Crashing waves in the San Juan Islands" \u2014 Public Domain, via Wikimedia Commons
- "1938 flood at Atwood" \u2014 CC BY 2.0, via Wikimedia Commons (Orange County Archives)
- "Pigeons at NTR Trust Bhavan" \u2014 CC BY-SA 4.0, via Wikimedia Commons
- "An olive tree grows in Gracie" \u2014 CC BY 4.0, via Wikimedia Commons
- "Grand Canyon National Park: Sunrise on the North Rim" \u2014 Public Domain (NPS), via Wikimedia Commons
- "Grande Ronde Wild and Scenic River" \u2014 Public Domain (US Forest Service), via Wikimedia Commons
- "Lenticular cloud over Longs Peak, Colorado" \u2014 CC0, via Wikimedia Commons"""
LONG_TITLE = meta["judul"]
LONG_DESC = meta["deskripsi"] + "\n" + ATRIBUSI
LONG_TAGS = meta["tags"]
LONG_THUMB = f"{W16}/out/thumbnail.jpg"
LONG_VIDEO = f"{W16}/out/kisah-alkitab-2026-10-16-long.mp4"
LONG_PUB = "2026-10-21T12:00:00.000Z"  # 19:00 WIB 2026-10-21


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
    qpath = os.path.join(QDIR, f"kisah-alkitab-{base}-2026-10-20.json")
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
    ipath = f"{W16}/upload-instruksi-2026-10-20.md"
    slot = "2026-10-21 19:00 WIB"

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
    m = {"title": title, "description": desc, "tags": LONG_TAGS, "made_for_kids": False}
    res = bu.upload_video(s, vpath, m, "private", LONG_PUB)
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
