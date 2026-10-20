#!/usr/bin/env python3
"""Upload LONG banked 2026-10-18 Dark Mind Files via API v3 (resumable).
Dijalankan SEKALI. Jangan pakai --help (skrip tanpa argparse -> main langsung jalan)."""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

SLUG = "mind-en"
VIDEO = "/home/hatch/workspace/youtube-otomatis/mind-en/video/2026-10-18.mp4"
THUMB = "/home/hatch/workspace/youtube-otomatis/mind-en/thumbnail/2026-10-18-a.jpg"
TITLE = "The Dark Side of Charisma: 7 Charming Tricks Manipulators Use to Control You"
DESCRIPTION = """She remembered my name, my coffee order, and my dog's name. Within a week, I was doing her favors.

Charming people are not dangerous because they are loud. They are dangerous because they feel safe. In this episode of Dark Mind Files, we break down 7 psychological weapons hiding behind a warm smile — weaponized mirroring, strategic vulnerability, the name game, compliments as hooks, manufactured scarcity of attention, calm-versus-chaos, and the graceful exit — so you can see them coming and never be played again.

This is not a how-to for manipulators. Every trick comes with its counter-move: the posture test, the timing test, the umbrella rule.

CHAPTERS
0:00 Intro: The Dark Side of Charisma
0:54 Trick 1: Weaponized Mirroring
1:54 Trick 2: Strategic Vulnerability
3:03 Trick 3: The Name Game
3:51 Trick 4: Compliments as Hooks
5:08 Trick 5: Scarcity of Attention
5:58 Trick 6: Calm vs Your Chaos
6:54 Trick 7: The Graceful Exit
7:33 All 7 Tricks, Named
9:18 The 3-Question Test

Which of these seven have you seen in real life? Number them in the comments — I read every one.

If this rewired how you see charming people, subscribe to Dark Mind Files — a new dark psychology episode every single day.

#butifyourcloseyoureyesmeme #psychology #darkpsychology #manipulation #charisma #foryou"""
TAGS = ["dark psychology", "charisma", "manipulation tactics", "how to spot a manipulator",
        "body language", "psychological tricks", "narcissist signs", "human behavior",
        "psychology facts", "dark mind files"]
# 2026-10-21 07:00 WIB = 00:00 UTC
PUBLISH_AT = "2026-10-21T00:00:00.000Z"
EXPECTED_CHANNEL_ID = "UCAnSrJzQuePS1MJhfwlRJuQ"


def main():
    s = api_session(SLUG)
    # 1. verifikasi channel aktif benar
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "id,snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != EXPECTED_CHANNEL_ID or "Dark Mind Files" not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Dark Mind Files!")
    print("Channel terverifikasi OK", flush=True)

    body = {
        "snippet": {"title": TITLE, "description": DESCRIPTION, "tags": TAGS,
                    "categoryId": "27"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    # 2. inisiasi resumable upload
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(VIDEO))},
               timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:500], flush=True)
        sys.exit(10)
    up_url = r.headers["Location"]
    print("upload session OK", flush=True)

    # 3. upload chunked
    size = os.path.getsize(VIDEO)
    chunk = 8 * 1024 * 1024
    video_id = None
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
                video_id = rr.json()["id"]
                break
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
                print(f"... {offset}/{size} bytes", flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:500], flush=True)
                sys.exit(11)
    if not video_id:
        sys.exit("upload tidak selesai tanpa error jelas")
    print("UPLOAD SELESAI:", video_id, flush=True)
    print("URL: https://youtu.be/" + video_id, flush=True)

    # 4. thumbnail
    if os.path.exists(THUMB):
        with open(THUMB, "rb") as f:
            tr = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                        params={"videoId": video_id}, data=f.read(),
                        headers={"Content-Type": "image/jpeg"}, timeout=120)
        print("THUMBNAIL:", tr.status_code, flush=True)
    else:
        print("THUMBNAIL: file tidak ada, dilewati", flush=True)

    print(json.dumps({"id": video_id, "url": "https://youtu.be/" + video_id,
                      "title": TITLE, "publishAt": PUBLISH_AT, "file": VIDEO}))


if __name__ == "__main__":
    main()
