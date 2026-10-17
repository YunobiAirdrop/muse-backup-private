#!/usr/bin/env python3
"""Upload backlog POV @ceritarakyat862 via YouTube Data API (resumable).
Dipakai 2026-10-17: upload video yang produksinya selesai tapi belum tayang
(Diponegoro 10-13, Templar 10-14, Aceh 10-15). AI disclosure TIDAK didukung API
-> WAJIB dicentang manual via Studio setelahnya (dicatat di laporan).

Urutan: long dulu per batch (ambil videoId -> URL untuk deskripsi shorts).
Slot (WIB): Templar long+shorts Sab 10-17 19:00; Aceh long Min 10-18 19:00;
Aceh shorts Sen 10-19 19:00; Diponegoro long+shorts Sel 10-20 19:00.
Jalankan dengan venv: ~/workspace/youtube-otomatis/yt-growth/venv/bin/python
"""
import json, os, re, sys, time

BASE = os.path.expanduser("~/workspace/youtube-otomatis")
sys.path.insert(0, os.path.join(BASE, "yt-growth"))
from auth import api_session

CHANNEL_ID = "UC1c8WpKGhFKpUOp5AqVueEg"
RESULT = os.path.join(BASE, "yt-growth", "hidden_files",
                      "upload-pov-backlog-2026-10-17.json")

def parse_md(path):
    t = open(path).read()
    out = {"long": None, "shorts": []}
    # ---- LONG (format A: "Judul: X" setelah ## VIDEO LONG) ----
    m = re.search(r"## VIDEO LONG.*?\nFile:\s*(\S+).*?\nJudul:\s*(.+?)\nDeskripsi:\n(.+?)\nTag YouTube:\s*(.+?)\n",
                  t, re.S)
    if m:
        out["long"] = {"video": m.group(1), "judul": m.group(2).strip(),
                       "deskripsi": m.group(3).strip(),
                       "tags": [x.strip() for x in m.group(4).split(",")]}
        th = re.search(r"Thumbnail:\s*upload\s*(\S+)", t)
        out["long"]["thumbnail"] = th.group(1) if th else None
    else:
        # ---- LONG (format B: ## Judul / ## Deskripsi / ## Tag) ----
        m = re.search(r"## Judul\n(.+?)\n\n## Deskripsi\n(.+?)\n\n## Tag\n(.+?)\n", t, re.S)
        if m:
            out["long"] = {"judul": m.group(1).strip(),
                           "deskripsi": m.group(2).strip(),
                           "tags": [x.strip() for x in m.group(3).split(",")]}
            vf = re.search(r"\*\*File video:\*\*\s*(\S+)", t)
            th = re.search(r"\*\*Thumbnail:\*\*\s*(\S+)", t)
            out["long"]["video"] = vf.group(1) if vf else None
            out["long"]["thumbnail"] = th.group(1) if th else None
    # ---- SHORTS format A: ## SHORT N — ... ----
    for sm in re.finditer(
            r"## SHORT (\d+).*?\nFile:\s*(\S+)\nJudul:\s*(.+?)\nDeskripsi:\n(.+?)\nTag:\s*(.+?)\n",
            t, re.S):
        out["shorts"].append({"video": sm.group(2), "judul": sm.group(3).strip(),
                              "deskripsi": sm.group(4).strip(),
                              "tags": [x.strip() for x in sm.group(5).split(",")]})
    # ---- SHORTS format B: ## Shorts N — <file> ----
    for sm in re.finditer(
            r"## Shorts (\d+)\s*[—-]\s*(\S+).*?\nJudul:\s*(.+?)\nDeskripsi:\s*(.+?)\nTag:\s*(.+?)\n",
            t, re.S):
        out["shorts"].append({"video": sm.group(2), "judul": sm.group(3).strip(),
                              "deskripsi": sm.group(4).strip(),
                              "tags": [x.strip() for x in sm.group(5).split(",")]})
    return out

def abs_path(p):
    p = p.strip()
    return p if p.startswith("/") else os.path.join(BASE, p)

