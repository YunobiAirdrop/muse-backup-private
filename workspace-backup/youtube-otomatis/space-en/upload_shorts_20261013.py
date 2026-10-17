#!/usr/bin/env python3
"""Upload 3 shorts Black Hole ke Cosmic Unknown via Data API v3 (resumable).
Alur: verifikasi channel -> upload UNLISTED -> update jadi TERJADWAL 2026-10-14 07:00 WIB.
Kena limit harian/kuota -> tulis retry-queue JSON, STOP (jangan retry).
"""
import json, os, sys, datetime

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session

BASE = "/home/hatch/workspace/youtube-otomatis/space-en"
META = json.load(open(os.path.join(BASE, "upload-2026-10-11.json")))["shorts"]
# publishAt 2026-10-14 07:00 WIB = 2026-10-14T00:00:00Z
PUBLISH_AT = "2026-10-14T00:00:00.000Z"
CHANNEL_ID = "UCQnUeh4-2AKgCsV_cjgUv4w"
QUEUE = "/home/hatch/workspace/youtube-otomatis/retry-queue/space-en-shorts-2026-10-13.json"

def queue_fail(sebab, video_path, idx):
    q = {"channel": "Cosmic Unknown (@CosmosUnknownTV)",
         "video_path": video_path,
         "instruksi_path": os.path.join(BASE, "instruksi-upload-2026-10-11-long.md"),
         "slot_target": "2026-10-14 07:00 WIB",
         "gagal_pada": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
         "sebab": sebab,
         "shorts_index": idx}
    json.dump(q, open(QUEUE, "w"), indent=1, ensure_ascii=False)
    print("ANTREAN DITULIS:", QUEUE)

def upload_one(s, m):
    path = os.path.join(BASE, m["file"])
    if not os.path.exists(path):
        print(f"FILE HILANG: {path}"); sys.exit(20)
    size = os.path.getsize(path)
    body = {"snippet": {"title": m["title"], "description": m["description"],
                        "tags": m.get("tags", []), "categoryId": "28",
                        "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False}}
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)}, timeout=60)
    if r.status_code not in (200, 201):
        txt = r.text[:300]
        print("INIT GAGAL:", r.status_code, txt)
        if r.status_code == 403 and any(k in txt for k in ("quotaExceeded", "dailyLimitExceeded", "uploadLimitExceeded", "rateLimitExceeded")):
            queue_fail(f"limit/kuota harian ({r.status_code})", path, m["file"]); sys.exit(30)
        sys.exit(10)
    up_url = r.headers["Location"]
    with open(path, "rb") as f:
        offset = 0
        chunk = 8 * 1024 * 1024
        while offset < size:
            data = f.read(chunk); end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": f"bytes {offset}-{end}/{size}"}, timeout=300)
            if rr.status_code in (200, 201):
                vid = rr.json()["id"]; break
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
            else:
                print("CHUNK GAGAL:", rr.status_code, rr.text[:300]); sys.exit(11)
    print(f"UPLOAD OK (unlisted): {vid} https://youtu.be/{vid} [{m['file']}]", flush=True)
    # jadikan terjadwal
    u = s.put("https://www.googleapis.com/youtube/v3/videos",
              params={"part": "status"},
              json={"id": vid, "status": {"privacyStatus": "private",
                                          "publishAt": PUBLISH_AT,
                                          "selfDeclaredMadeForKids": False}}, timeout=60)
    if u.status_code not in (200, 201):
        print("SCHEDULE GAGAL:", u.status_code, u.text[:300], "-> video tetap UNLISTED, aman")
    else:
        print(f"TERJADWAL 2026-10-14 07:00 WIB: {vid}", flush=True)
    return vid

def main():
    s = api_session("space-en")
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != CHANNEL_ID:
        sys.exit(f"BATAL: channel aktif {ch['id']} bukan Cosmic Unknown!")
    out = {}
    for m in META:
        out[m["file"]] = upload_one(s, m)
    json.dump(out, open(os.path.join(BASE, "upload-shorts-2026-10-13.json"), "w"), indent=1)
    print("SELESAI:", json.dumps(out))

if __name__ == "__main__":
    main()
