#!/usr/bin/env python3
"""Upload 1 long + 3 shorts Lima Misteri 2026-10-14 via YouTube Data API (yt-growth).
- Verifikasi channel: title mengandung 'Lima Misteri' + id UCQ0vHTsTqVeYy3zLno6pVfQ
- Cek duplikat judul di upload terbaru channel sebelum upload
- private + publishAt 2026-10-15T19:00:00+07:00 (slot tayang HARI INI 19:00 WIB, salvage)
- Set thumbnail per video
- Long dulu (URL untuk deskripsi shorts)
Penggunaan: python3 upload_lima_2026-10-14.py
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

SLUG = "lima-misteri"
CHANNEL_ID = "UCQ0vHTsTqVeYy3zLno6pVfQ"
PUBLISH_AT = "2026-10-15T12:00:00.000Z"  # = 2026-10-15 19:00 WIB
BASE = "/home/hatch/workspace/lima-misteri"

AFF_A = "🛒 Alat Rebus Telur Elektrik (Rp155.100): https://s.shopee.co.id/40gzb1K9Fi"
AFF_B = "🛒 New Balance Fresh Foam X 2025 (Rp850.000): https://s.shopee.co.id/1gJ4onHvca"
AFF_NOTE = "(Link di atas adalah link afiliasi — saya dapat komisi kecil tanpa biaya tambahan untuk kamu. Terima kasih sudah mendukung channel ini.)"
DISCLAIMER = "⚠️ Video ini adalah penceritaan ulang orisinal atas peristiwa yang terdokumentasi, diilustrasikan dengan gambar buatan AI. Bukan footage asli peristiwa."

VIDEOS = [
    {
        "file": f"{BASE}/video/video-2026-10-14-final.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-14-long.jpg",
        "judul": "5 Misteri Ini Bikin Saya Merinding, Nomor 1 Paling Tak Terjelaskan | Lima Misteri",
        "deskripsi": (
            "Hari ini saya merangkum 5 kejadian aneh yang terdokumentasi tapi belum punya jawaban tuntas — "
            "dari Teke Teke si hantu tanpa kaki di Jepang, Resurrection Mary penunggu jalanan Chicago, "
            "kota Centralia yang terbakar dari dalam sejak 1962, cahaya misterius Hessdalen di Norwegia, "
            "sampai batu-batu yang berjalan sendiri di Death Valley.\n\n"
            "Jujur, yang nomor 1 paling bikin saya merinding. Kalau kalian, nomor berapa yang paling nggak masuk akal? Tulis di komentar ya.\n\n"
            "🛒 Rekomendasi hari ini:\n" + AFF_A + "\n" + AFF_B + "\n" + AFF_NOTE + "\n\n"
            + DISCLAIMER + "\n\n"
            "#misteri #penampakan #kejadiananeh #indonesia #foryou #teketeke #batuberjalan"
        ),
        "tags": ["misteri", "penampakan", "kejadian aneh", "teke teke", "resurrection mary",
                 "centralia", "cahaya hessdalen", "batu berjalan racetrack", "lima misteri", "indonesia"],
    },
    {
        "file": f"{BASE}/shorts/2026-10-14-s1.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-14-s1.jpg",
        "judul": "Hantu Tanpa Kaki Berlari Lebih Cepat dari Manusia | Lima Misteri #shorts #misteri #hantu #foryou",
        "deskripsi": "Tonton versi lengkapnya: __LONG_URL__\n" + AFF_A + "\n" + DISCLAIMER,
        "tags": ["teke teke", "hantu jepang", "legenda urban", "misteri", "lima misteri", "shorts"],
    },
    {
        "file": f"{BASE}/shorts/2026-10-14-s2.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-14-s2.jpg",
        "judul": "Gadis Bergaun Putih Hilang dari Kursi Belakang Taksi | Lima Misteri #shorts #misteri #hantu #foryou",
        "deskripsi": "Tonton versi lengkapnya: __LONG_URL__\n" + AFF_B + "\n" + DISCLAIMER,
        "tags": ["resurrection mary", "hantu chicago", "penampakan", "misteri", "lima misteri", "shorts"],
    },
    {
        "file": f"{BASE}/shorts/2026-10-14-s3.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-14-s3.jpg",
        "judul": "Kota Ini Terbakar dari Dalam Sejak 1962 | Lima Misteri #shorts #misteri #kotahantu #foryou",
        "deskripsi": "Tonton versi lengkapnya: __LONG_URL__\n" + AFF_A + "\n" + DISCLAIMER,
        "tags": ["centralia", "kota hantu", "kebakaran tambang", "misteri", "lima misteri", "shorts"],
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
    if os.path.exists(meta["thumb"]):
        with open(meta["thumb"], "rb") as tf:
            tr = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                        params={"videoId": vid},
                        data=tf.read(),
                        headers={"Content-Type": "image/jpeg"}, timeout=60)
        print("thumbnail:", tr.status_code)
    return vid

def main():
    for v in VIDEOS:
        if not os.path.exists(v["file"]):
            sys.exit(f"BATAL: file video belum ada: {v['file']}")
    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet,contentDetails"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"])
    if "Lima Misteri" not in ch["snippet"]["title"] or ch["id"] != CHANNEL_ID:
        sys.exit("BATAL: channel aktif bukan Lima Misteri!")
    upl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    r = s.get("https://www.googleapis.com/youtube/v3/playlistItems",
              params={"playlistId": upl, "part": "snippet", "maxResults": 15}, timeout=30)
    r.raise_for_status()
    judul_ada = [it["snippet"]["title"] for it in r.json().get("items", [])]
    for v in VIDEOS:
        if v["judul"] in judul_ada:
            sys.exit(f"BATAL: judul sudah ada di channel (duplikat): {v['judul']}")
    print("cek duplikat OK: 4 judul belum ada")
    hasil = {}
    v = VIDEOS[0]
    print("upload LONG:", v["judul"][:60], flush=True)
    vid_long = upload_one(s, v)
    hasil["long"] = vid_long
    print("LONG OK:", vid_long, "https://youtu.be/" + vid_long, flush=True)
    long_url = "https://youtu.be/" + vid_long
    for i, vv in enumerate(VIDEOS[1:], start=1):
        vv = dict(vv)
        vv["deskripsi"] = vv["deskripsi"].replace("__LONG_URL__", long_url)
        print(f"upload SHORT {i}:", vv["judul"][:60], flush=True)
        vid = upload_one(s, vv)
        hasil[f"short{i}"] = vid
        print(f"SHORT {i} OK:", vid, "https://youtu.be/" + vid, flush=True)
    out = os.path.join(BASE, "upload-hasil-2026-10-14.json")
    json.dump({"publishAt": PUBLISH_AT, **hasil,
               "judul": {k: VIDEOS[0 if k == "long" else int(k[-1])]["judul"]
                         for k in hasil}}, open(out, "w"), indent=1, ensure_ascii=False)
    print("HASIL:", json.dumps(hasil, ensure_ascii=False))

if __name__ == "__main__":
    main()
