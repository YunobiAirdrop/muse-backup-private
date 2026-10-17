# yt-growth — toolkit SEO & analitik YouTube gratis (buatan sendiri)

Pengganti gratis bagian inti `adityaarsharma/youtube-marketing-skills` tanpa
Node.js, tanpa MCP server, tanpa DataForSEO berbayar. Murni API resmi YouTube.

## Komponen

| File | Fungsi |
|---|---|
| `auth.py` | OAuth2 per channel (17 brand account). Token di `~/.hermes/yt-growth/tokens/` (600) |
| `analytics.py` | Laporan channel: views, likes, menit tonton, durasi tonton rata-rata, subs per video (YouTube Analytics API). **CTR/impresi TIDAK tersedia** — API menolak metrik impressions/CTR langsung, jadi deteksi underperform pakai views + retensi. |
| `yt_push.py` | Update judul/deskripsi/tag video. Default DRY-RUN; `--apply` butuh approval user |
| `channels.yaml` | 17 channel: handle + workspace (+ channel_id terisi otomatis) |
| `SETUP.md` | Langkah setup untuk user (Google Cloud + OAuth) |

## Alur kerja mingguan (cron `yt-seo-refresh-mingguan`, aktif — run perdana Senin 12 Okt 2026 09:00 WIB)
1. `analytics.py` per channel → temukan video umur >90 hari dengan views di
   bawah median channel (tanpa metrik CTR — tidak didukung API).
2. Worker (AI) menulis judul/deskripsi/tag baru memakai
   `~/workspace/youtube-otomatis/packaging-formulas.md` + proteksi keyword:
   keyword yang sudah ranking top 20 TIDAK boleh hilang dari metadata baru.
3. Proposal dilaporkan ke user; eksekusi via `yt_push.py --apply` hanya setelah
   user setuju (ketukan).

## Status token (per 2026-10-08, 17/17 aktif)
Semua channel terotorisasi via OAuth manual (HP user, batch 4x). Token di
`~/.hermes/yt-growth/tokens/` (600), refresh otomatis oleh `auth.py`.
`analytics.py mystery-en --days 28` teruji end-to-end 2026-10-08.

## Yang TIDAK dicoba (sadar keterbatasan)
- Data volume keyword berbayar (DataForSEO) → diganti trend-radar internal
  (autocomplete + RSS) yang sudah jalan tiap hari.
- Komentar/sentimen massal → balas komentar sudah ada cron-nya sendiri.
VENV=~/workspace/youtube-otomatis/yt-growth/.venv/bin/python
