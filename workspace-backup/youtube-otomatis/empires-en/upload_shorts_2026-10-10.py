#!/usr/bin/env python3
"""Upload 3 shorts Maya (produksi 2026-10-08) ke Lost Empires via Data API v3.
Terjadwal 2026-10-11 07:00 WIB (= 2026-10-11T00:00:00Z).
AI disclosure 'Altered content' TIDAK didukung API -> dicentang via Studio setelahnya.
Cek channel (mine=true) SEBELUM upload; batal kalau bukan Lost Empires.
"""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "empires-en"
BASE = os.path.expanduser("~/workspace/youtube-otomatis/empires-en")
LONG_URL = "https://youtu.be/6DwpnronVQQ"
PUBLISH_AT = "2026-10-11T00:00:00.000Z"  # 07:00 WIB 11 Okt 2026
DESC = ("Watch the full story: %s\n\n"
        "A new lost civilization every day \u2014 subscribe to Lost Empires." % LONG_URL)
TAGS = ["maya collapse", "shorts", "history", "archaeology", "lost civilization"]

SHORTS = [
    ("shorts/2026-10-08-s1.mp4",
     "60 Maya Cities Died in One Lifetime \U0001F631 #shorts #history #archaeology"),
    ("shorts/2026-10-08-s2.mp4",
     "They Predicted Eclipses but Missed the Drought #shorts #history #archaeology"),
    ("shorts/2026-10-08-s3.mp4",
     "Only 4 Maya Books Survived the Fire #shorts #history #archaeology"),
]


def upload_one(s, video_path, title):
    size = os.path.getsize(video_path)
    body = {
        "snippet": {"title": title, "description": DESC,
                    "tags": TAGS, "categoryId": "27"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)},
               timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:300], flush=True)
        sys.exit(10)
    up_url = r.headers["Location"]
    chunk = 8 * 1024 * 1024
    with open(video_path, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": "bytes %d-%d/%d" % (offset, end, size)},
                       timeout=300)
            if rr.status_code in (200, 201):
                vid = rr.json()
                print("OK: %s https://youtu.be/%s" % (vid["id"], vid["id"]), flush=True)
                return vid["id"]
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
                print("... %d/%d bytes" % (offset, size), flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:300], flush=True)
                sys.exit(11)
    sys.exit("upload tidak selesai tanpa error jelas")


def main():
    s = api_session(SLUG)
    # 1. verifikasi channel SEBELUM upload
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL: %s %s" % (ch["snippet"]["title"], ch["id"]), flush=True)
    if "Lost Empires" not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Lost Empires!")
    ids = []
    for rel, title in SHORTS:
        p = os.path.join(BASE, rel)
        print("Uploading %s ..." % rel, flush=True)
        ids.append(upload_one(s, p, title))
    print(json.dumps({"ids": ids,
                      "urls": ["https://youtu.be/" + i for i in ids]}))


if __name__ == "__main__":
    main()
