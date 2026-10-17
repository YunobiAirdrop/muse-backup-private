---
id: share-3x-upload-harian
title: Share 3x video baru harian (semua channel)
enabled: true
owner: goal:toolkit-pertumbuhan-youtube-yt-growth
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 21:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
SHARE-3X SETIAP VIDEO BARU (otorisasi user 2026-10-15: "setiap upload video kamu share 3x" — berlaku untuk semua channel).

TOOLKIT: ~/workspace/youtube-otomatis/yt-growth/ (python: ./venv/bin/python dari folder itu).
LOG SHARE: ~/workspace/youtube-otomatis/yt-growth/hidden_files/share3x-log.json (format: {"upload_shared": [videoId...], "quiet_shared": {"videoId": "YYYY-MM-DD"}}).

LANGKAH:
1. Cari semua video yang dipublikasikan dalam 24 jam terakhir di 19 channel (via API yt-growth: untuk tiap channel slug, ambil uploads playlist → playlistItems dengan publishedAfter 24 jam lalu). Hanya yang privacyStatus PUBLIC.
2. Lewati videoId yang sudah ada di upload_shared pada log.
3. SHARE-3X via browser task: untuk tiap URL video (https://www.youtube.com/watch?v=VIDEOID atau https://www.youtube.com/shorts/VIDEOID), buka halaman → klik tombol Share → klik Copy (salin link) → ulangi total 3x per video. Batch ±10 video per browser task. Tidak perlu login; jika tombol Share tidak ada lewati saja.
4. Tambahkan videoId yang berhasil di-share ke upload_shared di log (buat file log bila belum ada).
5. LAPORKAN ke user SINGKAT: berapa video baru di-share 3x (sebut channel-nya bila ≤5 video, bila lebih cukup total + per channel).
6. Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.
