---
id: scan-review-video
title: Scan video pending untuk APK review (30 mnt)
enabled: true
owner: goal:dashboard-monitor-project
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-19T21:46:23
  every: 30m
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":4,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC26806F832A333F88C5A0FC65B502DF","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Jalankan `python3 /home/hatch/workspace/yt-dashboard/scan_review.py` untuk memindai video private/scheduled terbaru di 20 channel dan menulis ke Firebase /yt/review.json (dipakai APK Review Video). Laporkan jumlah video pending. Diam jika sukses tanpa perubahan signifikan.
