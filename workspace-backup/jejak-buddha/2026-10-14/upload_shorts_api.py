#!/usr/bin/env python3
"""Upload 3 SHORTS Jejak Buddha 2026-10-14 via YouTube Data API v3 (resumable).
Dipotong dari long 2026-10-12 'Pelepasan Agung' (https://youtu.be/6txAzECV24s).
Verifikasi channel ID WAJIB sebelum upload.
AI disclosure 'Altered content' TIDAK didukung API -> pending cek via Studio.
"""
import json, os, sys, time

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

EXPECTED_ID = "UC1PNEzhOmAH08p75vwp7n0A"
FULL_URL = "https://youtu.be/6txAzECV24s"
SHORTS = [
    {
        "file": "/home/hatch/workspace/jejak-buddha/2026-10-12/shorts/short1-ambang-kamar.mp4",
        "title": "Berdiri di Ambang Pintu, Tak Sanggup Berpamitan #shorts #buddha #kebijaksanaan #foryou",
        "description": "Malam itu, di ambang kamar istrinya, Pangeran Siddhartha berdiri lama memandangi Putri Yasodhara dan bayi Rahula yang tertidur pulas. Ia ingin menggendong putranya untuk terakhir kalinya, tetapi ia tahu, jika hatinya goyah malam itu juga, ia mungkin tidak akan pernah berangkat selamanya. Tonton kisah lengkap malam keberangkatan agung: " + FULL_URL + " \u2014 Semoga semua makhluk berbahagia. \u2014 Jejak Buddha",
        "publishAt": "2026-10-15T12:00:00.000Z",  # Kamis 15 Okt 19:00 WIB
        "tags": ["siddhartha gautama", "sang buddha", "jejak buddha", "kisah buddha", "pelepasan agung", "yasodhara", "kebijaksanaan buddha", "cerita buddha"],
    },
    {
        "file": "/home/hatch/workspace/jejak-buddha/2026-10-12/shorts/short2-kanthaka.mp4",
        "title": "Tengah Malam Menunggang Kuda Meninggalkan Istana #shorts #buddha #kebijaksanaan #foryou",
        "description": "Tanpa pasukan, tanpa perbekalan mewah. Hanya Siddhartha, kusir setianya Channa, dan kuda putih Kanthaka, menyelinap keluar dari Kapilavastu di bawah cahaya bulan. Malam itu para penjaga istana tertidur lebih lelap dari biasanya, seolah seluruh alam menjaga keberangkatan itu dalam diam. Tonton kisah lengkapnya: " + FULL_URL + " \u2014 Semoga semua makhluk berbahagia. \u2014 Jejak Buddha",
        "publishAt": "2026-10-15T12:05:00.000Z",  # Kamis 15 Okt 19:05 WIB
        "tags": ["siddhartha gautama", "sang buddha", "jejak buddha", "kisah buddha", "pelepasan agung", "kanthaka", "channa", "kebijaksanaan buddha"],
    },
    {
        "file": "/home/hatch/workspace/jejak-buddha/2026-10-12/shorts/short3-potong-rambut.mp4",
        "title": "Rambut Pangeran Dipotong, Lahirlah Seorang Petapa #shorts #buddha #kebijaksanaan #foryou",
        "description": "Di tepi Sungai Anoma, sang pangeran memotong rambut panjangnya, melepas perhiasan dan pakaian kebesarannya, lalu menukar jubah sutranya dengan jubah sederhana seorang pemburu. Sejak detik itu, ia bukan lagi Pangeran Siddhartha dari Kapilavastu. Ia adalah seorang petapa pencari kebenaran, tanpa rumah dan tanpa harta. Tonton kisah lengkapnya: " + FULL_URL + " \u2014 Semoga semua makhluk berbahagia. \u2014 Jejak Buddha",
        "publishAt": "2026-10-15T12:10:00.000Z",  # Kamis 15 Okt 19:10 WIB
        "tags": ["siddhartha gautama", "sang buddha", "jejak buddha", "kisah buddha", "pelepasan agung", "sungai anoma", "kebijaksanaan buddha", "cerita buddha"],
    },
]

def upload_one(s, meta):
    body = {
        "snippet": {"title": meta["title"], "description": meta["description"],
                    "tags": meta["tags"], "categoryId": "27", "defaultLanguage": "id"},
        "status": {"privacyStatus": "private", "publishAt": meta["publishAt"],
                   "selfDeclaredMadeForKids": False},
    }
    size = os.path.getsize(meta["file"])
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)}, timeout=60)
    if r.status_code not in (200, 201):
        return {"ok": False, "stage": "init", "status": r.status_code, "body": r.text[:600]}
    up_url = r.headers["Location"]
    chunk = 8 * 1024 * 1024
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
                vid = rr.json()
                return {"ok": True, "id": vid["id"], "url": "https://youtu.be/" + vid["id"]}
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                    f.seek(offset)
                else:
                    offset = end + 1
            else:
                return {"ok": False, "stage": "chunk", "status": rr.status_code, "body": rr.text[:600]}
    return {"ok": False, "stage": "eof", "body": "upload tidak selesai"}

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
    results = []
    for meta in SHORTS:
        res = upload_one(s, meta)
        res["title"] = meta["title"]
        res["file"] = meta["file"]
        res["publishAt"] = meta["publishAt"]
        results.append(res)
        print(json.dumps(res, ensure_ascii=False), flush=True)
        if not res["ok"]:
            print("BERHENTI setelah kegagalan (anti retry-limit).", flush=True)
            break
    out = "/home/hatch/workspace/jejak-buddha/2026-10-14/upload-hasil-shorts.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print("HASIL TERSIMPAN:", out)

if __name__ == "__main__":
    main()
