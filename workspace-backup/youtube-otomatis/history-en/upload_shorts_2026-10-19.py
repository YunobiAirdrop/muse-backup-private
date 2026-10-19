#!/usr/bin/env python3
"""Upload 3 shorts history-en 2026-10-18 -> @EchoesOfThePast-e9m (UCCBGIbsfMo2TmyhbUzHxD0A).
API-first (yt-growth auth.py, slug history-en). Verifikasi channel WAJIB sebelum upload.
AI disclosure 'Altered content' tidak didukung API -> dicentang manual via Studio.
"""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

WS = os.path.expanduser("~/workspace/youtube-otomatis/history-en/shorts")
# Besok 07:00 WIB = 2026-10-20T00:00:00Z
PUBLISH_AT = "2026-10-20T00:00:00.000Z"

SHORTS = [
    {
        "file": f"{WS}/2026-10-18-s1.mp4",
        "title": "The 8.15 AM Flash That Changed Everything #shorts #history #documentary #butifyourcloseyoureyesmeme #foryou",
        "description": "At 8:15 AM on August 6, 1945, a single bomb detonated over Hiroshima. This is the story of the flash that ended a war and started a new era. Full documentary on the channel.",
        "tags": ["hiroshima", "atomic bomb", "wwii", "world history", "history documentary"],
    },
    {
        "file": f"{WS}/2026-10-18-s2.mp4",
        "title": "One Plane, One City, One Second #shorts #history #documentary #butifyourcloseyoureyesmeme #foryou",
        "description": "The Enola Gay dropped a 4-ton bomb from 31,000 feet over Hiroshima. 43 seconds later, one second changed everything. Full documentary on the channel.",
        "tags": ["hiroshima", "enola gay", "atomic bomb", "wwii", "world history", "history documentary"],
    },
    {
        "file": f"{WS}/2026-10-18-s3.mp4",
        "title": "I Am Become Death: The Bomb Story #shorts #history #documentary #butifyourcloseyoureyesmeme #foryou",
        "description": "After the first atomic test, the scientists who built the bomb quoted a Hindu scripture: 'I am become Death, the destroyer of worlds.' This is the story behind those words. Full documentary on the channel.",
        "tags": ["hiroshima", "oppenheimer", "atomic bomb", "manhattan project", "world history", "history documentary"],
    },
]


def upload_one(s, item):
    video = item["file"]
    body = {
        "snippet": {
            "title": item["title"],
            "description": item["description"],
            "tags": item["tags"],
            "categoryId": "27",
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
                        "X-Upload-Content-Length": str(os.path.getsize(video))},
               timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", item["file"], r.status_code, r.text[:300], flush=True)
        return None
    up_url = r.headers["Location"]
    size = os.path.getsize(video)
    chunk = 8 * 1024 * 1024
    with open(video, "rb") as f:
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
                print("OK:", vid["id"], "https://youtu.be/" + vid["id"], flush=True)
                return vid["id"]
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                    f.seek(offset)
                else:
                    offset = end + 1
                print(f"... {offset}/{size} bytes", flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:300], flush=True)
                return None
    return None


def main():
    s = api_session("history-en")
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != "UCCBGIbsfMo2TmyhbUzHxD0A":
        sys.exit("BATAL: channel aktif bukan Echoes of History!")
    hasil = []
    for item in SHORTS:
        vid = upload_one(s, item)
        hasil.append({"file": item["file"], "video_id": vid,
                      "url": ("https://youtu.be/" + vid) if vid else None,
                      "title": item["title"], "description": item["description"]})
    out = os.path.expanduser("~/workspace/youtube-otomatis/history-en/upload-2026-10-19.json")
    json.dump({
        "video_type": "shorts x3",
        "channel_handle": "@EchoesOfThePast-e9m",
        "channel_id": "UCCBGIbsfMo2TmyhbUzHxD0A",
        "channel_name": "Echoes of History Channel",
        "channel_terverifikasi": "API channels.list(mine=true) -> Echoes of History Channel UCCBGIbsfMo2TmyhbUzHxD0A BENAR",
        "upload_method": "YouTube Data API v3 (yt-growth, slug history-en)",
        "publish_scheduled_wib": "2026-10-20 07:00 WIB",
        "privacy": "private", "category": "Education", "category_id": "27",
        "language": "en", "made_for_kids": False,
        "topic": "Hiroshima 1945 - 3 shorts dari long 2026-10-18",
        "deskripsi_tanpa_hashtag": "ya (hashtag hanya di akhir judul, ditutup #foryou)",
        "ai_disclosure": "TERTUNDA: API tidak mendukung Altered-content -> wajib centang manual di Studio sebelum tayang.",
        "comments": "TERTUNDA: centang manual 'Allow all comments' di Studio.",
        "videos": hasil,
    }, open(out, "w"), indent=1)
    print("ditulis:", out)
    gagal = [h for h in hasil if not h["video_id"]]
    if gagal:
        sys.exit(20)


if __name__ == "__main__":
    main()
