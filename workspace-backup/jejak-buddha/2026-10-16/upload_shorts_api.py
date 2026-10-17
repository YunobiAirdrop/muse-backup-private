#!/usr/bin/env python3
"""Upload 3 SHORTS Jejak Buddha (potongan long 2026-10-15 "Pertapaan dan Jalan Tengah") via YouTube Data API v3.
Terjadwal tayang Sabtu 2026-10-17 19:00/19:05/19:10 WIB.
Channel WAJIB terverifikasi: UC1PNEzhOmAH08p75vwp7n0A (@JejakBuddha).
Judul: hook + hashtag di AKHIR JUDUL, ditutup #foryou. Deskripsi: tanpa hashtag.
AI disclosure TIDAK didukung API -> pending centang manual di Studio.
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

EXPECTED_ID = "UC1PNEzhOmAH08p75vwp7n0A"
D = "/home/hatch/workspace/jejak-buddha/2026-10-16"
OUT = os.path.join(D, "upload-hasil-shorts.json")
LONG_URL = "https://youtu.be/sTwtnVn1pro"
ATRIBUSI = "Footage: Wikimedia Commons (CC0 / CC BY / CC BY-SA, lisensi aman komersial)."

SHORTS = [
    {
        "file": "short1-enam-tahun.mp4",
        "title": "6 Tahun Menyiksa Diri, Tapi Pencerahan Tak Kunjung Datang #shorts #buddha #kebijaksanaan #foryou",
        "description": (
            "Enam tahun ia menyiksa tubuhnya sendiri hingga tinggal tulang berbalut kulit. "
            "Di tepi Sungai Neranjara, Pangeran Siddhartha justru menemukan jalan yang mengubah sejarah manusia.\n\n"
            "Pernahkah Anda berusaha sekeras mungkin untuk sesuatu, tetapi hasilnya justru semakin jauh? "
            "Tulis pendapat Anda di kolom komentar.\n\n"
            f"Tonton kisah lengkapnya: {LONG_URL}\n\n"
            "Kalau kisah ini menyentuh hati Anda, subscribe channel Jejak Buddha dan nyalakan loncengnya.\n\n"
            f"{ATRIBUSI}\nSemoga semua makhluk berbahagia. \u2014 Jejak Buddha"
        ),
        "tags": ["buddha", "siddhartha gautama", "kisah buddha", "jejak buddha",
                 "pertapaan buddha", "renungan spiritual", "kisah inspiratif"],
        "publish_at": "2026-10-17T12:00:00.000Z",  # 19:00 WIB
    },
    {
        "file": "short2-senar-kecapi.mp4",
        "title": "Senar Kecapi yang Terlalu Kencang Pasti Putus #shorts #buddha #kebijaksanaan #foryou",
        "description": (
            "Senar kecapi yang dipasang terlalu kencang akan putus; yang terlalu kendur tidak berbunyi. "
            "Begitu pula jalan menuju pembebasan \u2014 Siddhartha menemukan Jalan Tengah: "
            "tidak tenggelam dalam kenikmatan, tidak menyiksa diri.\n\n"
            f"Tonton kisah lengkapnya: {LONG_URL}\n\n"
            "Kalau kisah ini menyentuh hati Anda, subscribe channel Jejak Buddha. "
            "Tulis di komentar, bagian mana yang paling menyentuh hati Anda?\n\n"
            f"{ATRIBUSI}\nSemoga semua makhluk berbahagia. \u2014 Jejak Buddha"
        ),
        "tags": ["jalan tengah", "buddha", "siddhartha gautama", "kisah buddha",
                 "jejak buddha", "kebijaksanaan buddha", "renungan spiritual"],
        "publish_at": "2026-10-17T12:05:00.000Z",  # 19:05 WIB
    },
    {
        "file": "short3-ambang-kematian.mp4",
        "title": "Di Ambang Kematian, Sebuah Kenangan Menyelamatkannya #shorts #buddha #kebijaksanaan #foryou",
        "description": (
            "Tubuhnya sudah tak kuat lagi; ia hampir tenggelam di Sungai Neranjara. "
            "Di ambang kematian, sebuah kenangan masa kecil di bawah pohon jambu menyadarkannya: "
            "mungkinkah jalan pencerahan justru ada di sana, bukan pada penyiksaan diri?\n\n"
            f"Tonton kisah lengkapnya: {LONG_URL}\n\n"
            "Subscribe Jejak Buddha untuk kisah penuh hikmah lainnya. "
            "Tulis di komentar, bagian mana yang paling menyentuh hati Anda?\n\n"
            f"{ATRIBUSI}\nSemoga semua makhluk berbahagia. \u2014 Jejak Buddha"
        ),
        "tags": ["sungai neranjara", "buddha", "siddhartha gautama", "kisah buddha",
                 "jejak buddha", "kisah inspiratif", "renungan spiritual"],
        "publish_at": "2026-10-17T12:10:00.000Z",  # 19:10 WIB
    },
]


def upload_one(s, path, title, description, tags, publish_at):
    body = {
        "snippet": {"title": title, "description": description, "tags": tags,
                    "categoryId": "27", "defaultLanguage": "id"},
        "status": {"privacyStatus": "private", "publishAt": publish_at,
                   "selfDeclaredMadeForKids": False},
    }
    size = os.path.getsize(path)
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)}, timeout=60)
    if r.status_code not in (200, 201):
        return {"ok": False, "stage": "init", "status": r.status_code,
                "body": r.text[:400]}
    up_url = r.headers["Location"]
    chunk = 8 * 1024 * 1024
    vid = None
    with open(path, "rb") as f:
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
                return {"ok": False, "stage": "chunk", "status": rr.status_code,
                        "body": rr.text[:400]}
    if not vid:
        return {"ok": False, "stage": "eof", "body": "upload tidak selesai"}
    video_id = vid["id"]
    vr = s.get("https://www.googleapis.com/youtube/v3/videos",
               params={"id": video_id, "part": "snippet,status"},
               timeout=30)
    vr.raise_for_status()
    v = vr.json()["items"][0]
    return {"ok": True, "id": video_id, "url": "https://youtu.be/" + video_id,
            "title": title, "publishAt": publish_at,
            "privacy": v["status"]["privacyStatus"],
            "scheduled": v["status"].get("publishAt")}


def main():
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

    hasil = []
    for sh in SHORTS:
        path = os.path.join(D, sh["file"])
        assert os.path.exists(path), f"video tidak ada: {path}"
        print("UPLOAD:", sh["file"], flush=True)
        res = upload_one(s, path, sh["title"], sh["description"],
                         sh["tags"], sh["publish_at"])
        res["file"] = sh["file"]
        hasil.append(res)
        print(json.dumps(res, ensure_ascii=False), flush=True)
        if not res["ok"]:
            break
    with open(OUT, "w") as f:
        json.dump(hasil, f, ensure_ascii=False, indent=1)
    print("HASIL TERSIMPAN:", OUT)


if __name__ == "__main__":
    main()
