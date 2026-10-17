---
id: trend-radar-youtube
title: Radar tren YouTube harian (10 niche)
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 13:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Jalankan radar tren YouTube harian: `cd ~/workspace/blog-otomatis && ./venv/bin/python trend_radar.py` (atau `python3 trend_radar.py`; durasi normal ~2 menit).

Radar membaca demand YouTube real-time (autocomplete suggestqueries.google.com, hl=id untuk 2 channel Indonesia dan hl=en untuk 8 channel Inggris) + judul video 7 hari terakhir dari channel top tiap niche via RSS publik, lalu menulis `data/trend-radar-YYYY-MM-DD.md` dan `data/trend-radar-YYYY-MM-DD.json` untuk 10 niche channel (horor_id, rakyat_id, truecrime_en, horror_en, mystery_en, history_en, space_en, darkpsych_en, weirdfacts_en, ancient_en).

Setelah jalan, verifikasi kedua file output hari ini ada dan JSON memuat 10 niche dengan top_terms tidak kosong. Jika sukses: diam saja, JANGAN kirim laporan ke chat (file adalah deliverable; cron produksi video/blog membaca JSON-nya). Jika gagal (error/timeout/output kosong): kirim pesan singkat ke chat berisi error-nya saja.
