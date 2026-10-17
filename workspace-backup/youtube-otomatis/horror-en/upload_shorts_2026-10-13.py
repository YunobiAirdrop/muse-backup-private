#!/usr/bin/env python3
"""Upload 3 shorts Watcher (produksi 2026-10-11) via YouTube Data API,
terjadwal 2026-10-14 07:00 WIB. Gagal karena limit/kuota -> tulis antrean retry JSON.
Jalankan via yt-growth venv.
"""
import json, os, sys, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session, yt_get

BASE = os.path.expanduser("~/workspace/youtube-otomatis/horror-en")
RETRY_DIR = os.path.expanduser("~/workspace/youtube-otomatis/retry-queue")
NOW_WIB = datetime.now(timezone.utc).astimezone()
NOW_ISO = NOW_WIB.isoformat(timespec="seconds")

SHORTS = [
    {"file": "shorts/2026-10-11-s1.mp4",
     "title": "The Sentence That Froze Their Blood \U0001f631 #shorts #horror #scarystories #foryou",
     "desc": ("The second Watcher letter knew things it could not possibly know \u2014 including "
              "which bedrooms faced the street. Watch the full true story: https://youtu.be/HHFNynfnmek")},
    {"file": "shorts/2026-10-11-s2.mp4",
     "title": "The Previous Owners Hid ONE Letter \U0001f631 #shorts #horror #scarystories #foryou",
     "desc": ("The family who sold 657 Boulevard got a Watcher letter too \u2014 and never told the buyers. "
              "Watch the full true story: https://youtu.be/HHFNynfnmek")},
    {"file": "shorts/2026-10-11-s3.mp4",
     "title": "The Watcher Was Never Caught \U0001f631 #shorts #horror #scarystories #foryou",
     "desc": ("Three letters, eight months, zero arrests. The Watcher of 657 Boulevard was never caught. "
              "Watch the full true story: https://youtu.be/HHFNynfnmek")},
]
TAGS = ["creepypasta", "ghost stories", "horror", "midnight dread tales", "scary stories", "short horror"]
PUBLISH_AT = "2026-10-14T00:00:00.000Z"  # 2026-10-14 07:00 WIB
EXPECTED_CID = "UCR7uhocCg9YZM7-Qoi1sVGA"

s = api_session("horror-en")
r = s.get("https://www.googleapis.com/youtube/v3/channels",
          params={"mine": "true", "part": "snippet"}, timeout=30)
r.raise_for_status()
ch = r.json()["items"][0]
print("CHANNEL:", ch["snippet"]["title"], ch["id"])
if ch["id"] != EXPECTED_CID:
    sys.exit("BATAL: channel aktif BUKAN Midnight Dread Tales!")

# anti-duplikat: judul sama sudah ada?
pl = yt_get("horror-en", "/playlistItems",
            {"playlistId": "UU" + EXPECTED_CID[2:], "part": "snippet", "maxResults": 20})
ada = [it["snippet"]["title"] for it in pl.get("items", [])]

def queue_retry(short, sebab):
    name = f"horror-en-2026-10-13-{os.path.basename(short['file']).replace('.mp4','')}.json"
    q = {"channel": "horror-en",
         "video_path": os.path.join(BASE, short["file"]),
         "instruksi_path": os.path.join(BASE, "upload-instruksi-shorts-2026-10-13.md"),
         "slot_target": "2026-10-15 07:00 WIB",
         "gagal_pada": NOW_ISO,
         "sebab": sebab,
         "judul": short["title"]}
    p = os.path.join(RETRY_DIR, name)
    json.dump(q, open(p, "w"), ensure_ascii=False, indent=1)
    print("  -> antrean:", p)

ok, gagal = [], []
for sh in SHORTS:
    path = os.path.join(BASE, sh["file"])
    if any(sh["title"][:30] in t[:35] for t in ada):
        print(sh["file"], "-> SUDAH ADA di channel, skip"); continue
    print("Uploading", sh["file"], f"({os.path.getsize(path)/1e6:.1f} MB)...")
    body = {"snippet": {"title": sh["title"], "description": sh["desc"], "tags": TAGS, "categoryId": "27"},
            "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                       "selfDeclaredMadeForKids": False}}
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"}, json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(path))}, timeout=60)
    if r.status_code not in (200, 201):
        txt = r.text[:300]
        print("  INIT GAGAL:", r.status_code, txt)
        queue_retry(sh, f"init {r.status_code}: {txt}")
        gagal.append(sh["file"]); continue
    up_url = r.headers["Location"]
    size = os.path.getsize(path); offset = 0; vid = None; fail = None
    with open(path, "rb") as f:
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
    if vid:
        print("  SELESAI:", vid, "https://youtu.be/" + vid)
        ok.append((sh["file"], vid))
    else:
        print("  GAGAL:", fail)
        queue_retry(sh, fail or "upload tak selesai")
        gagal.append(sh["file"])

print(f"\nRINGKASAN: {len(ok)} sukses, {len(gagal)} gagal -> {gagal}")
