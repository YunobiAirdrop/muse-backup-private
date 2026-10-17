---
id: tiktok-fyp-harian
title: Konten hiburan TikTok harian (kejar followers)
enabled: false
owner: goal:radar-cuan-affiliate-product-automation
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 19:11:00
timeout_secs: 3600
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC37001886C6E2FF85716F7C5A520332","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Buat dan posting 1 video hiburan TikTok hari ini untuk akun @ngeweb.yuk (mode kejar 600 followers), mengikuti ~/workspace/tiktok-shop-affiliate/fyp-content.md.

Langkah:
1. Baca fyp-content.md dan fyp-history.json. Pilih 1 format (jangan sama dengan kemarin; untuk drama bersambung lanjutkan nomor episode).
2. Tulis naskah Indonesia 25-35 detik dengan hook kuat di 3 detik pertama (rotasi trigger viral-hooks).
3. Generate 3 klip via media.generate_video (aktor AI Indonesia natural, vertical, sesuai adegan).
4. Voiceover via tts skill (Bahasa Indonesia natural).
5. Rakit via ~/workspace/youtube-otomatis/ffmpeg-queue.sh + film grain halus → output/fyp-{format}-{YYYYMMDD}.mp4.
6. Tulis caption sesuai panduan → file .txt.
7. Posting via `taisly posts:create --video <file> --platforms 6ac71c80572b2159e0a2f190 --description "<caption>"`. Verifikasi via `taisly posts:status --id <historyId>`.
8. Update fyp-history.json.

Laporan akhir ke user (Bahasa Indonesia, singkat): judul + format + status posting (ok/gagal). Akhiri SELALU dengan: "Followers sekarang berapa? Kabari saya kalau sudah 600 biar langsung mulai mode review produk."

Batasan: JANGAN menyebut/mempromosikan produk afiliasi di konten ini (mode hiburan murni). JANGAN retry posts:create buta setelah timeout — cek History dulu.
