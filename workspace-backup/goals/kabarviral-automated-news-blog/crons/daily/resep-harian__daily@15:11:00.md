---
id: resep-harian
title: Resep masakan harian IG
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
Generate & antrekan 3 resep masakan Indonesia per hari untuk IG @falcon_esport537.

Langkah:
0. RETRY OTOMATIS (baru 2026-10-09, permintaan user): sebelum bikin resep baru, cek file data/antrean-ig-*.json hari-hari sebelumnya — kalau ada item dengan status "gagal" (mis. 403 Meta), coba posting ulang item-item itu dulu via instagram-cli post-feed dengan gambar & caption yang tersimpan di antrean. Maksimal 3 posting per hari (termasuk retry). Update status tiap item di file antreannya.
1. cd ~/workspace/resep-otomatis
2. `python3 -u bikin_resep.py 3` → 3 resep orisinal Bahasa Indonesia → data/resep-YYYY-MM-DD.json (anti-ulang 60 hari otomatis via riwayat-resep.json; kalau file hari ini sudah ada, lewati)
3. Untuk TIAP resep: generate 1 gambar via media.generate_image — prompt: "Professional food photography of [nama hidangan]: [deskripsi singkat dari prompt_gambar resep], appetizing, soft natural light, no text" — simpan ke workspace/resep-otomatis/gambar/ dengan nama YYYY-MM-DD-[nama].jpg
4. `python3 -u posting_resep.py --dry-run` → caption (hook + bahan + CTA + hashtag + 1 link afiliasi peralatan dapur rotasi 7 hari) + antrean data/antrean-ig-YYYY-MM-DD.json
5. Posting IG via instagram-cli HANYA jika approval user tersedia. Aturan runtime: post-feed memicu kartu persetujuan — JANGAN bypass. Jika kartu persetujuan muncul dan user menyetujui, jalankan `python3 -u posting_resep.py --post`. Jika tidak ada persetujuan, biarkan antrean berstatus "menunggu persetujuan".

PENTING: Jangan posting lebih dari 3 per hari (termasuk retry). Jangan generate ulang resep jika data/resep-YYYY-MM-DD.json sudah ada.

Laporan ke user (Bahasa Indonesia): hasil retry (kalau ada) + 3 judul resep hari ini + status tiap postingan (terposting / menunggu persetujuan) + 1 contoh caption lengkap.
