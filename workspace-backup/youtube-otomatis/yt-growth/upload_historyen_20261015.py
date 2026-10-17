#!/usr/bin/env python3
"""Upload history-en LONG D-Day 1944 via Data API v3 (cron history-en-harian 2026-10-15).
Pola: upload_spaceen_20261014.py. Private + publishAt 2026-10-16 07:00 WIB.
AI disclosure TIDAK didukung API -> dicentang manual via Studio (browser task menyusul)."""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import api_session

SLUG = "history-en"
VIDEO = os.path.expanduser("~/workspace/youtube-otomatis/history-en/video/2026-10-15.mp4")
TITLE = "D-Day 1944: The Longest Day That Changed the World"
DESCRIPTION = open(os.path.expanduser(
    "~/workspace/youtube-otomatis/history-en/script/deskripsi-final-2026-10-15.txt")).read().strip()
TAGS = ["d-day", "wwii", "world war 2", "normandy", "omaha beach",
        "history documentary", "world history", "eisenhower", "1944",
        "longest day", "june 6 1944"]
PUBLISH_AT = "2026-10-16T00:00:00.000Z"  # 16 Okt 2026 07:00 WIB
EXPECTED_CHANNEL_ID = "UCCBGIbsfMo2TmyhbUzHxD0A"
EXPECTED_CHANNEL_NAME = "Echoes of History"


def main():
    s = api_session(SLUG)
    # 1. verifikasi channel aktif BENAR
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != EXPECTED_CHANNEL_ID or EXPECTED_CHANNEL_NAME not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Echoes of History Channel!")

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
    print("upload session OK", flush=True)

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
