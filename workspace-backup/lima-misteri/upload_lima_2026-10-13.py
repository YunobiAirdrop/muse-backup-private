#!/usr/bin/env python3
"""Upload 1 long + 3 shorts Lima Misteri 2026-10-13 via YouTube Data API (yt-growth).
- Verifikasi channel: title mengandung 'Lima Misteri' + id UCQ0vHTsTqVeYy3zLno6pVfQ
- Cek duplikat judul di upload terbaru channel sebelum upload
- private + publishAt 2026-10-14T19:00:00+07:00 (jadwal BESOK 19:00 WIB)
- Set thumbnail per video
Penggunaan: python3 upload_lima_2026-10-13.py
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

SLUG = "lima-misteri"
CHANNEL_ID = "UCQ0vHTsTqVeYy3zLno6pVfQ"
PUBLISH_AT = "2026-10-14T12:00:00.000Z"  # = 2026-10-14 19:00 WIB
BASE = "/home/hatch/workspace/lima-misteri"

AFF_TWS = "🛒 ThePods Gen 4 TWS Bluetooth ANC (Rp339.520): https://s.shopee.co.id/8AWYYltgKB"
AFF_KENTANG = "🛒 Kentang Mustofa Renyah Gurih (Rp33.740): https://s.shopee.co.id/7KxRazSZaC"
AFF_NOTE = "(Link di atas adalah link afiliasi — saya dapat komisi kecil tanpa biaya tambahan untuk kamu. Terima kasih sudah mendukung channel ini.)"
DISCLAIMER = "⚠️ Video ini adalah penceritaan ulang orisinal atas peristiwa yang terdokumentasi, diilustrasikan dengan gambar buatan AI. Bukan footage asli peristiwa."

VIDEOS = [
    {
        "file": f"{BASE}/video/video-2026-10-13-final.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-13-long.jpg",
        "judul": "5 Kejadian Aneh Ini Bikin Saya Merinding, Nomor 1 Tak Terjelaskan | Lima Misteri",
        "deskripsi": (
            "Hari ini saya merangkum 5 kejadian aneh yang terdokumentasi tapi belum punya jawaban tuntas — "
            "dari hantu Bell Witch yang meneror satu keluarga di Tennessee, Pulau Boneka di Meksiko, "
            "Chupacabra si penghisap darah, insiden UFO Rendlesham 1980, sampai hujan darah di Kerala, India.\n\n"
            "Jujur, yang nomor 1 paling bikin saya merinding. Kalau kalian, nomor berapa yang paling nggak masuk akal? Tulis di komentar ya.\n\n"
            "🛒 Rekomendasi hari ini:\n" + AFF_TWS + "\n" + AFF_KENTANG + "\n" + AFF_NOTE + "\n\n"
            + DISCLAIMER + "\n\n"
            "#misteri #penampakan #kejadiananeh #indonesia #foryou #bellwitch #hujandarahkerala"
        ),
        "tags": ["misteri", "penampakan", "kejadian aneh", "bell witch", "pulau boneka",
                 "chupacabra", "ufo rendlesham", "hujan darah", "lima misteri", "indonesia"],
    },
    {
        "file": f"{BASE}/shorts/2026-10-13-s1.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-13-s1.jpg",
        "judul": "Diteror Hantu 4 Tahun, Ayahnya Tewas Diracun | Lima Misteri #shorts #misteri #hantu #foryou",
        "deskripsi": "Tonton versi lengkapnya: __LONG_URL__\n" + AFF_TWS + "\n" + DISCLAIMER,
        "tags": ["misteri", "hantu", "bell witch", "shorts", "lima misteri"],
    },
    {
        "file": f"{BASE}/shorts/2026-10-13-s2.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-13-s2.jpg",
        "judul": "Ratusan Boneka Tergantung Menatap dari Kegelapan | Lima Misteri #shorts #misteri #boneka #foryou",
        "deskripsi": "Tonton versi lengkapnya: __LONG_URL__\n" + AFF_KENTANG + "\n" + DISCLAIMER,
        "tags": ["misteri", "pulau boneka", "tempat angker", "shorts", "lima misteri"],
    },
    {
        "file": f"{BASE}/shorts/2026-10-13-s3.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-13-s3.jpg",
        "judul": "Ternak Mati Kehabisan Darah, 3 Lubang di Leher | Lima Misteri #shorts #misteri #chupacabra #foryou",
        "deskripsi": "Tonton versi lengkapnya: __LONG_URL__\n" + AFF_TWS + "\n" + DISCLAIMER,
        "tags": ["misteri", "chupacabra", "legenda urban", "shorts", "lima misteri"],
    },
]

def upload_one(s, meta):
    size = os.path.getsize(meta["file"])
    body = {
        "snippet": {"title": meta["judul"], "description": meta["deskripsi"],
                    "tags": meta["tags"], "categoryId": "27"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)}, timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:500]); sys.exit(10)
    up_url = r.headers["Location"]
    chunk = 8 * 1024 * 1024
    vid = None
    with open(meta["file"], "rb") as f:
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
                break
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
                print(f"... {offset}/{size} bytes", flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:500]); sys.exit(11)
    if not vid:
        sys.exit("upload tidak selesai tanpa error jelas")
    # thumbnail
    if os.path.exists(meta["thumb"]):
        with open(meta["thumb"], "rb") as tf:
            tr = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                        params={"videoId": vid},
                        data=tf.read(),
                        headers={"Content-Type": "image/jpeg"}, timeout=60)
        print("thumbnail:", tr.status_code)
    return vid

def main():
    s = api_session(SLUG)
    # 1. verifikasi channel aktif
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet,contentDetails"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"])
    if "Lima Misteri" not in ch["snippet"]["title"] or ch["id"] != CHANNEL_ID:
        sys.exit("BATAL: channel aktif bukan Lima Misteri!")
    # 2. cek duplikat: 15 upload terbaru
    upl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    r = s.get("https://www.googleapis.com/youtube/v3/playlistItems",
              params={"playlistId": upl, "part": "snippet", "maxResults": 15}, timeout=30)
    r.raise_for_status()
    judul_ada = [it["snippet"]["title"] for it in r.json().get("items", [])]
    for v in VIDEOS:
        if v["judul"] in judul_ada:
            sys.exit(f"BATAL: judul sudah ada di channel (duplikat): {v['judul']}")
    print("cek duplikat OK: 4 judul belum ada")
    # 3. upload long dulu (untuk URL di deskripsi shorts)
    hasil = {}
    v = VIDEOS[0]
    print("upload LONG:", v["judul"][:60], flush=True)
    vid_long = upload_one(s, v)
    hasil["long"] = vid_long
    print("LONG OK:", vid_long, "https://youtu.be/" + vid_long, flush=True)
    long_url = "https://youtu.be/" + vid_long
    # 4. upload 3 shorts
    for i, vv in enumerate(VIDEOS[1:], start=1):
        vv = dict(vv)
        vv["deskripsi"] = vv["deskripsi"].replace("__LONG_URL__", long_url)
        print(f"upload SHORT {i}:", vv["judul"][:60], flush=True)
        vid = upload_one(s, vv)
        hasil[f"short{i}"] = vid
        print(f"SHORT {i} OK:", vid, "https://youtu.be/" + vid, flush=True)
    out = os.path.join(BASE, "upload-hasil-2026-10-13.json")
    json.dump({"publishAt": PUBLISH_AT, **hasil,
               "judul": {k: VIDEOS[0 if k == 'long' else int(k[-1])]["judul"]
                         for k in hasil}}, open(out, "w"), indent=1, ensure_ascii=False)
    print("HASIL:", json.dumps(hasil, ensure_ascii=False))

if __name__ == "__main__":
    main()