def upload_video(s, item, publish_at, dry=False):
    vp = abs_path(item["video"])
    size = os.path.getsize(vp)
    if dry:
        print(f"  DRY {item['judul'][:60]} | {size/1e6:.1f}MB | {publish_at}")
        return "DRY_ID"
    body = {"snippet": {"title": item["judul"][:100],
                        "description": item["deskripsi"][:5000],
                        "tags": item["tags"][:30],
                        "categoryId": "27",
                        "defaultLanguage": "id",
                        "defaultAudioLanguage": "id"},
            "status": {"privacyStatus": "private", "publishAt": publish_at,
                       "selfDeclaredMadeForKids": False}}
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)}, timeout=60)
    if r.status_code == 403 and "quotaExceeded" in r.text:
        raise QuotaStop(r.text[:200])
    if r.status_code not in (200, 201):
        raise RuntimeError(f"INIT GAGAL {r.status_code}: {r.text[:300]}")
    up_url = r.headers["Location"]
    chunk = 8 * 1024 * 1024
    vid = None
    with open(vp, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": f"bytes {offset}-{end}/{size}"},
                       timeout=300)
            if rr.status_code == 403 and "quotaExceeded" in rr.text:
                raise QuotaStop(rr.text[:200])
            if rr.status_code not in (200, 201, 308):
                raise RuntimeError(f"CHUNK GAGAL {rr.status_code}: {rr.text[:300]}")
            if rr.status_code in (200, 201):
                vid = rr.json()["id"]
            offset = end + 1
    # thumbnail untuk long
    if item.get("thumbnail") and vid:
        tp = abs_path(item["thumbnail"])
        if os.path.exists(tp):
            tr = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                        params={"videoId": vid},
                        data=open(tp, "rb").read(),
                        headers={"Content-Type": "image/jpeg"}, timeout=120)
            print(f"  thumbnail: {tr.status_code}")
    print(f"  OK videoId={vid}")
    return vid

class QuotaStop(Exception):
    pass

def main():
    dry = "--dry-run" in sys.argv
    s = api_session("youtube-pov")
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"], flush=True)
    if ch["id"] != CHANNEL_ID:
        sys.exit("BATAL: channel aktif bukan @ceritarakyat862!")

    batches = [
        ("templar", "upload-instruksi-pov-2026-10-14-templar.md",
         "2026-10-17T12:00:00.000Z", "2026-10-17T12:00:00.000Z"),
        ("aceh", "upload-instruksi-pov-2026-10-15-aceh.md",
         "2026-10-18T12:00:00.000Z", "2026-10-19T12:00:00.000Z"),
        ("diponegoro", "upload-instruksi-pov-2026-10-14-diponegoro.md",
         "2026-10-20T12:00:00.000Z", "2026-10-20T12:00:00.000Z"),
    ]
    results = {}
    try:
        for slug, md, slot_long, slot_shorts in batches:
            print(f"== {slug} ==", flush=True)
            data = parse_md(os.path.join(BASE, md))
            lg = data["long"]
            assert lg and lg["video"], f"parse long gagal: {md}"
            assert len(data["shorts"]) == 3, f"parse shorts gagal: {md} ({len(data['shorts'])})"
            print(f"  long: {lg['judul'][:60]}", flush=True)
            vid = upload_video(s, lg, slot_long, dry)
            results[slug] = {"long_id": vid, "long_slot": slot_long, "shorts": []}
            long_url = f"https://www.youtube.com/watch?v={vid}"
            for i, sh in enumerate(data["shorts"], 1):
                sh = dict(sh)
                sh["deskripsi"] = sh["deskripsi"].replace("[URL_LONG]", long_url)
                print(f"  short{i}: {sh['judul'][:60]}", flush=True)
                sid = upload_video(s, sh, slot_shorts, dry)
                results[slug]["shorts"].append({"id": sid, "slot": slot_shorts})
    except QuotaStop as e:
        print("QUOTA HABIS, berhenti:", e, flush=True)
        results["_quota_stop"] = True
    json.dump(results, open(RESULT, "w"), indent=1, ensure_ascii=False)
    print("Hasil tersimpan:", RESULT, flush=True)

if __name__ == "__main__":
    main()
