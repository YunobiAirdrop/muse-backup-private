#!/usr/bin/env python3
"""Upload 3 video Strange Tales (batch 2026-10-19) via YouTube Data API v3.
Channel WAJIB: Strange Tales / UCAVSqZjG8Af_pm_1uD5wRzA — BATAL total bila channel aktif beda.
privacyStatus=private + publishAt = terjadwal. AI disclosure TIDAK didukung API ->
dicentang manual via Studio sebelum tayang (video masih private sampai publishAt).
Hashtag judul: 5 hashtag, #butifyourcloseyoureyesmeme + #foryou + 3 paling ramai relevan (aturan 2026-10-18).
Slot (2026-10-19 21:00 / 2026-10-20 03:00 / 2026-10-20 07:00 WIB) — tidak konflik slot batch 10-17.
Limit harian/quota -> STOP TOTAL, tulis retry-queue JSON per video yg gagal."""
import json, os, sys, time, datetime

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

D = "/home/hatch/workspace/youtube-otomatis/strange-tales/2026-10-19"
RQ = "/home/hatch/workspace/youtube-otomatis/retry-queue"
BATCH = os.path.expanduser("~/workspace/youtube-otomatis/yt-growth/hidden_files/upload-batch-strangetales-2026-10-19.json")
INSTR = f"{D}/upload-instruksi-2026-10-19.md"

ATTRIB = ("\n\nFootage & photos via Wikimedia Commons (licenses verified per file: "
          "Public domain / CC BY / CC BY-SA).")

TAGS = ["butifyourcloseyoureyesmeme", "shorts", "viral", "mystery", "foryou"]

VIDEOS = [
  {"file": f"{D}/strange-tales-2026-10-19-naga-fireballs.mp4",
   "title": "Fireballs Rise From This River \u2014 WHY?! #butifyourcloseyoureyesmeme #shorts #viral #mystery #foryou",
   "desc": ("Every October, glowing fireballs rise from the Mekong River in Thailand and Laos. "
            "Locals credit the Naga serpent god, while scientists suspect burning natural gas \u2014 "
            "but the timing remains a mystery." + ATTRIB),
   "tags": TAGS,
   "slot_wib": "2026-10-19 21:00", "publish_at": "2026-10-19T14:00:00.000Z"},
  {"file": f"{D}/strange-tales-2026-10-19-fly-geyser.mp4",
   "title": "A Mistake Made This RAINBOW Geyser?! #butifyourcloseyoureyesmeme #shorts #viral #mystery #foryou",
   "desc": ("Fly Geyser in Nevada was born from a failed nineteen sixty four geothermal well. "
            "Heat loving algae paint its travertine mound red and green, and it is still growing." + ATTRIB),
   "tags": TAGS,
   "slot_wib": "2026-10-20 03:00", "publish_at": "2026-10-19T20:00:00.000Z"},
  {"file": f"{D}/strange-tales-2026-10-19-thors-well.mp4",
   "title": "The Ocean Is DRAINING Into This Hole?! #butifyourcloseyoureyesmeme #shorts #viral #mystery #foryou",
   "desc": ("Thors Well on the Oregon coast looks like a bottomless drain for the Pacific, "
            "but it is only twenty feet deep \u2014 a collapsed sea cave caught in an endless "
            "fill and drain loop." + ATTRIB),
   "tags": TAGS,
   "slot_wib": "2026-10-20 07:00", "publish_at": "2026-10-20T00:00:00.000Z"},
]

def write_queue(v, sebab):
    os.makedirs(RQ, exist_ok=True)
    slug = os.path.basename(v["file"]).replace("strange-tales-2026-10-19-", "").replace(".mp4", "")
    qf = os.path.join(RQ, f"strangetales-{slug}-2026-10-19.json")
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
