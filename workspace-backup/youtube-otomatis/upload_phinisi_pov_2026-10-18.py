#!/usr/bin/env python3
"""Upload POV Phinisi 1682 2026-10-18 ke @ceritarakyat862 via YouTube Data API (resumable).
Long + 3 shorts, semua terjadwal KAMIS 2026-10-22 19:00 WIB.
AI disclosure TIDAK didukung API -> WAJIB dicentang manual via Studio (dicatat di laporan).
Jalankan dengan venv: ~/workspace/youtube-otomatis/yt-growth/venv/bin/python
"""
import json, os, re, sys

BASE = os.path.expanduser("~/workspace/youtube-otomatis")
sys.path.insert(0, os.path.join(BASE, "yt-growth"))
from auth import api_session

CHANNEL_ID = "UC1c8WpKGhFKpUOp5AqVueEg"
MD = os.path.join(BASE, "upload-instruksi-pov-2026-10-18.md")
SLOT = "2026-10-22T12:00:00.000Z"  # Rabu 19:00 WIB
RESULT = os.path.join(BASE, "yt-growth", "hidden_files", "upload-pov-Samurai-2026-10-18.json")

def abs_path(p):
    p = p.strip()
    return p if p.startswith("/") else os.path.join(BASE, p)

def parse_md(path):
    t = open(path).read()
    out = {"long": None, "shorts": []}
    m = re.search(r"## VIDEO LONG.*?\nFile:\s*(\S+).*?\nThumbnail:\s*upload\s*(\S+).*?"
                  r"### Judul\n(.+?)\n\n### Deskripsi\n(.+?)\n\n### Tag YouTube\n(.+?)\n",
                  t, re.S)
    assert m, "parse long gagal"
    out["long"] = {"video": m.group(1), "thumbnail": m.group(2),
                   "judul": m.group(3).strip(), "deskripsi": m.group(4).strip(),
                   "tags": [x.strip() for x in m.group(5).split(",")]}
    for sm in re.finditer(r"## SHORT \d+.*?\nFile:\s*(\S+)\nJudul:\s*(.+?)\nDeskripsi:\n(.+?)\nTag:\s*(.+?)\n",
                          t, re.S):
        out["shorts"].append({"video": sm.group(1), "judul": sm.group(2).strip(),
                              "deskripsi": sm.group(3).strip(),
                              "tags": [x.strip() for x in sm.group(4).split(",")]})
    assert len(out["shorts"]) == 3, f"parse shorts gagal ({len(out['shorts'])})"
    return out

def upload_video(s, item, publish_at, dry=False):
    vp = abs_path(item["video"])
    size = os.path.getsize(vp)
    if dry:
        print(f"  DRY {item['judul'][:60]} | {size/1e6:.1f}MB | {publish_at}", flush=True)
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
    if item.get("thumbnail") and vid:
        tp = abs_path(item["thumbnail"])
        if os.path.exists(tp):
            tr = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                        params={"videoId": vid},
                        data=open(tp, "rb").read(),
                        headers={"Content-Type": "image/jpeg"}, timeout=120)
            print(f"  thumbnail: {tr.status_code}", flush=True)
    print(f"  OK videoId={vid}", flush=True)
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
    data = parse_md(MD)
    results = {}
    try:
        lg = data["long"]
        print(f"long: {lg['judul'][:60]}", flush=True)
        vid = upload_video(s, lg, SLOT, dry)
        results["long_id"] = vid
        results["long_slot"] = SLOT
        long_url = f"https://www.youtube.com/watch?v={vid}"
        results["shorts"] = []
        for i, sh in enumerate(data["shorts"], 1):
            sh = dict(sh)
            sh["deskripsi"] = sh["deskripsi"].replace("[URL_LONG]", long_url)
            print(f"short{i}: {sh['judul'][:60]}", flush=True)
            sid = upload_video(s, sh, SLOT, dry)
            results["shorts"].append({"id": sid, "slot": SLOT})
    except QuotaStop as e:
        print("QUOTA HABIS, berhenti:", e, flush=True)
        results["_quota_stop"] = True
    json.dump(results, open(RESULT, "w"), indent=1, ensure_ascii=False)
    print("Hasil tersimpan:", RESULT, flush=True)

if __name__ == "__main__":
    main()
