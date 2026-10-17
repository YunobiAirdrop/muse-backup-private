---
id: share-youtube-threads
title: Cross-promo YouTube ke Threads
enabled: false
owner: goal:toolkit-pertumbuhan-youtube-yt-growth
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 18:11:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"ACA8EEEE76AF53932CE8DFBF6E151C5F","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
**CROSS-PROMO YOUTUBE → THREADS (taktik growth riset 2026: kreator naik 2000 subs/30 hari dengan mempublikasikan tiap video ke Threads).**

Tiap run:
1. Untuk tiap channel YouTube (18 channel, via `~/workspace/youtube-otomatis/yt-growth/.venv/bin/python ~/workspace/youtube-otomatis/yt-growth/analytics.py SLUG --days 3`): ambil video yang dipublikasikan dalam 48 jam terakhir (ID, judul, URL, channel).
2. Baca `~/workspace/youtube-otomatis/threads-shared.json` (buat [] jika belum ada) — lewati video ID yang sudah ada.
3. Untuk tiap video BARU (maks 10 per run): posting ke Threads akun @beritaviraldotcom via threads-cli publish-post. Format teks (maks 450 karakter): 1 kalimat hook dari judul + URL YouTube + 2-3 hashtag niche (contoh: `#mystery #unsolved #shorts` untuk Shorts). Bahasa = bahasa video (ID/EN).
4. Update threads-shared.json dengan video ID yang sudah diposting.
5. Posting Threads butuh persetujuan user (aturan runtime) — biarkan approval card muncul, JANGAN bypass. Laporkan: berapa video baru ditemukan, berapa yang antre persetujuan.
6. Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.
