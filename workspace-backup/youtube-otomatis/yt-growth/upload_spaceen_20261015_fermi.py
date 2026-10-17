#!/usr/bin/env python3
"""Upload Cosmic Unknown long Fermi Paradox via Data API (space-en).
Pola disalin dari upload_spaceen_20261015.py (sukses).
CATATAN: via API tidak bisa centang AI disclosure / comments eksplisit /
custom thumbnail — itu tetap butuh sesi Studio manual.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import api_session

SLUG = "space-en"
CHANNEL_ID = "UCQnUeh4-2AKgCsV_cjgUv4w"
VIDEO = os.path.expanduser("~/workspace/youtube-otomatis/space-en/video/2026-10-15.mp4")
TITLE = "The Fermi Paradox: Where Is Everybody?"
DESCRIPTION = """In 1950, Enrico Fermi asked a question that still haunts science: the galaxy should be crawling with alien civilizations \u2014 so where IS everybody? It blows my mind that we have been listening to the cosmos for sixty years and heard nothing back. This is the story of the Drake Equation, the terrifying Great Filter, the zoo hypothesis, and the dark forest \u2014 plus the one answer nobody wants to hear: what if we are simply first? Just think about this for a second: you might be watching the most advanced moment the galaxy has ever produced. Watch, then tell me what YOU believe.

CHAPTERS:
0:00 The Question That Broke Science
0:30 Fermi Asks: Where Is Everybody
1:01 The Drake Equation
1:33 400 Billion Stars
2:04 Sixty Years of Silence
2:32 Our Tiny Whisper Bubble
3:09 The Great Filter
3:41 We Are the Miracle
4:19 A Graveyard of Stars
4:55 The Zoo Hypothesis
5:22 The Dark Forest
5:54 They Might Be Here
6:26 The Speed Limit of Reality
6:55 Listening With the Wrong Ears
7:24 What If We Are First
8:01 Do YOU Think We Are Alone
8:27 What the Silence Means
8:49 The Universe Is Still Talking

\U0001f514 Subscribe to Cosmic Unknown for a new cosmic mystery every day!

#space #universe #cosmos #fermiparadox #aliens #foryou"""
TAGS = ["fermi paradox", "where is everybody", "great filter", "drake equation",
        "are we alone in the universe", "alien life", "seti", "dark forest theory",
        "zoo hypothesis", "space documentary", "cosmos", "universe mystery",
        "astronomy", "astrophysics", "extraterrestrial life", "science documentary",
        "universe", "space"]
PUBLISH_AT = "2026-10-17T00:00:00.000Z"  # 17 Okt 2026 07:00 WIB
OUT_JSON = os.path.expanduser("~/workspace/youtube-otomatis/space-en/upload-2026-10-15-fermi-api.json")


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
