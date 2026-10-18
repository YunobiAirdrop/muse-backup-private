#!/usr/bin/env python3
"""Upload LONG horor 2026-10-17 (Sumur Tua yang Memanggil Nama) via YouTube Data API v3.
- Channel WAJIB "Kisah Horor" UCUEHu-nQXxGuru5Bviy4DKQ (assert)
- privacy=private + publishAt terjadwal Senin 2026-10-19 19:00 WIB
- AI disclosure TIDAK didukung API -> manual via Studio (lihat upload-instruksi)
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

SLUG = "horor"
VIDEO = "/home/hatch/workspace/horor-otomatis/video/2026-10-17.mp4"
THUMB = "/home/hatch/workspace/horor-otomatis/thumbnail-2026-10-17.jpg"

TITLE = "Sumur Tua Ini Memanggil Namaku Tiap Malam"

DESCRIPTION = """Tiap malam jam setengah dua belas, sumur tua di belakang rumah nenek memanggil namaku — dengan suara yang persis seperti suara nenekku yang sudah meninggal sepuluh tahun lalu. Tetangga bilang: sekali kau menjawab, kau gantiin yang di dalam.

Raka pulang kampung untuk menjual rumah warisan neneknya di Desa Cikembang. Tapi sumur tua di belakang rumah itu menyimpan rahasia mengerikan: airnya hitam pekat, tidak pernah surut, dan tiap malam memanggil nama orang dengan suara orang yang paling mereka sayangi. Tiga orang sudah hilang tanpa jejak. Neneknya sendiri meninggalkan diary berisi peringatan terakhir. Dan tetangga yang memperingatkannya... ternyata sudah meninggal tujuh tahun lalu.

Jujur, bagian diary nenek yang bikin saya merinding — tulisan tangannya yang gemetar. Kalau menurut saya, yang paling seram bukan hantunya, tapi rasa penasaran yang bikin orang menjawab.

Kalau kamu suka cerita horor kayak gini, subscribe channel Kisah Horor — tiap hari ada cerita baru yang bikin merinding.

🎬 Tonton juga: CCTV Apartemen Ini Rekam Sosok Aneh Tiap Jam 02.47 https://youtu.be/U6F-BbZ1Lns — sama-sama soal "panggilan dari yang tak kasat mata", tapi versi apartemen.

Rekomendasi:
🛒 ThePods Gen 4 TWS Bluetooth ANC - Rp339.520: https://s.shopee.co.id/8AWYYltgKB
🛒 Puzzle Kayu Edukasi Montessori - Rp21.890: https://s.shopee.co.id/9pemZScr45

#horor #ceritahoror #misteri #foryou #sumurtua #misterisumur"""

TAGS = ["cerita horor", "sumur tua", "hantu indonesia", "misteri indonesia",
        "cerita seram", "kisah horor", "urban legend", "tempat angker"]

# Terjadwal Senin 2026-10-19 19:00 WIB = 2026-10-19 12:00 UTC
PUBLISH_AT = "2026-10-19T12:00:00.000Z"

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
