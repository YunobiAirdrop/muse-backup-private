#!/usr/bin/env python3
"""Upload LONG Dark Mind Files 2026-10-15 ("7 Mind Tricks Your Own Brain Plays on You")
via YouTube Data API (yt-growth auth). Dieksekusi 2026-10-18 (hari LONG;
video antre sejak 2026-10-15 per meta/upload-instruksi-long-2026-10-15.md).
AI disclosure 'Altered content' + komentar ON + thumbnail Test&Compare
TIDAK didukung API -> browser task sesi-ada setelah upload (tanpa login baru).
Exit 20 = limit harian (tulis retry-queue, JANGAN retry langsung).
"""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "mind-en"
CHANNEL_ID = "UCAnSrJzQuePS1MJhfwlRJuQ"
BASE = os.path.expanduser("~/workspace/youtube-otomatis/mind-en")
VIDEO = f"{BASE}/video/2026-10-15.mp4"
TITLE = "7 Mind Tricks Your Own Brain Plays on You"
DESCRIPTION = """Your brain lies to you every single day. These 7 cognitive biases — confirmation bias, sunk cost fallacy, anchoring, loss aversion, and more — secretly control your money, your fears, and your decisions.

This is not a textbook lecture. These are the mental glitches I have watched bend smart people in real life — a sharp businessman, a stubborn dieter, a brilliant hire who could only talk about the work. Once you know their names, they lose their power over you.

CHAPTERS
0:00 Intro: Your Brain Is Lying to You
0:48 Trick 1: Confirmation Bias
1:57 Trick 2: Sunk Cost Fallacy
3:14 Trick 3: Anchoring
4:28 Trick 4: Loss Aversion
5:52 Trick 5: Availability Heuristic
7:15 Trick 6: Bandwagon Effect
8:27 Trick 7: Halo Effect
9:38 All 7 Tricks, Named

If this rewired how you see your own mind, subscribe to Dark Mind Files — a new dark psychology episode every single day.

Watch next: 7 Ways People Test Your Boundaries Before They Control You — https://youtu.be/SXGwivf_KQA

#psychology #cognitivebias #mindset #darkpsychology #foryou"""
TAGS = ["cognitive biases", "confirmation bias", "sunk cost fallacy",
        "anchoring effect", "loss aversion", "availability heuristic",
        "bandwagon effect", "halo effect", "dark psychology", "psychology tricks",
        "mind tricks", "brain hacks", "psychology facts", "human behavior",
        "decision making", "behavioral psychology", "mindset shift",
        "psychology", "self improvement", "dark mind files"]
PUBLISH_AT = "2026-10-19T00:00:00.000Z"  # 2026-10-19 07:00 WIB (= 2026-10-18 19:00 US Eastern)

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
                with open(f"{BASE}/meta/upload-long-2026-10-18.json", "w") as out:
                    json.dump({"duplicate": True, "id": it["id"]["videoId"],
                               "url": "https://youtu.be/" + it["id"]["videoId"],
                               "title": TITLE, "publishAt": PUBLISH_AT}, out, indent=1)
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
                with open(f"{BASE}/meta/upload-long-2026-10-18.json", "w") as out:
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
