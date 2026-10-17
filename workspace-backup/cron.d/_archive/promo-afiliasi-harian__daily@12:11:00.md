---
id: promo-afiliasi-harian
title: Promo afiliasi harian sosmed
enabled: true
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 12:11:00
timeout_secs: 7200
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"ACC9863A3D6464639324B1AF1ADFB6FD","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Jalankan promo afiliasi harian: 5 produk berbeda setiap hari ke 4 akun sosmed (IG @falcon_esport537, Threads @beritaviraldotcom, Threads @ngewebyuk, FB Page BeritaViraldotcom).

Langkah:
1. cd ~/workspace/blog-otomatis && python3 share_promo.py --dry-run — tampilkan 5 produk hari ini
2. Jika semua foto produk tersedia di promo_img/, jalankan: python3 share_promo.py (tanpa dry-run) untuk generate gambar promo + video dan posting ke semua akun
3. CATATAN: posting IG/FB/Threads memicu approval user (aturan runtime) — jika posting tertunda menunggu persetujuan, laporkan sebagai "menunggu persetujuan" bukan gagal
4. Laporkan ke user: produk apa saja yang dipromosikan hari ini + status posting per akun

Jika foto produk belum lengkap, laporkan produk mana yang fotonya belum ada dan lanjutkan dengan yang tersedia.
