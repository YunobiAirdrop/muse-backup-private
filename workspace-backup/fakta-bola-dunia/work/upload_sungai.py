#!/usr/bin/env python3
"""Upload shorts Fakta Bola Dunia 2026-10-19 (3 sungai terpanjang) via Data API v3.
Pola: upload_bendera.py. Upload sebagai private + publishAt terjadwal
(Selasa 2026-10-20 19:00 WIB), menunggu approval user 20:00-23:00 WIB.
Exit code: 0 = OK; 20 = batas upload harian (retry-queue, JANGAN retry); 11 = gagal lain.
"""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "fakta-bola-dunia"
FILE = "/home/hatch/workspace/fakta-bola-dunia/output/sungai-terpanjang.mp4"
EXPECTED_CHANNEL_ID = "UCU9QUVkWqqjnEFtrj6QACDA"
EXPECTED_CHANNEL_NAME = "Fakta Bola Dunia"

JUDUL = ("3 Sungai Terpanjang di Dunia! \U0001F30A #butifyourcloseyoureyesmeme "
         "#shorts #faktaunik #sungai #foryou")
DESKRIPSI = (
    "Tiga sungai terpanjang di dunia versi countryball! \U0001F30A\n\n"
    "Sungai Nil di Mesir dan Sungai Amazon di Brasil masih rebutan gelar "
    "sungai terpanjang sedunia sampai sekarang! Amazon memang kalah tipis, "
    "tapi dia punya aliran air paling deras di dunia. Dan dari Indonesia, "
    "Sungai Kapuas di Kalimantan membentang seribu seratus empat belas "
    "kilometer, lebih panjang dari Jakarta ke Surabaya bolak-balik!\n\n"
    "Sungai mana yang paling bikin kamu kaget? Tulis di komentar! "
    "Jangan lupa like dan subscribe biar nggak ketinggalan fakta seru lainnya. \U0001F60E\n\n"
    "#faktaunik #countryball #sungai #shorts #viralindonesia #foryou"
)
TAGS = ["fakta unik", "sungai terpanjang", "sungai nil", "sungai amazon",
        "sungai kapuas", "indonesia", "mesir", "brasil", "countryball",
        "fakta", "shorts", "viral indonesia"]

body = {
    "snippet": {
        "title": JUDUL,
        "description": DESKRIPSI,
        "tags": TAGS,
        "categoryId": "27",
        "defaultLanguage": "id",
    },
    "status": {
        "privacyStatus": "private",
        "publishAt": "2026-10-20T12:00:00.000Z",  # Selasa 19:00 WIB
        "selfDeclaredMadeForKids": False,
    },
}


def main():
    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != EXPECTED_CHANNEL_ID or EXPECTED_CHANNEL_NAME not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Fakta Bola Dunia!")

    size = os.path.getsize(FILE)
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)},
               timeout=60)
    if r.status_code not in (200, 201):
        txt = r.text[:500]
        print("INIT GAGAL:", r.status_code, txt, flush=True)
        if "uploadLimitExceeded" in txt or "dailyLimitExceeded" in txt:
            sys.exit(20)
        sys.exit(11)
    up_url = r.headers["Location"]
    chunk = 8 * 1024 * 1024
    with open(FILE, "rb") as f:
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
                print("UPLOAD SELESAI:", vid["id"], "https://youtu.be/" + vid["id"], flush=True)
                with open("/home/hatch/workspace/fakta-bola-dunia/output/sungai-terpanjang-upload.json", "w") as g:
                    json.dump({"video_id": vid["id"], "slug": "fakta-bola-dunia",
                               "file": FILE, "judul": JUDUL,
                               "uploaded_at": "2026-10-19",
                               "publishAt": "2026-10-20T12:00:00.000Z"}, g, ensure_ascii=False)
                return
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
            else:
                txt = rr.text[:500]
                print("CHUNK GAGAL:", rr.status_code, txt, flush=True)
                if "uploadLimitExceeded" in txt or "dailyLimitExceeded" in txt:
                    sys.exit(20)
                sys.exit(11)
    sys.exit("upload tidak selesai tanpa error jelas")


if __name__ == "__main__":
    main()
