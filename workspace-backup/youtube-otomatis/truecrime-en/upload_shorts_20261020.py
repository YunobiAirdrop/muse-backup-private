#!/usr/bin/env python3
"""Upload 3 SHORTS truecrime-en (produksi 2026-10-16, kasus Max Headroom) via Data API.
Terjadwal: 21 Okt 2026 07:00 WIB (= 2026-10-21T00:00:00Z). Private + publishAt.
ANTI-MOGOK: gagal karena limit harian -> tulis retry-queue JSON, JANGAN retry.
Run: ~/workspace/youtube-otomatis/yt-growth/venv/bin/python upload_shorts_20261020.py
"""
import json, os, sys, datetime

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "truecrime-en"
EXPECT_ID = "UC2df1xY_WqWdX33oLqeXE2w"  # Dark Case Files
PUBLISH_AT = "2026-10-21T00:00:00.000Z"  # besok 07:00 WIB
BASE = os.path.expanduser("~/workspace/youtube-otomatis/truecrime-en/shorts")
LONG_URL = "https://youtu.be/MC5PENurBOE"
TAGS = ["true crime", "unsolved mystery", "max headroom", "tv hijacking",
        "1980s mystery", "documentary", "mystery", "shorts"]

ITEMS = [
    ("2026-10-16-s1.mp4",
     "Chicago's TV Went Black \u2014 Then HE Appeared #shorts #truecrime #unsolved #foryou",
     "Chicago's TV went black in 1987 \u2014 and something else took over the signal. "
     "Watch the full story: " + LONG_URL),
    ("2026-10-16-s2.mp4",
     "He Hijacked Live TV for 90 Seconds (Never Caught) #shorts #truecrime #mystery #foryou",
     "For 90 seconds, a masked figure hijacked live TV in Chicago. Nobody was ever "
     "caught. Full documentary: " + LONG_URL),
    ("2026-10-16-s3.mp4",
     "How One Man Hacked Every TV in Chicago #shorts #truecrime #1980s #foryou",
     "This is how one man overpowered a TV station's signal in 1987. "
     "The full case file: " + LONG_URL),
]

RETRY_DIR = os.path.expanduser("~/workspace/youtube-otomatis/retry-queue")
VENV = os.path.expanduser("~/workspace/youtube-otomatis/yt-growth/venv/bin/python")


def wib_now():
    return datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=7))).isoformat()


def cek_duplikat(s):
    """Ambil 25 upload terbaru channel; return set judul."""
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "contentDetails"}, timeout=30)
    r.raise_for_status()
    up_id = r.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    judul = set()
    page = None
    while len(judul) < 60:
        p = {"playlistId": up_id, "part": "snippet", "maxResults": 50}
        if page:
            p["pageToken"] = page
        r = s.get("https://www.googleapis.com/youtube/v3/playlistItems",
                  params=p, timeout=30)
        r.raise_for_status()
        d = r.json()
        for it in d.get("items", []):
            judul.add(it["snippet"]["title"])
        page = d.get("nextPageToken")
        if not page:
            break
    return judul


def tulis_retry(video_path, title, desc, sebab):
    os.makedirs(RETRY_DIR, exist_ok=True)
    fn = os.path.join(RETRY_DIR, "truecrime-en-2026-10-20.json")
    data = {}
    if os.path.exists(fn):
        data = json.load(open(fn))
    key = os.path.basename(video_path)
    data[key] = {
        "channel": "truecrime-en (@TrueCaseFilesTV)",
        "video_path": video_path,
        "instruksi_path": os.path.abspath(__file__),
        "judul": title,
        "deskripsi": desc,
        "hashtag": "di akhir judul, ditutup #foryou",
        "slot_target": "2026-10-21 07:00 WIB",
        "publishAt": PUBLISH_AT,
        "ai_disclosure": "centang 'Altered content' di Studio setelah terupload",
        "gagal_pada": wib_now(),
        "sebab": sebab,
    }
    json.dump(data, open(fn, "w"), indent=1, ensure_ascii=False)
    print("RETRY-QUEUE ditulis:", fn, flush=True)


def upload_one(s, fname, title, desc):
    path = os.path.join(BASE, fname)
    size = os.path.getsize(path)
    body = {
        "snippet": {"title": title, "description": desc, "tags": TAGS,
                    "categoryId": "27", "defaultLanguage": "en"},
        "status": {"privacyStatus": "private", "publishAt": PUBLISH_AT,
                   "selfDeclaredMadeForKids": False},
    }
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)}, timeout=60)
    if r.status_code not in (200, 201):
        return None, f"INIT {r.status_code}: {r.text[:300]}"
    up_url = r.headers["Location"]
    with open(path, "rb") as f:
        offset = 0
        chunk = 8 * 1024 * 1024
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": f"bytes {offset}-{end}/{size}"},
                       timeout=300)
            if rr.status_code in (200, 201):
                vid = rr.json()["id"]
                print(f"UPLOAD OK {fname}: {vid} https://youtu.be/{vid}", flush=True)
                return vid, None
            if rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
            else:
                return None, f"CHUNK {rr.status_code}: {rr.text[:300]}"
    return None, "upload tidak selesai tanpa error jelas"


def main():
    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != EXPECT_ID:
        sys.exit("BATAL: channel aktif bukan Dark Case Files!")

    sudah = cek_duplikat(s)
    print(f"Cek duplikat: {len(sudah)} judul terbaru diambil", flush=True)

    hasil = {}
    for fname, title, desc in ITEMS:
        if title in sudah:
            print(f"SKIP (sudah ada di channel): {fname}", flush=True)
            hasil[fname] = {"ok": False, "skipped": "duplikat judul"}
            continue
        vid, err = upload_one(s, fname, title, desc)
        if err:
            print(f"GAGAL {fname}: {err}", flush=True)
            low = err.lower()
            if any(k in low for k in ("limitharian", "upload limit",
                                      "uploadlimitexceeded", "quota",
                                      "daily", "batas")):
                tulis_retry(os.path.join(BASE, fname), title, desc, err)
            hasil[fname] = {"ok": False, "error": err}
        else:
            hasil[fname] = {"ok": True, "id": vid,
                            "url": f"https://youtu.be/{vid}"}

    out = os.path.expanduser(
        "~/workspace/youtube-otomatis/truecrime-en/upload-shorts-2026-10-20-api.json")
    json.dump({"publishAt": PUBLISH_AT, "items": hasil}, open(out, "w"), indent=1)
    print("Hasil tersimpan:", out, flush=True)
    ok = sum(1 for v in hasil.values() if v.get("ok"))
    print(f"SELESAI: {ok}/3 berhasil", flush=True)
    sys.exit(0 if ok == 3 else 20)


if __name__ == "__main__":
    main()
