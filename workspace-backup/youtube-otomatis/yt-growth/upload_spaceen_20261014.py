#!/usr/bin/env python3
"""Upload Cosmic Unknown long Black Hole via Data API (space-en).
Dipakai karena staging file browser rusak (insufficient live capacity)."""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import api_session

SLUG = "space-en"
VIDEO = os.path.expanduser("~/workspace/youtube-otomatis/space-en/video/2026-10-11.mp4")
TITLE = "What Happens If You Fall Into a Black Hole?"
DESCRIPTION = """You're falling. Feet first, head last, straight toward the darkest thing in the universe \u2014 and in a few minutes you will cross a boundary from which nothing has ever returned. It blows my mind that the universe has a force so extreme it can unravel a human body atom by atom. In this episode of Cosmic Unknown, Captain Nova takes the fall with you: spaghettification, time slowing to a crawl, the event horizon, the singularity where physics gives up, Sagittarius A* in our own backyard, TON 618 at 66 billion suns, Hawking radiation, and the wild idea that black holes might be seeds of new universes. Sources woven through the episode: Einstein's general relativity, Hawking's 1974 evaporation work, and the Event Horizon Telescope's first black hole image (April 10, 2019).

CHAPTERS:
0:00 You're Falling Into a Black Hole
0:27 What Is Inside a Black Hole?
0:51 Spaghettification: Stretched Like Taffy
1:13 Time Itself Slows Down
1:39 Crossing the Event Horizon
2:03 The Singularity: Where Physics Breaks
2:28 Sagittarius A*: The Giant in Our Backyard
2:48 TON 618: 66 Billion Suns
3:09 Subscribe for Daily Cosmic Mysteries
3:39 Hawking Radiation: Black Holes Evaporate
4:04 The Information Paradox
4:31 The First Photo: April 10, 2019
4:59 Black Holes Sculpt Galaxies
5:24 Could Anyone Survive the Fall?
5:55 Math That Predicted Everything
6:22 Are Black Holes Seeds of New Universes?
6:51 The Final Fall
7:17 Would YOU Take the Fall?

\U0001f514 Subscribe to Cosmic Unknown for a new cosmic mystery every day!

#space #universe #cosmos #blackhole #astronomy #foryou"""
TAGS = ["black hole", "event horizon", "spaghettification", "sagittarius a",
        "ton 618", "hawking radiation", "space documentary", "cosmos",
        "universe", "astronomy", "deep space", "space mysteries"]
PUBLISH_AT = "2026-10-15T00:00:00.000Z"  # 15 Okt 2026 07:00 WIB


def main():
    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != "UCQnUeh4-2AKgCsV_cjgUv4w":
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
        print("INIT GAGAL:", r.status_code, r.text[:500])
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
                json.dump(out, open(os.path.expanduser(
                    "~/workspace/youtube-otomatis/space-en/upload-2026-10-14-api.json"), "w"), indent=1)
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
