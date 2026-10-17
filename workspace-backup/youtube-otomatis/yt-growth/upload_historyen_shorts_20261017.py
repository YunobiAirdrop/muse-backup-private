#!/usr/bin/env python3
"""Upload history-en 3 SHORTS (D-Day 1944, produksi 2026-10-15) via Data API v3
(cron history-en-harian slot 2026-10-16, dijalankan 2026-10-17).
Pola: upload_historyen_20261015.py. Private + publishAt 2026-10-18 07:00 WIB.
AI disclosure TIDAK didukung API -> dicentang manual via Studio (browser task menyusul).
Exit code: 0 = semua OK; 20 = kena Batas upload harian (masuk retry-queue, JANGAN retry);
11 = gagal lain.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import api_session

SLUG = "history-en"
BASE = os.path.expanduser("~/workspace/youtube-otomatis/history-en")
PUBLISH_AT = "2026-10-18T00:00:00.000Z"  # 18 Okt 2026 07:00 WIB
EXPECTED_CHANNEL_ID = "UCCBGIbsfMo2TmyhbUzHxD0A"
EXPECTED_CHANNEL_NAME = "Echoes of History"

SHORTS = [
    {
        "key": "s1",
        "file": f"{BASE}/shorts/2026-10-15-s1.mp4",
        "judul": "Ten Thousand Crosses: Where D-Day Ended #shorts #history #documentary #foryou",
        "deskripsi": "Ten thousand white crosses above the sea in Normandy. This is where the story of D-Day ends \u2014 and where our documentary begins. Full story on the channel.",
        "tags": ["d-day", "wwii", "world war 2", "normandy", "omaha beach",
                 "history documentary", "world history", "1944"],
    },
    {
        "key": "s2",
        "file": f"{BASE}/shorts/2026-10-15-s2.mp4",
        "judul": "The Night 13,000 Men Fell From the Sky #shorts #history #documentary #foryou",
        "deskripsi": "Midnight, June 6, 1944: thirteen thousand paratroopers dropped into the dark over Normandy. Hours later, the ramps dropped on Omaha Beach. Full D-Day documentary on the channel.",
        "tags": ["d-day", "wwii", "world war 2", "normandy", "paratroopers",
                 "history documentary", "world history", "1944"],
    },
    {
        "key": "s3",
        "file": f"{BASE}/shorts/2026-10-15-s3.mp4",
        "judul": "Hitler Was ASLEEP During D-Day #shorts #history #documentary #foryou",
        "deskripsi": "While 150,000 Allied troops stormed Normandy, Hitler's best tanks sat waiting near Calais \u2014 and no one dared wake him. Full D-Day documentary on the channel.",
        "tags": ["d-day", "wwii", "world war 2", "normandy", "hitler",
                 "history documentary", "world history", "1944"],
    },
]


def upload_one(s, meta):
    body = {
        "snippet": {
            "title": meta["judul"],
            "description": meta["deskripsi"],
            "tags": meta["tags"],
            "categoryId": "27",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": PUBLISH_AT,
            "selfDeclaredMadeForKids": False,
        },
    }
    size = os.path.getsize(meta["file"])
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)},
               timeout=60)
    if r.status_code not in (200, 201):
        txt = r.text[:500]
        print(f"[{meta['key']}] INIT GAGAL:", r.status_code, txt, flush=True)
        if "uploadLimitExceeded" in txt or "dailyLimitExceeded" in txt:
            sys.exit(20)  # batas upload harian -> retry-queue, jangan retry
        sys.exit(11)
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
                print(f"[{meta['key']}] UPLOAD SELESAI: {vid['id']} "
                      f"https://youtu.be/{vid['id']}", flush=True)
                return vid["id"]
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
            else:
                txt = rr.text[:500]
                print(f"[{meta['key']}] CHUNK GAGAL:", rr.status_code, txt,
                      flush=True)
                if "uploadLimitExceeded" in txt or "dailyLimitExceeded" in txt:
                    sys.exit(20)
                sys.exit(11)
    sys.exit("upload tidak selesai tanpa error jelas")


def main():
    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != EXPECTED_CHANNEL_ID or EXPECTED_CHANNEL_NAME not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Echoes of History Channel!")
    hasil = []
    for meta in SHORTS:
        vid = upload_one(s, meta)
        hasil.append({"key": meta["key"], "video_id": vid,
                      "url": "https://youtu.be/" + vid,
                      "judul": meta["judul"], "file": meta["file"]})
    print(json.dumps(hasil, ensure_ascii=False))


if __name__ == "__main__":
    main()
