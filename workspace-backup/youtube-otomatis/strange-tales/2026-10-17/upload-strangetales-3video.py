#!/usr/bin/env python3
"""Upload 3 video Strange Tales (batch 2026-10-17, diproduksi ulang 2026-10-18) via YouTube Data API v3.
Channel WAJIB: Strange Tales / UCAVSqZjG8Af_pm_1uD5wRzA — BATAL total bila channel aktif beda.
privacyStatus=private + publishAt = terjadwal. AI disclosure TIDAK didukung API ->
dicentang manual via Studio sebelum tayang (video masih private sampai publishAt).
Hashtag judul: 5 hashtag, #butifyourcloseyoureyesmeme + #foryou + 3 paling ramai relevan (aturan 2026-10-18).
Slot (2026-10-18 21:00 / 2026-10-19 03:00 / 2026-10-19 07:00 WIB) — tidak konflik slot batch 10-15.
Limit harian/quota -> STOP TOTAL, tulis retry-queue JSON per video yg gagal."""
import json, os, sys, time, datetime

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

D = "/home/hatch/workspace/youtube-otomatis/strange-tales/2026-10-17"
RQ = "/home/hatch/workspace/youtube-otomatis/retry-queue"
BATCH = os.path.expanduser("~/workspace/youtube-otomatis/yt-growth/hidden_files/upload-batch-strangetales-2026-10-17.json")
INSTR = f"{D}/upload-instruksi-2026-10-17.md"

ATTRIB = ("\n\nFootage & photos via Wikimedia Commons (licenses verified per file: "
          "CC0 / CC BY / CC BY-SA).")

VIDEOS = [
  {"file": f"{D}/strange-tales-2026-10-17-lake-hillier.mp4",
   "title": "This Lake Is PINK — But WHY?! #butifyourcloseyoureyesmeme #shorts #viral #mystery #foryou",
   "desc": ("Lake Hillier in Australia stays bubblegum pink all year — an algae and salt-loving "
            "bacteria paint it that way, and yes, you can swim in it. Would you jump in?" + ATTRIB),
   "tags": ["butifyourcloseyoureyesmeme", "shorts", "viral", "mystery", "foryou"],
   "slot_wib": "2026-10-18 21:00", "publish_at": "2026-10-18T14:00:00.000Z"},
  {"file": f"{D}/strange-tales-2026-10-17-kentucky-meat-shower.mp4",
   "title": "In 1876, MEAT Fell From the SKY — HOW?! #butifyourcloseyoureyesmeme #shorts #viral #mystery #foryou",
   "desc": ("In 1876, chunks of fresh meat fell from the sky over Kentucky for several minutes. "
            "The leading theory? Vultures flying high above, all vomiting at once." + ATTRIB),
   "tags": ["butifyourcloseyoureyesmeme", "shorts", "viral", "mystery", "foryou"],
   "slot_wib": "2026-10-19 03:00", "publish_at": "2026-10-18T20:00:00.000Z"},
  {"file": f"{D}/strange-tales-2026-10-17-upside-down-jellyfish.mp4",
   "title": "Jellyfish Farms SUNLIGHT — Upside Down?! #butifyourcloseyoureyesmeme #shorts #fyp #mystery #foryou",
   "desc": ("The upside down jellyfish rests bell down on the ocean floor so the algae in its "
            "tentacles can farm sunlight through photosynthesis. Nature keeps surprising us." + ATTRIB),
   "tags": ["butifyourcloseyoureyesmeme", "shorts", "fyp", "mystery", "foryou"],
   "slot_wib": "2026-10-19 07:00", "publish_at": "2026-10-19T00:00:00.000Z"},
]

def write_queue(v, sebab):
    os.makedirs(RQ, exist_ok=True)
    slug = os.path.basename(v["file"]).replace("strange-tales-2026-10-17-", "").replace(".mp4", "")
    qf = os.path.join(RQ, f"strangetales-{slug}-2026-10-17.json")
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    data = {"channel": "strangetales",
            "video_path": v["file"],
            "instruksi_path": INSTR,
            "slot_target": v["slot_wib"] + " WIB",
            "gagal_pada": now.isoformat(timespec="seconds"),
            "sebab": sebab}
    json.dump(data, open(qf, "w"), indent=1)
    print(f"QUEUE DITULIS: {qf}", flush=True)

def upload_one(s, v):
    body = {"snippet": {"title": v["title"], "description": v["desc"],
                        "tags": v["tags"],
                        "categoryId": "24"},
            "status": {"privacyStatus": "private", "publishAt": v["publish_at"],
                       "selfDeclaredMadeForKids": False}}
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(os.path.getsize(v["file"]))},
               timeout=60)
    if r.status_code not in (200, 201):
        return ("init", r.status_code, r.text[:300])
    up_url = r.headers["Location"]
    size = os.path.getsize(v["file"])
    chunk = 8 * 1024 * 1024
    with open(v["file"], "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": f"bytes {offset}-{end}/{size}"},
                       timeout=300)
            if rr.status_code in (200, 201):
                return ("ok", rr.json()["id"], "")
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                offset = int(rng.split("-")[1]) + 1 if rng else end + 1
                f.seek(offset)
                print(f"... {offset}/{size}", flush=True)
            else:
                return ("chunk", rr.status_code, rr.text[:300])
    return ("incomplete", 0, "upload tidak selesai tanpa error jelas")

def main():
    for v in VIDEOS:
        assert len(v["title"]) <= 100, f"JUDUL >100 ({len(v['title'])}): {v['title']}"
    s = api_session("strangetales")
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != "UCAVSqZjG8Af_pm_1uD5wRzA":
        sys.exit("BATAL: channel aktif bukan Strange Tales (UCAVSqZjG8Af_pm_1uD5wRzA)!")
    results = []
    for v in VIDEOS:
        if not os.path.exists(v["file"]):
            print(f"SKIP (file belum ada): {v['file']}", flush=True)
            write_queue(v, "file video belum tersedia saat batch upload (assembly belum selesai)")
            continue
        print(f"UPLOAD: {os.path.basename(v['file'])} -> {v['slot_wib']} WIB", flush=True)
        st, code, msg = upload_one(s, v)
        if st == "ok":
            url = "https://youtu.be/" + code
            print(f"SELESAI: {code} {url}", flush=True)
            results.append({"file": os.path.basename(v["file"]), "video_id": code,
                            "url": url, "slot_wib": v["slot_wib"]})
        else:
            sebab = f"{st} HTTP {code}: {msg}"
            print(f"GAGAL: {sebab}", flush=True)
            low = (msg + " " + str(code)).lower()
            if any(k in low for k in ("daily", "limit", "quota", "uploadlimit", "403")):
                write_queue(v, sebab)
                for rest in VIDEOS[VIDEOS.index(v) + 1:]:
                    write_queue(rest, "tidak dicoba (STOP TOTAL setelah limit) — FIFO")
                json.dump(results, open(BATCH, "w"), indent=1)
                sys.exit(20)
            write_queue(v, sebab)
            time.sleep(5)
    json.dump(results, open(BATCH, "w"), indent=1)
    print(f"SEMUA UPLOAD SELESAI: {len(results)}/{len(VIDEOS)}", flush=True)

if __name__ == "__main__":
    main()
