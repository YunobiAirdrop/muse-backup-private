#!/usr/bin/env python3
"""Upload LONG 'The Payphone at Mile 61' (produksi 2026-10-13) via YouTube Data API,
terjadwal 2026-10-15 07:00 WIB. Channel verify by ID. Thumbnail via thumbnails.set.
Gagal karena limit -> antrean retry JSON. Jalankan via yt-growth venv."""
import json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session, yt_get

BASE = os.path.expanduser("~/workspace/youtube-otomatis/horror-en")
RETRY_DIR = os.path.expanduser("~/workspace/youtube-otomatis/retry-queue")
NOW_ISO = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

VIDEO = os.path.join(BASE, "video/2026-10-13.mp4")
THUMB = os.path.join(BASE, "thumbnail-2026-10-13.jpg")
TITLE = "The Payphone at Mile 61"
DESC = """A dead payphone rang at 3:33 in the morning — and the caller ID showed my mother's phone number. She had been dead for eleven years.

I'm Jack Doyle. For three years I worked the night shift at Mile 61, a gas station off Interstate 40 with forty miles of nothing on either side. Bolted to the brick wall by the restrooms sat a gray payphone that had been dead since 1994. Everybody in the county knew it was dead. Then, on October the fourteenth, it rang.

Honestly, this one genuinely scared me, because it happened to me. The voice on that line warned me about a leaking gas pump, a card skimmer, a woman being followed — and it was right every single time. But on the fourteenth night, it told me who it was. And what happens when it finally counts down to one.

CHAPTERS:
0:00 The 3:33 Call
0:24 I Am Jack Doyle
0:50 The Night It Rang
1:16 I Picked It Up
1:49 This One Genuinely Scared Me
2:08 The Black Pickup
2:41 Pump Four Is Leaking
3:23 The Blue Truck
4:07 Night Eleven
4:41 The Man Who Did Not Lock His Door
5:09 The Handwriting Was Not Mine
5:46 He Walks In
6:09 He Was Me
6:53 I Quit That Morning
7:09 It Rang Again

If this one got under your skin, subscribe to Midnight Dread Tales for a new horror story every night. Tell me in the comments: would YOU have picked up?

More horror: https://www.youtube.com/@TalesOfDreadTV

#horrorstories #scarystories #creepypasta #truehorror #foryou"""
TAGS = ["payphone horror", "haunted payphone", "horror stories", "scary stories",
        "night shift horror", "gas station horror", "creepypasta", "3am horror",
        "phone call horror", "midnight dread tales", "horror narration",
        "scary story to fall asleep", "true scary stories", "desert horror",
        "doppelganger horror", "mysterious phone calls", "horror stories reddit",
        "haunted highway", "dread", "never pick up"]
PUBLISH_AT = "2026-10-15T00:00:00.000Z"  # 2026-10-15 07:00 WIB
EXPECTED_CID = "UCR7uhocCg9YZM7-Qoi1sVGA"

def queue_retry(sebab):
    q = {"channel": "horror-en",
         "video_path": VIDEO,
         "instruksi_path": os.path.join(BASE, "upload-instruksi-2026-10-14.md"),
         "slot_target": "2026-10-16 07:00 WIB",
         "gagal_pada": NOW_ISO,
         "sebab": sebab,
         "judul": TITLE}
    p = os.path.join(RETRY_DIR, "horror-en-2026-10-14.json")
    json.dump(q, open(p, "w"), ensure_ascii=False, indent=1)
    print("  -> antrean:", p)

def main():
    s = api_session("horror-en")
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"])
    if ch["id"] != EXPECTED_CID:
        print("BATAL: channel aktif BUKAN Midnight Dread Tales!")
        return 2

    pl = yt_get("horror-en", "/playlistItems",
                {"playlistId": "UU" + EXPECTED_CID[2:], "part": "snippet", "maxResults": 20})
    for it in pl.get("items", []):
        if TITLE.lower() in it["snippet"]["title"].lower():
            print("SUDAH ADA di channel, skip upload:", it["snippet"]["title"])
            return 0

    print("Uploading", os.path.basename(VIDEO), f"({os.path.getsize(VIDEO)/1e6:.1f} MB)...")
    body = {"snippet": {"title": TITLE, "description": DESC, "tags": TAGS, "categoryId": "27"},
            "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                       "selfDeclaredMadeForKids": False}}
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"}, json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(VIDEO))}, timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:300])
        queue_retry(f"init {r.status_code}: {r.text[:200]}")
        return 1
    up_url = r.headers["Location"]
    size = os.path.getsize(VIDEO); offset = 0; vid = None; fail = None
    with open(VIDEO, "rb") as f:
        while offset < size:
            data = f.read(8 * 1024 * 1024)
            end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": f"bytes {offset}-{end}/{size}"}, timeout=300)
            if rr.status_code in (200, 201):
                vid = rr.json()["id"]; break
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
            else:
                fail = f"chunk {rr.status_code}: {rr.text[:200]}"; break
    if not vid:
        print("GAGAL:", fail)
        queue_retry(fail or "upload tak selesai")
        return 1
    print("SELESAI:", vid, "https://youtu.be/" + vid)
    with open(THUMB, "rb") as f:
        tr = s.post(f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                    params={"videoId": vid},
                    headers={"Content-Type": "image/jpeg"}, data=f.read(), timeout=60)
    print("thumbnail:", tr.status_code)
    json.dump({"id": vid, "url": "https://youtu.be/" + vid, "judul": TITLE,
               "jadwal": "2026-10-15 07:00 WIB", "file": VIDEO},
              open(os.path.join(BASE, "upload-status-2026-10-14.json"), "w"), ensure_ascii=False, indent=1)
    return 0

sys.exit(main())
