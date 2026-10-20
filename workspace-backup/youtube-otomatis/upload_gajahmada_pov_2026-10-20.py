#!/usr/bin/env python3
"""Upload POV Gajah Mada 2026-10-20 (LONG saja) ke @ceritarakyat862 via YouTube Data API (resumable).
Terjadwal KAMIS 2026-10-22 19:00 WIB. AI disclosure manual via Studio.
Jalankan: ~/workspace/youtube-otomatis/yt-growth/venv/bin/python upload_gajahmada_pov_2026-10-20.py
"""
import json, os, re, sys

BASE = os.path.expanduser("~/workspace/youtube-otomatis")
sys.path.insert(0, os.path.join(BASE, "yt-growth"))
from auth import api_session, yt_get

CHANNEL_ID = "UC1c8WpKGhFKpUOp5AqVueEg"
MD = os.path.join(BASE, "upload-instruksi-pov-2026-10-20.md")
SLOT = "2026-10-22T12:00:00.000Z"  # Kamis 19:00 WIB
RESULT = os.path.join(BASE, "yt-growth", "hidden_files", "upload-pov-gajahmada-2026-10-20.json")

class QuotaStop(Exception): pass

def parse_md(path):
    t = open(path).read()
    m = re.search(r"## VIDEO LONG.*?File:\s*(\S+).*?Thumbnail:\s*upload\s*(\S+).*?"
                  r"### Judul\n(.+?)\n\n### Deskripsi\n(.+?)\n\n### Tag YouTube\n(.+?)\n", t, re.S)
    assert m, "parse long gagal"
    return {"video": m.group(1), "thumbnail": m.group(2), "judul": m.group(3).strip(),
            "deskripsi": m.group(4).strip(),
            "tags": [x.strip() for x in m.group(5).split(",")]}

def upload_video(s, item, publish_at):
    vp = item["video"]
    size = os.path.getsize(vp)
    print(f"UPLOAD {size/1e6:.1f}MB -> slot {publish_at}", flush=True)
    body = {"snippet": {"title": item["judul"][:100], "description": item["deskripsi"][:5000],
                        "tags": item["tags"][:30], "categoryId": "27",
                        "defaultLanguage": "id", "defaultAudioLanguage": "id"},
            "status": {"privacyStatus": "private", "publishAt": publish_at,
                       "selfDeclaredMadeForKids": False}}
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"}, json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)}, timeout=60)
    if r.status_code == 403 and "quotaExceeded" in r.text: raise QuotaStop(r.text[:200])
    if r.status_code not in (200, 201): raise RuntimeError(f"INIT GAGAL {r.status_code}: {r.text[:300]}")
    up_url = r.headers["Location"]
    chunk = 8 * 1024 * 1024
    vid = None
    with open(vp, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": f"bytes {offset}-{end}/{size}"}, timeout=300)
            if rr.status_code == 403 and "quotaExceeded" in rr.text: raise QuotaStop(rr.text[:200])
            if rr.status_code not in (200, 201, 308): raise RuntimeError(f"CHUNK GAGAL {rr.status_code}: {rr.text[:300]}")
            if rr.status_code in (200, 201): vid = rr.json()["id"]
            offset = end + 1
            print(f"  {offset/size*100:.0f}%", flush=True)
    assert vid, "tidak dapat videoId"
    return vid

def set_thumbnail(s, vid, path):
    tp = os.path.join(BASE, path)
    with open(tp, "rb") as f:
        data = f.read()
    r = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
               params={"videoId": vid}, data=data,
               headers={"Content-Type": "image/jpeg"}, timeout=120)
    if r.status_code != 200: raise RuntimeError(f"THUMBNAIL GAGAL {r.status_code}: {r.text[:300]}")
    print("  thumbnail OK", flush=True)

def main():
    item = parse_md(MD)
    print("Judul:", item["judul"][:80], flush=True)
    s = api_session("youtube-pov")
    ch = yt_get("youtube-pov", "/channels", {"mine": "true", "part": "id,snippet"})
    cid = ch["items"][0]["id"]
    assert cid == CHANNEL_ID, f"CHANNEL SALAH: {cid}"
    print("Channel OK:", ch["items"][0]["snippet"]["title"].strip(), flush=True)
    vid = upload_video(s, item, SLOT)
    print("videoId:", vid, flush=True)
    set_thumbnail(s, vid, item["thumbnail"])
    json.dump({"videoId": vid, "slot": SLOT, "judul": item["judul"]}, open(RESULT, "w"), ensure_ascii=False, indent=1)
    print("SELESAI:", vid)

if __name__ == "__main__":
    main()
