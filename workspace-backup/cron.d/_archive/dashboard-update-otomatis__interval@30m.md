---
id: dashboard-update-otomatis
title: Update dashboard monitoring (30 mnt)
enabled: true
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-09T00:44:03
  every: 30m
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC6151CD91DD89E283BCFFA68B2880C6","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Update dashboard monitoring otomatis (silent).

Langkah:
1. Jalankan via shell: `bash ~/workspace/dashboard/update-dan-push.sh` (regenerate dashboard.html dari data live → commit → push ke GitHub Pages).
2. Jika script sukses (push OK / tidak ada perubahan): SELESAI, jangan kirim apa-apa ke chat.
3. Jika script GAGAL (error/push ditolak): laporkan ke chat ini dengan ringkas apa errornya + saran perbaikan.

Jangan edit file lain. Jangan push manual di luar script.
