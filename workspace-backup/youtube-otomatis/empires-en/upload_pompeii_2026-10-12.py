#!/usr/bin/env python3
"""Upload LONG Pompeii ke Lost Empires via YouTube Data API v3 (resumable).
Verifikasi channel WAJIB: Lost Empires UCd2wADmj47v3XCPcCpk-fSg.
AI disclosure 'Altered content' TIDAK didukung API -> dicentang via Studio setelahnya.
Jadwal: private + publishAt 2026-10-16T00:00:00Z (= 07:00 WIB 16 Okt 2026).
"""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

BASE = os.path.expanduser("~/workspace/youtube-otomatis/empires-en")
META = json.load(open(os.path.join(BASE, "upload-2026-10-12.json")))["long"]
VIDEO = META["video"]
PUBLISH_AT = "2026-10-16T00:00:00.000Z"
EXPECT_ID = "UCd2wADmj47v3XCPcCpk-fSg"

def main():
    s = api_session("empires-en")
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"])
    if ch["id"] != EXPECT_ID or "Lost Empires" not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Lost Empires!")

    body = {
        "snippet": {
            "title": META["title"],
            "description": META["description"],
            "tags": META["tags"],
            "categoryId": "27",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": PUBLISH_AT,
            "selfDeclaredMadeForKids": False,
        },
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(VIDEO))},
               timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:500]); sys.exit(10)
    up_url = r.headers["Location"]
    print("upload session OK, size:", os.path.getsize(VIDEO))

    size = os.path.getsize(VIDEO)
    chunk = 8 * 1024 * 1024
    with open(VIDEO, "rb") as f:
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
                print("UPLOAD SELESAI:", vid["id"])
                print("URL: https://youtu.be/" + vid["id"])
                return
            elif rr.status_code == 308:
                offset = end + 1
                print(f"  ...{offset}/{size}", flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:300]); sys.exit(11)

if __name__ == "__main__":
    main()
