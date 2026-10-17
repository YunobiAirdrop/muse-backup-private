---
id: yt-dashboard-fb-bridge
title: YT Dashboard Firebase bridge (tiap 5 menit)
enabled: true
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-15T11:29:57
  every: 5m
timeout_secs: 300
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":2,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC0C42989058FD78D48D75888C568852","conversation_id":"whatsapp_channel","provider":"whatsapp","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Jalankan skrip jembatan YT Dashboard -> Firebase: `/home/hatch/workspace/yt-dashboard/venv/bin/python /home/hatch/workspace/yt-dashboard/fb_bridge.py`. Skrip ini sinkronisasi data YouTube (channel, antrean review, revenue) ke Firebase Realtime Database dan mengeksekusi perintah publish dari aplikasi HP. Tunggu sampai selesai (bisa ~2 menit saat sync penuh). Jika sukses: DIAM, jangan laporkan apa pun ke chat. Jika gagal/error: laporkan ringkas errornya ke chat.
