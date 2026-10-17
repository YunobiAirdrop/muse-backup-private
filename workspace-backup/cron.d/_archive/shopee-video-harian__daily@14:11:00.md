---
id: shopee-video-harian
title: Upload Shopee Video harian
enabled: true
owner: goal:radar-cuan-affiliate-product-automation
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 14:11:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC3A218C280D68054D883D59B5C75F4A","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Upload 5 video afiliasi harian ke Shopee Video (akun stokakunwebyunobi@gmail.com).

Video sudah dibuat oleh cron promo-afiliasi-harian (jam 12:11) di ~/workspace/blog-otomatis/promo_out/YYYY-MM-DD/*/final-wa.mp4 (5 video, 20 detik, vertikal 9:16, voiceover Indonesia).

Langkah:
1. Baca ~/workspace/blog-otomatis/promo_out/manifest-YYYY-MM-DD.json untuk daftar 5 produk hari ini (nama, harga, link afiliasi)
2. Untuk tiap produk (JEDA 30-45 MENIT antar upload agar terlihat natural, jangan sekaligus):
   a. Via browser (login Shopee stokakunwebyunobi@gmail.com, sesi sudah ada): buka Shopee Video → Upload
   b. Upload final-wa.mp4 produk tersebut
   c. Isi caption: review singkat + harga + ajakan checkout (Bahasa Indonesia)
   d. Tambahkan link afiliasi produk (fitur tag produk/keranjang kuning Shopee Video)
   e. Posting sebagai publik
3. CATATAN: upload memicu approval user (aturan runtime) — tertunda = "menunggu persetujuan"
4. Laporkan: 5 produk + status upload per video

PENTING: Jeda antar upload WAJIB 30-45 menit (gunakan jeda acak dalam rentang itu). Jangan upload 5 sekaligus — pola itu yang memicu deteksi spam Shopee. Konten 100% orisinal (video buatan sendiri), bukan reupload.
