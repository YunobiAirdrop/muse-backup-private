---
id: refresh-mingguan
title: Refresh mingguan artikel evergreen
enabled: true
mode: task
schedule:
  kind: weekly
  timezone: Asia/Jakarta
  time: 18:00:00
  dow: [Sun]
timeout_secs: 7200
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC1016910464030373017072CE798CFB","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Refresh mingguan artikel evergreen (Minggu sore): perbarui 2 panduan TERLAMA per blog dengan info terkini bulan ini, lalu posting.

Langkah:
1. cd ~/workspace/blog-otomatis
2. Untuk tiap blog (kabarviral, cuanpintar, teknogebrakan, sehatbugar): ./venv/bin/python -u refresh.py --blog NAMABLOG
   (2 req AI per blog, total 8; tiap artikel bisa 2-10 menit — total bisa ~1 jam, jangan dibatalkan)
3. Untuk tiap blog: ./venv/bin/python -u posting.py --blog NAMABLOG
   (posting.py otomatis baca data/artikel-NAMABLOG.json yang baru dibuat refresh.py; jeda 300 detik antar posting sudah otomatis)

Catatan: refresh.py menulis file artikel fresh per blog; JANGAN jalankan bersamaan dengan cron pagi (jadwal ini Minggu 18:00, jauh dari jadwal pagi 07:11 — aman).

Laporan ke user (Bahasa Indonesia, singkat): per blog berapa artikel refresh berhasil terposting + judulnya.
