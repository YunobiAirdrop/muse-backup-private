#!/usr/bin/env python3
"""Refresh mingguan: ambil 2 artikel evergreen TERLAMA per blog dari arsip,
minta AI perbarui dengan info terkini bulan ini → artikel 'Update'.
Output: data/artikel-<blog>.json (fresh) → siap diposting cron mingguan.
Pakai: ./venv/bin/python refresh.py --blog cuanpintar  (2 req/blog)
"""
import argparse, datetime, json, os, sys, time
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
sys.path.insert(0, BASE)
_src = open(os.path.join(BASE, "tulis_ulang.py")).read()
_g = {"__name__": "__lib__", "__file__": "tulis_ulang.py"}
sys.argv = ["tulis_ulang.py", "--blog", "kabarviral"]
exec(compile(_src.split("def main():")[0], "tulis_ulang.py", "exec"), _g)
ROUTER_URL, MODELS, get_api_keys = _g["ROUTER_URL"], _g["MODELS"], _g["get_api_keys"]

PROMPT = """Kamu editor blog Indonesia. PERBARUI panduan lama ini dengan informasi terkini {bulan}:

JUDUL LAMA: {judul}
ISI LAMA (ringkas): {isi}

Tugas:
- Pertahankan struktur & info yang masih valid
- Perbarui angka, fakta, rekomendasi produk yang berubah; tambahkan bagian "<h2>Update {bulan}</h2>" di awal isi
- Gaya manusiawi, 500-700 kata, minimal 3 <h2>
- Balas HANYA JSON valid:
{{"judul": "judul baru + embel 'Update {bulan_pendek}' (maks 60 karakter)",
  "slug": "slug-url",
  "meta_deskripsi": "maks 160 karakter",
  "label": ["label1", "label2"],
  "artikel_html": "<p>...</p>...",
  "varian_judul": ["alt1", "alt2", "alt3"],
  "faq_html": "",
  "alt_gambar": "teks alt"}}"""

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
    arsip_path = os.path.join(DATA, f"evergreen-archive-{a.blog}.json")
    if not os.path.exists(arsip_path):
        print(f"arsip evergreen {a.blog} belum ada")
        return
    arsip = json.load(open(arsip_path))
    done_path = os.path.join(DATA, "refresh_done.json")
    done = json.load(open(done_path)) if os.path.exists(done_path) else {}
    sudah = set(done.get(a.blog, []))
    kandidat = [x for x in arsip if x["judul"] not in sudah][:a.jumlah]
    if not kandidat:
        print(f"semua arsip {a.blog} sudah di-refresh")
        return
    bulan = datetime.date.today().strftime("%B %Y")
    bulan_id = {"January": "Januari", "February": "Februari", "March": "Maret",
                "April": "April", "May": "Mei", "June": "Juni", "July": "Juli",
                "August": "Agustus", "September": "September", "October": "Oktober",
                "November": "November", "December": "Desember"}
    for en, idn in bulan_id.items():
        bulan = bulan.replace(en, idn)
    bulan_pendek = bulan.split()[0] + " " + bulan.split()[1]
    hasil = []
    for k in kandidat:
        print(f"Refresh {a.blog}: {k['judul'][:50]}...")
        art = panggil(PROMPT.format(bulan=bulan, bulan_pendek=bulan_pendek,
                                    judul=k["judul"], isi=k["artikel_html"][:1500]))
        if art:
            art["link_sumber"] = blog.get("url", "")
            hasil.append(art)
            sudah.add(k["judul"])
            print(f"  OK: {art['judul'][:55]}")
        else:
            print("  GAGAL")
        time.sleep(3)
    if hasil:
        path = os.path.join(DATA, f"artikel-{a.blog}.json")
        json.dump(hasil, open(path, "w"), ensure_ascii=False, indent=1)
        done[a.blog] = sorted(sudah)
        json.dump(done, open(done_path, "w"), ensure_ascii=False, indent=1)
        print(f"Siap posting: {len(hasil)} artikel refresh")

if __name__ == "__main__":
    main()
