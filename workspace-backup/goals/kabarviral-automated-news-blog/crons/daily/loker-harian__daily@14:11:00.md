---
id: loker-harian
title: Info loker harian
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 14:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Info loker harian otomatis: agregasi → tulis artikel → posting ke blog loker via web UI.

Langkah tiap run:
1. cd ~/workspace/loker-otomatis && ./jalan.sh
   - agregasi_loker.py: ambil RSS Google News (lowongan kerja, rekrutmen BUMN 2026, loker kota besar) → filter hoaks/penipuan → anti-duplikat via data/loker_riwayat.json → data/antrean-loker.json
   - tulis_loker.py: tulis artikel per loker (posisi, perusahaan, kualifikasi, cara melamar, deadline). ATURAN ANTI-HALUSINASI: dilarang mengarang deadline/link/gaji; info yang tidak ada ditulis "cek situs resmi"
   - posting_web.py: rakit HTML (JSON-LD NewsArticle + FAQ + baca-juga) → data/webpost/loker.json + instruksi-loker.txt, lalu spawn browser task yang posting via blogger.com web UI (login khususstokyunobi@gmail.com)
2. CATATAN: blog_id blog loker tersimpan di config.json (blogs[0].blog_id). Jika masih kosong, run hanya sampai tahap tulis artikel; posting menunggu blog dibuat.
3. Maks 10 artikel/hari.

Laporan ke user (Bahasa Indonesia): jumlah loker diagregasi + daftar judul artikel + status posting (berhasil/menunggu persetujuan).
