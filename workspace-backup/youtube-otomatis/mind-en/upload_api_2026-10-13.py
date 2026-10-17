#!/usr/bin/env python3
"""Upload LONG Dark Mind Files 2026-10-10 via YouTube Data API (yt-growth auth).
Rencana lanjutan 2026-10-12: jalur API karena prompt 2FA browser tidak muncul di HP user.
AI disclosure 'Altered content' + komentar ON + thumbnail kustom TIDAK didukung API
-> dikerjakan via browser task sesi-ada setelah upload (tanpa login baru).
"""
import json, os, sys, time

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "mind-en"
CHANNEL_ID = "UCAnSrJzQuePS1MJhfwlRJuQ"
VIDEO = os.path.expanduser("~/workspace/youtube-otomatis/mind-en/video/2026-10-10-upload.mp4")
TITLE = "6 Mind Tricks That Make You Say YES"
DESCRIPTION = """I once paid $200 for a jacket I didn't even want — in ninety seconds. These are the 6 mind tricks that make you say YES before you think: reciprocity, scarcity, authority, liking, commitment, and social proof.

The football salesman story still stings. Which trick has gotten YOU? Tell me below.

CHAPTERS:
0:00 Cold open
1:07 Trick 1: The free gift trap
2:25 Trick 2: The disappearing deal
3:47 Trick 3: The costume of authority
4:59 Trick 4: The stranger who likes you
6:26 Trick 5: The small yes
7:54 Trick 6: Everybody is doing it
9:04 Recap

Learn these to protect yourself — never to manipulate others. Spotting the trick is the whole game.

#darkpsychology #psychology #mindset #foryou"""
TAGS = ["dark psychology", "psychology tricks", "how to say no", "persuasion techniques",
        "manipulation tactics", "reciprocity psychology", "scarcity effect", "authority bias",
        "liking principle", "commitment and consistency", "social proof psychology",
        "human behavior", "mind tricks", "psychological tricks", "how manipulators work",
        "self defense psychology", "critical thinking", "behavioral psychology",
        "influence people", "protect yourself manipulation"]
PUBLISH_AT = "2026-10-14T00:00:00.000Z"  # 2026-10-14 07:00 WIB

def main():
    s = api_session(SLUG)
    # 1. verifikasi channel aktif
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != CHANNEL_ID or "Dark Mind" not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Dark Mind Files!")
    # 2. cek duplikat: video dgn judul sama di channel ini
    r = s.get("https://www.googleapis.com/youtube/v3/search",
              params={"part": "snippet", "channelId": CHANNEL_ID, "q": TITLE,
                      "type": "video", "maxResults": 5}, timeout=30)
    if r.status_code == 200:
        for it in r.json().get("items", []):
            if it["snippet"]["title"].strip().lower() == TITLE.lower():
                print("DUPLIKAT DITEMUKAN:", it["id"]["videoId"],
                      "https://youtu.be/" + it["id"]["videoId"])
                print(json.dumps({"duplicate": True, "id": it["id"]["videoId"],
                                  "url": "https://youtu.be/" + it["id"]["videoId"]}))
                return
    # 3. inisiasi resumable upload
    body = {
        "snippet": {"title": TITLE, "description": DESCRIPTION, "tags": TAGS,
                    "categoryId": "27", "defaultLanguage": "en"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    size = os.path.getsize(VIDEO)
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)},
               timeout=60)
    if r.status_code == 403 and "uploadLimitExceeded" in r.text:
        print("LIMIT_HARIAN:", r.text[:300])
        sys.exit(20)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:500])
        sys.exit(10)
    up_url = r.headers["Location"]
    print("upload session OK", flush=True)
    # 4. upload chunked
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
                print(json.dumps({"id": vid["id"],
                                  "url": "https://youtu.be/" + vid["id"]}))
                return
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                else:
                    offset = end + 1
                f.seek(offset)
                print(f"  ... {offset}/{size}", flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:300])
                sys.exit(11)

if __name__ == "__main__":
    main()
