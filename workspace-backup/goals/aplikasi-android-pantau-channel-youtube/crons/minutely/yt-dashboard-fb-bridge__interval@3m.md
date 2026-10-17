---
id: yt-dashboard-fb-bridge
title: YT Dashboard Firebase bridge (tiap 3 menit)
enabled: true
owner: goal:aplikasi-android-pantau-channel-youtube
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-15T13:18:12
  every: 3m
timeout_secs: 300
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Jalankan skrip jembatan YT Dashboard -> Firebase: `/home/hatch/workspace/yt-dashboard/venv/bin/python /home/hatch/workspace/yt-dashboard/fb_bridge.py`. Skrip ini sinkronisasi data YouTube (channel, antrean review, revenue) ke Firebase Realtime Database dan mengeksekusi perintah publish dari aplikasi HP. Tunggu sampai selesai (bisa ~2 menit saat sync penuh). Jika sukses: DIAM, jangan laporkan apa pun ke chat. Jika gagal/error: laporkan ringkas errornya ke chat.
