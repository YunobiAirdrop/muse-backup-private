---
id: tiktok-affiliate-harian
title: TikTok affiliate harian @ngeweb.yuk
enabled: false
owner: goal:radar-cuan-affiliate-product-automation
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 10:11:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC78E347FF52E8DB6E75C64CD2BEB719","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
# TikTok affiliate harian — @ngeweb.yuk via Taisly

1. Jalankan: `python3 ~/workspace/blog-otomatis/tiktok_affiliate.py 3`
   - Script memilih 3 produk (prioritas komisi terbesar: buku 81.5%, skincare 80%, vitamin 77%, lalu rotasi anti-ulang via tiktok_history.json), pakai video 9:16 yang sudah ada (final-wa.mp4) atau generate Ken Burns fallback, posting via `taisly posts:create` ke TikTok @ngeweb.yuk.
2. Cek hasil di `~/workspace/blog-otomatis/hasil-tiktok-YYYY-MM-DD.json`. Untuk tiap historyId, boleh cek `taisly posts:status --id <historyId>` untuk memastikan status posted.
3. Jika ada yang gagal: catat di laporan, jangan retry spam (maks 1x retry per video).
4. JANGAN edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md.

LAPORAN (Bahasa Indonesia, singkat, ke chat ini): daftar 3 produk yang diposting + status (ok/gagal) + 1 baris catatan bila ada kendala. Tidak perlu detail panjang.
