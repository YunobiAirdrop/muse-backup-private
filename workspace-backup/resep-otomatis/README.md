# Resep Otomatis — akun resep masakan harian

Pipeline mandiri (terpisah dari blog-otomatis):
1. `bikin_resep.py` — generate 3 resep orisinal/hari via OpenRouter (model gratis,
   rotasi key & model mengikuti `tulis_ulang.py`). Output: `data/resep-YYYY-MM-DD.json`.
   Anti-ulang 60 hari via `riwayat-resep.json`, pool 85 resep di `pool-resep.json`.
2. Gambar: 1 foto makanan per resep via `media.generate_image`
   (food photography profesional, appetizing, tanpa teks) → `gambar/`.
3. `posting_resep.py` — bikin caption (hook + bahan + CTA + hashtag + 1 link
   afiliasi peralatan dapur, rotasi 7 hari via `riwayat-afiliasi.json`) dan antrean IG.
   - Default `--dry-run`: tulis `data/antrean-ig-YYYY-MM-DD.json`, TIDAK posting.
   - `--post`: posting via `instagram-cli post-feed` — BUTUH APPROVAL USER (aturan runtime).

Cron `resep-harian`: daily 10:11 Asia/Jakarta.

## Struktur
```
resep-otomatis/
├── pool-resep.json        # 90 resep Indonesia (lauk/sop/mie/nasi/sayur/jajanan/minuman/sambal)
├── riwayat-resep.json     # {nama: tanggal} anti-ulang 60 hari
├── riwayat-afiliasi.json  # {idx_produk: tanggal} rotasi afiliasi 7 hari
├── bikin_resep.py
├── posting_resep.py
├── gambar/                # foto makanan per resep
├── data/                  # resep-*.json, antrean-ig-*.json
└── README.md
```
