#!/usr/bin/env python3
"""Upload video ke YouTube via Data API v3 (resumable) untuk channel Jejak Islami.
AI disclosure 'Altered content' TIDAK didukung API -> dicentang via Studio setelahnya.

Usage:
  python3 upload_jejakislami.py --video PATH --title "T" --desc-file PATH \
      --tags "a,b,c" --publish-at "2026-10-19T12:00:00.000Z" [--slug jejakislami]
"""
import argparse, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import api_session

EXPECT_ID = "UC81zPJnIJbKU5lhTKx-6Hyg"
EXPECT_NAME = "Jejak Islami"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--desc-file", required=True)
    ap.add_argument("--tags", default="")
    ap.add_argument("--publish-at", required=True)
    ap.add_argument("--slug", default="jejakislami")
    a = ap.parse_args()

    if not os.path.isfile(a.video):
        sys.exit(f"video tidak ada: {a.video}")
    with open(a.desc_file) as f:
        desc = f.read()

    s = api_session(a.slug)
    # 1. verifikasi channel
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "id,snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != EXPECT_ID or EXPECT_NAME not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Jejak Islami!")

    body = {
        "snippet": {
            "title": a.title,
            "description": desc,
            "tags": [t.strip() for t in a.tags.split(",") if t.strip()],
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": a.publish_at,
            "selfDeclaredMadeForKids": False,
        },
    }
    size = os.path.getsize(a.video)
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)},
               timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:500])
        sys.exit(10)
    up_url = r.headers["Location"]
    print("upload session OK", flush=True)

    chunk = 8 * 1024 * 1024
    with open(a.video, "rb") as f:
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
                print(json.dumps({"id": vid["id"],
                                  "url": "https://youtu.be/" + vid["id"]}))
                return
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                else:
                    offset = end + 1
                print(f"  ... {offset}/{size}", flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:300])
                sys.exit(11)
    print("SELESAI tanpa konfirmasi akhir (cek Studio)")

if __name__ == "__main__":
    main()
