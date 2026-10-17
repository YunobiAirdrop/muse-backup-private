#!/usr/bin/env python3
"""Upload Cosmic Unknown long Oumuamua via Data API (space-en).
Fallback API-first karena browser task gagal (infra browser unavailable).
Pola disalin dari upload_spaceen_20261014.py yang sukses.
CATATAN: via API tidak bisa centang AI disclosure / comments eksplisit /
custom thumbnail — itu tetap butuh sesi Studio manual.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import api_session

SLUG = "space-en"
CHANNEL_ID = "UCQnUeh4-2AKgCsV_cjgUv4w"
VIDEO = os.path.expanduser("~/workspace/youtube-otomatis/space-en/video/2026-10-13.mp4")
TITLE = "Oumuamua: The Alien Visitor That Broke Every Rule?"
DESCRIPTION = """In October 2017, something entered our solar system that did not belong here. It came from another star, moving too fast for the Sun to ever capture \u2014 and as it left, it did the impossible: it sped up, with no visible engine. No tail. No jets. Nothing pushing it. It blows my mind that the first visitor from another star system broke every rule we had. This is the story of Oumuamua, the Harvard scientist who dared to say "alien technology," and the two visitors that followed \u2014 including one carrying ice older than the Sun itself. Just think about this for a second: strangers from other star systems have been sailing past us for all of human history, and we only learned to see them a decade ago. Rock or ship? Watch, then tell me what YOU believe.

CHAPTERS:
0:00 The Visitor From Another Star
0:28 Rock or Ship? You Decide
0:56 Found: October 19, 2017
1:22 A Cigar the Size of a Skyscraper
1:49 It Sped Up... With No Engine
2:20 The Harvard Scientist Who Said "Alien Tech"
2:51 Nobody Can Agree What It Was
3:23 Why Oumuamua Matters
3:56 The "Normal" Visitor: 2I/Borisov
4:31 Subscribe for Daily Cosmic Mysteries
4:54 The Third Visitor: 3I/ATLAS
5:26 Webb Found Methane on an Interstellar Body
6:00 Older Than the Sun Itself
6:32 Billions of Wanderers
7:03 Postcards From Destroyed Worlds
7:35 Never Coming Back
8:07 Rock or Ship? My Honest Answer
8:39 What Do YOU Believe?

\U0001f514 Subscribe to Cosmic Unknown for a new cosmic mystery every day!

#space #universe #cosmos #oumuamua #interstellar #foryou"""
TAGS = ["oumuamua", "interstellar object", "1I/2017 U1", "3I/ATLAS",
        "2I/Borisov", "Avi Loeb", "alien technology", "space documentary",
        "cosmos", "universe", "astronomy", "deep space"]
PUBLISH_AT = "2026-10-16T00:00:00.000Z"  # 16 Okt 2026 07:00 WIB
OUT_JSON = os.path.expanduser("~/workspace/youtube-otomatis/space-en/upload-2026-10-15-api.json")


def main():
    dur = float(os.popen(
        f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{VIDEO}"'
    ).read().strip() or 0)
    print(f"Durasi: {dur:.0f} dtk", flush=True)
    if dur < 480:
        sys.exit("BATAL: durasi < 480 dtk")

    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != CHANNEL_ID:
        sys.exit("BATAL: channel aktif bukan Cosmic Unknown!")

    body = {
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": TAGS,
            "categoryId": "28",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": PUBLISH_AT,
            "selfDeclaredMadeForKids": False,
        },
    }
    size = os.path.getsize(VIDEO)
    print(f"File: {size/1e6:.1f} MB", flush=True)
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)},
               timeout=60)
    if r.status_code not in (200, 201):
        txt = r.text[:500]
        print("INIT GAGAL:", r.status_code, txt)
        low = txt.lower()
        if r.status_code == 403 and ("uploadlimitexceeded" in low or "daily" in low
                                    or "limit" in low or "batas" in low):
            print("DAILY_LIMIT_DETECTED")
            sys.exit(20)
        sys.exit(10)
    up_url = r.headers["Location"]
    print("upload session OK", flush=True)

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
                print("UPLOAD SELESAI:", vid["id"], flush=True)
                print("URL: https://youtu.be/" + vid["id"], flush=True)
                out = {"id": vid["id"], "url": "https://youtu.be/" + vid["id"],
                       "publishAt": PUBLISH_AT, "title": TITLE}
                json.dump(out, open(OUT_JSON, "w"), indent=1)
                return
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                else:
                    offset = end + 1
                f.seek(offset)
                print(f"... {offset/1e6:.0f}/{size/1e6:.0f} MB", flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:300])
                sys.exit(11)


if __name__ == "__main__":
    main()
