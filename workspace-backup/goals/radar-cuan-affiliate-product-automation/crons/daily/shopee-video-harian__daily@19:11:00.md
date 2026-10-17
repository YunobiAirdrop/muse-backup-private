---
id: shopee-video-harian
title: Upload Shopee Video harian
enabled: false
owner: goal:radar-cuan-affiliate-product-automation
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 19:11:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"ACA8EEEE76AF53932CE8DFBF6E151C5F","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Siapkan paket 5 video afiliasi harian untuk upload MANUAL via aplikasi Shopee (akun stokakunwebyunobi@gmail.com).

KONTEKS PENTING: upload via browser/Seller Center TERBUKTI jalan buntu 2x (QR mengarah ke alur pendaftaran seller, salah untuk akun afiliasi). JANGAN coba upload via browser. Jalur resmi yang terbukti jalan: user upload sendiri dari aplikasi Shopee (tab Video → tombol +). Tugas cron ini HANYA menyiapkan paket siap-upload.

Langkah:
1. Baca ~/workspace/blog-otomatis/promo_out/manifest-YYYY-MM-DD.json untuk hari ini (mis. manifest-2026-10-06.json). Kalau file belum ada → video hari ini belum dibuat → laporkan singkat "paket video hari ini belum tersedia (promo-afiliasi-harian belum selesai)" dan SELESAI. Ini bukan error; jangan coba lagi.
2. Untuk tiap dari 5 produk di manifest: ambil video final-wa.mp4 (~/workspace/blog-otomatis/promo_out/YYYY-MM-DD/<slug>/final-wa.mp4), caption (review singkat + harga + ajakan checkout, Bahasa Indonesia), link afiliasi, dan hashtag dari manifest.
3. Kirim ke chat ini sebagai paket siap-upload: 5 video sebagai lampiran + daftar per produk (nama, harga, caption siap-copy, link afiliasi). Tambahkan instruksi singkat: buka aplikasi Shopee → tab Video → + → upload satu per satu dengan jeda 30-45 menit antar video.
4. JANGAN buka browser, JANGAN coba Seller Center, JANGAN minta approval upload.
5. Laporkan: 5 produk + status paket (terkirim ke chat / belum tersedia).
