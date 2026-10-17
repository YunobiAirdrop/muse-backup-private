---
id: hapus-video-terupload-harian
title: Hapus video lokal yang sudah terupload (harian)
enabled: true
owner: goal:toolkit-pertumbuhan-youtube-yt-growth
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 22:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Jalankan skrip hapus video terupload: `python3 /home/hatch/workspace/youtube-otomatis/hapus-video-terupload.py --execute`.

Kebijakan user (2026-10-15): video yang SUDAH terupload ke YouTube langsung dihapus dari lokal agar disk tidak penuh; YouTube menjadi arsip. Skrip hanya menghapus file yang terbukti terupload (ada upload-*.json berisi video_id, atau retry-queue/done/*.json) dan OTOMATIS melindungi video yang masih antre di retry-queue/*.json (bank aktif) serta shorts_bank.

Jika sukses: DIAM, jangan laporkan apa pun ke chat. Jika gagal/error: laporkan ringkas errornya ke chat.
