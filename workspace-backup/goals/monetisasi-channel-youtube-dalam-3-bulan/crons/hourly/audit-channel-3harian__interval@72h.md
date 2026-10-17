---
id: audit-channel-3harian
title: Audit channel 3-harian + koreksi
enabled: true
owner: goal:monetisasi-channel-youtube-dalam-3-bulan
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-13T22:51:08
  every: 72h
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
**AUDIT CHANNEL 3-HARIAN (pengecekan rutin + koreksi).** Tiap run:

1. Untuk tiap channel di `~/workspace/youtube-otomatis/yt-growth/channels.yaml`: jalankan `python3 ~/workspace/youtube-otomatis/yt-growth/analytics.py <slug> --days 28` → kumpulkan: subscriber, views 28 hari, watch hours, CTR rata-rata, 3 video top, 3 video flop (CTR <2% atau retensi <40%).
2. Diagnosa tiap channel dengan 3 gerbang (seen → clicked → watched) + progres ke ambang monetisasi (500 subs / 3.000 jam tayang / 3M Shorts views 90 hari).
3. **Koreksi otomatis yang aman** via `yt_push.py` (dry-run dulu): re-title video flop ikut formula packaging, update deskripsi + hashtag, masukkan video tanpa playlist ke playlist yang sesuai.
4. Koreksi yang butuh browser (ganti thumbnail, Test & Compare, perbaiki 15 detik pertama via Studio Editor): tulis daftarnya ke `~/workspace/goals/monetisasi-channel-youtube-dalam-3-bulan/hidden_files/audit-YYYY-MM-DD.md`.
5. Update papan skor: `~/workspace/goals/monetisasi-channel-youtube-dalam-3-bulan/hidden_files/scoreboard.md` — subs, watch hours, % ke ambang per channel.
6. Lapor singkat ke chat: 3 channel paling naik, 3 channel paling perlu perhatian, koreksi yang diterapkan, dan 1 rekomendasi double-down berikutnya.

Aturan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.
