#!/usr/bin/env python3
"""Upload LONG horor 2026-10-13 via YouTube Data API v3 (resumable), Terjadwal 2026-10-15 19:00 WIB.
Metadata dibaca dari upload-2026-10-13.json. Channel WAJIB Kisah Horor (UCUEHu-nQXxGuru5Bviy4DKQ).
AI disclosure TIDAK didukung API -> browser task Studio setelahnya (lihat upload-instruksi).
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

BASE = "/home/hatch/workspace/horor-otomatis"
CHANNEL_ID = "UCUEHu-nQXxGuru5Bviy4DKQ"

meta = json.load(open(os.path.join(BASE, "upload-2026-10-13.json")))
VIDEO = meta["video_path"]
THUMB = meta["thumbnail"]
TITLE = meta["judul"]
DESCRIPTION = meta["deskripsi"]
TAGS = meta["tags"]
PUBLISH_AT = meta["publish_at"]  # 2026-10-15T12:00:00.000Z

def main():
    assert os.path.exists(VIDEO) and os.path.getsize(VIDEO) > 10_000_000, f"video hilang/kecil: {VIDEO}"
    assert os.path.exists(THUMB), f"thumbnail hilang: {THUMB}"
    s = api_session("horor")
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    assert ch["id"] == CHANNEL_ID, f"BATAL: {ch['id']} bukan Kisah Horor!"
    assert "Kisah Horor" in ch["snippet"]["title"], "BATAL: nama channel bukan Kisah Horor!"

    # cek duplikat judul di uploads playlist
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
            if it["snippet"]["title"].strip().lower() == TITLE.strip().lower():
                print("DUPLIKAT: judul sudah ada ->", "https://youtu.be/" + it["snippet"]["resourceId"]["videoId"])
                print(json.dumps({"duplicate": True}))
                return
        page = pl.get("nextPageToken")
        if not page: break
    print("cek duplikat: bersih", flush=True)

    body = {
        "snippet": {"title": TITLE, "description": DESCRIPTION,
                    "tags": TAGS, "categoryId": "24", "defaultLanguage": "id"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(VIDEO))},
               timeout=60)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:500]); sys.exit(10)
    up_url = r.headers["Location"]
    print("upload session OK", flush=True)

    size = os.path.getsize(VIDEO)
    chunk = 8 * 1024 * 1024
    vid = None
    with open(VIDEO, "rb") as f:
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
                break
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                f.seek(offset)
                print(f"  ... {offset*100//size}%", flush=True)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:300]); sys.exit(11)
    if not vid:
        print("UPLOAD TAK SELESAI"); sys.exit(12)
    print("UPLOAD SELESAI:", vid)
    print("URL: https://youtu.be/" + vid)
    with open(THUMB, "rb") as tf:
        tr = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                    params={"videoId": vid}, data=tf.read(),
                    headers={"Content-Type": "image/jpeg"}, timeout=60)
    print("THUMBNAIL:", tr.status_code)
    json.dump({"id": vid, "url": "https://youtu.be/" + vid,
               "publish_at": PUBLISH_AT, "terjadwal": "2026-10-15 19:00 WIB"},
              open(os.path.join(BASE, "upload-hasil-2026-10-13.json"), "w"))
    print(json.dumps({"id": vid, "url": "https://youtu.be/" + vid}))

if __name__ == "__main__":
    main()
