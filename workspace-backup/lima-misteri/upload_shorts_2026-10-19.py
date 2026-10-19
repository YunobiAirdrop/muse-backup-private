#!/usr/bin/env python3
"""Upload 3 shorts Lima Misteri 2026-10-19 (lanjutan: long sudah terupload).
Judul <=100 karakter, ditutup #foryou. Long URL: https://youtu.be/vgt2CeMXkQc
Penggunaan: venv/bin/python upload_shorts_2026-10-19.py
"""
import json, os, sys, importlib.util

BASE = "/home/hatch/workspace/lima-misteri"
TGL = "2026-10-19"
LONG_URL = "https://youtu.be/vgt2CeMXkQc"
LONG_ID = "vgt2CeMXkQc"
PUBLISH_AT = "2026-10-20T12:00:00.000Z"

spec = importlib.util.spec_from_file_location("upl",
    os.path.join(BASE, "upload_lima_2026-10-19.py"))
upl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upl)

AFF_A = upl.AFF_A
AFF_B = upl.AFF_B
AFF_NOTE = upl.AFF_NOTE
DISCLAIMER = upl.DISCLAIMER

SHORTS = [
    {
        "key": "s1",
        "file": f"{BASE}/shorts/{TGL}-s1.mp4",
        "thumb": f"{BASE}/thumbnail-{TGL}-s1.jpg",
        "judul": "Hantu Mulut Tersayat | Lima Misteri #butifyourcloseyoureyesmeme #shorts #foryou",
        "deskripsi": f"Tonton versi lengkapnya: {LONG_URL}\n" + AFF_A + "\n" + AFF_NOTE + "\n" + DISCLAIMER,
        "tags": ["kuchisake-onna", "hantu jepang", "legenda urban", "misteri", "lima misteri", "shorts"],
    },
    {
        "key": "s2",
        "file": f"{BASE}/shorts/{TGL}-s2.mp4",
        "thumb": f"{BASE}/thumbnail-{TGL}-s2.jpg",
        "judul": "Rumah Ditinggal Setelah 28 Hari | Lima Misteri #butifyourcloseyoureyesmeme #shorts #foryou",
        "deskripsi": f"Tonton versi lengkapnya: {LONG_URL}\n" + AFF_B + "\n" + AFF_NOTE + "\n" + DISCLAIMER,
        "tags": ["amityville", "rumah berhantu", "rumah terkutuk", "misteri", "lima misteri", "shorts"],
    },
    {
        "key": "s3",
        "file": f"{BASE}/shorts/{TGL}-s3.mp4",
        "thumb": f"{BASE}/thumbnail-{TGL}-s3.jpg",
        "judul": "Lubang Api Menyala 50 Tahun | Lima Misteri #butifyourcloseyoureyesmeme #shorts #foryou",
        "deskripsi": f"Tonton versi lengkapnya: {LONG_URL}\n" + AFF_A + "\n" + AFF_NOTE + "\n" + DISCLAIMER,
        "tags": ["darvaza", "pintu neraka", "lubang api", "misteri", "lima misteri", "shorts"],
    },
]


def main():
    for v in SHORTS:
        assert len(v["judul"]) <= 100, f"judul s1/s2/s3 {len(v['judul'])} > 100"
        if not os.path.exists(v["file"]):
            sys.exit(f"BATAL: file belum ada: {v['file']}")
    s = upl.api_session(upl.SLUG)
    r = s.get("https://www.googleapis.com/youtube/v3/channels",
              params={"mine": "true", "part": "snippet,contentDetails"}, timeout=30)
    r.raise_for_status()
    ch = r.json()["items"][0]
    print("CHANNEL:", ch["snippet"]["title"], ch["id"])
    if "Lima Misteri" not in ch["snippet"]["title"] or ch["id"] != upl.CHANNEL_ID:
        sys.exit("BATAL: channel aktif bukan Lima Misteri!")
    uplw = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    r = s.get("https://www.googleapis.com/youtube/v3/playlistItems",
              params={"playlistId": uplw, "part": "snippet", "maxResults": 15}, timeout=30)
    r.raise_for_status()
    judul_ada = [it["snippet"]["title"] for it in r.json().get("items", [])]
    for v in SHORTS:
        if v["judul"] in judul_ada:
            sys.exit(f"BATAL: duplikat judul: {v['judul']}")
    print("cek duplikat OK: 3 judul shorts belum ada")
    hasil = {"long": LONG_ID}
    try:
        for v in SHORTS:
            print(f"upload SHORT {v['key']}:", v["judul"][:60], flush=True)
            vid = upl.upload_one(s, v)
            hasil[v["key"]] = vid
            print(f"SHORT {v['key']} OK:", vid, "https://youtu.be/" + vid, flush=True)
    except Exception as e:
        sebab = str(e)
        print("UPLOAD GAGAL:", sebab[:300], flush=True)
        done = set(hasil.keys())
        if upl.is_limit_error(sebab):
            for v in SHORTS:
                if v["key"] not in done:
                    upl.tulis_antrean(v, "Batas upload harian telah tercapai: " + sebab[:200], LONG_URL)
            print("LIMIT HARIAN: antrean ditulis, TIDAK retry.", flush=True)
        else:
            raise
    out = os.path.join(BASE, f"upload-hasil-{TGL}.json")
    json.dump({"publishAt": PUBLISH_AT, **hasil,
               "judul": {"long": upl.LONG_JUDUL,
                         **{v["key"]: v["judul"] for v in SHORTS if v["key"] in hasil}}},
              open(out, "w"), indent=1, ensure_ascii=False)
    print("HASIL:", json.dumps(hasil, ensure_ascii=False))


if __name__ == "__main__":
    main()
