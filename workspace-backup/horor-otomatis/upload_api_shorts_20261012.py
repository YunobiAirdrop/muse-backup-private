#!/usr/bin/env python3
"""Upload 3 Shorts horor 2026-10-10 via YouTube Data API v3 (resumable).
AI disclosure TIDAK didukung API -> set manual via Studio setelahnya.
Channel diverifikasi via ID UCUEHu-nQXxGuru5Bviy4DKQ sebelum upload apa pun.
"""
import json, os, sys
sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

PUBLISH_AT = "2026-10-13T12:00:00.000Z"  # 2026-10-13 19:00 WIB
LONG_URL = "https://youtu.be/U6F-BbZ1Lns"
SHORTS = [
    ("/home/hatch/workspace/horor-otomatis/shorts/2026-10-10-s1.mp4",
     "Namaku Ada di Daftar Korban 2004! | Suster Ngesot #shorts #horor #ceritahoror #foryou",
     "Cream JRG Original BPOM 30gr - Rp28.000: https://s.shopee.co.id/9V1w99dZY0"),
    ("/home/hatch/workspace/horor-otomatis/shorts/2026-10-10-s2.mp4",
     "Hantu Itu Selamatkan Pasienku! | Suster Ngesot #shorts #horor #ceritahoror #foryou",
     "Spion Koso Lipat Universal Motor - Rp59.999: https://s.shopee.co.id/3qNZOxWSZe"),
    ("/home/hatch/workspace/horor-otomatis/shorts/2026-10-10-s3.mp4",
     "Gantian Kamu Jaga Shift! Kata Suster Itu | Suster Ngesot #shorts #horor #ceritahoror #foryou",
     "Sabun Cuci Piring 5 Liter Premium - Rp12.000: https://s.shopee.co.id/2gBc2APRvk"),
]
TAGS = ["cerita horor", "hantu indonesia", "suster ngesot", "rumah sakit angker", "kisah horor", "shorts"]

def upload_one(s, path, title, produk):
    desc = f"Tonton versi lengkapnya di sini: {LONG_URL}\n\n🛒 {produk}"
    body = {"snippet": {"title": title, "description": desc, "tags": TAGS, "categoryId": "27"},
            "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT, "selfDeclaredMadeForKids": False}}
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"}, json=body,
               headers={"X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(os.path.getsize(path))}, timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", path, r.status_code, r.text[:500], flush=True); return None
    up_url = r.headers["Location"]; size = os.path.getsize(path); chunk = 8*1024*1024
    with open(path, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk); end = offset + len(data) - 1
            rr = s.put(up_url, data=data, headers={"Content-Length": str(len(data)), "Content-Range": f"bytes {offset}-{end}/{size}"}, timeout=300)
            if rr.status_code in (200, 201):
                vid = rr.json()["id"]; print("UPLOAD SELESAI:", path, vid, flush=True); return vid
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
            else:
                print("CHUNK GAGAL:", path, rr.status_code, rr.text[:300], flush=True); return None

def main():
    s = api_session("horor")
    r = s.get("https://www.googleapis.com/youtube/v3/channels", params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status(); ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    assert ch["id"] == "UCUEHu-nQXxGuru5Bviy4DKQ", f"BATAL: channel {ch['id']} bukan Kisah Horor!"
    assert "Kisah Horor" in ch["snippet"]["title"]
    results = []
    for path, title, produk in SHORTS:
        vid = upload_one(s, path, title, produk)
        results.append({"file": path, "title": title, "id": vid, "url": f"https://youtube.com/shorts/{vid}" if vid else None})
    print(json.dumps(results, ensure_ascii=False))
    with open("/home/hatch/workspace/horor-otomatis/upload-2026-10-12.json", "w") as f:
        json.dump({"channel": "Kisah Horor", "channel_id": "UCUEHu-nQXxGuru5Bviy4DKQ", "metode": "YouTube Data API v3",
                   "terjadwal": "2026-10-13 19:00 WIB", "ai_disclosure": "manual via browser task (pending)",
                   "long_ref": LONG_URL, "shorts": results}, f, ensure_ascii=False, indent=1)
    if any(x["id"] is None for x in results): sys.exit(2)

if __name__ == "__main__":
    main()
