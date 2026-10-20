#!/usr/bin/env python3
"""Upload LONG Jejak Buddha 2026-10-20 ("Khotbah pertama di Taman Rusa Isipatana") via YouTube Data API v3.
Terjadwal tayang Rabu 2026-10-21 19:00 WIB.
Channel WAJIB terverifikasi: UC1PNEzhOmAH08p75vwp7n0A (@JejakBuddha).
AI disclosure TIDAK didukung API -> pending centang manual di Studio.
Thumbnail custom via API kemungkinan 403 (belum verifikasi HP) -> catat, jangan retry.
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

EXPECTED_ID = "UC1PNEzhOmAH08p75vwp7n0A"
D = "/home/hatch/workspace/jejak-buddha/2026-10-20"
VIDEO = os.path.join(D, "jejak-buddha-2026-10-20-upload.mp4")
THUMB = os.path.join(D, "thumbnail.png")
OUT = os.path.join(D, "upload-hasil-long.json")

TITLE = "Khotbah Pertama Sang Buddha yang Melahirkan Sebuah Agama"
DESCRIPTION = """Di sebuah taman rusa yang sunyi di Sarnath, lebih dari 2.500 tahun lalu, sebuah roda mulai berputar — Roda Dhamma — dan tidak pernah berhenti hingga hari ini.

Kisah masyhur dari riwayat hidup Sang Buddha: 49 hari setelah pencerahan di Bodh Gaya, Sang Buddha sempat ragu untuk mengajar — hingga permohonan Brahma Sahampati meneguhkan hatinya. Setelah dua gurunya wafat, beliau berjalan kaki ratusan kilometer menuju Isipatana, Taman Rusa di Sarnath. Di sana, kepada lima petapa — Kondanna, Vappa, Bhaddiya, Mahanama, dan Assaji — beliau memutar Roda Dhamma untuk pertama kalinya: menghindari dua ekstrem, menempuh Jalan Tengah, dan menguraikan Empat Kebenaran Mulia beserta Jalan Mulia Berunsur Delapan. Di akhir khotbah itu, Kondanna mencapai pemahaman pertama. Saya menuturkannya kembali dengan penuh takzim untuk kita renungkan bersama.

Bab:
00:00 Khotbah pertama di Taman Rusa
01:01 Empat puluh sembilan hari keheningan
01:51 Permohonan dan keputusan mengajar
02:38 Perjalanan ke Sarnath
03:47 Jalan Tengah
04:46 Empat Kebenaran Mulia
05:49 Sangha pertama lahir
06:34 Harapan dari khotbah pertama

Kalau kisah ini menyentuh hati Anda, subscribe channel Jejak Buddha dan nyalakan loncengnya. Tulis di komentar, bagian mana dari khotbah pertama ini yang paling menyentuh hati Anda?

Video terkait: Pencerahan di bawah pohon Bodhi — https://youtu.be/JDELqvSXPGc

Semoga semua makhluk berbahagia. — Jejak Buddha

#butifyourcloseyoureyesmeme #buddha #khotbahbuddha #sarnath #foryou

Atribusi footage (Wikimedia Commons): "Sacred Serenity at Mahabodhi Temple, Bodhgaya, Bihar" © Rohit Sharma, CC BY-SA 4.0; "Chandavaram buddha stupa 360 degree view" © Arjunaraoc, CC BY-SA 4.0; "Buddhist Monuments - Sanchi Hill" © Biswarup Ganguly, CC BY 3.0; "Drone footage of temple in Chiang Mai, Thailand" © freestockvids, CC BY 3.0; "Borobudur, Java, Indonesia, February 2012" © Mutante, CC BY-SA 3.0; "Ajatsatru Stupa - Rajgir 03" © Sumitsurai, CC BY-SA 4.0; "Statue of Buddha" © youtube.com/user/Editor, CC BY 3.0; "Timelapse of amazing lotus flowers in pond" © Mike Seyfang, CC BY 3.0; "From the mountain high, the forest stretches like a green ocean" © Mathanprasath K, CC BY 4.0; "Vairochana the Cosmic Buddha 720p" © Miamiller, CC BY-SA 3.0; "Borobudur 2019" & "Borobudur 2019 02" © Spasimir Pilev, CC BY-SA 4.0. Sisanya CC0/Domain publik."""
TAGS = ["khotbah pertama buddha", "sarnath", "taman rusa", "isipatana",
        "roda dhamma", "dhammacakkappavattana", "empat kebenaran mulia",
        "jalan mulia berunsur delapan", "jalan tengah", "sang buddha",
        "siddhartha gautama", "kondanna", "lima petapa", "jejak buddha",
        "kisah buddha", "cerita buddha", "agama buddha", "ajaran buddha",
        "kebijaksanaan buddha", "renungan spiritual"]
PUBLISH_AT = "2026-10-21T12:00:00.000Z"  # Rabu 19:00 WIB


def main():
    assert os.path.exists(VIDEO), f"video tidak ada: {VIDEO}"
    s = api_session("jejakbuddha")
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        sys.exit("BATAL: token tidak mengembalikan channel")
    ch = items[0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != EXPECTED_ID:
        sys.exit(f"BATAL: channel aktif {ch['id']} bukan {EXPECTED_ID}")

    body = {
        "snippet": {"title": TITLE, "description": DESCRIPTION, "tags": TAGS,
                    "categoryId": "27", "defaultLanguage": "id"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    size = os.path.getsize(VIDEO)
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)}, timeout=60)
    if r.status_code not in (200, 201):
        res = {"ok": False, "stage": "init", "status": r.status_code,
               "body": r.text[:600]}
        print(json.dumps(res, ensure_ascii=False), flush=True)
        sys.exit(1)
    up_url = r.headers["Location"]
    chunk = 8 * 1024 * 1024
    vid = None
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
                vid = rr.json()
                break
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                    f.seek(offset)
                else:
                    offset = end + 1
            else:
                res = {"ok": False, "stage": "chunk", "status": rr.status_code,
                       "body": rr.text[:600]}
                print(json.dumps(res, ensure_ascii=False), flush=True)
                sys.exit(1)
    if not vid:
        print(json.dumps({"ok": False, "stage": "eof",
                          "body": "upload tidak selesai"}, ensure_ascii=False))
        sys.exit(1)
    video_id = vid["id"]
    print("VIDEO_ID:", video_id, "https://youtu.be/" + video_id, flush=True)

    thumb_ok = False
    if os.path.exists(THUMB):
        with open(THUMB, "rb") as f:
            tr = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                        params={"videoId": video_id}, data=f.read(),
                        headers={"Content-Type": "image/png"}, timeout=120)
        thumb_ok = tr.status_code in (200, 201)
        print("THUMBNAIL:", tr.status_code, "ok=" + str(thumb_ok), flush=True)

    vr = s.get("https://www.googleapis.com/youtube/v3/videos",
               params={"id": video_id,
                       "part": "snippet,status,contentDetails"}, timeout=30)
    vr.raise_for_status()
    v = vr.json()["items"][0]
    res = {"ok": True, "id": video_id, "url": "https://youtu.be/" + video_id,
           "title": TITLE, "publishAt": PUBLISH_AT,
           "privacy": v["status"]["privacyStatus"],
           "scheduled": v["status"].get("publishAt"),
           "thumbnail_ok": thumb_ok,
           "duration": v["contentDetails"]["duration"]}
    with open(OUT, "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False), flush=True)
    print("HASIL TERSIMPAN:", OUT)


if __name__ == "__main__":
    main()
