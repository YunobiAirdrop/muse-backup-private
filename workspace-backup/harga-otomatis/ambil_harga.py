#!/usr/bin/env python3
"""Ambil harga harian: sembako (BI PIHPS API) + emas Antam (logammulia.com).
Output: data/harga-YYYY-MM-DD.json
Semua gratis, tanpa API key.
"""
import json, os, re, sys, time, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)
WIB = timezone(timedelta(hours=7))

PIHPS = "https://www.bi.go.id/hargapangan/WebSite/Home/GetDetailGridData2"
LOGAMMULIA = "https://www.logammulia.com/id/harga-emas-hari-ini"

# comId PIHPS -> (label pendek, satuan)
KOMODITAS = {
    3:  ("Beras Medium", "kg"),
    10: ("Telur Ayam", "kg"),
    14: ("Cabai Merah Keriting", "kg"),
    11: ("Bawang Merah", "kg"),
    12: ("Bawang Putih", "kg"),
    17: ("Minyak Goreng Curah", "liter"),
    21: ("Gula Pasir", "kg"),
    7:  ("Daging Ayam", "kg"),
    8:  ("Daging Sapi", "kg"),
}

def get(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")

def ambil_pihps():
    """Return dict comId -> {tanggal, harga, harga_kemarin} level nasional."""
    hasil = {}
    tgl_en = datetime.now(WIB).strftime("%d %B %Y")  # "03 October 2026"
    for com_id, (label, satuan) in KOMODITAS.items():
        try:
            q = urllib.parse.urlencode({
                "ProvId": 0, "PriceTypeId": 1, "ComId": com_id,
                "date": tgl_en, "isPasokan": 1, "_": int(time.time() * 1000)})
            d = json.loads(get(f"{PIHPS}?{q}"))
            rows = d.get("data", [])
            nas = next((r for r in rows if r.get("level") == 0), None)
            if not nas:
                print(f"  ! {label}: baris nasional tidak ada"); continue
            tgls = sorted(k for k in nas.keys()
                          if re.fullmatch(r"\d{2}/\d{2}/\d{4}", k))
            if len(tgls) < 2:
                print(f"  ! {label}: data tanggal kurang"); continue
            t_baru, t_lama = tgls[-1], tgls[-2]
            h_baru, h_lama = nas.get(t_baru), nas.get(t_lama)
            if h_baru is None:
                print(f"  ! {label}: harga terbaru kosong"); continue
            hasil[label] = {"tanggal": t_baru, "harga": round(h_baru),
                            "harga_kemarin": round(h_lama) if h_lama else None,
                            "satuan": satuan, "sumber": "PIHPS-BI"}
            print(f"  OK {label}: Rp{h_baru:,.0f}/{satuan} ({t_baru})")
        except Exception as e:
            print(f"  X {label}: {str(e)[:100]}")
        time.sleep(0.3)  # courtesy delay
    return hasil

LM_API = "https://logam-mulia-api.iamutaki.workers.dev/api/prices/logammulia"

def ambil_emas():
    """Return dict harga emas Antam 1 gram via API publik gratis.
    Fallback: scrape logammulia.com (sering 403 dari datacenter)."""
    # 1) API publik
    try:
        d = json.loads(get(LM_API))
        rows = d.get("data", [])
        r1 = next((r for r in rows if r.get("weight") == 1
                   and r.get("materialType") == "Emas Batangan"), None)
        if r1 and r1.get("sellPrice"):
            harga = int(r1["sellPrice"])
            tgl = r1.get("recordedDate", "")
            print(f"  OK Emas Antam 1gr: Rp{harga:,} ({tgl}, via API)")
            return {"Emas Antam 1gr": {"tanggal": tgl, "harga": harga,
                    "harga_kemarin": None, "satuan": "gram",
                    "sumber": "logam-mulia-api"}}
        print("  ! Emas API: baris 1gr tidak ada")
    except Exception as e:
        print(f"  ! Emas API gagal: {str(e)[:80]}")
    # 2) fallback scrape langsung
    try:
        html = get(LOGAMMULIA)
        m = re.search(r"## Harga Emas Hari Ini,\s*([^\n<]+)", html)
        tgl = m.group(1).strip() if m else datetime.now(WIB).strftime("%d %b %Y")
        m2 = re.search(r"\|\s*1 gr\s*\|\s*([\d,]+)\s*\|", html)
        if not m2:
            print("  X Emas: baris 1 gr tidak ketemu"); return {}
        harga = int(m2.group(1).replace(",", ""))
        print(f"  OK Emas Antam 1gr: Rp{harga:,} ({tgl}, via scrape)")
        return {"Emas Antam 1gr": {"tanggal": tgl, "harga": harga,
                "harga_kemarin": None, "satuan": "gram", "sumber": "logammulia.com"}}
    except Exception as e:
        print(f"  X Emas: {str(e)[:100]}")
        return {}

def main():
    print("Ambil harga sembako (PIHPS BI)...")
    data = ambil_pihps()
    print("Ambil harga emas (Logam Mulia)...")
    data.update(ambil_emas())
    # harga_kemarin emas: ambil dari file kemarin
    today = datetime.now(WIB).date()
    out = {"tanggal": today.isoformat(), "diambil": datetime.now(WIB).isoformat(),
           "items": data}
    # isi harga_kemarin emas dari data kemarin bila ada
    for f in sorted(os.listdir(DATA), reverse=True):
        if f.startswith("harga-") and f < f"harga-{today.isoformat()}":
            try:
                lama = json.load(open(os.path.join(DATA, f)))
                for k, v in data.items():
                    lk = lama.get("items", {}).get(k)
                    if v.get("harga_kemarin") is None and lk:
                        v["harga_kemarin"] = lk.get("harga")
                break
            except Exception:
                pass
    path = os.path.join(DATA, f"harga-{today.isoformat()}.json")
    json.dump(out, open(path, "w"), indent=1, ensure_ascii=False)
    print(f"Tersimpan: {path} ({len(data)} item)")
    return 0 if data else 1

if __name__ == "__main__":
    sys.exit(main())
