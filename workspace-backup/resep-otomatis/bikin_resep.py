#!/usr/bin/env python3
"""Generate 3 resep masakan Indonesia orisinal per hari via OpenRouter (model gratis).
Pola rotasi key & model mengikuti blog-otomatis/tulis_ulang.py.
Output: data/resep-YYYY-MM-DD.json ; anti-ulang 60 hari via riwayat-resep.json
"""
import json, os, re, sys, time, random
from datetime import date, timedelta
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

def _load_proxy_env():
    try:
        with open("/etc/9router-proxy.env") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass
_load_proxy_env()

ROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS = [
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "nvidia/nemotron-3.5-lightning:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "thinkingmachines/inkling:free",
    "inclusionai/ling-3.0-flash-sante:free",
    "qwen/qwen3.8-27b:free",
    "google/gemma-4-31b-it:free",
]
# model non-reasoning diutamakan (anti reasoning leak)
MODELS_NON_REASON = [m for m in MODELS if "reasoning" not in m]

def get_api_keys():
    env_path = os.path.expanduser("~/.hermes/.env")
    keys = []
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("OPENROUTER_KEYS="):
                keys = [k.strip().strip('"').strip("'") for k in line.split("=", 1)[1].split(",") if k.strip()]
            elif line.startswith("NINEROUTER_API_KEY=") and not keys:
                keys = [line.split("=", 1)[1].strip('"').strip("'")]
    if not keys:
        raise RuntimeError("Tidak ada API key (OPENROUTER_KEYS / NINEROUTER_API_KEY)")
    return keys

PROMPT = """Kamu chef & food writer Indonesia. Buatkan SATU resep orisinal Bahasa Indonesia untuk: {nama} (kategori: {kategori}).

Gaya: hangat, jelas, seperti ditulis food blogger manusia — hindari pola AI kaku. DILARANG: kalimat klise ("di era digital", "sebagai kesimpulan"), pola "bukan X melainkan Y".

Balas HANYA JSON valid (tanpa markdown):
{{
  "judul": "judul menarik maks 60 karakter, misal 'Rendang Daging Empuk, Bumbu Meresap!'",
  "deskripsi": "1-2 kalimat pembuka yang menggugah selera",
  "bahan": ["500 gr daging sapi, potong dadu", "takaran JELAS tiap bahan"],
  "bumbu_halus": ["5 siung bawang merah", "..."] atau [],
  "langkah": ["1. Langkah bernomor, jelas, urut", "..."],
  "tips": ["2-3 tips praktis"],
  "waktu": "misal '90 menit'",
  "porsi": "misal '4 porsi'",
  "kesulitan": "Mudah/Sedang",
  "prompt_gambar": "deskripsi 1 kalimat untuk food photography: hidangan + penyajian + background, tanpa teks"
}}
Bahan: takaran jelas (gr, sdm, sdt, siung, buah). Langkah: minimal 5, maksimal 10, urut dan praktis.
"""

def extract_json(text):
    text = re.sub(r"```(?:json)?", "", text).strip()
    start = text.find("{")
    if start < 0:
        raise ValueError("tidak ada JSON")
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        c = text[i]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
        else:
            if c == '"': in_str = True
            elif c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(text[start:i + 1])
    raise ValueError("JSON tidak seimbang")

def panggil_ai(nama, kategori):
    msg = PROMPT.format(nama=nama, kategori=kategori)
    keys = get_api_keys()
    last_err = None
    keys_kena_limit = 0
    for key in keys:
        pindah = False
        for model in MODELS_NON_REASON + MODELS:
            if pindah: break
            for attempt in range(2):
                try:
                    r = requests.post(ROUTER_URL, headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://kabarviralterkiniterbaru.blogspot.com/",
                        "X-Title": "Resep Otomatis",
                    }, json={"model": model,
                             "messages": [{"role": "user", "content": msg}],
                             "temperature": 0.8, "max_tokens": 1500},
                             timeout=120)
                    if r.status_code in (429, 503):
                        last_err = f"{model} {r.status_code}"
                        if "per-day" in r.text or "free-models" in r.text:
                            keys_kena_limit += 1
                            if keys_kena_limit >= len(keys):
                                raise RuntimeError("QUOTA_HABIS: limit harian model gratis habis di semua akun")
                            pindah = True
                            break
                        time.sleep(5 * (attempt + 1))
                        continue
                    r.raise_for_status()
                    obj = r.json()
                    ch = obj.get("choices") or []
                    text = (ch[0].get("message", {}).get("content") if ch else "") or ""
                    if not text.strip():
                        raise ValueError("respons tanpa konten")
                    if "thinking process" in text.lower():
                        raise ValueError("reasoning leak, coba model lain")
                    resep = extract_json(text)
                    resep["model"] = model
                    return resep
                except (requests.RequestException, ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
                    last_err = str(e)[:120]
                    time.sleep(2)
                    continue
    raise RuntimeError(f"Gagal generate resep '{nama}': {last_err}")

def pilih_resep(n=3, anti_hari=60):
    pool = json.load(open(os.path.join(BASE, "pool-resep.json")))
    riw_path = os.path.join(BASE, "riwayat-resep.json")
    riw = json.load(open(riw_path)) if os.path.exists(riw_path) else {}
    batas = date.today() - timedelta(days=anti_hari)
    kandidat = [p for p in pool
                if not p["nama"] in riw
                or date.fromisoformat(riw[p["nama"]]) < batas]
    if len(kandidat) < n:
        kandidat = pool  # pool habis, reset siklus
    return random.sample(kandidat, n)

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    hari = date.today().isoformat()
    out_path = os.path.join(DATA, f"resep-{hari}.json")
    if os.path.exists(out_path):
        print(f"Resep hari ini sudah ada: {out_path}")
        return
    pilihan = pilih_resep(n)
    hasil = []
    for p in pilihan:
        print(f"Generate: {p['nama']} ...", flush=True)
        try:
            r = panggil_ai(p["nama"], p["kategori"])
        except RuntimeError as e:
            print(f"  GAGAL: {e}")
            continue
        r["nama_pool"] = p["nama"]
        r["kategori"] = p["kategori"]
        hasil.append(r)
    if not hasil:
        print("Tidak ada resep berhasil dibuat.")
        sys.exit(1)
    json.dump(hasil, open(out_path, "w"), ensure_ascii=False, indent=1)
    riw_path = os.path.join(BASE, "riwayat-resep.json")
    riw = json.load(open(riw_path)) if os.path.exists(riw_path) else {}
    for r in hasil:
        riw[r["nama_pool"]] = hari
    json.dump(riw, open(riw_path, "w"), ensure_ascii=False, indent=1)
    print(f"OK: {len(hasil)} resep -> {out_path}")

if __name__ == "__main__":
    main()
