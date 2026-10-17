---
id: yt-seo-refresh-mingguan
title: Refresh SEO mingguan YouTube (17 channel)
enabled: true
owner: goal:toolkit-pertumbuhan-youtube-yt-growth
mode: task
schedule:
  kind: weekly
  timezone: Asia/Jakarta
  time: 09:11:00
  dow: [Mon]
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
YT-SEO REFRESH MINGGUAN (toolkit yt-growth gratis — analitik asli + refresh metadata).

TUJUAN: menaikkan performa video lama yang underperform via refresh judul/deskripsi/tag berbasis data, bukan tebakan. PLUS: review retensi mingguan (kurva asli per video) + pola kompetitor untuk memandu produksi.

SEMUA perintah memakai: ~/workspace/youtube-otomatis/yt-growth/venv/bin/python ~/workspace/youtube-otomatis/yt-growth/<skrip>

LANGKAH:
1. Cek token: `auth.py status`. Jika 0 token → laporkan "setup OAuth yt-growth belum selesai" dan BERHENTI.
2. Untuk tiap channel yang punya token: `analytics.py SLUG --days 28` → simpan JSON ke `~/workspace/youtube-otomatis/yt-growth/hidden_files/analytics-YYYY-MM-DD/{slug}.json` (buat foldernya).
3. Dari data: temukan video underperform (umur >14 hari, views + rata-rata durasi tonton di bawah median channel-nya). CATATAN: CTR/impresi TIDAK tersedia di API YouTube — jangan mengklaim angka CTR; sinyal resmi = views + retensi + durasi tonton.
4. Untuk tiap kandidat (maks 5/channel): tulis proposal metadata baru memakai `~/workspace/youtube-otomatis/packaging-formulas.md` (pilih 1 formula judul, buat 3-5 varian, pakai terkuat; 150 karakter pertama deskripsi = hook + keyword utama). PROTEKSI: jangan hapus keyword/frasa yang sudah memberi traffic; judul tetap jujur (janjinya ditepati 30 detik pertama video). Validasi tiap proposal dengan `seo_audit.py file <metadata.json>` — proposal yang FAIL tidak boleh diajukan.
5. Tulis proposal ke `~/workspace/youtube-otomatis/yt-growth/proposals/proposal-YYYY-MM-DD.md` (per channel: video ID + URL, judul lama → judul baru + alasan). Untuk 1 kandidat terkuat per channel, daftarkan juga sebagai A/B test mode PROPOSAL: `ab_test.py propose SLUG VIDEO_ID --title "Judul B"` (judul B WAJIB tetap mengikuti aturan hashtag channel: shorts ditutup #foryou). JANGAN jalankan start --apply tanpa persetujuan user.
6. REVIEW RETENSI (kurva asli): untuk 3 video teratas + 3 terbawah per channel (dari langkah 2), jalankan `retention.py SLUG VIDEO_ID` → catat retensi 25/50/75/akhir + 3 titik jatuh terbesar (dalam detik). Pola menang vs pola kalah per channel ditulis ke review-retensi-YYYY-MM-DD.md + rekomendasi konkret 1-2 kalimat per channel untuk produksi minggu ini. Bila Analytics timeout/kosong untuk sebuah video, catat apa adanya — jangan mengarang.
7. SCAN KOMPETITOR: jalankan `competitor_scan.py` (output otomatis ke ~/workspace/blog-otomatis/data/competitor-YYYY-MM-DD.md). Kutip 2-3 pola judul/kadens yang relevan per niche ke laporan (bahan packaging minggu ini).
8. STATUS A/B TEST: jalankan `ab_test.py status` → sertakan test yang sedang jalan + perbandingan metriknya di laporan.
9. LAPORKAN ke user (SINGKAT): ringkasan per channel + proposal + temuan retensi + pola kompetitor. Minta persetujuan.
10. HANYA setelah user setuju (ketukan/pesan eksplisit), eksekusi: metadata via `yt_push.py SLUG --video ID --title "..." --description "..." --tags "a,b,c" --apply` dan/atau A/B test via `ab_test.py start SLUG VIDEO_ID --apply`. Tanpa persetujuan: JANGAN push/jalankan apa pun.
11. Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.
