#!/usr/bin/env python3
"""Upload 3 SHORTS Dark Mind Files (potongan long 2026-10-18 "The Dark Side of
Charisma: 7 Charming Tricks Manipulators Use to Control You") via YouTube Data API.
Channel: @TheDarkMindFiles-s6i (UCAnSrJzQuePS1MJhfwlRJuQ), akun khususstokyunobi@gmail.com.
Terjadwal: 2026-10-20 07:00 WIB (= 2026-10-20T00:00:00Z = 2026-10-19 19:00 US Eastern).
AI disclosure + komentar ON: browser task lanjutan (sesi ada, tanpa login baru).
Exit 20 = limit harian (tulis retry-queue, JANGAN retry langsung).
Dieksekusi: run terjadwal 2026-10-19.
"""
import json, os, sys, datetime

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "mind-en"
CHANNEL_ID = "UCAnSrJzQuePS1MJhfwlRJuQ"
PUBLISH_AT = "2026-10-20T00:00:00.000Z"  # 2026-10-20 07:00 WIB
TAGS = ["dark psychology", "psychology", "mindset", "shorts", "manipulation tactics",
        "psychology facts", "human behavior", "narcissist signs"]
BASE = os.path.expanduser("~/workspace/youtube-otomatis/mind-en/shorts/2026-10-18")
QDIR = os.path.expanduser("~/workspace/youtube-otomatis/retry-queue")
LONG_TITLE = "The Dark Side of Charisma: 7 Charming Tricks Manipulators Use to Control You"
INSTR = os.path.expanduser("~/workspace/youtube-otomatis/mind-en/meta/upload-instruksi-shorts-2026-10-19.md")

SHORTS = [
    ("short1-mirroring.mp4",
     "They Mirror You on Purpose. Here Is the 5-Second Test #shorts #psychology #mindset #foryou",
     "Your brain reads similarity as safety, so within minutes your guard drops. "
     "Real friends mirror you by accident; manipulators mirror you on purpose. "
     "The test is simple: change your posture suddenly. A real person keeps being "
     "themselves; a manipulator snaps into your new posture within seconds. "
     f"Full video: {LONG_TITLE}, on Dark Mind Files. "
     "Subscribe for a new dark psychology episode every day."),
    ("short2-vulnerability.mp4",
     "The Sad Story Right Before the Ask Is a Setup #shorts #psychology #mindset #foryou",
     "Real vulnerability is messy and badly timed. Strategic vulnerability is smooth, "
     "and the confession always comes right before the ask. That timing is never an "
     "accident. This one hit close to home for me \u2014 I once loaned money to someone "
     "whose sad story I never verified. Money gone. Friendship gone. "
     f"Full video: {LONG_TITLE}, on Dark Mind Files. "
     "Subscribe for a new dark psychology episode every day."),
    ("short3-calmchaos.mp4",
     '"Calm Down" Is How They Win Every Argument #shorts #psychology #mindset #foryou',
     "They stay perfectly still while you get emotional, then say the line: why are "
     "you so upset? Calm down. And just like that, you look like the problem. "
     "Psychologists call it tone policing. I call it losing an argument you were "
     "right to have. "
     f"Full video: {LONG_TITLE}, on Dark Mind Files. "
     "Subscribe for a new dark psychology episode every day."),
]

def queue_item(fname, sebab):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    item = {
        "channel": "mind-en",
        "video_path": os.path.join(BASE, fname),
        "instruksi_path": INSTR,
        "slot_target": "2026-10-20 07:00 WIB",
        "gagal_pada": now.isoformat(),
        "sebab": sebab,
    }
    tag = fname.replace("short", "s").replace(".mp4", "")
    qp = os.path.join(QDIR, f"mind-en-2026-10-19-{tag}.json")
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
        "~/workspace/youtube-otomatis/mind-en/meta/upload-shorts-2026-10-19.json"), "w"),
        indent=1)
    if limited:
        print("LIMIT_HARIAN: antrean ditulis, JANGAN retry langsung", flush=True)
        sys.exit(20)
    print("OK semua", flush=True)

if __name__ == "__main__":
    main()
