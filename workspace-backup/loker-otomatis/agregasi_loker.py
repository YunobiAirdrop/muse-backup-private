#!/usr/bin/env python3
"""Agregasi lowongan kerja harian dari RSS Google News (gratis, tanpa login).

Mengambil item dari sumber RSS di config.json, memfilter yang benar-benar
lowongan (bukan berita hoaks/isu), anti-duplikat via data/loker_riwayat.json,
lalu menulis data/antrean-loker.json dengan format yang dimengerti tulis_loker.py:
{judul_asli, link, ringkasan, sumber, tanggal}

Pakai: ./venv-blog/bin/python agregasi_loker.py  (atau python3 agregasi_loker.py)
"""
import json, os, re, sys, time
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

try:
    import requests
except ImportError:
    print("butuh requests: pip install requests")
    sys.exit(1)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# kata yang menandakan item BUKAN lowongan asli -> buang
BUANG = re.compile(r"hoaks|hoax|penipuan|waspada.*penipuan|klarifikasi", re.I)
# kata yang menandakan item lowongan -> pertahankan
LOKER = re.compile(r"lowongan|loker|rekrutmen|dibuka|buka.*posisi|formasi|pendaftaran|bursa kerja|job fair|magang|cpns|pppk", re.I)

def fetch_rss(url, nama):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=25)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    items = []
    for it in root.findall(".//item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()
        src_el = it.find("source")
        sumber = (src_el.text or "").strip() if src_el is not None else ""
        guid = (it.findtext("guid") or link or title).strip()
        if not title:
            continue
        items.append({"judul_asli": title, "link": link, "sumber": sumber,
                      "tanggal": pub, "guid": guid, "rss": nama})
    return items

def main():
    cfg = json.load(open(os.path.join(BASE, "config.json")))
    maks = cfg.get("maks_artikel_per_hari", 10)
    riwayat_path = os.path.join(DATA, "loker_riwayat.json")
    riwayat = set(json.load(open(riwayat_path))) if os.path.exists(riwayat_path) else set()

    semua = []
    for s in cfg["sumber_rss"]:
        try:
            items = fetch_rss(s["url"], s["nama"])
            print(f"{s['nama']}: {len(items)} item")
            semua.extend(items)
        except Exception as e:
            print(f"{s['nama']}: GAGAL ({str(e)[:80]}) -> lanjut sumber lain")
        time.sleep(1)

    # filter: buang hoaks/penipuan, pertahankan yang berbau loker
    bagus = []
    for it in semua:
        t = it["judul_asli"]
        if BUANG.search(t):
            continue
        if not LOKER.search(t):
            continue
        bagus.append(it)

    # dedupe antar-sumber (judul mirip) + anti-duplikat riwayat
    unik, seen = [], set()
    for it in bagus:
        kunci = re.sub(r"\W+", "", it["judul_asli"].lower())[:60]
        if kunci in seen or it["guid"] in riwayat:
            continue
        seen.add(kunci)
        unik.append(it)

    pilih = unik[:maks]
    # ringkasan: dari judul (RSS Google News tidak bawa isi artikel).
    # tulis_loker.py memakai judul+sumber sebagai bahan; link disimpan untuk referensi.
    antrean = []
    for it in pilih:
        antrean.append({
            "judul_asli": it["judul_asli"],
            "link": it["link"],
            "ringkasan": it["judul_asli"] + f" (sumber: {it['sumber']}).",
            "sumber": it["sumber"],
            "tanggal": it["tanggal"],
        })

    json.dump(antrean, open(os.path.join(DATA, "antrean-loker.json"), "w"),
              ensure_ascii=False, indent=1)
    # update riwayat
    riwayat.update(it["guid"] for it in pilih)
    json.dump(sorted(riwayat)[-2000:], open(riwayat_path, "w"))
    print(f"Selesai: {len(antrean)} loker masuk antrean "
          f"(riwayat total {len(riwayat)})")
    for a in antrean:
        print(" -", a["judul_asli"][:70])

if __name__ == "__main__":
    main()
