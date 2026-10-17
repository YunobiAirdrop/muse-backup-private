#!/usr/bin/env python3
"""Retry regenerasi Video 3 saja (masih bocor). Model non-reasoning, validasi ketat."""
import json, os, re, sys, time
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
_src = open(os.path.join(BASE, "tulis_ulang.py")).read()
_g = {"__name__": "__lib__", "__file__": os.path.join(BASE, "tulis_ulang.py")}
sys.argv = ["tulis_ulang.py", "--blog", "kabarviral"]
exec(compile(_src.split("def main():")[0], "tulis_ulang.py", "exec"), _g)
ROUTER_URL, get_api_keys = _g["ROUTER_URL"], _g["get_api_keys"]

MODELS_NR = ["qwen/qwen3.8-27b:free", "google/gemma-4-31b-it:free",
             "google/gemma-4-26b-a4b-it:free", "inclusionai/ling-3.0-flash-sante:free"]
SYSTEM = ("Jawab LANGSUNG dengan format yang diminta saja. DILARANG keras menulis "
          "proses berpikir, monolog internal, atau analisis. Langsung ke output final.")

PROMPT = """Kamu scriptwriter konten viral Indonesia (TikTok/Reels/Shorts). Buat SCRIPT VIDEO 30-45 detik dari berita ini:

JUDUL: Persiapan Mudik Lebaran: Panduan Lengkap & Praktis
ISI SINGKAT: Panduan praktis persiapan mudik Lebaran: cek kondisi kendaraan (rem, ban, oli), siapkan budget terpisah untuk bensin/tol/makan, kemas barang esensial secukupnya, bawa obat pribadi dan snack untuk macet.

Wajib pakai format persis ini (Bahasa Indonesia santai):
[HOOK 0-3 detik]: 1 kalimat pembuka maks 12 kata, tanpa clickbait bohong.
[ISI 3-30 detik]: 3 poin penting, 1 kalimat per poin, gaya ngobrol.
[CTA 30-45 detik]: ajakan komen/follow + "link lengkap di bio".
[TEKS LAYAR]: 3 teks singkat untuk overlay video.
[VISUAL]: saran visual per segmen, 1 baris per segmen.

Balas HANYA dengan format di atas."""

LEAK = ["thinking process", "here's a thinking", "here is a thinking",
        "i need to", "i should", "let me think", "pola hook fyp ini",
        "format strictly", "1 kalimat pembuka yang bikin"]

def valid(s):
    low = s.lower()
    for p in LEAK:
        if p in low: return False, p
    for m in ["[HOOK", "[ISI", "[CTA", "[TEKS LAYAR]", "[VISUAL]"]:
        if m not in s: return False, m
    return True, "ok"

def main():
    keys = get_api_keys()
    print(f"{len(keys)} keys")
    for ki, key in enumerate(keys):
        for model in MODELS_NR:
            name = model.split("/")[1][:22]
            try:
                r = requests.post(ROUTER_URL, headers={
                    "Authorization": f"Bearer {key}", "Content-Type": "application/json",
                    "HTTP-Referer": "https://kabarviralterkiniterbaru.blogspot.com/",
                    "X-Title": "Blog Otomatis",
                }, json={"model": model, "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": PROMPT}],
                    "temperature": 0.7, "max_tokens": 1000}, timeout=120)
                if r.status_code in (429, 503):
                    print(f"  key{ki} {name}: {r.status_code} {(r.text[:60])}")
                    if "per-day" in r.text or "free-models" in r.text:
                        break
                    time.sleep(5); continue
                r.raise_for_status()
                obj, _ = json.JSONDecoder().raw_decode(r.text.strip())
                teks = obj["choices"][0]["message"]["content"].strip()
                ok, why = valid(teks)
                print(f"  key{ki} {name}: valid={ok} ({why})")
                if ok:
                    md_path = os.path.join(BASE, "data", "video-script-2026-10-03.md")
                    md = open(md_path).read()
                    header = "## Video 3 — KabarViral"
                    pat = re.compile(re.escape(header) + r".*?\n---\n", re.S)
                    new = (f"{header}\n**Berita:** Persiapan Mudik Lebaran: "
                           f"Panduan Lengkap & Praktis\n\n{teks}\n\n---\n")
                    md, n = pat.subn(new, md, count=1)
                    open(md_path, "w").write(md)
                    print(f"  diganti: {n} -> {md_path}")
                    return
            except Exception as e:
                print(f"  key{ki} {name}: err {str(e)[:70]}")
                time.sleep(3)
    print("GAGAL semua")

if __name__ == "__main__":
    main()
