---
id: harga-harian
title: Info harga harian (sembako + emas)
enabled: false
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 15:11:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"ACA8EEEE76AF53932CE8DFBF6E151C5F","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Info harga harian otomatis (sembako + emas Antam).

Langkah tiap run:
1. cd ~/workspace/harga-otomatis && ./jalan.sh
   - ambil_harga.py: harga sembako nasional dari BI PIHPS API (https://www.bi.go.id/hargapangan/WebSite/Home/GetDetailGridData2) + emas Antam 1gr dari API publik logam-mulia-api.iamutaki.workers.dev (fallback: scrape logammulia.com — sering 403, jangan andalkan)
   - buat_infografis.py: generate img/harga-YYYY-MM-DD.png (1080x1080, PIL)
   - posting_harga.py: posting infografis + caption ke IG @falcon_esport537 (instagram-cli post-feed) dan Threads @beritaviraldotcom (threads-cli publish-post)
2. PENTING: posting IG & Threads WAJIB butuh approval/persetujuan user per posting (aturan runtime). Saat approval card muncul, tulis di laporan "menunggu persetujuan"; JANGAN bypass. Kalau user tidak menyetujui, catat sebagai "menunggu persetujuan" bukan gagal.
3. Data tersimpan di data/harga-YYYY-MM-DD.json (dipakai untuk indikator naik/turun vs kemarin).

Laporan ke user (Bahasa Indonesia): daftar harga hari ini (10 item) + status posting IG/Threads (berhasil/menunggu persetujuan).
