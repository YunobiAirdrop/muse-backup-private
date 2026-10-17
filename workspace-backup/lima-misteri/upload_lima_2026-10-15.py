#!/usr/bin/env python3
"""Upload 1 long + 3 shorts Lima Misteri 2026-10-15 via YouTube Data API (yt-growth).
- Verifikasi channel: title mengandung 'Lima Misteri' + id UCQ0vHTsTqVeYy3zLno6pVfQ
- Cek duplikat judul di upload terbaru channel sebelum upload
- private + publishAt 2026-10-16T19:00:00+07:00 (slot tayang BESOK 19:00 WIB)
- Set thumbnail per video
Penggunaan: python3 upload_lima_2026-10-15.py
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

SLUG = "lima-misteri"
CHANNEL_ID = "UCQ0vHTsTqVeYy3zLno6pVfQ"
PUBLISH_AT = "2026-10-16T12:00:00.000Z"  # = 2026-10-16 19:00 WIB
BASE = "/home/hatch/workspace/lima-misteri"

AFF_A = "🛒 New Balance Fuelcell Rebel V5 (Rp850.000): https://s.shopee.co.id/6VOKZgYrb7"
AFF_B = "🛒 Spion Koso Lipat Universal Motor (Rp59.999): https://s.shopee.co.id/3qNZOxWSZe"
AFF_NOTE = "(Link di atas adalah link afiliasi — saya dapat komisi kecil tanpa biaya tambahan untuk kamu. Terima kasih sudah mendukung channel ini.)"
DISCLAIMER = "⚠️ Video ini adalah penceritaan ulang orisinal atas peristiwa yang terdokumentasi, diilustrasikan dengan gambar buatan AI. Bukan footage asli peristiwa."

VIDEOS = [
    {
        "file": f"{BASE}/video/video-2026-10-15-final.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-15-long.jpg",
        "judul": "Kapal Berhantu Ini Bikin Tamu Kabur Tengah Malam, Nomor 1 Paling Seram | Lima Misteri",
        "deskripsi": (
            "Hari ini saya merangkum 5 kejadian aneh yang terdokumentasi tapi belum punya jawaban tuntas — "
            "dari kapal Queen Mary yang disebut paling berhantu di dunia, Spring-heeled Jack si manusia melompat "
            "misterius di London, pulau Poveglia yang dilarang dimasuki di Italia, benda jatuh dari langit di "
            "Kecksburg 1965, sampai air terjun darah di Antartika.\n\n"
            "Jujur, yang nomor 1 paling bikin saya merinding — ratusan saksi lintas generasi melaporkan hal yang sama. "
            "Kalau kalian, nomor berapa yang paling nggak masuk akal? Tulis di komentar ya.\n\n"
            "🛒 Rekomendasi hari ini:\n" + AFF_A + "\n" + AFF_B + "\n" + AFF_NOTE + "\n\n"
            + DISCLAIMER + "\n\n"
            "#misteri #penampakan #kejadiananeh #indonesia #foryou #queenmary #springheeledjack"
        ),
        "tags": ["misteri", "penampakan", "kejadian aneh", "queen mary", "spring-heeled jack",
                 "pulau poveglia", "insiden kecksburg", "blood falls", "lima misteri", "indonesia"],
    },
    {
        "file": f"{BASE}/shorts/2026-10-15-s1.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-15-s1.jpg",
        "judul": "Kapal Ini Disebut Paling Berhantu di Dunia | Lima Misteri #shorts #misteri #hantu #foryou",
        "deskripsi": "Tonton versi lengkapnya: __LONG_URL__\n" + AFF_A + "\n" + DISCLAIMER,
        "tags": ["queen mary", "kapal hantu", "penampakan", "misteri", "lima misteri", "shorts"],
    },
    {
        "file": f"{BASE}/shorts/2026-10-15-s2.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-15-s2.jpg",
        "judul": "Manusia Ini Melompat Setinggi Atap Rumah | Lima Misteri #shorts #misteri #legenda #foryou",
        "deskripsi": "Tonton versi lengkapnya: __LONG_URL__\n" + AFF_B + "\n" + DISCLAIMER,
        "tags": ["spring-heeled jack", "legenda urban", "misteri london", "lima misteri", "shorts"],
    },
    {
        "file": f"{BASE}/shorts/2026-10-15-s3.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-15-s3.jpg",
        "judul": "Pulau Ini Dilarang Dimasuki Manusia | Lima Misteri #shorts #misteri #pulauhantu #foryou",
        "deskripsi": "Tonton versi lengkapnya: __LONG_URL__\n" + AFF_A + "\n" + DISCLAIMER,
        "tags": ["pulau poveglia", "pulau berhantu", "misteri italia", "lima misteri", "shorts"],
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
    out = os.path.join(BASE, "upload-hasil-2026-10-15.json")
    json.dump({"publishAt": PUBLISH_AT, **hasil,
               "judul": {k: VIDEOS[0 if k == "long" else int(k[-1])]["judul"]
                         for k in hasil}}, open(out, "w"), indent=1, ensure_ascii=False)
    print("HASIL:", json.dumps(hasil, ensure_ascii=False))

if __name__ == "__main__":
    main()
