#!/usr/bin/env python3
"""Upload LONG Alexandria (produksi 2026-10-18) ke Lost Empires via YouTube Data API v3.
Run: empires-en-harian 2026-10-19 14:15 WIB (hari LONG; upload-terakhir=shorts:2026-10-18).
Terjadwal 2026-10-20 07:00 WIB (= 2026-10-20T00:00:00Z).
Verifikasi channel WAJIB: Lost Empires UCd2wADmj47v3XCPcCpk-fSg; batal kalau bukan.
AI disclosure 'Altered content' TIDAK didukung API -> dicentang via Studio setelahnya (pending).
Kena batas harian -> tulis antrean retry-queue JSON, JANGAN retry saat itu juga.
"""
import json, os, sys, datetime

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

BASE = os.path.expanduser("~/workspace/youtube-otomatis/empires-en")
VIDEO = os.path.join(BASE, "video/alexandria-2026-10-18-upload.mp4")
THUMB = os.path.join(BASE, "thumbnail/thumb-alexandria-2026-10-18.jpg")
PUBLISH_AT = "2026-10-20T00:00:00.000Z"  # BESOK 07:00 WIB
EXPECT_ID = "UCd2wADmj47v3XCPcCpk-fSg"

TITLE = "Alexandria: The Day Humanity's Memory Burned"

DESC = """Half a million books. One night of fire. And a mystery we're still trying to solve.

I stood on the corniche of Alexandria watching the same harbor Alexander's ships once used \u2014 and I couldn't stop thinking about what vanished here. The Great Library of Alexandria wasn't just a building. For 600 years it was humanity's backup drive: every ship searched, every scroll copied, the world's first search engine invented on its steps.

In this episode of Lost Empires, I trace the library from Alexander's wild dream to Caesar's torch, from Eratosthenes measuring the Earth with a stick to Cleopatra's last lamplit evenings \u2014 and the uncomfortable truth that the fire wasn't the whole story.

CHAPTERS:
0:00 The Night We Lost Everything
0:21 Alexandria Today
0:47 One Scroll to Save
1:04 Alexander's Dream
1:29 The Wild Idea
1:55 The First Copyright Pirates
2:22 Inside the Brain of the World
2:48 The First Search Engine
3:12 Measuring the Earth
3:39 Medicine Is Born Here
4:04 Paid to Wonder
4:29 The Fire
4:48 48 BC: Caesar's Torch
5:15 Midnight at the Harbor
5:39 The Slow Death
6:07 What We Lost
6:31 A Scroll Could Rewrite History
6:58 Cleopatra's Last Light
7:23 The Sunken Library
7:48 The Digs Go On
8:11 Sentences from the Fire
8:31 The Library Rises Again
8:55 Memory Is a Choice
9:19 Next: Pompeii

SOURCES & FURTHER READING:
- Lionel Casson, "Libraries in the Ancient World"
- Encyclopaedia Britannica: Library of Alexandria
- Bibliotheca Alexandrina \u2014 bibalex.org
- Freesound.org (CC0): digging (kyles), trowel work (be_a_hero_not_a_patriot), crow (nigelcoop); OrangeFreeSounds (free): birds ambience, wind; CC BY 4.0: brick slide (DanielMarais) via Freesound

If the fire of Alexandria moved you, watch what a volcano did to an entire Roman city in a single morning \u2014 our Pompeii story: https://www.youtube.com/watch?v=xN8si7OLEIc

The fire is coming and you can save exactly ONE scroll. What would you choose? Tell me in the comments \u2014 I read every single one.

#butifyourcloseyoureyesmeme #history #archaeology #mystery #foryou"""

TAGS = ["library of alexandria", "ancient history", "lost library",
        "alexandria egypt", "ptolemy", "cleopatra", "eratosthenes",
        "ancient egypt", "history documentary", "lost empires",
        "archaeology", "ancient civilizations", "julius caesar",
        "hypatia", "mysteries of history"]

LIMIT_HINTS = ["daily limit", "uploadLimitExceeded", "quotaExceeded",
               "exceeded", "batas upload harian", "too many recent uploads"]


def queue_retry(sebab):
    q = {"channel": "Lost Empires (@AncientEmpiresTV)",
         "video_path": VIDEO,
         "instruksi_path": os.path.join(
             BASE, "meta/instruksi-upload-long-2026-10-19.md"),
         "slot_target": "2026-10-20 07:00 WIB",
         "gagal_pada": datetime.datetime.now(
             datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
         "sebab": sebab}
    os.makedirs(os.path.expanduser("~/workspace/youtube-otomatis/retry-queue"),
                exist_ok=True)
    qp = os.path.expanduser(
        "~/workspace/youtube-otomatis/retry-queue/empires-en-2026-10-19.json")
    json.dump(q, open(qp, "w"), indent=1, ensure_ascii=False)
    print("ANTREAN RETRY ditulis:", qp, flush=True)


def is_limit(txt):
    t = txt.lower()
    return any(h.lower() in t for h in LIMIT_HINTS)


def main():
    s = api_session("empires-en")
    # 1. verifikasi channel SEBELUM upload
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL: %s %s" % (ch["snippet"]["title"], ch["id"]), flush=True)
    if ch["id"] != EXPECT_ID or "Lost Empires" not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Lost Empires!")

    size = os.path.getsize(VIDEO)
    body = {
        "snippet": {"title": TITLE, "description": DESC, "tags": TAGS,
                    "categoryId": "27", "defaultLanguage": "en"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)},
               timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:500], flush=True)
        if is_limit(r.text):
            queue_retry("batas upload harian (init): %s" % r.text[:200])
        sys.exit(10)
    up_url = r.headers["Location"]
    print("upload session OK, size:", size, flush=True)

    vid = None
    chunk = 8 * 1024 * 1024
    with open(VIDEO, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": "bytes %d-%d/%d"
                                % (offset, end, size)},
                       timeout=300)
            if rr.status_code in (200, 201):
                vid = rr.json()
                print("UPLOAD SELESAI:", vid["id"], flush=True)
                break
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
                print("  ... %d/%d" % (offset, size), flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:500], flush=True)
                if is_limit(rr.text):
                    queue_retry("batas upload harian (chunk): %s"
                                % rr.text[:200])
                sys.exit(11)
    if not vid:
        sys.exit("upload tidak selesai tanpa error jelas")

    video_id = vid["id"]
    # 2. pasang thumbnail
    with open(THUMB, "rb") as f:
        tr = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                    params={"videoId": video_id},
                    data=f.read(),
                    headers={"Content-Type": "image/jpeg"}, timeout=60)
    print("THUMBNAIL:", tr.status_code, flush=True)

    out = os.path.join(BASE, "upload-2026-10-19.json")
    json.dump({"run": "empires-en-harian 2026-10-19 14:15 WIB",
               "channel": "Lost Empires (@AncientEmpiresTV) UCd2wADmj47v3XCPcCpk-fSg",
               "video_id": video_id,
               "url": "https://youtu.be/" + video_id,
               "judul": TITLE,
               "publishAt": PUBLISH_AT,
               "thumbnail_status": tr.status_code,
               "ai_disclosure": "PENDING: centang 'Altered content' via YouTube Studio (API tidak support)"},
              open(out, "w"), indent=1, ensure_ascii=False)
    print("URL: https://youtu.be/" + video_id)
    print("Tersimpan:", out)


if __name__ == "__main__":
    main()
