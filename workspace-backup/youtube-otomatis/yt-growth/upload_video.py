#!/usr/bin/env python3
"""Upload video ke YouTube via Data API v3 (resumable), memakai auth.py yt-growth.
Dipakai saat upload via browser gagal teknis (file picker tidak bisa diotomatisasi).
AI disclosure 'Altered content' TIDAK didukung API -> dicentang manual via Studio setelahnya.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import api_session

SLUG = "empires-en"
VIDEO = os.path.expanduser("~/workspace/youtube-otomatis/empires-en/video/maya-2026-10-08-upload-small.mp4")
META = json.load(open(os.path.expanduser("~/workspace/youtube-otomatis/empires-en/upload-2026-10-09.json")))

TITLE = META["judul"]
DESCRIPTION = META["deskripsi"]
TAGS = META["tags"]
# 07:00 WIB 10 Okt 2026 = 00:00 UTC
PUBLISH_AT = "2026-10-10T00:00:00.000Z"

def main():
    s = api_session(SLUG)
    # 1. verifikasi channel
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"])
    if "Lost Empires" not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Lost Empires!")

    body = {
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": TAGS,
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": PUBLISH_AT,
            "selfDeclaredMadeForKids": False,
        },
    }
    # 2. inisiasi resumable upload
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(VIDEO))},
               timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:500])
        sys.exit(10)
    up_url = r.headers["Location"]
    print("upload session OK")

    # 3. upload chunked
    size = os.path.getsize(VIDEO)
    chunk = 8 * 1024 * 1024
    with open(VIDEO, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            rr = s.put(up_url,
                       data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": f"bytes {offset}-{end}/{size}"},
                       timeout=300)
            if rr.status_code in (200, 201):
                vid = rr.json()
                print("UPLOAD SELESAI:", vid["id"])
                print("URL: https://youtu.be/" + vid["id"])
                print(json.dumps({"id": vid["id"],
                                  "url": "https://youtu.be/" + vid["id"]}))
                return
            elif rr.status_code == 308:
                # resume: baca Range header
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                    f.seek(offset)
                else:
                    offset = end + 1
                print(f"... {offset}/{size} bytes", flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:500])
                sys.exit(11)
    sys.exit("upload tidak selesai tanpa error jelas")

if __name__ == "__main__":
    main()
