---
id: upload-batch-api-14okt
title: Batch upload API antrean retry (pasca-reset kuota)
enabled: true
owner: goal:toolkit-pertumbuhan-youtube-yt-growth
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-10-13T14:05:00
timeout_secs: 3600
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":2,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"ACC6CE3FBAE18A5926E563D83BAED484","conversation_id":"whatsapp_channel","provider":"whatsapp","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Jalankan batch upload API untuk antrean retry YouTube SETELAH kuota harian reset (±14:00 WIB).

Perintah (jalankan via shell):
cd ~/workspace/youtube-otomatis/yt-growth && ./venv/bin/python hidden_files/batch_upload_2026-10-13.py

Konteks: skrip memproses /home/hatch/workspace/youtube-otomatis/retry-queue/*.json dari gagal_pada tertua, verifikasi channel ID, cek duplikat judul via API (skip bila sudah ada), upload via resumable API (public bila slot_target lewat, private+publishAt bila masih masa depan), berhenti otomatis saat 403 quotaExceeded, menulis hasil inkremental ke yt-growth/hidden_files/upload-batch-2026-10-13.json dan memindahkan JSON sukses ke done/.

Jika skrip gagal/error sebelum mulai (mis. file hilang), JANGAN membuat skrip baru — laporkan errornya. Jika kuota masih 403 saat dijalankan, laporkan "kuota belum reset" tanpa retry paksa.

Laporkan ke chat: jumlah video terupload + URL-nya, jumlah skip duplikat, alasan berhenti.
