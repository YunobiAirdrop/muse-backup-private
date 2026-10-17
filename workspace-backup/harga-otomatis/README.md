# Info Harga Harian Otomatis

Posting harian harga sembako + emas Antam ke IG & Threads. Semua gratis.

## Cara kerja
`jalan.sh` → `ambil_harga.py` → `buat_infografis.py` → `posting_harga.py`

## File
| File | Fungsi |
|---|---|
| `ambil_harga.py` | Ambil 9 harga sembako (BI PIHPS API) + emas Antam 1gr (API publik logam-mulia-api) → `data/harga-YYYY-MM-DD.json` |
| `buat_infografis.py` | Generate `img/harga-YYYY-MM-DD.png` (1080x1080, PIL) + indikator ▲▼ vs kemarin |
| `posting_harga.py` | Posting ke IG @falcon_esport537 & Threads @beritaviraldotcom (`--dry-run` tersedia) |
| `jalan.sh` | Pipeline penuh + log ke `data/jalan-YYYY-MM-DD.log` |

## Sumber data (tertest 2026-10-04)
- **Sembako**: `https://www.bi.go.id/hargapangan/WebSite/Home/GetDetailGridData2` (API publik, tanpa key). 9 komoditas: beras medium, telur ayam, cabai merah keriting, bawang merah, bawang putih, minyak goreng curah, gula pasir, daging ayam, daging sapi. Level nasional ("Semua Provinsi").
- **Emas**: `https://logam-mulia-api.iamutaki.workers.dev/api/prices/logammulia` (API publik gratis). Fallback scrape `logammulia.com` (sering 403 dari datacenter — jangan andalkan).

## Cron
`harga-harian` — daily 07:11 WIB (Asia/Jakarta), owner goal:kabarviral-automated-news-blog.
Posting butuh approval user (aturan runtime) — worker lapor "menunggu persetujuan", jangan bypass.

## Catatan
- PIHPS update tiap hari termasuk weekend; jam update tidak pasti — data yang tampil = data terbaru yang tersedia di API (tanggal data tertera di JSON).
- Harga kemarin untuk indikator ▲▼ diambil dari 5 hari data API (sembako) / file kemarin (emas).
