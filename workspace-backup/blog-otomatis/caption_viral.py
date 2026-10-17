#!/usr/bin/env python3
"""Bikin caption IG gaya viral untuk 1 artikel (dipanggil share_ig.py).
Pakai: ./venv/bin/python caption_viral.py --judul "..." --blog KabarViral
"""
import argparse, json, os, sys, time
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

# pinjam koneksi + key dari tulis_ulang tanpa eksekusi main()
_src = open(os.path.join(BASE, "tulis_ulang.py")).read()
_g = {"__name__": "__lib__", "__file__": "tulis_ulang.py"}
import sys as _s
_s.argv = ["tulis_ulang.py", "--blog", "kabarviral"]
exec(compile(_src.split("def main():")[0], "tulis_ulang.py", "exec"), _g)
ROUTER_URL, MODELS, get_api_keys = _g["ROUTER_URL"], _g["MODELS"], _g["get_api_keys"]

PROMPT = """Kamu admin sosmed Indonesia yang jago bikin caption viral. Buat caption Instagram untuk berita ini:

JUDUL: {judul}
BLOG: {blog}

Aturan:
- Baris 1: HOOK maksimal 8 kata, bikin orang berhenti scroll (boleh pakai emoji 1-2, tanpa clickbait bohong).
  Pakai SALAH SATU pola hook FYP ini: (a) curiosity gap — "Ternyata selama ini kita salah soal X"; (b) angka spesifik — "3 hal yang berubah setelah X"; (c) kontras — "Bukan X, tapi Y yang bikin ..."; (d) statement berani dari faktanya — "X resmi berlaku mulai hari ini"; (e) pertanyaan langsung — "Kamu kena dampaknya?"; (f) urgensi — "Sebelum kamu X, baca ini". Pilih yang paling cocok dengan beritanya, jangan dipaksa.
- 1-2 kalimat teaser isi berita, gaya ngobrol
- CTA: "Baca selengkapnya, link di bio" / ajak komen pendapat
- Hashtag 8-12 dengan STRATEGI: 2-3 tag besar (#fyp #viral #foryoupage), 4-5 tag niche
  sesuai topik (misal berita keuangan: #investasi #keuangan #saham), 2-3 tag spesifik
  dari isi berita (nama orang/tempat/peristiwa). Jangan asal tempel yang tidak relevan.
- Total maksimal 400 karakter
- Balas HANYA dengan caption, tanpa penjelasan"""

def bikin_caption(judul, blog):
    msg = PROMPT.format(judul=judul, blog=blog)
    last_err = None
    for key in get_api_keys():
        for model in MODELS[:4]:
            try:
                r = requests.post(ROUTER_URL, headers={
                    "Authorization": f"Bearer {key}", "Content-Type": "application/json",
                    "HTTP-Referer": "https://kabarviralterkiniterbaru.blogspot.com/",
                    "X-Title": "Blog Otomatis",
                }, json={"model": model,
                          "messages": [{"role": "user", "content": msg}],
                          "temperature": 0.9, "max_tokens": 400}, timeout=90)
                if r.status_code in (429, 503):
                    if "per-day" in r.text or "free-models" in r.text:
                        break
                    time.sleep(5)
                    continue
                r.raise_for_status()
                dec = json.JSONDecoder()
                obj, _ = dec.raw_decode(r.text.strip())
                teks = obj["choices"][0]["message"]["content"].strip()
                if teks:
                    return teks[:2000]
            except Exception as e:
                last_err = str(e)[:60]
                time.sleep(3)
    raise RuntimeError(f"caption gagal: {last_err}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judul", required=True)
    ap.add_argument("--blog", default="KabarViral")
    a = ap.parse_args()
    print(bikin_caption(a.judul, a.blog))
