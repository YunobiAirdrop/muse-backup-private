---
id: tiktok-shop-review-harian
title: Video review TikTok Shop harian
enabled: false
owner: goal:radar-cuan-affiliate-product-automation
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 09:11:00
timeout_secs: 3600
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC56FDD92CF05C6775D8426060F9C7B4","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Buat 1 video review TikTok Shop Affiliate hari ini mengikuti SOP di ~/workspace/tiktok-shop-affiliate/SOP.md.

Langkah:
1. Baca ~/workspace/tiktok-shop-affiliate/produk.json dan history.json.
2. Pilih produk berikutnya sesuai aturan rotasi di SOP (belum pernah diposting; jika semua sudah 1x, mulai siklus baru varian+1).
3. Tulis naskah voiceover Indonesia ±30 detik mengikuti 4 beat tetap (hook → demo pemakaian → komentar terbaik → CTA keranjang kuning), dengan hook dan angle BERBEDA dari varian sebelumnya (rotasi formula hook di SOP).
4. Generate 3 klip video via media.generate_video (presenter wanita Indonesia natural memakai produk sesuai field `demo`).
5. Voiceover via tts skill (Bahasa Indonesia, suara perempuan natural).
6. Rakit via ~/workspace/youtube-otomatis/ffmpeg-queue.sh + film grain halus. Simpan ke output/review-{id}-{YYYYMMDD}-v{varian}.mp4.
7. Update history.json dengan produk + tanggal + varian hari ini.
8. Tulis caption sesuai SOP ke output/review-{id}-{YYYYMMDD}-v{varian}.txt.

Laporan akhir ke user (Bahasa Indonesia, singkat): lampirkan info produk (nama, komisi Rp, harga), dan instruksi: "Video siap — upload di aplikasi TikTok lalu tempel produk via keranjang kuning." Jika ini awal siklus baru (semua produk sudah diposting), tambahkan: "Semua produk sudah diposting 1x — kirim screenshot produk baru kalau mau ganti."

Batasan: JANGAN posting video ke TikTok (upload + tempel produk hanya bisa user di aplikasi). JANGAN klaim testimoni adalah review asli.
