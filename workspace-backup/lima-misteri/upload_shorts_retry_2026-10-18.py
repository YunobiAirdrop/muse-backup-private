#!/usr/bin/env python3
"""Retry upload 3 shorts Lima Misteri 2026-10-18 (long sudah terupload: Pmep7DRs7hY).
Judul shorts diperpendek agar <=100 karakter (batas YouTube).
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/lima-misteri")
sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "upl18", "/home/hatch/workspace/lima-misteri/upload_lima_2026-10-18.py")
_upl = importlib.util.module_from_spec(_spec)
sys.modules["upl18"] = _upl
_spec.loader.exec_module(_upl)
api_session, upload_one = _upl.api_session, _upl.upload_one
is_limit_error, tulis_antrean = _upl.is_limit_error, _upl.tulis_antrean
SLUG, CHANNEL_ID, PUBLISH_AT = _upl.SLUG, _upl.CHANNEL_ID, _upl.PUBLISH_AT
BASE, VIDEOS = _upl.BASE, _upl.VIDEOS
AFF_A, AFF_B, AFF_NOTE, DISCLAIMER = _upl.AFF_A, _upl.AFF_B, _upl.AFF_NOTE, _upl.DISCLAIMER

def tulis_antrean_shorts(video, sebab, long_url):
    instr = os.path.join(BASE, "upload-instruksi-2026-10-18.md")
    with open(instr, "w") as f:
        f.write(f"# Instruksi upload Lima Misteri 2026-10-18 (channel: Lima Misteri / {CHANNEL_ID})\n\n")
        f.write("Slot tayang: 2026-10-19 19:00 WIB (publishAt 2026-10-19T12:00:00.000Z), privacy private.\n")
        f.write("AI disclosure: WAJIB centang 'Altered content' di YouTube Studio setelah upload.\n")
        f.write(f"Long SUDAH terupload: {long_url}\n\n")
        for vv in shorts:
            f.write(f"## {vv['key']}\nJudul: {vv['judul']}\nFile: {vv['file']}\nThumbnail: {vv['thumb']}\nTags: {', '.join(vv['tags'])}\n\nDeskripsi:\n{vv['deskripsi']}\n\n---\n")
    entry = {
        "channel": "Lima Misteri",
        "video_path": video["file"],
        "instruksi_path": instr,
        "slot_target": "2026-10-19 19:00 WIB",
        "gagal_pada": __import__("datetime").datetime.now(
            __import__("datetime").timezone(__import__("datetime").timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00"),
        "sebab": sebab,
    }
    rqp = os.path.join("/home/hatch/workspace/youtube-otomatis/retry-queue",
                       f"lima-misteri-2026-10-18-{video['key']}.json")
    json.dump(entry, open(rqp, "w"), indent=1, ensure_ascii=False)
    print(f"ANTREAN ditulis: {rqp}", flush=True)
SHORT_TITLES = {
    "s1": "Hantu Brown Lady | Lima Misteri #butifyourcloseyoureyesmeme #shorts #misteri #penampakan #foryou",
    "s2": "Legenda dari Internet | Lima Misteri #butifyourcloseyoureyesmeme #shorts #misteri #legenda #foryou",
    "s3": "Kastil Terlarang | Lima Misteri #butifyourcloseyoureyesmeme #shorts #misteri #kastilhantu #foryou",
}

def main():
    shorts = []
    for v in VIDEOS[1:]:
        vv = dict(v)
        vv["judul"] = SHORT_TITLES[vv["key"]]
        vv["deskripsi"] = vv["deskripsi"].replace("__LONG_URL__", LONG_URL)
        shorts.append(vv)
    for vv in shorts:
        assert len(vv["judul"]) <= 100, f"judul {vv['key']} {len(vv['judul'])} > 100"
        assert os.path.exists(vv["file"]), f"file hilang: {vv['file']}"
    s = api_session(SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"])
    if "Lima Misteri" not in ch["snippet"]["title"] or ch["id"] != CHANNEL_ID:
        sys.exit("BATAL: channel aktif bukan Lima Misteri!")
    hasil = {"long": "Pmep7DRs7hY"}
    try:
        for vv in shorts:
            print(f"upload SHORT {vv['key']}:", vv["judul"][:60], flush=True)
            vid = upload_one(s, vv)
            hasil[vv["key"]] = vid
            print(f"SHORT {vv['key']} OK:", vid, "https://youtu.be/" + vid, flush=True)
    except Exception as e:
        sebab = str(e)
        print("UPLOAD GAGAL:", sebab[:300], flush=True)
        if is_limit_error(sebab):
            for vv in shorts:
                if vv["key"] not in hasil:
                    tulis_antrean(vv, "Batas upload harian telah tercapai: " + sebab[:200], LONG_URL)
            print("LIMIT HARIAN: antrean ditulis, TIDAK retry.", flush=True)
        else:
            raise
    out = os.path.join(BASE, "upload-hasil-2026-10-18.json")
    prev = json.load(open(out)) if os.path.exists(out) else {}
    prev.update({"publishAt": PUBLISH_AT, **hasil})
    json.dump(prev, open(out, "w"), indent=1, ensure_ascii=False)
    print("HASIL:", json.dumps(hasil, ensure_ascii=False))

if __name__ == "__main__":
    main()
