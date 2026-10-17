# Loker Otomatis — info lowongan kerja harian

Pipeline harian: agregasi RSS → tulis artikel (OpenRouter gratis) → posting via web UI Blogger.

## Status
**MENUNGGU blog_id** — blog Blogger untuk loker BELUM dibuat. Setelah parent agent
membuat blog via browser, isi di `config.json`:
- `blogs[0].blog_id` (wajib)
- `blogs[0].url` (mis. https://lokerharian-xxx.blogspot.com)
- `blogs[0].blogger_email` (alamat Mail-to-Blogger, opsional)

## Cara jalan manual
```bash
cd ~/workspace/loker-otomatis
./jalan.sh          # agregasi -> tulis -> siapkan posting_web
# lalu agen baca data/webpost/loker.json dan spawn browser task
# (instruksi lengkap: data/webpost/instruksi-loker.txt)
```

## File
- `config.json` — blog (blog_id kosong) + 3 sumber RSS Google News (teruji OK)
- `agregasi_loker.py` — ambil RSS, filter loker, anti-duplikat (data/loker_riwayat.json)
- `tulis_loker.py` — prompt khusus loker + anti-halusinasi (dilarang mengarang
  deadline/link/gaji; tahun salah otomatis dikoreksi ke 2026)
- `posting_web.py` — rakit HTML (JSON-LD + FAQ + baca juga) → data/webpost/
- `jalan.sh` — orkestrasi 3 tahap

## Sumber teruji (2026-10-03)
1. Google News RSS "lowongan kerja" → 100 item OK
2. Google News RSS "rekrutmen BUMN 2026" → 100 item OK
3. Google News RSS "loker terbaru jakarta surabaya medan" → 75 item OK
Gagal/ditolak: Indeed id (403), Glints (firewall), Karir.com (404), loker.id (403 Cloudflare), JobStreet RSS (404).

## Catatan
- Gambar artikel: picsum seed per judul (placeholder). Bisa diganti foto asli bila ada.
- 8-10 artikel/hari (maks_artikel_per_hari di config).
- Cron `loker-harian` daily 08:11 Asia/Jakarta — aktif, menunggu blog_id.
