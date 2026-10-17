# Sisa modul dari riset GitHub — status & rancangan (dicek 12 Okt 2026, 16:24 WIB)

User (12 Okt 16:06 WIB): "nah yang belum punya itu pasang ke sistem kita" —
mengacu pada daftar "yang belum punya" dari bedah repo GitHub di chat hari yang sama.

## SUDAH TERPASANG & TERVERIFIKASI (12 Okt 16:08–16:09 WIB)

| Modul | File | Verifikasi |
|---|---|---|
| Audit SEO sebelum publish | `yt-growth/seo_audit.py` | `py_compile` OK; uji file-mode pada metadata Shorts contoh: skor 90/100, aturan #foryou terakhir + maks 4 hashtag judul bekerja, exit 0 |
| Analisis retensi per adegan | `yt-growth/retention.py` | `py_compile` OK. Jujur data: header skrip sendiri mencatat endpoint Analytics pernah timeout total 12 Okt; hasil kosong harus dilaporkan apa adanya, bukan dikarang |

## BELUM ADA (grep 16:24 WIB — tidak ditemukan di yt-growth/ maupun trend_radar.py)

### 1. Loop A/B testing judul & thumbnail
- Ditawarkan di chat (AgentTube): putar 2 varian, ukur, kunci yang menang.
- Kendala nyata dari README yt-growth: **CTR/impresi TIDAK tersedia via YouTube Analytics API** — jadi metrik A/B tidak bisa CTR asli. Pakai proksi: kecepatan views 48 jam pertama + retensi rata-rata (dari analytics.py/retention.py), dinyatakan terus-terang sebagai proksi di laporan.
- Kendala izin: `yt_push.py --apply` butuh persetujuan user per perubahan metadata. Desain: 1 eksperimen = 1 video, varian B diajukan sebagai proposal (bukan auto-apply), hasil dibaca sesudah jendela ukur, keputusan kunci/pulihkan juga via proposal. Jangan buat loop yang mengganti judul diam-diam.
- Penyimpanan: `yt-growth/ab_tests.json` — {video_id, slug, varian_A (judul+thumb saat ini), varian_B, mulai, jendela_jam, metrik_A_awal, hasil, status}.

### 2. Analisis pola kompetitor + pelacak video breakout
- Ditawarkan di chat dari open-ai-youtube-agent (pola kompetitor + keyword ala VidIQ) dan ops growth pipeline (breakout tracker); dijanjikan ditempel ke trend radar.
- `blog-otomatis/trend_radar.py` saat ini: belum ada kode competitor/breakout (grep "kompetitor|competitor|breakout" = 0 hasil).
- Desain: perlu daftar channel kompetitor per niche (belum ada di channels.yaml — itu daftar channel sendiri). Sumber aman: Data API publik via yt-growth auth yang sudah ada; breakout = video kompetitor umur <7 hari dengan views >5x median channel-nya. Output menempel ke `data/trend-radar-YYYY-MM-DD.md` yang sudah dibaca produksi harian, bukan file baru yang yatim.
- Langkah pertama yang belum ada datanya: daftar kompetitor per 10 niche — bisa diturunkan dari hasil trend radar yang sudah jalan (video non-channel-sendiri yang berulang muncul), tanpa input user.

## Yang TIDAK dipasang (keputusan sudah final di chat, jangan ditawarkan lagi)
Bot jam tayang/views (waliarubal/YoutubeTools, Setiawan007/YouTubeBot, aragle/youtube-booster) dan tool sejenis dari screenshot user — ditolak karena fake engagement, risiko hapus channel + akun Google yang menaungi 19 channel.
