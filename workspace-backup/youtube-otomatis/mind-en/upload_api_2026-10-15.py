#!/usr/bin/env python3
"""Upload LONG Dark Mind Files 2026-10-12 ("7 Ways People Test Your Boundaries...")
via YouTube Data API (yt-growth auth). Dieksekusi 2026-10-15 (hari LONG).
AI disclosure 'Altered content' + komentar ON + thumbnail kustom TIDAK didukung API
-> dikerjakan via browser task sesi-ada setelah upload (tanpa login baru).
Exit 20 = limit harian (tulis retry-queue, JANGAN retry langsung).
"""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "mind-en"
CHANNEL_ID = "UCAnSrJzQuePS1MJhfwlRJuQ"
VIDEO = os.path.expanduser("~/workspace/youtube-otomatis/mind-en/video/2026-10-12-upload.mp4")
TITLE = "7 Ways People Test Your Boundaries Before They Control You"
DESCRIPTION = """She smiled, asked for one tiny favor \u2014 and six months later she was running my entire schedule. These are the 7 boundary tests people run on you before they try to control you.

This one hit close to home for me. Which test have YOU failed without noticing? Tell me below.

CHAPTERS:
0:00 Cold open
1:25 Test 1: The small favor that keeps growing
2:27 Test 2: The insult disguised as a joke
3:31 Test 3: The chronic lateness test
4:26 Test 4: The secret-for-a-secret trade
5:37 Test 5: The guilt test
6:38 Test 6: The public embarrassment test
7:33 Test 7: The silent treatment probe
8:28 The defense framework
9:43 Recap

Learn these to protect yourself \u2014 never to use them on others. Spotting the test early, while it is still small, is the whole game.

#darkpsychology #psychology #mindset #boundaries #foryou"""
TAGS = ["dark psychology", "boundary tests", "how to set boundaries", "manipulation tactics",
        "people test your boundaries", "guilt tripping", "silent treatment psychology",
        "human behavior", "psychology facts", "how manipulators work",
        "self protection psychology", "behavioral psychology", "mind tricks",
        "spot manipulation", "saying no"]
PUBLISH_AT = "2026-10-16T00:00:00.000Z"  # 2026-10-16 07:00 WIB (= 2026-10-15 19:00 US Eastern)

def main():
    assert os.path.exists(VIDEO), f"file tidak ada: {VIDEO}"
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
    print(f"file: {VIDEO} ({size/1048576:.1f} MB)", flush=True)
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
                with open(os.path.expanduser(
                        "~/workspace/youtube-otomatis/mind-en/meta/upload-2026-10-15.json"),
                        "w") as out:
                    json.dump({"id": vid["id"],
                               "url": "https://youtu.be/" + vid["id"],
                               "title": TITLE, "publishAt": PUBLISH_AT,
                               "file": VIDEO}, out, indent=1)
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
