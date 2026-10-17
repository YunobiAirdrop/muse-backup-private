#!/usr/bin/env python3
"""Upload 3 Titanic shorts ke Echoes of History Channel via YouTube Data API v3.
Dipakai cron history-en-harian 2026-10-14. Verifikasi channel dulu (WAJIB),
lalu upload resumable satu per satu. Jika kena batas harian/kuota -> berhenti,
tulis laporan parsial (aturan anti-mogok: jangan retry, antrekan ke retry-queue).
"""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

BASE = os.path.expanduser("~/workspace/youtube-otomatis/history-en")
PUBLISH_AT = "2026-10-15T00:00:00.000Z"  # = 2026-10-15 07:00 WIB

SHORTS = [
    {
        "key": "s1",
        "file": f"{BASE}/shorts/2026-10-13-s1.mp4",
        "judul": "The Night Titanic Hit the Iceberg #shorts #history #documentary #foryou",
        "deskripsi": (
            "At 11:40 PM on April 14, 1912, the RMS Titanic struck an iceberg in the North Atlantic. "
            "Warnings had been ignored all day - and in less than three hours, the 'unsinkable' ship was gone.\n\n"
            "What strikes me most about this story is how avoidable it all was: a calmer sea, a few more minutes, "
            "and the story ends differently. Imagine being there - the engines stopping, the band playing, "
            "the lifeboats going down half-empty.\n\n"
            "If these true stories move you, subscribe to Echoes of History Channel - a new true story every single day."
        ),
        "tags": ["Titanic", "History", "Shorts", "Documentary", "Shipwreck",
                 "Titanic1912", "TrueStory", "HistoryFacts", "EchoesOfHistory"],
    },
    {
        "key": "s2",
        "file": f"{BASE}/shorts/2026-10-13-s2.mp4",
        "judul": "The Ship That Watched Titanic Sink #shorts #history #documentary #foryou",
        "deskripsi": (
            "Nineteen kilometers from the sinking Titanic, the SS Californian sat still in the ice field. "
            "Her radio operator was asleep. Her crew saw the distress rockets - and did nothing.\n\n"
            "What strikes me most about this story is the cruelty of proximity: rescue was so close, yet so far. "
            "Imagine being there - watching lights blink out across the water, never knowing what they meant.\n\n"
            "If these true stories move you, subscribe to Echoes of History Channel - a new true story every single day."
        ),
        "tags": ["Titanic", "History", "Shorts", "Documentary", "Shipwreck",
                 "Titanic1912", "TrueStory", "HistoryFacts", "EchoesOfHistory"],
    },
    {
        "key": "s3",
        "file": f"{BASE}/shorts/2026-10-13-s3.mp4",
        "judul": "Titanic's Final 20 Minutes #shorts #history #documentary #foryou",
        "deskripsi": (
            "At 2:00 AM on April 15, 1912, the Titanic broke in two and plunged into the freezing Atlantic. "
            "Fifteen hundred souls were lost - and the band played until the very end.\n\n"
            "What strikes me most is the courage in those final minutes: musicians, officers, passengers who chose "
            "dignity over panic. Imagine being there - the deck tilting, the lights flickering, the ship standing "
            "vertical before the sea swallowed her.\n\n"
            "If these true stories move you, subscribe to Echoes of History Channel - a new true story every single day."
        ),
        "tags": ["Titanic", "History", "Shorts", "Documentary", "Shipwreck",
                 "Titanic1912", "TrueStory", "HistoryFacts", "EchoesOfHistory"],
    },
]

LIMIT_REASONS = {"uploadLimitExceeded", "dailyLimitExceeded", "quotaExceeded",
                 "rateLimitExceeded", "userRateLimitExceeded"}


def limit_error(body_text):
    try:
        errs = json.loads(body_text).get("error", {}).get("errors", [])
    except Exception:
        return None
    for e in errs:
        r = e.get("reason", "")
        if r in LIMIT_REASONS or "limit" in r.lower() or "quota" in r.lower():
            return r or e.get("message", "limit")
    return None


def upload_one(s, meta):
    video = meta["file"]
    if not os.path.exists(video):
        return {"key": meta["key"], "ok": False, "error": "file tidak ada: " + video}
    body = {
        "snippet": {"title": meta["judul"], "description": meta["deskripsi"],
                    "tags": meta["tags"], "categoryId": "27"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(video))},
               timeout=60)
    if r.status_code not in (200, 201):
        lr = limit_error(r.text)
        return {"key": meta["key"], "ok": False,
                "error": ("LIMIT:" + lr) if lr else f"init {r.status_code}: {r.text[:200]}"}
    up_url = r.headers["Location"]
    size = os.path.getsize(video)
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
                return {"key": meta["key"], "ok": True, "video_id": vid,
                        "url": "https://youtu.be/" + vid, "judul": meta["judul"]}
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = (int(rng.split("-")[1]) + 1) if rng else (end + 1)
                f.seek(offset)
            else:
                lr = limit_error(rr.text)
                return {"key": meta["key"], "ok": False,
                        "error": ("LIMIT:" + lr) if lr else f"chunk {rr.status_code}: {rr.text[:200]}"}
    return {"key": meta["key"], "ok": False, "error": "upload tidak selesai tanpa error jelas"}


def main():
    s = api_session("history-en")
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != "UCCBGIbsfMo2TmyhbUzHxD0A" or \
            "Echoes of History" not in ch["snippet"]["title"]:
        print("BATAL: channel aktif bukan Echoes of History Channel!", flush=True)
        sys.exit(2)
    hasil = []
    for meta in SHORTS:
        print("UPLOAD", meta["key"], "...", flush=True)
        res = upload_one(s, meta)
        hasil.append(res)
        print(json.dumps(res, ensure_ascii=False), flush=True)
        if not res["ok"] and res["error"].startswith("LIMIT:"):
            print("LIMIT KENA -> berhenti, sisanya masuk retry-queue", flush=True)
            break
    print("HASIL:" + json.dumps(hasil, ensure_ascii=False))
    return 0 if all(h.get("ok") for h in hasil) else 3


if __name__ == "__main__":
    sys.exit(main())
