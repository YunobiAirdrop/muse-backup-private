#!/usr/bin/env python3
"""Upload 3 SHORTS Jejak Buddha (potongan long 2026-10-18 "Pencerahan di bawah pohon Bodhi") via YouTube Data API v3.
Terjadwal tayang Selasa 2026-10-20 19:00/19:05/19:10 WIB.
Channel WAJIB terverifikasi: UC1PNEzhOmAH08p75vwp7n0A (@JejakBuddha).
Judul: hook + hashtag di AKHIR JUDUL, ditutup #foryou. Deskripsi: tanpa hashtag.
AI disclosure TIDAK didukung API -> pending centang manual di Studio.
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

EXPECTED_ID = "UC1PNEzhOmAH08p75vwp7n0A"
D = "/home/hatch/workspace/jejak-buddha/2026-10-19"
OUT = os.path.join(D, "upload-hasil-shorts.json")
LONG_URL = "https://youtu.be/JDELqvSXPGc"
ATRIBUSI = "Footage: Wikimedia Commons (CC0 / CC BY / CC BY-SA, lisensi aman komersial)."

SHORTS = [
    {
        "file": "short1-serangan-mara.mp4",
        "title": "Duduk Tak Bergeming Saat Kegelapan Menyerbu #shorts #buddha #kebijaksanaan #foryou",
        "description": (
            "Langit malam di Bodh Gaya gelap gulita. Pasukan kegelapan yang tak terhitung jumlahnya "
            "menyerbu dari segala arah, membawa panah, tombak, dan teriakan yang mengguncang bumi. "
            "Di tengah semua itu, seorang manusia duduk bersila di bawah pohon beringin. Tidak lari. "
            "Tidak gemetar. Hanya duduk, dengan satu tangan menyentuh tanah.\n\n"
            "Pernahkah Anda berada dalam malam tergelap hidup Anda, ketika semua terasa menyerang sekaligus? "
            "Tulis di kolom komentar, apa yang membuat seseorang tetap tegak di tengah badai seperti itu?\n\n"
            f"Tonton kisah lengkapnya: {LONG_URL}\n\n"
            "Kalau kisah ini menyentuh hati Anda, subscribe channel Jejak Buddha dan nyalakan loncengnya.\n\n"
            f"{ATRIBUSI}\nSemoga semua makhluk berbahagia. \u2014 Jejak Buddha"
        ),
        "tags": ["buddha", "siddhartha gautama", "kisah buddha", "pencerahan buddha",
                 "pohon bodhi", "mara", "jejak buddha", "renungan spiritual"],
        "publish_at": "2026-10-20T12:00:00.000Z",  # 19:00 WIB
    },
    {
        "file": "short2-bhumisparsha.mp4",
        "title": "Senjata Mara Berubah Jadi Bunga Sebelum Menyentuhnya #shorts #buddha #kebijaksanaan #foryou",
        "description": (
            "Mara mengirim tiga putrinya yang jelita untuk menggoda \u2014 Siddhartha tidak bergeming. "
            "Lalu Mara mengerahkan pasukannya yang menyeramkan, dengan gajah-gajah perang dan senjata "
            "yang berkilat, melemparkan panah dan tombak ke arahnya. Konon, semua senjata itu berubah "
            "menjadi untaian bunga sebelum menyentuhnya, dan jatuh lembut di sekitar tempat duduknya.\n\n"
            "Lalu serangan paling licik: keraguan. \u201cSiapa yang menjadi saksimu?\u201d Maka ia "
            "mengulurkan tangan kanannya dan menyentuh bumi \u2014 inilah bhumisparsha. "
            "Bumi berguncang menjadi saksinya. Dan kegelapan pun mundur.\n\n"
            f"Tonton kisah lengkapnya: {LONG_URL}\n\n"
            "Kapan terakhir kali keraguan menyerang Anda? Tulis di kolom komentar. "
            "Subscribe Jejak Buddha untuk kisah penuh hikmah lainnya.\n\n"
            f"{ATRIBUSI}\nSemoga semua makhluk berbahagia. \u2014 Jejak Buddha"
        ),
        "tags": ["bhumisparsha", "mara", "buddha", "pohon bodhi", "bodh gaya",
                 "kisah buddha", "jejak buddha", "renungan spiritual"],
        "publish_at": "2026-10-20T12:05:00.000Z",  # 19:05 WIB
    },
    {
        "file": "short3-tiga-jaga.mp4",
        "title": "Satu Malam, Satu Pohon: Lahirlah Sang Buddha #shorts #buddha #kebijaksanaan #foryou",
        "description": (
            "Pada jaga pertama malam itu, Siddhartha mengingat kembali kehidupan-kehidupannya yang lampau, "
            "satu per satu, dengan jernih. Pada jaga kedua, ia melihat makhluk-makhluk lahir dan meninggal "
            "sesuai perbuatannya masing-masing. Dan pada jaga ketiga, menjelang fajar, ia menembus "
            "kebenaran yang paling dalam: Empat Kebenaran Mulia tersingkap di hadapannya, dan kegelapan "
            "batinnya lenyap untuk selamanya.\n\n"
            "Satu manusia, satu pohon, satu malam \u2014 dan lahirlah kebijaksanaan yang menerangi "
            "jutaan hati hingga hari ini.\n\n"
            f"Tonton kisah lengkapnya: {LONG_URL}\n\n"
            "Bagian mana yang paling menyentuh hati Anda? Tulis di kolom komentar. "
            "Subscribe Jejak Buddha agar tidak ketinggalan kisah penuh hikmah berikutnya.\n\n"
            f"{ATRIBUSI}\nSemoga semua makhluk berbahagia. \u2014 Jejak Buddha"
        ),
        "tags": ["empat kebenaran mulia", "pencerahan buddha", "siddhartha gautama",
                 "kisah buddha", "kebijaksanaan buddha", "jejak buddha", "renungan spiritual"],
        "publish_at": "2026-10-20T12:10:00.000Z",  # 19:10 WIB
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
