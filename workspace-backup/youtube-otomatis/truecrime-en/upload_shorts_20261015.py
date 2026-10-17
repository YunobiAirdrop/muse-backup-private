#!/usr/bin/env python3
"""Upload 3 SHORTS truecrime-en (produksi 2026-10-14) via Data API.
Terjadwal: 16 Okt 2026 07:00 WIB (= 2026-10-16T00:00:00Z). Private + publishAt.
ANTI-MOGOK: gagal karena limit harian -> tulis retry-queue JSON, JANGAN retry.
"""
import json, os, sys, datetime

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

SLUG = "truecrime-en"
EXPECT_ID = "UC2df1xY_WqWdX33oLqeXE2w"  # Dark Case Files
PUBLISH_AT = "2026-10-16T00:00:00.000Z"
BASE = os.path.expanduser("~/workspace/youtube-otomatis/truecrime-en/shorts")
LONG_URL = "https://youtu.be/MsvOo6y4Bko"
TAGS = ["true crime", "unsolved mystery", "art heist", "isabella stewart gardner",
        "fbi investigation", "mystery", "documentary", "shorts"]

ITEMS = [
    ("2026-10-14-s1.mp4",
     "Two Fake Cops Stole $500M in 81 Minutes #shorts #truecrime #mystery #foryou",
     "On March 18, 1990, two men dressed as Boston police talked their way into the "
     "Isabella Stewart Gardner Museum \u2014 and walked out with $500 million in art. "
     "81 minutes. 13 masterpieces. Zero arrests. Honestly, the fact that this is still "
     "unsolved decades later is what keeps me up at night.\n\n"
     f"Watch the full case: {LONG_URL}"),
    ("2026-10-14-s2.mp4",
     "They Cut Rembrandt Right Out of the Frame #shorts #truecrime #artheist #foryou",
     "Among the stolen works: Vermeer's 'The Concert' \u2014 the most valuable stolen "
     "painting in the world \u2014 and a Rembrandt cut straight out of its frame. "
     "The empty frames still hang in the museum today, waiting.\n\n"
     f"Watch the full case: {LONG_URL}"),
    ("2026-10-14-s3.mp4",
     "The FBI Knows WHO \u2014 But Not WHERE #shorts #truecrime #unsolved #foryou",
     "The FBI says it knows who pulled off the Gardner heist. But the paintings have "
     "never been found, and the $10 million reward still stands. In my opinion, this "
     "is the greatest unsolved art crime in history.\n\n"
     f"Watch the full case: {LONG_URL}"),
]

RETRY_DIR = os.path.expanduser("~/workspace/youtube-otomatis/retry-queue")


def tulis_retry(video_path, sebab):
    os.makedirs(RETRY_DIR, exist_ok=True)
    fn = os.path.join(RETRY_DIR, "truecrime-en-2026-10-15.json")
    data = {}
    if os.path.exists(fn):
        data = json.load(open(fn))
    key = os.path.basename(video_path)
    data[key] = {
        "channel": "truecrime-en (@TrueCaseFilesTV)",
        "video_path": video_path,
        "instruksi_path": os.path.abspath(__file__),
        "slot_target": "2026-10-16 07:00 WIB",
        "gagal_pada": datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
        "sebab": sebab,
    }
    json.dump(data, open(fn, "w"), indent=1, ensure_ascii=False)
    print("RETRY-QUEUE ditulis:", fn)


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

    hasil = {}
    for fname, title, desc in ITEMS:
        vid, err = upload_one(s, fname, title, desc)
        if err:
            print(f"GAGAL {fname}: {err}", flush=True)
            low = err.lower()
            if any(k in low for k in ("limitharian", "upload limit", "uploadlimitexceeded",
                                      "quota", "daily", "batas")):
                tulis_retry(os.path.join(BASE, fname), err)
            hasil[fname] = {"ok": False, "error": err}
        else:
            hasil[fname] = {"ok": True, "id": vid,
                            "url": f"https://youtu.be/{vid}"}
    out = os.path.expanduser(
        "~/workspace/youtube-otomatis/truecrime-en/upload-shorts-2026-10-15-api.json")
    json.dump({"publishAt": PUBLISH_AT, "items": hasil}, open(out, "w"), indent=1)
    print("Hasil tersimpan:", out)
    ok = sum(1 for v in hasil.values() if v["ok"])
    print(f"SELESAI: {ok}/3 berhasil")
    sys.exit(0 if ok == 3 else 20)


if __name__ == "__main__":
    main()
