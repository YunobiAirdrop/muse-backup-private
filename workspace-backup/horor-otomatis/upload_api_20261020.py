#!/usr/bin/env python3
"""Upload LONG horor 2026-10-20 (Lift yang Berhenti di Lantai yang Tak Ada) via YouTube Data API v3.
- Channel WAJIB "Kisah Horor" UCUEHu-nQXxGuru5Bviy4DKQ (assert) — JANGAN @ceritarakyat862
- privacy=private + publishAt terjadwal Rabu 2026-10-21 19:00 WIB
- AI disclosure TIDAK didukung API -> manual via Studio (lihat upload-instruksi-2026-10-20.md)
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

SLUG = "horor"
VIDEO = "/home/hatch/workspace/horor-otomatis/video/2026-10-20.mp4"
THUMB = "/home/hatch/workspace/horor-otomatis/thumbnail-2026-10-20.jpg"

TITLE = "Lift Ini Berhenti di Lantai yang Tak Ada... Padahal Gedungnya Cuma 12 Lantai!"

DESCRIPTION = """Jam 21.40 malam, Bima lembur sendirian di kantornya. Lift yang ia naiki berhenti sendiri — display digital menyala merah: lantai 13. Padahal gedung itu cuma punya 12 lantai. Di balik pintu lift yang terbuka, ada lorong yang seharusnya tidak ada... dan tiga belas karyawan yang sudah 28 tahun menunggu penumpang pengganti.

Jujur, ini salah satu cerita yang paling bikin saya merinding — bukan karena jumpscare-nya, tapi karena idenya: terjebak di sebuah tempat yang "tidak ada". Buat kalian yang kerja di gedung tua dan sering lembur sendirian... tonton sampai habis, terus tulis di komentar: kalian berani naik lift sendirian malam ini?

Kalau kamu suka cerita horor kayak gini, subscribe channel Kisah Horor — tiap hari ada cerita baru yang bikin merinding.

🎬 Tonton juga: Sumur Tua Ini Memanggil Namaku Tiap Malam https://youtu.be/HyKgoj2Bnuk — sama-sama soal "panggilan dari tempat yang tak kasat mata", tapi versi sumur tua di desa.

Rekomendasi:
Paket Cream JRG Glowing BPOM - Rp76.000: https://s.shopee.co.id/4fwgOHU4Q8
Panci Wajan Cast Iron Pancaguna - Rp364.100: https://s.shopee.co.id/7faHxkFSgS

#horor #ceritahoror #misteri #foryou #liftangker #urbanlegend"""

TAGS = ["cerita horor", "lift angker", "hantu indonesia", "misteri indonesia",
        "cerita seram", "kisah horor", "urban legend", "gedung angker"]

# Terjadwal Rabu 2026-10-21 19:00 WIB = 2026-10-21 12:00 UTC
PUBLISH_AT = "2026-10-21T12:00:00.000Z"

def main():
    for p in (VIDEO, THUMB):
        assert os.path.exists(p) and os.path.getsize(p) > 100000, f"file hilang/kecil: {p}"

    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    assert ch["id"] == "UCUEHu-nQXxGuru5Bviy4DKQ", f"BATAL: channel {ch['id']} bukan Kisah Horor!"
    assert "Kisah Horor" in ch["snippet"]["title"], "BATAL: nama channel bukan Kisah Horor!"

    body = {
        "snippet": {"title": TITLE, "description": DESCRIPTION,
                    "tags": TAGS, "categoryId": "27"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(VIDEO))},
               timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:500]); sys.exit(10)
    up_url = r.headers["Location"]
    print("upload session OK", flush=True)

    size = os.path.getsize(VIDEO)
    chunk = 8 * 1024 * 1024
    with open(VIDEO, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": f"bytes {offset}-{end}/{size}"},
                       timeout=300)
            if rr.status_code in (200, 201):
                vid = rr.json()["id"]
                print("UPLOAD SELESAI:", vid)
                print("URL: https://youtu.be/" + vid)
                with open(THUMB, "rb") as tf:
                    tr = s.post(
                        "https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                        params={"videoId": vid},
                        data=tf.read(),
                        headers={"Content-Type": "image/jpeg"}, timeout=60)
                print("THUMBNAIL:", tr.status_code)
                print(json.dumps({"id": vid, "url": "https://youtu.be/" + vid}))
                return
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                print(f"  {offset}/{size}...", flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:300]); sys.exit(11)

if __name__ == "__main__":
    main()
