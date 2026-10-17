---
id: retry-promo-gagal-sore
title: Retry 7 postingan promo yang gagal (rate limit)
enabled: true
owner: goal:radar-cuan-affiliate-product-automation
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-10-04T19:11:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Kirim ulang 7 postingan promo afiliasi yang gagal tadi siang karena rate limit Instagram/Threads (HTTP 429).

Perintah: `cd ~/workspace/blog-otomatis && python3 -u retry_promo_pending.py`

Script ini hanya memposting ulang yang statusnya belum TERPOSTING di promo_out/posting_report_2026-10-04.json (anti-duplikat). Posting ke IG/Threads/FB butuh persetujuan user per aturan runtime — biarkan approval muncul, jangan di-bypass.

Laporan akhir (Bahasa Indonesia, singkat): berapa yang berhasil tayang dari 7 yang gagal, sebutkan produk + akunnya. Jika masih gagal karena rate limit, jelaskan dan sarankan coba lagi besok pagi.
