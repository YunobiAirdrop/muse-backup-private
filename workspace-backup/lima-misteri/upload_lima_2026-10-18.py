#!/usr/bin/env python3
"""Upload 1 long + 3 shorts Lima Misteri 2026-10-18 via YouTube Data API (yt-growth).
- Verifikasi channel: title mengandung 'Lima Misteri' + id UCQ0vHTsTqVeYy3zLno6pVfQ
- Cek duplikat judul di upload terbaru channel sebelum upload
- private + publishAt 2026-10-19T12:00:00.000Z (slot tayang BESOK 19:00 WIB)
- Set thumbnail per video
- Gagal karena limit harian -> tulis antrean retry JSON (jangan retry)
Penggunaan: python3 upload_lima_2026-10-18.py
"""
import json, os, sys, datetime

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

SLUG = "lima-misteri"
CHANNEL_ID = "UCQ0vHTsTqVeYy3zLno6pVfQ"
PUBLISH_AT = "2026-10-19T12:00:00.000Z"  # = 2026-10-19 19:00 WIB
BASE = "/home/hatch/workspace/lima-misteri"
RQ = "/home/hatch/workspace/youtube-otomatis/retry-queue"

AFF_A = "🛒 Tumbler 900ml Stainless Steel (Rp63.990): https://s.shopee.co.id/3LRIpS3LxT"
AFF_B = "🛒 Gamis Mewah Karina Dress Ceruty (Rp125.000): https://s.shopee.co.id/5LCND9LjY8"
AFF_NOTE = "(Link di atas adalah link afiliasi — saya dapat komisi kecil tanpa biaya tambahan untuk kamu.)"
DISCLAIMER = "⚠️ Video ini adalah penceritaan ulang orisinal atas peristiwa yang terdokumentasi, diilustrasikan dengan gambar buatan AI. Bukan footage asli peristiwa."

LONG_JUDUL = "Hantu Brown Lady 1936, Nomor 1 Paling Seram | Lima Misteri"
LONG_DESK = (
    "Hari ini saya merangkum 5 kejadian misterius yang terdokumentasi tapi belum punya jawaban tuntas — "
    "dari hantu Brown Lady yang tertangkap kamera di Raynham Hall tahun 1936, Slenderman si legenda urban yang lahir "
    "dari internet tapi korbannya nyata, Kastil Bhangarh di India yang dilarang dimasuki pemerintah setelah matahari "
    "terbenam, cahaya misterius Marfa yang muncul di gurun Texas lebih dari seratus tahun, sampai insiden Roswell 1947 "
    "yang ditutup-tutupi militer Amerika.\n\n"
    "Jujur, yang nomor 1 paling bikin saya merinding — fotografernya bahkan tidak melihat apa-apa saat memotret, "
    "tapi ada sosok di dalam fotonya. Kalau kalian, nomor berapa yang paling nggak masuk akal? Tulis di komentar ya.\n\n"
    "🛒 Rekomendasi hari ini:\n" + AFF_A + "\n" + AFF_B + "\n" + AFF_NOTE + "\n\n"
    + DISCLAIMER + "\n\n"
    "#misteri #penampakan #kejadiananeh #indonesia #butifyourcloseyoureyesmeme #foryou #brownlady #roswell"
)

VIDEOS = [
    {
        "key": "long",
        "file": f"{BASE}/video/video-2026-10-18-final.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-18-long.jpg",
        "judul": LONG_JUDUL,
        "deskripsi": LONG_DESK,
        "tags": ["misteri", "penampakan", "kejadian aneh", "brown lady", "raynham hall",
                 "slenderman", "bhangarh", "marfa lights", "roswell", "lima misteri", "indonesia"],
    },
    {
        "key": "s1",
        "file": f"{BASE}/shorts/2026-10-18-s1.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-18-s1.jpg",
        "judul": "Hantu Ini Tertangkap Kamera Tahun 1936 | Lima Misteri #butifyourcloseyoureyesmeme #shorts #misteri #penampakan #foryou",
        "deskripsi": "Tonton versi lengkapnya: __LONG_URL__\n" + AFF_A + "\n" + AFF_NOTE + "\n" + DISCLAIMER,
        "tags": ["brown lady", "raynham hall", "hantu", "penampakan", "misteri", "lima misteri", "shorts"],
    },
    {
        "key": "s2",
        "file": f"{BASE}/shorts/2026-10-18-s2.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-18-s2.jpg",
        "judul": "Legenda Urban Ini Lahir dari Internet | Lima Misteri #butifyourcloseyoureyesmeme #shorts #misteri #legenda #foryou",
        "deskripsi": "Tonton versi lengkapnya: __LONG_URL__\n" + AFF_B + "\n" + AFF_NOTE + "\n" + DISCLAIMER,
        "tags": ["slenderman", "legenda urban", "misteri", "lima misteri", "shorts"],
    },
    {
        "key": "s3",
        "file": f"{BASE}/shorts/2026-10-18-s3.mp4",
        "thumb": f"{BASE}/thumbnail-2026-10-18-s3.jpg",
        "judul": "Kastil Ini Dilarang Dimasuki Malam Hari | Lima Misteri #butifyourcloseyoureyesmeme #shorts #misteri #kastilhantu #foryou",
        "deskripsi": "Tonton versi lengkapnya: __LONG_URL__\n" + AFF_A + "\n" + AFF_NOTE + "\n" + DISCLAIMER,
        "tags": ["kastil bhangarh", "kastil berhantu", "misteri india", "lima misteri", "shorts"],
    },
]


