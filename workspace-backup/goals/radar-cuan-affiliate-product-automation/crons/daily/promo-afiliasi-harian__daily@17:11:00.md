---
id: promo-afiliasi-harian
title: Promo afiliasi harian sosmed
enabled: false
owner: goal:radar-cuan-affiliate-product-automation
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 17:11:00
timeout_secs: 10800
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"ACA8EEEE76AF53932CE8DFBF6E151C5F","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Jalankan promo afiliasi harian: 5 produk berbeda setiap hari ke 4 akun sosmed (IG @falcon_esport537, Threads @beritaviraldotcom, Threads @ngewebyuk, FB Page BeritaViraldotcom). HANYA 5 video (satu per produk), video yang sama dishare ke 4 akun.

**JADWAL KETUKAN: produksi 17:11, ketukan persetujuan muncul ~20:00-23:00 WIB (user senggang malam hari).**

FORMAT VIDEO FINAL (disetujui user 2026-10-03):
- Durasi 20 detik, 2 segmen @ ~10 detik, format vertikal 9:16
- Segmen 1: orang me-REVIEW produknya (presenter ngomong ke kamera sambil pegang produk) + voiceover Bahasa Indonesia (naskah review)
- Segmen 2: orang MEMAKAI produknya (lifestyle shot profesional) + voiceover Bahasa Indonesia (harga + ajakan checkout)
- Voiceover: TTS Bahasa Indonesia (--language id), suara natural, FASIH (jangan seperti dubbing, jangan berlogat Inggris)

Langkah:
1. cd ~/workspace/blog-otomatis && python3 share_promo.py --dry-run — tampilkan 5 produk hari ini (rotasi otomatis anti-ulang via promo_history.json)
2. Untuk tiap dari 5 produk:
   a. Generate segmen 1 via media.generate_video: prompt English "A friendly Indonesian woman/man product reviewer talking directly to camera, holding up [nama produk], gesturing enthusiastically while explaining, mouth moving as if speaking, bright studio lighting, vertical 9:16, professional product review" + foto produk dari promo_img/ sebagai image input
   b. Generate segmen 2 via media.generate_video: prompt English "A stylish Indonesian woman/man USING/WEARING [nama produk], lifestyle shot, enjoying the product, professional commercial style, vertical 9:16" + foto produk sebagai image input
   c. Buat naskah voiceover ID 2 bagian: segmen 1 = review antusias (~10 detik), segmen 2 = pengalaman pakai + harga + CTA checkout (~10 detik). Tulis angka dalam kata-kata ("tiga ratus ribu" bukan "300.000")
   d. Generate audio via: /opt/hatch/bin/tts speak --language id --voice avocado_v2:lumi --output voice-segN.mp3 --text-stdin (stdin = naskah)
   e. Gabung: ffmpeg -i seg1.mp4 -i voice1.mp3 -c:v copy -c:a aac -shortest seg1v.mp4 (ulang untuk seg2), lalu concat kedua segmen jadi final 20 detik
   f. Encode WhatsApp-friendly: -vf scale=540:-2 -c:v libx264 -profile:v baseline -level 3.0 -pix_fmt yuv420p -movflags +faststart
3. Generate gambar promo via share_promo.py (siapkan_konten)
4. Posting ke 4 akun: tiap produk = 1 gambar + 1 video final + caption (bikin_caption) + link afiliasi
5. CATATAN: posting memicu approval user (aturan runtime) — tertunda = "menunggu persetujuan", bukan gagal. Ketukan muncul malam 20:00-23:00 WIB.
6. Laporkan: 5 produk hari ini + status posting per akun

Jika generate video gagal untuk suatu produk, fallback ke video Ken Burns dari gambar promo.
