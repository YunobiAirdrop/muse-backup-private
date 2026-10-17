#!/usr/bin/env python3
"""Upload 3 SHORTS Maura Murray (bank produksi 2026-10-12) via API yt-growth.
Channel: Dark Case Files (@TrueCaseFilesTV, UC2df1xY_WqWdX33oLqeXE2w).
Jadwal tayang: 2026-10-14 07:00 WIB = 2026-10-14T00:00:00.000Z.
"""
import json, os, sys, time

BASE = os.path.expanduser("~/workspace/youtube-otomatis")
sys.path.insert(0, os.path.join(BASE, "yt-growth"))
from auth import api_session

SLUG = "truecrime-en"
WS = os.path.join(BASE, "truecrime-en")
TITLES = json.load(open(os.path.join(WS, "shorts", "2026-10-12-titles.json")))
PUBLISH_AT = "2026-10-14T00:00:00.000Z"
EXPECT_ID = "UC2df1xY_WqWdX33oLqeXE2w"

def upload_one(s, path, title, description):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["maura murray", "true crime", "unsolved mystery", "missing person",
                     "dark case files", "true crime shorts", "shorts"],
            "categoryId": "27",  # Education
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": PUBLISH_AT,
            "selfDeclaredMadeForKids": False,
        },
    }
    size = os.path.getsize(path)
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)},
               timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", path, r.status_code, r.text[:400], flush=True)
        return None
    up_url = r.headers["Location"]
    with open(path, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(8 * 1024 * 1024)
            end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": f"bytes {offset}-{end}/{size}"},
                       timeout=300)
            if rr.status_code in (200, 201):
                return rr.json()["id"]
            if rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                else:
                    offset = end + 1
                continue
            print("CHUNK GAGAL:", path, rr.status_code, rr.text[:400], flush=True)
            return None
    return None

def main():
    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != EXPECT_ID or "Dark Case Files" not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Dark Case Files!")
    results = []
    for t in TITLES:
        path = os.path.join(WS, "shorts", t["clip"] + ".mp4")
        print("UPLOAD:", t["clip"], t["title"][:60], flush=True)
        vid = upload_one(s, path, t["title"], t["description"])
        if vid:
            print("OK:", vid, "https://youtu.be/" + vid, flush=True)
            results.append({"clip": t["clip"], "videoId": vid,
                            "url": "https://youtu.be/" + vid})
        else:
            print("GAGAL:", t["clip"], flush=True)
            results.append({"clip": t["clip"], "videoId": None})
        time.sleep(2)
    print(json.dumps(results, indent=1))

if __name__ == "__main__":
    main()
