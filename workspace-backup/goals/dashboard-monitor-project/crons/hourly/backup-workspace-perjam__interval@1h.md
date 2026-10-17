---
id: backup-workspace-perjam
title: Backup workspace per jam (anti VM reset)
enabled: true
owner: goal:dashboard-monitor-project
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-17T17:14:41
  every: 1h
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Backup workspace per jam ke repo GitHub private (anti VM reset).

Jalankan: bash ~/workspace/muse-backup-private/hourly-backup.sh

Skrip ini:
- Sinkron ~/workspace/ ke folder workspace-backup/ di repo private YunobiAirdrop/muse-backup-private
- SKIP otomatis: file secret (.env, *token*, *secret*, *.pem, *.key), file video/audio/gambar besar, node_modules, __pycache__
- Hanya commit+push kalau ada perubahan (tidak ada perubahan = diam, tidak spam)
- Auth pakai token dari ~/.hermes/github-dashboard-token

JANGAN laporkan ke user tiap jam — cukup tulis ke log:
~/workspace/goals/dashboard-monitor-project/hidden_files/backup-perjam.log

Laporkan ke user HANYA kalau: push gagal 3x berturut-turut, atau token github tidak valid/hilang.
