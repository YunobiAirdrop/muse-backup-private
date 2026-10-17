#!/usr/bin/env python3
"""Upload 3 Shorts horor 2026-10-13 via YouTube Data API v3 (resumable).
Potongan dari long "CCTV Apartemen Ini Rekam Sosok Aneh Tiap Jam 02.47" (https://youtu.be/-k5qqlU3JR8).
AI disclosure TIDAK didukung API -> set manual via Studio setelahnya.
Channel diverifikasi via ID UCUEHu-nQXxGuru5Bviy4DKQ sebelum upload apa pun.
"""
import json, os, sys
sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

CHANNEL_ID = "UCUEHu-nQXxGuru5Bviy4DKQ"
PUBLISH_AT = "2026-10-16T12:00:00.000Z"  # BESOK 2026-10-16 19:00 WIB
LONG_URL = "https://youtu.be/-k5qqlU3JR8"
BASE = "/home/hatch/workspace/horor-otomatis"

SHORTS = [
    (f"{BASE}/shorts/2026-10-13-s1.mp4",
     "Wajah Sosok di CCTV Itu... Wajahku Sendiri?! | CCTV 02.47 #shorts #horor #ceritahoror #foryou",
     "Alat Rebus Telur Elektrik - Rp155.100: https://s.shopee.co.id/40gzb1K9Fi"),
    (f"{BASE}/shorts/2026-10-13-s2.mp4",
     "4 Satpam Tewas di Pos Ini, Semua Umur 29?! | CCTV 02.47 #shorts #horor #ceritahoror #foryou",
     "New Balance Fresh Foam X 2025 - Rp850.000: https://s.shopee.co.id/1gJ4onHvca"),
    (f"{BASE}/shorts/2026-10-13-s3.mp4",
     "Mereka Bilang: Sekarang Giliranmu Patroli! | CCTV 02.47 #shorts #horor #ceritahoror #foryou",
     "New Balance Fuelcell Rebel V5 - Rp850.000: https://s.shopee.co.id/6VOKZgYrb7"),
]
TAGS = ["cerita horor", "cctv horor", "hantu indonesia", "urban legend indonesia", "kisah horor", "shorts"]

def cek_duplikat(s, judul):
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "contentDetails"}, timeout=30).json()
    upl = r["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    page = None
    while True:
        pr = {"playlistId": upl, "part": "snippet", "maxResults": 50}
        if page: pr["pageToken"] = page
        pl = s.get("https://www.googleapis.com/youtube/v3/playlistItems",
                   params=pr, timeout=30).json()
        for it in pl.get("items", []):
            if it["snippet"]["title"].strip().lower() == judul.strip().lower():
                return "https://youtu.be/" + it["snippet"]["resourceId"]["videoId"]
        page = pl.get("nextPageToken")
        if not page: break
    return None

def upload_one(s, path, title, produk):
    desc = f"Tonton versi lengkapnya di sini: {LONG_URL}\n\n\U0001f6d2 {produk}"
    body = {"snippet": {"title": title, "description": desc, "tags": TAGS,
                        "categoryId": "24", "defaultLanguage": "id"},
            "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                       "selfDeclaredMadeForKids": False}}
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"}, json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(path))}, timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", path, r.status_code, r.text[:500], flush=True)
        return None, f"init:{r.status_code}:{r.text[:200]}"
    up_url = r.headers["Location"]; size = os.path.getsize(path); chunk = 8*1024*1024
    with open(path, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk); end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": f"bytes {offset}-{end}/{size}"}, timeout=300)
            if rr.status_code in (200, 201):
                vid = rr.json()["id"]
                print("UPLOAD SELESAI:", path, vid, flush=True)
                return vid, None
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
            else:
                print("CHUNK GAGAL:", path, rr.status_code, rr.text[:300], flush=True)
                return None, f"chunk:{rr.status_code}:{rr.text[:200]}"
    return None, "unknown"

def main():
    for path, title, _ in SHORTS:
        assert os.path.exists(path) and os.path.getsize(path) > 1_000_000, f"video hilang/kecil: {path}"
    s = api_session("horor")
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    assert ch["id"] == CHANNEL_ID, f"BATAL: channel {ch['id']} bukan Kisah Horor!"
    assert "Kisah Horor" in ch["snippet"]["title"], "BATAL: nama channel bukan Kisah Horor!"
    print("cek duplikat: mulai", flush=True)
    results = []
    for path, title, produk in SHORTS:
        dupe = cek_duplikat(s, title)
        if dupe:
            print("DUPLIKAT, lewati:", title, "->", dupe, flush=True)
            results.append({"file": path, "title": title, "id": None, "duplicate_of": dupe})
            continue
        vid, err = upload_one(s, path, title, produk)
        results.append({"file": path, "title": title,
                        "id": vid,
                        "url": f"https://youtube.com/shorts/{vid}" if vid else None,
                        "error": err})
    print(json.dumps(results, ensure_ascii=False))
    with open(f"{BASE}/upload-2026-10-15-shorts.json", "w") as f:
        json.dump({"publish_at": PUBLISH_AT, "results": results}, f, ensure_ascii=False, indent=1)
    gagal = [x for x in results if not x["id"] and not x.get("duplicate_of")]
    if gagal:
        print("GAGAL:", len(gagal), flush=True)
        sys.exit(2)

if __name__ == "__main__":
    main()
