#!/usr/bin/env python3
"""Upload video horor 2026-10-10 via YouTube Data API v3 (resumable).
AI disclosure TIDAK didukung API -> cek manual via Studio/browser task setelahnya.
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

SLUG = "horor"
VIDEO = "/home/hatch/workspace/horor-otomatis/video/2026-10-10-youtube.mp4"
THUMB = "/home/hatch/workspace/horor-otomatis/thumbnail-2026-10-10.jpg"

TITLE = "Suster Ngesot Itu Nyuruh Aku Gantian Jaga Shift!"
DESCRIPTION = """Malam pertama jaga shift di rumah sakit tua yang mau tutup, Dimas diganggu suster tanpa kaki yang katanya meninggal 20 tahun lalu. Tapi ternyata suster itu masih "jaga shift"... dan dia menyelamatkan seorang pasien dari kesalahan dosis obat. Sampai akhirnya Dimas menemukan satu nama di daftar korban kebakaran 2004 yang bikin darahnya berhenti mengalir: namanya sendiri. Cerita ini bikin saya mikir ulang soal siapa yang sebenarnya masih hidup.
Kalau kamu suka cerita horor kayak gini, subscribe channel Kisah Horor — tiap hari ada cerita baru yang bikin merinding.
Rekomendasi:
🛒 ThePods Gen 4 TWS Bluetooth ANC - Rp339.520: https://s.shopee.co.id/8AWYYltgKB
🛒 Puzzle Kayu Edukasi Montessori - Rp21.890: https://s.shopee.co.id/9pemZScr45
Subscribe channel Kisah Horor untuk cerita horor tiap hari.
#horor #ceritahoror #misteri #susterngesot #rumahsakitangker"""
TAGS = ["cerita horor", "hantu indonesia", "suster ngesot", "rumah sakit angker", "kisah horor"]
# Terjadwal 2026-10-12 19:00 WIB = 2026-10-12 12:00 UTC
PUBLISH_AT = "2026-10-12T12:00:00.000Z"

def main():
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
                # thumbnail
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
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                else:
                    offset = end + 1
                print(f"  {offset}/{size}...", flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:300]); sys.exit(11)

if __name__ == "__main__":
    main()