def is_limit_error(text):
    t = text.lower()
    return any(k in t for k in ["upload limit", "daily limit", "batas upload",
                                "quotaexceeded", "uploadlimitexceeded", "rateLimitExceeded"])


def tulis_antrean(video, sebab, long_url=None):
    instr = os.path.join(BASE, "upload-instruksi-2026-10-18.md")
    url_note = long_url or "(URL long, isi setelah long terupload)"
    with open(instr, "w") as f:
        f.write(f"# Instruksi upload Lima Misteri 2026-10-18 (channel: Lima Misteri / {CHANNEL_ID})\n\n")
        f.write("Slot tayang: 2026-10-19 19:00 WIB (publishAt 2026-10-19T12:00:00.000Z), privacy private.\n")
        f.write("AI disclosure: WAJIB centang 'Altered content' di YouTube Studio setelah upload.\n\n")
        for v in VIDEOS:
            f.write(f"## {v['key']}\nJudul: {v['judul']}\nFile: {v['file']}\nThumbnail: {v['thumb']}\nTags: {', '.join(v['tags'])}\n\nDeskripsi:\n{v['deskripsi'].replace('__LONG_URL__', url_note)}\n\n---\n")
    entry = {
        "channel": "Lima Misteri",
        "video_path": video["file"],
        "instruksi_path": instr,
        "slot_target": "2026-10-19 19:00 WIB",
        "gagal_pada": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00"),
        "sebab": sebab,
    }
    os.makedirs(RQ, exist_ok=True)
    qp = os.path.join(RQ, f"lima-misteri-2026-10-18-{video['key']}.json")
    json.dump(entry, open(qp, "w"), indent=1, ensure_ascii=False)
    print(f"ANTREAN ditulis: {qp}", flush=True)


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
        raise RuntimeError(f"INIT {r.status_code}: {r.text[:500]}")
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
                raise RuntimeError(f"CHUNK {rr.status_code}: {rr.text[:500]}")
    if not vid:
        raise RuntimeError("upload tidak selesai tanpa error jelas")
    if os.path.exists(meta["thumb"]):
        with open(meta["thumb"], "rb") as tf:
            tr = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                        params={"videoId": vid},
                        data=tf.read(),
                        headers={"Content-Type": "image/jpeg"}, timeout=60)
        print("thumbnail:", tr.status_code)
    return vid


def main():
    assert len(LONG_JUDUL) <= 60, f"judul long {len(LONG_JUDUL)} > 60"
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
    pending = list(VIDEOS)
    try:
        v = pending[0]
        print("upload LONG:", v["judul"][:60], flush=True)
        vid_long = upload_one(s, v)
        hasil["long"] = vid_long
        print("LONG OK:", vid_long, "https://youtu.be/" + vid_long, flush=True)
        long_url = "https://youtu.be/" + vid_long
        for vv in pending[1:]:
            vv = dict(vv)
            vv["deskripsi"] = vv["deskripsi"].replace("__LONG_URL__", long_url)
            print(f"upload SHORT {vv['key']}:", vv["judul"][:60], flush=True)
            vid = upload_one(s, vv)
            hasil[vv["key"]] = vid
            print(f"SHORT {vv['key']} OK:", vid, "https://youtu.be/" + vid, flush=True)
    except Exception as e:
        sebab = str(e)
        print("UPLOAD GAGAL:", sebab[:300], flush=True)
        done_keys = set(hasil.keys())
        if is_limit_error(sebab):
            long_url = ("https://youtu.be/" + hasil["long"]) if "long" in hasil else None
            for v in pending:
                if v["key"] not in done_keys:
                    tulis_antrean(v, "Batas upload harian telah tercapai: " + sebab[:200], long_url)
            print("LIMIT HARIAN: antrean ditulis, TIDAK retry.", flush=True)
        else:
            raise
    out = os.path.join(BASE, "upload-hasil-2026-10-18.json")
    json.dump({"publishAt": PUBLISH_AT, **hasil,
               "judul": {v["key"]: v["judul"] for v in VIDEOS if v["key"] in hasil}},
              open(out, "w"), indent=1, ensure_ascii=False)
    print("HASIL:", json.dumps(hasil, ensure_ascii=False))


if __name__ == "__main__":
    main()
