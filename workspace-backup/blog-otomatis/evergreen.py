#!/usr/bin/env python3
"""Artikel evergreen: 2 panduan timeless per blog per hari (konten yang
tetap dicari bertahun-tahun, fondasi trafik organik jangka panjang).
Topik dari evergreen_topik.json, anti-duplikat via data/evergreen_done.json.
Output di-append ke artikel-*.json agar ikut terposting.
Pakai: ./venv/bin/python evergreen.py --blog cuanpintar
"""
import argparse, json, os, sys, time
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
sys.path.insert(0, BASE)
_src = open(os.path.join(BASE, "tulis_ulang.py")).read()
_g = {"__name__": "__lib__", "__file__": "tulis_ulang.py"}
sys.argv = ["tulis_ulang.py", "--blog", "kabarviral"]
exec(compile(_src.split("def main():")[0], "tulis_ulang.py", "exec"), _g)
ROUTER_URL, MODELS, get_api_keys = _g["ROUTER_URL"], _g["MODELS"], _g["get_api_keys"]

PROMPT = """Kamu penulis panduan Indonesia yang ahli. Tulis ARTIKEL orisinal Bahasa Indonesia tentang topik ini:

TOPIK: {topik}
NICHE BLOG: {niche}

Syarat: 600-800 kata, gaya manusiawi (hindari pola AI kaku), minimal 4 subjudul <h2> deskriptif, sertakan tips praktis bernomor/langkah konkret, contoh angka nyata, dan FAQ 3 pertanyaan di akhir. Kata kunci utama harus ada di judul, satu <h2>, dan paragraf pertama.

ATURAN FORMAT (ikuti sesuai jenis topik):
{format_rule}

Balas HANYA JSON valid:
{{"judul": "judul SEO maks 60 karakter",
  "slug": "slug-url",
  "meta_deskripsi": "maks 160 karakter",
  "label": ["label1", "label2"],
  "artikel_html": "<p>...</p><h2>...</h2>...<h2>Pertanyaan Umum</h2><p><strong>Q?</strong><br>A.</p>",
  "varian_judul": ["alt1", "alt2", "alt3"],
  "faq_html": "",
  "alt_gambar": "teks alt deskriptif"}}"""

def aturan_format(topik):
    tl = topik.lower()
    if " vs " in tl or "perbandingan" in tl or "plus minus" in tl:
        return ("Topik ini PERBANDINGAN: buat tabel perbandingan (HTML <table>) plus-minus tiap opsi, "
                "beri skor/penilaian tiap aspek, dan akhiri dengan <h2>Kesimpulan: Pilih Mana?</h2> berisi rekomendasi jelas per profil pembaca.")
    if "rekomendasi" in tl or "terbaik" in tl:
        return ("Topik ini REKOMENDASI: tulis sebagai daftar bernomor (<ol>), tiap item ada deskripsi + kelebihan + kisaran harga/angka, "
                "awali dengan <h2>Kriteria Memilih</h2> agar pembaca paham cara menilai.")
    if tl.startswith("cara ") or "cara " in tl:
        return ("Topik ini TUTORIAL: tulis langkah-langkah bernomor (<ol>) yang runut dan bisa langsung dipraktikkan, "
                "tambahkan <h2>Kesalahan Umum</h2> berisi hal yang harus dihindari.")
    return ("Topik ini PANDUAN UMUM: struktur logis dari dasar sampai tips lanjutan, "
            "gunakan contoh nyata dan data/angka agar meyakinkan.")

def panggil(msg):
    for key in get_api_keys():
        for model in MODELS:
            for _ in range(2):
                try:
                    r = requests.post(ROUTER_URL, headers={
                        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
                        "HTTP-Referer": "https://kabarviralterkiniterbaru.blogspot.com/",
                        "X-Title": "Blog Otomatis",
                    }, json={"model": model, "messages": [{"role": "user", "content": msg}],
                              "temperature": 0.7, "max_tokens": 2500}, timeout=180)
                    if r.status_code in (429, 503):
                        if "per-day" in r.text or "free-models" in r.text:
                            break
                        time.sleep(5)
                        continue
                    r.raise_for_status()
                    dec = json.JSONDecoder()
                    obj, _ = dec.raw_decode(r.text.strip())
                    teks = obj["choices"][0]["message"]["content"]
                    teks = teks.replace("```json", "").replace("```", "").strip()
                    return json.loads(teks[teks.find("{"):])
                except Exception:
                    time.sleep(5)
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blog", required=True)
    ap.add_argument("--jumlah", type=int, default=2)
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(BASE, "config.json")))
    blog = next(b for b in cfg["blogs"] if b["nama"] == a.blog)
    niche = blog.get("niche", "campuran")
    bank = json.load(open(os.path.join(BASE, "evergreen_topik.json")))
    daftar = bank.get(niche, bank["campuran"])
    done_path = os.path.join(DATA, "evergreen_done.json")
    done = json.load(open(done_path)) if os.path.exists(done_path) else {}
    sudah = set(done.get(a.blog, []))
    antre = [t for t in daftar if t not in sudah][:a.jumlah]
    if not antre:
        print("semua topik sudah dipakai, reset daftar")
        sudah.clear()
        antre = daftar[:a.jumlah]
    path = os.path.join(DATA, f"artikel-{a.blog}.json")
    artikels = json.load(open(path)) if os.path.exists(path) else []
    for topik in antre:
        print(f"Evergreen {a.blog}: {topik[:50]}...")
        art = panggil(PROMPT.format(topik=topik, niche=niche, format_rule=aturan_format(topik)))
        if art:
            art["link_sumber"] = blog.get("url", "")
            art["_evergreen_baru"] = True
            artikels.append(art)
            sudah.add(topik)
            print(f"  OK: {art['judul'][:55]}")
        else:
            print("  GAGAL")
        time.sleep(3)
    json.dump(artikels, open(path, "w"), ensure_ascii=False, indent=1)
    done[a.blog] = sorted(sudah)
    json.dump(done, open(done_path, "w"), ensure_ascii=False, indent=1)
    # arsip khusus evergreen (untuk refresh mingguan)
    arsip_path = os.path.join(DATA, f"evergreen-archive-{a.blog}.json")
    arsip = json.load(open(arsip_path)) if os.path.exists(arsip_path) else []
    for art in artikels:
        if art.get("_evergreen_baru"):
            arsip.append({"judul": art["judul"], "artikel_html": art["artikel_html"][:2000],
                          "tanggal": time.strftime("%Y-%m-%d")})
            del art["_evergreen_baru"]
    json.dump(artikels, open(path, "w"), ensure_ascii=False, indent=1)
    json.dump(arsip, open(arsip_path, "w"), ensure_ascii=False, indent=1)
    print(f"Selesai evergreen {a.blog}: {len(antre)} topik")

if __name__ == "__main__":
    main()
