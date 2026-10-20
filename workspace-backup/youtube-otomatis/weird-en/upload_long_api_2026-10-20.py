#!/usr/bin/env python3
"""Upload LONG weird-en 2026-10-20 via YouTube Data API v3 (resumable).
Manifest: upload-2026-10-20.json
Verifikasi channel ID eksplisit sebelum upload (pelajaran 2026-10-11).
private + publishAt -> TERJADWAL 2026-10-21 07:00 WIB.
Hasil: upload-2026-10-20-result.json
"""
import json, os, sys, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "yt-growth"))
from auth import api_session

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(BASE, "upload-2026-10-20.json")
RESULT = os.path.join(BASE, "upload-2026-10-20-result.json")
EXPECT_ID = "UCJ6KqdYvVJ-PaxhGLfTFVhA"


def dup_check(s, title):
    """Cek 25 upload terbaru channel; True jika judul sama sudah ada."""
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "contentDetails"}, timeout=30)
    r.raise_for_status()
    uploads = r.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    page = None
    seen = []
    for _ in range(2):
        p = {"playlistId": uploads, "part": "snippet", "maxResults": 25}
        if page:
            p["pageToken"] = page
        rr = s.get("https://www.googleapis.com/youtube/v3/playlistItems",
                   params=p, timeout=30)
        rr.raise_for_status()
        items = rr.json().get("items", [])
        for it in items:
            t = it["snippet"]["title"]
            seen.append(t)
            if t.strip().lower() == title.strip().lower():
                return True, it["snippet"]["resourceId"]["videoId"]
        page = rr.json().get("nextPageToken")
        if not page:
            break
    return False, seen[:5]


def upload_one(s, m):
    video = m["video_path"]
    size = os.path.getsize(video)
    body = {
        "snippet": {
            "title": m["title"],
            "description": m["description"],
            "tags": m.get("tags", []),
            "categoryId": m.get("categoryId", "27"),
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": m["publishAt"],
            "selfDeclaredMadeForKids": False,
        },
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)},
               timeout=60)
    if r.status_code not in (200, 201):
        return {"ok": False, "error": f"init {r.status_code}: {r.text[:300]}"}
    up_url = r.headers["Location"]
    chunk = 8 * 1024 * 1024
    with open(video, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            for attempt in range(4):
                rr = s.put(up_url, data=data,
                           headers={"Content-Length": str(len(data)),
                                    "Content-Range": f"bytes {offset}-{end}/{size}"},
                           timeout=300)
                if rr.status_code in (200, 201):
                    return {"ok": True, "videoId": rr.json()["id"],
                            "url": "https://youtu.be/" + rr.json()["id"]}
                elif rr.status_code == 308:
                    rng = rr.headers.get("Range", "")
                    offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                    f.seek(offset)
                    break
                else:
                    time.sleep(5 * (attempt + 1))
            else:
                return {"ok": False, "error": f"chunk {rr.status_code}: {rr.text[:300]}"}
    return {"ok": False, "error": "upload tidak selesai tanpa error jelas"}


def set_thumbnail(s, video_id, thumb_path):
    if not thumb_path or not os.path.exists(thumb_path):
        return "thumbnail file tidak ada"
    with open(thumb_path, "rb") as f:
        rr = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                    params={"videoId": video_id},
                    data=f.read(),
                    headers={"Content-Type": "image/jpeg"}, timeout=120)
    if rr.status_code == 200:
        return "OK"
    return f"DITOLAK {rr.status_code}: {rr.text[:200]}"


def main():
    m = json.load(open(MANIFEST))
    s = api_session(m.get("slug", "weird-en"))
    # 1. verifikasi channel aktif
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != EXPECT_ID:
        sys.exit(f"BATAL: channel aktif {ch['id']} bukan {EXPECT_ID}!")
    # 2. cek duplikat
    is_dup, info = dup_check(s, m["title"])
    if is_dup:
        out = {"ok": False, "skipped": "duplikat", "existing_videoId": info,
               "title": m["title"]}
        json.dump(out, open(RESULT, "w"), indent=1, ensure_ascii=False)
        print("DOBEL: judul sudah ada ->", info, flush=True)
        return
    print("dup-check OK (5 terbaru:", info, ")", flush=True)
    # 3. upload
    res = upload_one(s, m)
    res["title"] = m["title"]
    res["channel"] = m["channel"]
    res["channel_id"] = EXPECT_ID
    res["publishAt"] = m["publishAt"]
    res["slot_target"] = m.get("slot_target")
    if res.get("ok"):
        res["thumbnail"] = set_thumbnail(s, res["videoId"], m.get("thumbnail_path"))
    json.dump(res, open(RESULT, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(res, ensure_ascii=False)[:600], flush=True)
    if not res.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
