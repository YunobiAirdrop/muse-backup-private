---
id: share-ig-harian
title: Auto-share IG harian
enabled: false
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 20:11:00
timeout_secs: 3600
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC660C34E5D9889E4C65D2272BEE7805","conversation_id":"whatsapp_channel","provider":"whatsapp","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Jalankan paket konten sore harian untuk 4 blog (meme + video berita + thread + paket WA):

1. cd ~/workspace/blog-otomatis
2. ./venv/bin/python -u share_ig.py — 3 artikel terbaik → video berita 9:16 (reel) + caption viral AI → posting ke IG @falcon_esport537 (FULL OTOMATIS, maks 3/hari)
3. ./venv/bin/python -u video_script.py — 3 script video TikTok/Reels → data/video-script-HARI-INI.md
4. ./venv/bin/python -u thread_gen.py — 3 thread X/Threads → data/thread-HARI-INI.md
5. ./venv/bin/python -u share_fb.py — 3 artikel terbaik → video berita + caption + link → posting ke Facebook Page BeritaViraldotcom
6. ./venv/bin/python -u share_threads.py — 3 artikel terbaik → video berita + postingan ringkas → posting ke Threads @beritaviraldotcom
7. ./venv/bin/python -u wa_broadcast.py — paket broadcast WhatsApp Channel: 3 meme + teks siap-forward → data/wa-broadcast-HARI-INI/

PENTING:
- Langkah 5 (FB) dan 6 (Threads) WAJIB butuh approval/persetujuan user per posting (aturan keamanan facebook-cli & threads-cli). Saat approval card muncul, tulis di laporan bahwa menunggu persetujuan user; JANGAN lewati/bypass. Kalau user tidak menyetujui, catat sebagai "menunggu persetujuan" bukan gagal.
- Jangan posting lebih dari 3 per platform per hari (batas anti-spam).
- Jika tidak ada artikel hari ini, laporkan saja tanpa posting.
- Langkah 7 (WA): TIDAK ADA API resmi WhatsApp untuk auto-posting ke Channel — paketnya disiapkan otomatis, user forward manual ke Channel-nya (2x tap).

Laporan ke user (Bahasa Indonesia): hasil per platform (IG/FB/Threads: berapa berhasil/gagal/menunggu persetujuan + judulnya), lalu TAMPILKAN ISI LENGKAP file video-script-HARI-INI.md dan thread-HARI-INI.md supaya user bisa langsung rekam video & simpan threadnya. Terakhir: bagian "PAKET BROADCAST WA" — tampilkan isi data/wa-broadcast-HARI-INI/broadcast.txt (teks siap-forward per item) dan sebutkan file gambarnya (data/wa-broadcast-HARI-INI/wa_1.jpg dst) supaya user bisa forward ke WhatsApp Channel.
