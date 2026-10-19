#!/usr/bin/env python3
"""Upload 3 shorts weird-en via YouTube Data API v3 (resumable).
Manifest: upload-shorts-2026-10-19.json
Verifikasi channel ID eksplisit sebelum upload (pelajaran 2026-10-11).
Hasil: upload-shorts-2026-10-19-result.json
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../yt-growth")
from auth import api_session

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(BASE, "upload-shorts-2026-10-19.json")
RESULT = os.path.join(BASE, "upload-shorts-2026-10-19-result.json")

def upload_one(s, item, publish_at, category_id, tags):
    video = item.get("video_path") or item.get("file")
    if not os.path.exists(video):
        return {"ok": False, "error": "file tidak ada: " + video}
    body = {
        "snippet": {
            "title": item["title"],
            "description": item["description"],
            "tags": item.get("tags") or tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at,
            "selfDeclaredMadeForKids": False,
        },
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(video))},
               timeout=60)
    if r.status_code not in (200, 201):
        return {"ok": False, "error": f"init {r.status_code}: {r.text[:300]}"}
    up_url = r.headers["Location"]
    size = os.path.getsize(video)
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
                vid = rr.json()
                return {"ok": True, "videoId": vid["id"],
                        "url": "https://youtu.be/" + vid["id"]}
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
            else:
                return {"ok": False, "error": f"chunk {rr.status_code}: {rr.text[:300]}"}
    return {"ok": False, "error": "upload tidak selesai tanpa error jelas"}

def main():
    m = json.load(open(MANIFEST))
    slug = m.get("slug", "weird-en")
    expect_id = m["channel_id"]
    if "items" not in m and "shorts" in m:
        m["items"] = m["shorts"]
    s = api_session(slug)
    # 1. verifikasi channel aktif
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != expect_id:
        sys.exit(f"BATAL: channel aktif {ch['id']} bukan {expect_id}!")
    # 2. cek duplikat: daftar upload terbaru channel, bandingkan judul
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "contentDetails"}, timeout=30)
    r.raise_for_status()
    uploads_pl = r.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    r = s.get("https://www.googleapis.com/youtube/v3/playlistItems",
              params={"playlistId": uploads_pl, "part": "snippet",
                      "maxResults": 25}, timeout=30)
    r.raise_for_status()
    existing = [it["snippet"]["title"] for it in r.json().get("items", [])]
    def norm(t): return " ".join(t.lower().split())
    for item in m["items"]:
        base = item["title"].rsplit(" #shorts", 1)[0]
        for e in existing:
            if norm(e).startswith(norm(base)[:40]) or norm(base) in norm(e):
                sys.exit(f"BATAL: judul '{item['title'][:60]}' kemungkinan sudah ada di channel ('{e[:60]}')")
    print(f"OK: tidak ada duplikat dari {len(existing)} video terbaru", flush=True)
    results = []
    for item in m["items"]:
        print("UPLOAD:", item["title"][:60], flush=True)
        res = upload_one(s, item, m["publishAt"], m["categoryId"], m.get("tags", []))
        res["title"] = item["title"]
        results.append(res)
        print(" ->", res.get("videoId") or res.get("error"), flush=True)
    json.dump({"channel": ch["snippet"]["title"], "channel_id": ch["id"],
               "results": results}, open(RESULT, "w"), indent=1)
    fails = [x for x in results if not x["ok"]]
    if fails:
        print(f"{len(fails)} GAGAL")
        sys.exit(20)
    print("SEMUA OK")

if __name__ == "__main__":
    main()
