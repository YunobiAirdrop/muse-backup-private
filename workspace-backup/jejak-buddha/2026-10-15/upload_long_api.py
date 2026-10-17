#!/usr/bin/env python3
"""Upload LONG Jejak Buddha 2026-10-15 ("Pertapaan dan Jalan Tengah") via YouTube Data API v3.
Terjadwal tayang Jumat 2026-10-16 19:00 WIB.
Channel WAJIB terverifikasi: UC1PNEzhOmAH08p75vwp7n0A (@JejakBuddha).
AI disclosure TIDAK didukung API -> pending centang manual di Studio.
Thumbnail custom via API kemungkinan 403 (belum verifikasi HP) -> catat, jangan retry.
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

EXPECTED_ID = "UC1PNEzhOmAH08p75vwp7n0A"
D = "/home/hatch/workspace/jejak-buddha/2026-10-15"
VIDEO = os.path.join(D, "jejak-buddha-2026-10-15-upload.mp4")
THUMB = os.path.join(D, "thumbnail.png")
OUT = os.path.join(D, "upload-hasil-long.json")

TITLE = "Ternyata Menyiksa Diri Tak Membawa Pencerahan"
DESCRIPTION = """Enam tahun ia menyiksa tubuhnya sendiri hingga tinggal tulang berbalut kulit. Di ambang kematian di tepi Sungai Neranjara, Pangeran Siddhartha justru menemukan jalan yang mengubah sejarah manusia.

Kisah masyhur dari riwayat hidup Sang Buddha: setelah berguru pada Alara Kalama dan Uddaka Ramaputta, Siddhartha bertapa keras enam tahun di hutan Uruvela hingga nyaris mati. Sebuah kenangan masa kecil di bawah pohon jambu menyadarkannya bahwa penyiksaan diri tidak membawa pencerahan. Persembahan nasi susu Sujata memulihkan tubuhnya, dan ia pun menemukan Jalan Tengah — tidak tenggelam dalam kenikmatan, tidak menyiksa diri — sebelum melangkah ke Bodh Gaya. Saya menuturkannya kembali dengan penuh takzim untuk kita renungkan bersama.

Bab:
00:00 Nyaris mati di tepi Sungai Neranjara
02:00 Dua guru besar telah dilampaui
03:02 Enam tahun menyiksa tubuh
04:05 Kenangan di bawah pohon jambu
05:14 Nasi susu Sujata memulihkan tubuh
06:28 Menemukan Jalan Tengah
07:29 Tekad di bawah pohon Bodhi
08:31 Hikmah Jalan Tengah untuk kita

Kalau kisah ini menyentuh hati Anda, subscribe channel Jejak Buddha dan nyalakan loncengnya. Tulis di komentar, bagian mana dari kisah ini yang paling menyentuh hati Anda?

Video terkait: Pelepasan Agung — https://youtu.be/6txAzECV24s

Semoga semua makhluk berbahagia. — Jejak Buddha

#buddha #kebijaksanaan #jejakbuddha #sejarahbuddha #inspirasi #foryou

Atribusi footage (Wikimedia Commons): "Golden hour rays break through mist on Diana Creek" (CC0); "Yogyakarta Sunrise, One" (CC BY 4.0); "From the mountain high, the forest stretches like a green ocean" (CC BY 4.0); "Forest Pokljuka and river Nadiža - Slovenia" (CC BY 3.0); "Timelapse of amazing lotus flowers in pond" (CC BY 3.0); "Statue of Buddha" (CC BY 3.0); "Flowing stream with rippling water in Bidibidi" (CC BY-SA 4.0); "Vairochana the Cosmic Buddha" (CC BY-SA 3.0); "Borobudur 2019" & "Borobudur 2019 02" (CC BY-SA 4.0). Sisanya CC0/Domain publik."""
TAGS = ["pertapaan buddha", "jalan tengah", "sang buddha", "siddhartha gautama",
        "jejak buddha", "kisah buddha", "cerita buddha", "sujata",
        "sungai neranjara", "bodh gaya", "alara kalama", "uddaka ramaputta",
        "agama buddha", "sejarah buddha", "kebijaksanaan buddha",
        "kisah inspiratif", "renungan spiritual", "middle way", "enam tahun bertapa"]
PUBLISH_AT = "2026-10-16T12:00:00.000Z"  # Jumat 19:00 WIB


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
