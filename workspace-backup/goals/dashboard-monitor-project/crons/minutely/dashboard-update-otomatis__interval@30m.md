---
id: dashboard-update-otomatis
title: Update dashboard monitoring (30 mnt)
enabled: true
owner: goal:dashboard-monitor-project
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-09T00:44:03
  every: 30m
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Update dashboard monitoring otomatis (silent).

Langkah:
1. Jalankan via shell: `bash ~/workspace/dashboard/update-dan-push.sh` (regenerate dashboard.html dari data live → commit → push ke GitHub Pages).
2. Jika script sukses (push OK / tidak ada perubahan): SELESAI, jangan kirim apa-apa ke chat.
3. Jika script GAGAL (error/push ditolak): laporkan ke chat ini dengan ringkas apa errornya + saran perbaikan.

Jangan edit file lain. Jangan push manual di luar script.
