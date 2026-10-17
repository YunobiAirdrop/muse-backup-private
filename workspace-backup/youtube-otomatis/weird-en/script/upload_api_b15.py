#!/usr/bin/env python3
"""Upload weird-en long 2026-10-15 via YouTube Data API (resumable).
Langkah: verifikasi channel -> anti-dobel (cek judul di uploads) -> upload
private + publishAt -> coba set thumbnail -> verifikasi metadata.
Keluar non-zero bila channel salah / judul sudah ada / upload gagal."""
import json, os, sys, time

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
META = json.load(open(os.path.join(W, "upload-2026-10-15.json")))
SLUG = "weird-en"
VIDEO = META["video_path"]
THUMB = META["thumbnail"]
EXPECTED_CH = "UCJ6KqdYvVJ-PaxhGLfTFVhA"

s = api_session(SLUG)

# 1. verifikasi channel
ch = s.get("https://www.googleapis.com/youtube/v3/channels",
           params={"mine": "true", "part": "snippet"}).json()["items"][0]
print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
if ch["id"] != EXPECTED_CH or "Weird World Daily" not in ch["snippet"]["title"]:
    sys.exit("BATAL: channel aktif bukan Weird World Daily!")

# 2. anti-dobel: cek 10 upload terakhir
pl = s.get("https://www.googleapis.com/youtube/v3/channels",
           params={"mine": "true", "part": "contentDetails"}).json(
           )["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
items = s.get("https://www.googleapis.com/youtube/v3/playlistItems",
              params={"playlistId": pl, "part": "snippet", "maxResults": 10}).json()["items"]
for it in items:
    if it["snippet"]["title"].strip().lower() == META["title"].strip().lower():
        sys.exit(f"BATAL: judul sudah ada di channel (id={it['snippet']['resourceId']['videoId']})")
print("ANTI-DOBEL: lolos", flush=True)

# 3. inisiasi resumable upload
body = {
    "snippet": {"title": META["title"], "description": META["description"],
                "tags": META["tags"], "categoryId": META.get("categoryId", "27"),
                "defaultLanguage": "en", "defaultAudioLanguage": "en"},
    "status": {"privacyStatus": "private", "publishAt": META["publishAt"],
               "selfDeclaredMadeForKids": False},
}
size = os.path.getsize(VIDEO)
r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
           params={"uploadType": "resumable", "part": "snippet,status"},
           json=body,
           headers={"X-Upload-Content-Type": "video/mp4",
                    "X-Upload-Content-Length": str(size)}, timeout=60)
if r.status_code not in (200, 201):
    print("INIT GAGAL:", r.status_code, r.text[:300])
    if "quota" in r.text.lower() or "uploadLimit" in r.text:
        sys.exit("LIMIT_HARIAN")
    sys.exit(10)
up_url = r.headers["Location"]
print("upload session OK, size", size, flush=True)

# 4. upload chunked
chunk = 8 * 1024 * 1024
vid_id = None
with open(VIDEO, "rb") as f:
    offset = 0
    while offset < size:
        data = f.read(chunk)
        end = offset + len(data) - 1
        rr = s.put(up_url, data=data,
                   headers={"Content-Length": str(len(data)),
                            "Content-Range": f"bytes {offset}-{end}/{size}"}, timeout=300)
        if rr.status_code in (200, 201):
            vid_id = rr.json()["id"]
            break
        elif rr.status_code == 308:
            rng = rr.headers.get("Range", "")
            offset = int(rng.split("-")[1]) + 1 if rng else end + 1
            f.seek(offset)
            print(f"... {offset}/{size}", flush=True)
        else:
            print("CHUNK GAGAL:", rr.status_code, rr.text[:300])
            if "quota" in rr.text.lower() or "uploadLimit" in rr.text:
                sys.exit("LIMIT_HARIAN")
            sys.exit(11)
if not vid_id:
    sys.exit("upload tidak selesai tanpa error jelas")
print("UPLOAD SELESAI:", vid_id)
print("URL: https://youtu.be/" + vid_id, flush=True)

# 5. coba set thumbnail
thumb_status = "OK"
try:
    with open(THUMB, "rb") as f:
        tr = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                    params={"videoId": vid_id},
                    files={"media_body": ("thumb.jpg", f, "image/jpeg")}, timeout=60)
    if tr.status_code in (200, 201):
        print("THUMBNAIL: terpasang", flush=True)
    else:
        thumb_status = f"DITOLAK {tr.status_code}: {tr.text[:200]}"
        print("THUMBNAIL:", thumb_status, flush=True)
except Exception as e:
    thumb_status = f"ERROR: {e}"
    print("THUMBNAIL:", thumb_status, flush=True)

# 6. verifikasi metadata read-back
v = s.get("https://www.googleapis.com/youtube/v3/videos",
          params={"id": vid_id, "part": "snippet,status"}).json()["items"][0]
print("VERIFY:", v["snippet"]["title"], "| privacy:", v["status"]["privacyStatus"],
      "| publishAt:", v["status"].get("publishAt"), flush=True)

json.dump({"videoId": vid_id, "url": "https://youtu.be/" + vid_id,
           "thumbnail": thumb_status},
          open(os.path.join(W, "upload-2026-10-15-result.json"), "w"), indent=1)
