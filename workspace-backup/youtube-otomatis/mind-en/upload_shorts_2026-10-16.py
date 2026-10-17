#!/usr/bin/env python3
"""Upload 3 SHORTS Dark Mind Files (potongan long 2026-10-15 "7 Mind Tricks Your
Own Brain Plays on You") via YouTube Data API.
Channel: @TheDarkMindFiles-s6i (UCAnSrJzQuePS1MJhfwlRJuQ), akun khususstokyunobi@gmail.com.
Terjadwal: 2026-10-18 07:00 WIB (= 2026-10-18T00:00:00Z = 2026-10-17 19:00 US Eastern).
AI disclosure + komentar ON: browser task lanjutan (sesi ada, tanpa login baru).
Exit 20 = limit harian (tulis retry-queue, JANGAN retry langsung).
Dieksekusi: run terjadwal 2026-10-16 (telat, jalan 2026-10-17).
"""
import json, os, sys, datetime

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "mind-en"
CHANNEL_ID = "UCAnSrJzQuePS1MJhfwlRJuQ"
PUBLISH_AT = "2026-10-18T00:00:00.000Z"  # 2026-10-18 07:00 WIB
TAGS = ["dark psychology", "psychology", "mindset", "shorts", "cognitive bias",
        "manipulation tactics", "psychology facts", "human behavior"]
BASE = os.path.expanduser("~/workspace/youtube-otomatis/mind-en/shorts/2026-10-15")
QDIR = os.path.expanduser("~/workspace/youtube-otomatis/retry-queue")
LONG_TITLE = "7 Mind Tricks Your Own Brain Plays on You"

SHORTS = [
    ("short1-lawyer.mp4",
     "Your Brain Is a Lawyer, Not a Detective #shorts #psychology #mindset #foryou",
     "Your brain does not search for the truth. It builds a case for what it already "
     "believes \u2014 cherry-picking evidence like a lawyer, never like a detective. "
     f"Full video: {LONG_TITLE}, on Dark Mind Files. "
     "Subscribe for a new dark psychology episode every day."),
    ("short2-sunkcost.mp4",
     "Why You Cannot Quit (It Is Not Your Fault) #shorts #psychology #mindset #foryou",
     "You stay because of everything you already spent \u2014 not because it is still "
     "worth it. The past is a sunk cost, but your brain treats it like an investment. "
     f"Full video: {LONG_TITLE}, on Dark Mind Files. "
     "Subscribe for a new dark psychology episode every day."),
    ("short3-bandwagon.mp4",
     "40 Strangers Cannot Be Wrong. They Can. #shorts #psychology #mindset #foryou",
     "Forty strangers all walking the same way \u2014 your brain whispers they cannot "
     "all be wrong. They can. The bandwagon effect hijacks your judgment in seconds. "
     f"Full video: {LONG_TITLE}, on Dark Mind Files. "
     "Subscribe for a new dark psychology episode every day."),
]

def queue_item(fname, sebab):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    item = {
        "channel": "mind-en",
        "video_path": os.path.join(BASE, fname),
        "instruksi_path": os.path.expanduser(
            "~/workspace/youtube-otomatis/mind-en/meta/upload-instruksi-shorts-2026-10-16.md"),
        "slot_target": "2026-10-18 07:00 WIB",
        "gagal_pada": now.isoformat(),
        "sebab": sebab,
    }
    tag = fname.replace("short", "s").replace(".mp4", "")
    qp = os.path.join(QDIR, f"mind-en-2026-10-16-{tag}.json")
    json.dump(item, open(qp, "w"), indent=1, ensure_ascii=False)
    print("QUEUE:", qp, flush=True)

def upload_one(s, fname, title, desc):
    video = os.path.join(BASE, fname)
    size = os.path.getsize(video)
    # cek duplikat by judul persis
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
    print(f"upload {fname} ({size/1048576:.1f} MB)", flush=True)
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
            if rr.status_code not in (308,):
                return {"error": f"chunk {rr.status_code} {rr.text[:300]}"}
            offset = end + 1
    return {"error": "upload selesai tanpa video id"}

def main():
    s = api_session(SLUG)
    # 1. verifikasi channel aktif (WAJIB sebelum upload)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != CHANNEL_ID or "Dark Mind" not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Dark Mind Files!")
    results, limited = {}, False
    for fname, title, desc in SHORTS:
        res = upload_one(s, fname, title, desc)
        results[fname] = res
        print(fname, "->", json.dumps(res)[:200], flush=True)
        if res.get("limit"):
            limited = True
            queue_item(fname, "Batas upload harian YouTube (uploadLimitExceeded)")
    json.dump(results, open(os.path.expanduser(
        "~/workspace/youtube-otomatis/mind-en/meta/upload-shorts-2026-10-16.json"), "w"),
        indent=1)
    if limited:
        print("LIMIT_HARIAN: antrean ditulis, JANGAN retry langsung", flush=True)
        sys.exit(20)
    print("OK semua", flush=True)

if __name__ == "__main__":
    main()
