#!/usr/bin/env python3
"""Upload 3 SHORTS Dark Mind Files (potongan long 2026-10-12) via YouTube Data API.
Channel: @TheDarkMindFiles-s6i (UCAnSrJzQuePS1MJhfwlRJuQ), akun khususstokyunobi@gmail.com.
Terjadwal: 2026-10-15 07:00 WIB (= 2026-10-15T00:00:00Z). AI disclosure browser lanjutan.
"""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "mind-en"
CHANNEL_ID = "UCAnSrJzQuePS1MJhfwlRJuQ"
PUBLISH_AT = "2026-10-15T00:00:00.000Z"  # 2026-10-15 07:00 WIB
TAGS = ["dark psychology", "psychology", "mindset", "shorts",
        "manipulation tactics", "psychology facts", "human behavior"]
BASE = os.path.expanduser("~/workspace/youtube-otomatis/mind-en/shorts/2026-10-12")

SHORTS = [
    ("short1-favor.mp4",
     "The Tiny Favor That Ends Up Controlling You #shorts #psychology #mindset #foryou",
     "It starts innocent: cover my shift, just this once? Each yes becomes a receipt they wave when you finally hesitate. The favor was never the goal \u2014 your yes was. Full breakdown: 7 Ways People Test Your Boundaries Before They Control You, on Dark Mind Files."),
    ("short2-joke.mp4",
     "That Joke About You Was a Test #shorts #psychology #mindset #foryou",
     "It was not humor. It was a probe: will you object, or swallow it to keep the mood light? Real friends stop when it stings. Testers take notes. Full video: 7 Ways People Test Your Boundaries Before They Control You, on Dark Mind Files."),
    ("short3-silence.mp4",
     "The Silent Treatment Is a Boundary Test #shorts #psychology #mindset #foryou",
     "You set one small boundary, then: silence. Space is announced \u2014 punishment is not, and it ends the moment you surrender. Let the silence be silent. Full video: 7 Ways People Test Your Boundaries Before They Control You, on Dark Mind Files."),
]

def upload_one(s, video, title, desc):
    size = os.path.getsize(video)
    # cek duplikat
    r = s.get("https://www.googleapis.com/youtube/v3/search",
              params={"part": "snippet", "channelId": CHANNEL_ID, "q": title,
                      "type": "video", "maxResults": 5}, timeout=30)
    if r.status_code == 200:
        for it in r.json().get("items", []):
            if it["snippet"]["title"].strip().lower() == title.lower():
                return {"duplicate": True, "id": it["id"]["videoId"],
                        "url": "https://youtu.be/" + it["id"]["videoId"]}
    body = {
        "snippet": {"title": title, "description": desc, "tags": TAGS,
                    "categoryId": "27", "defaultLanguage": "en"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)},
               timeout=60)
    if r.status_code == 403 and "uploadLimitExceeded" in r.text:
        return {"limit": True, "raw": r.text[:300]}
    if r.status_code not in (200, 201):
        return {"error": f"init {r.status_code} {r.text[:400]}"}
    up_url = r.headers["Location"]
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
                vid = rr.json()["id"]
                return {"id": vid, "url": "https://youtu.be/" + vid}
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
                print(f"  ... {offset}/{size}", flush=True)
            else:
                return {"error": f"chunk {rr.status_code} {rr.text[:400]}"}

def main():
    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != CHANNEL_ID or "Dark Mind" not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Dark Mind Files!")
    out = []
    for fname, title, desc in SHORTS:
        video = os.path.join(BASE, fname)
        print("UPLOAD:", fname, flush=True)
        res = upload_one(s, video, title, desc)
        res["file"] = fname
        out.append(res)
        print(json.dumps(res), flush=True)
        if "limit" in res:
            print("LIMIT_HARIAN terdeteksi, berhenti.")
            sys.exit(20)
    print(json.dumps({"results": out}))

if __name__ == "__main__":
    main()
