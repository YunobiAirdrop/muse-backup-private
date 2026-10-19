#!/usr/bin/env python3
"""Upload API long InkTime 2026-10-19 (Tambora 1815). JANGAN DIJALANKAN manual
oleh worker produksi — dieksekusi oleh uploader/parent dengan approval user.
Channel: InkTime UCoZl5OaqjXSVkE4S96RY8_g. Terjadwal 2026-10-20 07:00 WIB."""
import json, os, sys, time

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "inktime"
VIDEO = os.path.expanduser("~/workspace/youtube-otomatis/inktime/video/inktime-2026-10-19-long.mp4")
THUMB = os.path.expanduser("~/workspace/youtube-otomatis/inktime/video/thumb-2026-10-19.jpg")
META = json.load(open(os.path.expanduser("~/workspace/youtube-otomatis/inktime/meta/seo-2026-10-19-long.json")))
PUBLISH_AT = "2026-10-20T00:00:00.000Z"  # 20 Okt 2026 07:00 WIB

def main():
    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != "UCoZl5OaqjXSVkE4S96RY8_g":
        sys.exit("BATAL: channel aktif bukan InkTime!")

    body = {
        "snippet": {"title": META["title"], "description": META["description"],
                    "tags": META["tags"], "categoryId": "27",
                    "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(VIDEO))},
               timeout=60)
    if r.status_code == 403 and "uploadLimitExceeded" in r.text or \
       r.status_code == 403 and "exceeded" in r.text.lower():
        print("LIMIT_HARIAN:", r.text[:300], flush=True)
        sys.exit(20)
    if r.status_code not in (200, 201):
        print("INIT GAGAL:", r.status_code, r.text[:500], flush=True)
        sys.exit(10)
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
            for attempt in range(4):
                try:
                    rr = s.put(up_url, data=data,
                               headers={"Content-Length": str(len(data)),
                                        "Content-Range": f"bytes {offset}-{end}/{size}"},
                               timeout=300)
                    break
                except Exception as e:
                    print(f"chunk {offset} attempt {attempt+1} error: {e}", flush=True)
                    time.sleep(5 * (attempt + 1))
            else:
                print("CHUNK GAGAL TOTAL", flush=True)
                sys.exit(11)
            if rr.status_code in (200, 201):
                vid = rr.json(); break
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                    f.seek(offset)
                    continue
                offset = end + 1
            else:
                print("UPLOAD GAGAL:", rr.status_code, rr.text[:500], flush=True)
                sys.exit(12)
    if not vid:
        print("UPLOAD TIDAK SELESAI", flush=True); sys.exit(13)
    vid_id = vid["id"]
    print("UPLOAD SELESAI:", vid_id, flush=True)
    print("URL: https://youtu.be/" + vid_id, flush=True)

    # Thumbnail (bisa 403 bila channel belum verifikasi HP)
    try:
        with open(THUMB, "rb") as f:
            rt = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                        params={"videoId": vid_id}, data=f.read(),
                        headers={"Content-Type": "image/jpeg"}, timeout=120)
        print("THUMBNAIL:", rt.status_code, rt.text[:200], flush=True)
    except Exception as e:
        print("THUMBNAIL ERROR:", e, flush=True)

    # Playlist "Ancient History" (cari / buat)
    try:
        rp = s.get("https://www.googleapis.com/youtube/v3/playlists",
                   params={"mine": "true", "part": "snippet", "maxResults": 25}, timeout=30)
        rp.raise_for_status()
        pl_id = next((p["id"] for p in rp.json()["items"]
                      if p["snippet"]["title"].lower() == "ancient history"), None)
        if not pl_id:
            rc = s.post("https://www.googleapis.com/youtube/v3/playlists",
                        params={"part": "snippet,status"},
                        json={"snippet": {"title": "Ancient History",
                                          "description": "Ancient history explained on a whiteboard."},
                              "status": {"privacyStatus": "public"}}, timeout=30)
            rc.raise_for_status()
            pl_id = rc.json()["id"]
            print("PLAYLIST DIBUAT:", pl_id, flush=True)
        ri = s.post("https://www.googleapis.com/youtube/v3/playlistItems",
                    params={"part": "snippet"},
                    json={"snippet": {"playlistId": pl_id,
                                      "resourceId": {"kind": "youtube#video", "videoId": vid_id}}},
                    timeout=30)
        print("PLAYLIST ITEM:", ri.status_code, flush=True)
    except Exception as e:
        print("PLAYLIST ERROR:", e, flush=True)

    print(json.dumps({"id": vid_id, "url": "https://youtu.be/" + vid_id}))

if __name__ == "__main__":
    main()
