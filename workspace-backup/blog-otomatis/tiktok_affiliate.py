#!/usr/bin/env python3
"""TikTok affiliate harian via Taisly — @ngeweb.yuk.
Pilih produk (prioritas komisi terbesar + rotasi anti-ulang),
pakai video 9:16 yang sudah ada (final-wa.mp4 / Ken Burns fallback),
posting via: taisly posts:create --platforms <tiktok-id>

Catatan: posting API TikTok tidak bisa menempelkan keranjang kuning
TikTok Shop — caption mengarahkan "Link di bio". Pastikan bio TikTok
berisi link hub (Lynk.id/dll) ke link afiliasi Shopee.
"""
import json, os, sys, time, subprocess, random
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from share_promo import PRODUK, MANFAAT, CAPTION_BUILDERS, OUT_DIR, bikin_video, bikin_promo, IMG_DIR

TIKTOK_ID = "6ac71c80572b2159e0a2f190"
HIST = os.path.join(BASE, "tiktok_history.json")

# Komisi Shopee yang diketahui (%, dari dashboard affiliate). Default 10%.
KOMISI = {
    "buku-medical.jpg": 81.5, "buku-kesling.jpg": 81.5,
    "skincare-jrg.jpg": 80, "skincare-paket.jpg": 80,
    "toneup.jpg": 80, "serum-hanasui.jpg": 80,
    "vitamin-kucing.jpg": 77, "vitamin-cerna.jpg": 77,
}

def komisi(p):
    return KOMISI.get(p[0], 10.0)

def pilih_produk(n=3):
    hist = {}
    if os.path.exists(HIST):
        try: hist = json.load(open(HIST))
        except Exception: pass
    def skor(i):
        last = hist.get(str(i), "2000-01-01")
        # makin lama tidak diposting + makin besar komisi = prioritas
        return (last, -komisi(PRODUK[i]))
    urutan = sorted(range(len(PRODUK)), key=skor)
    pilih = urutan[:n]
    hari = datetime.now(WIB).date().isoformat()
    for i in pilih: hist[str(i)] = hari
    json.dump(hist, open(HIST, "w"))
    return [PRODUK[i] for i in pilih]

def cari_video(p):
    """Cari video 9:16 yang sudah ada untuk produk ini."""
    fimg = p[0]
    slug = os.path.splitext(fimg)[0]
    # 1. final-wa.mp4 dari batch promo
    for root, _, files in os.walk(os.path.join(OUT_DIR)):
        if "final-wa.mp4" in files and slug in root:
            return os.path.join(root, "final-wa.mp4")
    return None

def bikin_video_baru(p):
    """Fallback: generate video Ken Burns dari gambar promo."""
    fimg, nama, harga, warna, _, _ = p
    src = os.path.join(IMG_DIR, fimg)
    if not os.path.exists(src):
        return None
    ts = int(time.time() * 1000) % 100000000
    img_out = os.path.join(OUT_DIR, f"tt_{ts}.jpg")
    vid_out = os.path.join(OUT_DIR, f"tt_{ts}.mp4")
    try:
        bikin_promo(src, nama, harga, img_out, warna=warna)
        bikin_video(img_out, vid_out)
        return vid_out if os.path.exists(vid_out) else None
    except Exception as e:
        print(f"  video gagal: {str(e)[:80]}")
        return None

def caption_tiktok(p):
    fimg, nama, harga, _, link, tags = p
    manfaat = MANFAAT.get(fimg, "praktis dipakai sehari-hari")
    hooks = [
        f"POV: nemu {nama} cuma {harga} 😱",
        f"Racun TikTok nih! {nama} {harga} aja 🔥",
        f"Jangan beli {nama} sebelum nonton ini! {harga} doang 💸",
        f"Yang lagi viral: {nama} cuma {harga} ✨",
    ]
    body = random.choice(hooks)
    tag_str = " ".join(f"#{t}" for t in tags[:4])
    desc = (f"{body}\n{manfaat}.\n🔗 Link pembelian di bio!\n\n"
            f"#racuntiktok #tiktokshop #affiliate {tag_str}")
    return desc[:2200]

def post_tiktok(video, desc):
    cmd = ["taisly", "posts:create", "--video", video,
           "--platforms", TIKTOK_ID, "--description", desc]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        out = (r.stdout or "")[:300]
        try:
            d = json.loads(r.stdout)
            ok = d.get("success", False)
            hid = d.get("historyId", d.get("data", {}).get("historyId", "?"))
            return ok, f"historyId={hid}"
        except Exception:
            return r.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)[:120]

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    dry = "--dry-run" in sys.argv
    hasil = {"tanggal": datetime.now(WIB).date().isoformat(), "posting": []}
    for p in pilih_produk(n):
        nama = p[1]
        vid = cari_video(p) or bikin_video_baru(p)
        desc = caption_tiktok(p)
        if not vid:
            hasil["posting"].append({"produk": nama, "status": "gagal", "info": "tidak ada video"})
            print(f"✗ {nama}: tidak ada video")
            continue
        if dry:
            print(f"[dry] {nama} ({komisi(p)}%) -> {vid}\n  {desc[:90]}...")
            hasil["posting"].append({"produk": nama, "status": "dry-run", "video": vid})
            continue
        ok, info = post_tiktok(vid, desc)
        print(f"{'✓' if ok else '✗'} {nama} ({komisi(p)}%): {info}")
        hasil["posting"].append({"produk": nama, "status": "ok" if ok else "gagal",
                                 "komisi": komisi(p), "info": info})
        time.sleep(5)
    out = os.path.join(BASE, f"hasil-tiktok-{hasil['tanggal']}.json")
    json.dump(hasil, open(out, "w"), ensure_ascii=False, indent=1)
    print("Hasil:", out)

if __name__ == "__main__":
    main()
