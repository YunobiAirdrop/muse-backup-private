#!/usr/bin/env python3
"""Upload API 3 shorts InkTime (potongan long 2026-10-15 Alexandria).
Channel: InkTime UCoZl5OaqjXSVkE4S96RY8_g. Terjadwal 2026-10-19 07:00 WIB.
Pola: upload_api_2026-10-15.py (API-first, verifikasi channel ID, private+publishAt).
Hashtag: format lama 4 hashtag (aturan 5 hashtag user 2026-10-18 berlaku mulai produksi besok).
"""
import json, os, sys, time

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "inktime"
CHANNEL_ID = "UCoZl5OaqjXSVkE4S96RY8_g"
PUBLISH_AT = "2026-10-19T00:00:00.000Z"  # 19 Okt 2026 07:00 WIB
PLAYLIST_ID = "PLIPkgd0Pz5Fk"  # "Ancient History" (dibuat saat upload long 10-15)
BASE = os.path.expanduser("~/workspace/youtube-otomatis/inktime/shorts")

SHORTS = [
    {"file": "2026-10-15-s1.mp4",
     "title": "The Library of Alexandria Never Burned Down #shorts #history #explainer #foryou",
     "description": "The greatest library of the ancient world did NOT burn down in one dramatic night of flames \u2014 it died slowly, quietly, while almost nobody noticed. Hundreds of thousands of scrolls, gone piece by piece over centuries. Full story in the long video \"The Library of Alexandria: What We Actually Lost\" on the InkTime channel. Sources: Canfora, L. (1990) The Vanished Library, UC Press; El-Abbadi, M. (1992) The Life and Fate of the Ancient Library of Alexandria, UNESCO/UNDP."},
    {"file": "2026-10-15-s2.mp4",
     "title": "He Measured the Earth With a Stick #shorts #history #explainer #foryou",
     "description": "Over 2,200 years ago, a librarian in Alexandria measured the entire planet using nothing but a stick, a well, and shadows \u2014 and got it almost exactly right. His name was Eratosthenes, and he ran the greatest library on Earth. Full story in the long video \"The Library of Alexandria: What We Actually Lost\" on the InkTime channel. Sources: MacLeod, R. ed. (2000) The Library of Alexandria, I.B. Tauris; Casson, L. (2001) Libraries in the Ancient World, Yale UP."},
    {"file": "2026-10-15-s3.mp4",
     "title": "90 Plays Written, Only 7 Survived #shorts #history #explainer #foryou",
     "description": "The ancient playwright Sophocles wrote around 120 plays. Only 7 survived. Across the whole ancient world, countless masterpieces vanished \u2014 burned, rotted, or simply never copied again. What we lost at Alexandria is a warning: knowledge is not automatically safe. Full story in the long video \"The Library of Alexandria: What We Actually Lost\" on the InkTime channel. Sources: Canfora, L. (1990) The Vanished Library, UC Press; Strabo, Geography 17.1.8."},
]

def is_limit(resp):
    return resp.status_code == 403 and ("uploadLimitExceeded" in resp.text or "exceeded" in resp.text.lower())

def already_live(s, title):
    """Cek duplikat: cari judul di channel via search API."""
    try:
        r = s.get("https://www.googleapis.com/youtube/v3/search",
                  params={"part": "snippet", "channelId": CHANNEL_ID, "q": title[:60],
                          "type": "video", "maxResults": 5}, timeout=30)
        if r.status_code != 200:
            return False
        for it in r.json().get("items", []):
            if it["snippet"]["title"].strip().lower() == title.strip().lower():
                return it["id"]["videoId"]
    except Exception as e:
        print("CEK DUPLIKAT ERROR:", e, flush=True)
    return False

def upload_one(s, meta):
    path = os.path.join(BASE, meta["file"])
    if not os.path.exists(path):
        print("FILE HILANG:", path, flush=True); return None
    dup = already_live(s, meta["title"])
    if dup:
        print("SUDAH LIVE (skip):", meta["title"], "->", dup, flush=True)
        return {"id": dup, "url": "https://youtu.be/" + dup, "skipped_duplicate": True}
    body = {
        "snippet": {"title": meta["title"], "description": meta["description"],
                    "categoryId": "27", "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(path))},
               timeout=60)
    if is_limit(r):
        print("LIMIT_HARIAN:", r.text[:300], flush=True); sys.exit(20)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:500], flush=True); sys.exit(10)
    up_url = r.headers["Location"]
    size = os.path.getsize(path); chunk = 8 * 1024 * 1024; vid = None
    with open(path, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk); end = offset + len(data) - 1
            for attempt in range(4):
                try:
                    rr = s.put(up_url, data=data,
                               headers={"Content-Length": str(len(data)),
                                        "Content-Range": f"bytes {offset}-{end}/{size}"},
                               timeout=300)
                    break
                except Exception as e:
                    print(f"chunk {offset} attempt {attempt+1}: {e}", flush=True)
                    time.sleep(5 * (attempt + 1))
            else:
                print("CHUNK GAGAL TOTAL", flush=True); sys.exit(11)
            if rr.status_code in (200, 201):
                vid = rr.json(); break
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1; f.seek(offset); continue
                offset = end + 1
            else:
                print("UPLOAD GAGAL:", rr.status_code, rr.text[:500], flush=True); sys.exit(12)
    if not vid:
        print("UPLOAD TIDAK SELESAI", flush=True); sys.exit(13)
    vid_id = vid["id"]
    print("UPLOAD SELESAI:", meta["file"], vid_id, flush=True)
    try:
        ri = s.post("https://www.googleapis.com/youtube/v3/playlistItems",
                    params={"part": "snippet"},
                    json={"snippet": {"playlistId": PLAYLIST_ID,
                                      "resourceId": {"kind": "youtube#video", "videoId": vid_id}}},
                    timeout=30)
        print("PLAYLIST ITEM:", ri.status_code, flush=True)
    except Exception as e:
        print("PLAYLIST ERROR:", e, flush=True)
    return {"id": vid_id, "url": "https://youtu.be/" + vid_id}

def main():
    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != CHANNEL_ID:
        sys.exit("BATAL: channel aktif bukan InkTime!")
    out = {}
    for meta in SHORTS:
        out[meta["file"]] = upload_one(s, meta)
    print("HASIL:", json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
