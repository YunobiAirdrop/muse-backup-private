---
id: pra-screen-duplikat-retry
title: Pra-screen anti-duplikat antrean retry
enabled: true
owner: goal:retry-otomatis-upload-youtube
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-14T11:04:03
  every: 1h
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
**PRA-SCREEN ANTI-DUPLIKAT RETRY (disetujui user 2026-10-14).** Latar: cron watchdog-retry-upload-youtube dan retry-upload-cepat dimiliki chat WhatsApp sehingga bodinya tidak bisa diubah dari sini — pra-screen ini adalah implementasi pengamannya dari main chat.

Tiap run:
1. List ~/workspace/youtube-otomatis/retry-queue/*.json (abaikan folder done/ dan claimed/). Jika kosong → selesai diam-diam.
2. Untuk tiap JSON: baca channel + instruksi_path. Jalankan `cd ~/workspace/youtube-otomatis/yt-growth && ./venv/bin/python cek_duplikat.py {channel} --instruksi {instruksi_path}`.
3. Jika hasil `duplikat: true` → pindahkan JSON ke retry-queue/done/ (jangan hapus). Catat judul + video_id live.
4. Jika `duplikat: false` → biarkan di antrean. Jika script error → biarkan di antrean, catat errornya.
5. Jika ada yang dipindah ke done/ → laporkan singkat ke chat (judul + "sudah live, duplikat dicegah"). Jika tidak ada → diam.

Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.
