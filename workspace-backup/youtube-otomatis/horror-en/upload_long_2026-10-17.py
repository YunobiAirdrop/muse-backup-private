#!/usr/bin/env python3
"""Upload LONG 'The Dashcam on Route 17' (produksi 2026-10-14, rakit 2026-10-17)
via YouTube Data API, terjadwal 2026-10-18 07:00 WIB.
Channel verify by ID. Thumbnail via thumbnails.set.
Chapter timestamps dihitung dari durasi-beat JSON + geser bumper.
Gagal karena limit -> antrean retry JSON. Jalankan via yt-growth venv."""
import json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session, yt_get

BASE = os.path.expanduser("~/workspace/youtube-otomatis/horror-en")
RETRY_DIR = os.path.expanduser("~/workspace/youtube-otomatis/retry-queue")
NOW_ISO = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

VIDEO = os.path.join(BASE, "video/2026-10-14.mp4")
THUMB = os.path.join(BASE, "thumbnail-2026-10-14.jpg")
TITLE = "The Dashcam on Route 17"
PUBLISH_AT = "2026-10-18T00:00:00.000Z"  # 2026-10-18 07:00 WIB
SLOT_TXT = "2026-10-18 07:00 WIB"
EXPECTED_CID = "UCR7uhocCg9YZM7-Qoi1sVGA"
SCARE = {4, 24, 33, 47, 58, 66}
N = 72

CHAPTER_BEATS = [  # (beat mulai, judul)
    (1, "The Empty Highway"), (4, "Someone Else Is Driving"),
    (5, "I Am Dale Mercer"), (10, "The Shortcut Through the Barrens"),
    (15, "Mile Marker 41"), (19, "Mile Marker 48"), (23, "Mile Marker 55"),
    (24, "The Trailer Jackknifed"), (28, "The Curtain Was Swaying"),
    (33, "Do Not Look Back"), (38, "This One Genuinely Scared Me"),
    (43, "The Seal Was Broken"), (47, "The Footprints"),
    (54, "Three Frames of Wrong"), (63, "The Fourth Camera File"),
    (66, "Thanks for the Ride, Dale"), (70, "I Do Not Drive Nights Anymore"),
]

def build_desc():
    dj = json.load(open(os.path.join(BASE, "audio/durasi-beat-2026-10-14.json")))
    S = [3.0]
    for i in range(1, N + 1):
        S.append(S[-1] + (2.2 if i in SCARE else 0.4) + float(dj[f"beat-{i:03d}"]))
    shift, tcut = 0.0, 1e9
    info_p = os.path.join(BASE, "bumper-info-2026-10-14.json")
    if os.path.exists(info_p):
        bi = json.load(open(info_p))
        tcut = float(bi.get("t_cut", 1e9)); shift = float(bi.get("bumper_d", 0))
    def fmt(s):
        s = int(s); return f"{s//60}:{s%60:02d}"
    ch = []
    for b, nama in CHAPTER_BEATS:
        t = S[b - 1]
        if t >= tcut: t += shift
        ch.append(f"{fmt(t)} {nama}")
    ch[0] = "0:00 " + ch[0].split(" ", 1)[1]
    return ("My dashcam recorded four hours of empty highway that night — and in every "
            "single frame, I am dead asleep in the sleeper berth. In the driver's seat, "
            "hands on my wheel, there is someone else.\n\n"
            "I'm Dale Mercer. I drive night freight. One night in the Pine Barrens, a "
            "hitchhiker in a gray hoodie appeared at three different mile markers — "
            "miles apart, minutes apart. Then my CB spoke in my own voice. And the "
            "footage showed me something I will never unsee.\n\n"
            "This one genuinely scared me when I watched it back, because the dashcam "
            "caught what I missed that night. I still think about mile marker 41 every "
            "time I pass a hitchhiker I do not pick up.\n\n"
            "CHAPTERS:\n" + "\n".join(ch) + "\n\n"
            "If this one got under your skin, subscribe to Midnight Dread Tales for a "
            "new horror story every night. Tell me in the comments: would YOU have "
            "stopped at mile marker 41?\n\n"
            "More horror: https://www.youtube.com/@TalesOfDreadTV\n\n"
            "#horrorstories #scarystories #creepypasta #truehorror #foundfootage #foryou")

DESC = build_desc()
TAGS = ["dashcam horror", "trucker horror", "highway horror", "horror stories",
        "scary stories", "creepypasta", "night drive horror", "haunted highway",
        "pine barrens", "hitchhiker horror", "midnight dread tales", "horror narration",
        "scary story to fall asleep", "true scary stories", "doppelganger horror",
        "found footage horror", "dashcam caught", "horror stories reddit",
        "3am horror", "dread"]

def queue_retry(sebab):
    q = {"channel": "horror-en", "video_path": VIDEO,
         "instruksi_path": os.path.join(BASE, "upload-instruksi-2026-10-17.md"),
         "slot_target": SLOT_TXT, "gagal_pada": NOW_ISO, "sebab": sebab,
         "judul": TITLE}
    p = os.path.join(RETRY_DIR, "horror-en-2026-10-17.json")
    json.dump(q, open(p, "w"), ensure_ascii=False, indent=1)
    print("  -> antrean:", p)

def main():
    if not os.path.exists(VIDEO):
        print("BATAL: video belum ada:", VIDEO); return 2
    s = api_session("horror-en")
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"])
    if ch["id"] != EXPECTED_CID:
        print("BATAL: channel aktif BUKAN Midnight Dread Tales!"); return 2
    pl = yt_get("horror-en", "/playlistItems",
                {"playlistId": "UU" + EXPECTED_CID[2:], "part": "snippet", "maxResults": 20})
    for it in pl.get("items", []):
        if TITLE.lower() in it["snippet"]["title"].lower():
            print("SUDAH ADA di channel, skip upload:", it["snippet"]["title"]); return 0
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
        queue_retry(f"init {r.status_code}: {r.text[:200]}"); return 1
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
        queue_retry(fail or "upload tak selesai"); return 1
    print("SELESAI:", vid, "https://youtu.be/" + vid)
    with open(THUMB, "rb") as f:
        tr = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                    params={"videoId": vid},
                    headers={"Content-Type": "image/jpeg"}, data=f.read(), timeout=60)
    print("thumbnail:", tr.status_code)
    json.dump({"id": vid, "url": "https://youtu.be/" + vid, "judul": TITLE,
               "jadwal": SLOT_TXT, "file": VIDEO},
              open(os.path.join(BASE, "upload-status-2026-10-17.json"), "w"),
              ensure_ascii=False, indent=1)
    return 0

sys.exit(main())
