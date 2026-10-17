#!/usr/bin/env python3
"""Artikel roundup harian 'Terpopuler Hari Ini' per blog: AI rangkum 5 artikel
terbaik hari ini jadi 1 artikel rekap + teaser. Di-append ke artikel-*.json
agar ikut terposting. Pakai: ./venv/bin/python digest.py --blog kabarviral
"""
import argparse, datetime, json, os, sys, time
from urllib.parse import quote
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
sys.path.insert(0, BASE)
_src = open(os.path.join(BASE, "tulis_ulang.py")).read()
_g = {"__name__": "__lib__", "__file__": "tulis_ulang.py"}
sys.argv = ["tulis_ulang.py", "--blog", "kabarviral"]
exec(compile(_src.split("def main():")[0], "tulis_ulang.py", "exec"), _g)
ROUTER_URL, MODELS, get_api_keys = _g["ROUTER_URL"], _g["MODELS"], _g["get_api_keys"]

NAMES = {"kabarviral": "KabarViral", "cuanpintar": "CuanPintar",
         "teknogebrakan": "TeknoGebrakan", "sehatbugar": "SehatBugar"}

PROMPT = """Kamu editor blog Indonesia "{blog}". Tulis artikel REKAP harian "Terpopuler Hari Ini" dari 5 berita berikut. Gaya santai, tiap berita 2-3 kalimat teaser yang bikin penasaran (tanpa mengulang isi penuh).

Berita:
{daftar}

Balas HANYA JSON valid:
{{"judul": "Terpopuler Hari Ini: <topik paling panas> dan 4 Berita Lainnya",
  "artikel_html": "<p>Pembuka 2 kalimat...</p><h2>1. ...</h2><p>teaser...</p> ... (5 item) <p>Sumber: Redaksi {blog}</p>"}}
Maks 350 kata."""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blog", required=True)
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(BASE, "config.json")))
    blog = next(b for b in cfg["blogs"] if b["nama"] == a.blog)
    blog_url = blog.get("url", "").rstrip("/")
    path = os.path.join(DATA, f"artikel-{a.blog}.json")
    if not os.path.exists(path):
        print("tidak ada artikel hari ini")
        return
    artikels = json.load(open(path))
    if len(artikels) < 3:
        print("artikel kurang dari 3, digest dilewati")
        return
    top5 = artikels[:5]
    daftar = "\n".join(f"- {x['judul']}" for x in top5)
    msg = PROMPT.format(blog=NAMES.get(a.blog, a.blog), daftar=daftar)
    hasil = None
    for key in get_api_keys():
        for model in MODELS[:4]:
            try:
                r = requests.post(ROUTER_URL, headers={
                    "Authorization": f"Bearer {key}", "Content-Type": "application/json",
                    "HTTP-Referer": "https://kabarviralterkiniterbaru.blogspot.com/",
                    "X-Title": "Blog Otomatis",
                }, json={"model": model, "messages": [{"role": "user", "content": msg}],
                          "temperature": 0.7, "max_tokens": 1500}, timeout=150)
                if r.status_code in (429, 503):
                    if "per-day" in r.text or "free-models" in r.text:
                        break
                    time.sleep(5)
                    continue
                r.raise_for_status()
                dec = json.JSONDecoder()
                obj, _ = dec.raw_decode(r.text.strip())
                teks = obj["choices"][0]["message"]["content"].replace("```json", "").replace("```", "").strip()
                hasil = json.loads(teks[teks.find("{"):])
                break
            except Exception:
                time.sleep(3)
        if hasil:
            break
    if not hasil:
        print("digest gagal")
        return
    # tambahkan link baca selengkapnya per item via search URL
    html = hasil["artikel_html"]
    for x in top5:
        q = quote(x["judul"][:40])
        html += f'\n<p><a href="{blog_url}/search?q={q}">Baca selengkapnya: {x["judul"][:60]}</a></p>'
    tanggal = datetime.date.today().strftime("%d %B %Y")
    digest = {
        "judul": hasil["judul"][:70],
        "slug": f"terpopuler-hari-ini-{datetime.date.today().isoformat()}",
        "meta_deskripsi": "Rangkuman 5 berita terpopuler hari ini.",
        "label": ["Terpopuler", "Headline"],
        "artikel_html": html,
        "gambar": top5[0].get("gambar", ""),
        "link_sumber": blog_url,
    }
    artikels.append(digest)
    json.dump(artikels, open(path, "w"), ensure_ascii=False, indent=1)
    print(f"digest ditambahkan: {digest['judul'][:60]}")

if __name__ == "__main__":
    main()
