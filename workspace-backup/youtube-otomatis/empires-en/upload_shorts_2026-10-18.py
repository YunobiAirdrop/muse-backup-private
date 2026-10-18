#!/usr/bin/env python3
"""Upload 3 shorts Pompeii (produksi 2026-10-15) ke Lost Empires via Data API v3.
Run: empires-en-harian 2026-10-18 14:11 WIB (hari SHORTS; upload-terakhir=long:2026-10-15).
Terjadwal 2026-10-19 07:00 WIB (= 2026-10-19T00:00:00Z).
Hashtag: aturan user 2026-10-18 — 5 hashtag di AKHIR JUDUL, #butifyourcloseyoureyesmeme
wajib ada, ditutup #foryou.
AI disclosure 'Altered content' TIDAK didukung API -> dicentang via Studio setelahnya.
Cek channel (mine=true) SEBELUM upload; batal kalau bukan Lost Empires.
"""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "empires-en"
BASE = os.path.expanduser("~/workspace/youtube-otomatis/empires-en")
LONG_URL = "https://youtu.be/xN8si7OLEIc"  # Pompeii long
PUBLISH_AT = "2026-10-19T00:00:00.000Z"  # 07:00 WIB 19 Okt 2026
DESC = ("Watch the full story: %s\n\n"
        "A new lost civilization every day \u2014 subscribe to Lost Empires." % LONG_URL)
TAGS = ["pompeii", "shorts", "history", "archaeology", "lost civilization"]
HT = "#butifyourcloseyoureyesmeme #shorts #history #archaeology #foryou"

SHORTS = [
    ("shorts/2026-10-15-s1.mp4",
     "20,000 Died in One Morning \U0001F631 " + HT),
    ("shorts/2026-10-15-s2.mp4",
     "Nothing Outruns the Surge \U0001F30B " + HT),
    ("shorts/2026-10-15-s3.mp4",
     "Bread Survived 2,000 Years \U0001F35E " + HT),
]


def upload_one(s, video_path, title):
    size = os.path.getsize(video_path)
    body = {
        "snippet": {"title": title, "description": DESC,
                    "tags": TAGS, "categoryId": "27"},
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
        return None
    up_url = r.headers["Location"]
    chunk = 8 * 1024 * 1024
    with open(video_path, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": "bytes %d-%d/%d" % (offset, end, size)},
                       timeout=300)
            if rr.status_code in (200, 201):
                vid = rr.json()
                print("OK: %s https://youtu.be/%s" % (vid["id"], vid["id"]), flush=True)
                return vid["id"]
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
                print("... %d/%d bytes" % (offset, size), flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:500], flush=True)
                return None
    print("upload tidak selesai tanpa error jelas", flush=True)
    return None


def main():
    s = api_session(SLUG)
    # 1. verifikasi channel SEBELUM upload
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL: %s %s" % (ch["snippet"]["title"], ch["id"]), flush=True)
    if ch["id"] != "UCd2wADmj47v3XCPcCpk-fSg" or "Lost Empires" not in ch["snippet"]["title"]:
        sys.exit("BATAL: channel aktif bukan Lost Empires!")
    ids = []
    for rel, title in SHORTS:
        p = os.path.join(BASE, rel)
        print("Uploading %s ..." % rel, flush=True)
        print("  judul: %s" % title, flush=True)
        vid = upload_one(s, p, title)
        ids.append({"file": rel, "judul": title, "video_id": vid,
                    "url": ("https://youtu.be/" + vid) if vid else None})
    out = os.path.join(BASE, "upload-2026-10-18-shorts.json")
    json.dump({"run": "empires-en-harian 2026-10-18 14:11 WIB",
               "channel": "Lost Empires (@AncientEmpiresTV) UCd2wADmj47v3XCPcCpk-fSg",
               "publishAt": PUBLISH_AT,
               "ai_disclosure": "WAJIB centang Altered content via Studio (API tidak support)",
               "shorts": ids}, open(out, "w"), indent=1, ensure_ascii=False)
    print("Tersimpan:", out)
    print(json.dumps(ids, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
