---
id: youtube-pov-harian
title: Video POV YouTube harian
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 15:11:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC3B4AE0B2A38FBA782CC2478060A235","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Produksi & upload 1 video POV sejarah per hari ke channel YouTube "Yunobi BerCERITA RAKYAT +62" (@ceritarakyat862, akun khususstokyunobi@gmail.com). PENTING: pakai channel INI, bukan channel "Kisah POV" — user perintahkan 2026-10-03 pakai channel yang sudah jadi.

**ATURAN TOPIK KERAS: SETIAP HARI HARUS CERITA BERBEDA.** Pool 40 topik di ~/workspace/youtube-otomatis/pool-topik.md (20 Nusantara + 20 Dunia). Cara pilih:
1. Baca ~/workspace/youtube-otomatis/riwayat-topik.json (daftar topik 60 hari terakhir)
2. Pilih topik yang BELUM pernah dipakai — bergantian Nusantara ↔ Dunia tiap hari
3. Kalau pool habis, buat topik BARU yang orisinal (jangan paksa ulang)
4. Setelah produksi, catat topik + tanggal ke riwayat-topik.json

FORMAT FINAL:
- Durasi MINIMAL 15 menit
- Naskah orisinal Bahasa Indonesia ~2000 kata, 15-20 adegan, sudut pandang orang pertama dramatis
- 15-20 gambar sinematik photorealistic 16:9 (BUKAN kartun/AI-looking)
- Voiceover TTS Indonesia natural
- Ken Burns + film grain + color grading + vignette — terlihat natural, bukan AI murahan

SEMUA OTOMATIS:
- Judul: "POV: Kamu Jadi [tokoh] di [tempat] | Kisah Sejarah"
- Deskripsi: 2-3 paragraf sinopsis + ajakan subscribe + daftar isi
- Hashtag: #pov #sejarah #kisahsejarah #indonesia + 2 spesifik topik
- Thumbnail: python3 ~/workspace/youtube-otomatis/bikin_thumbnail.py <gambar_terbaik> "<judul_pendek>" thumb.jpg

Langkah:
1. Pilih topik (aturan anti-ulang di atas) → script/YYYY-MM-DD.txt (2000 kata, 15-20 adegan)
2. Voiceover per adegan (tts --language id --voice avocado_v2:mudiwa), gabung ffmpeg
3. 15-20 gambar via media.generate_image ("Cinematic first-person POV view, [adegan], photorealistic historical drama film still, 16:9")
4. Rakit: python3 ~/workspace/youtube-otomatis/rakit_video.py gambar/YYYY-MM-DD/ audio/gabungan.mp3 video/YYYY-MM-DD.mp4
5. Thumbnail otomatis
6. Upload via browser ke channel @ceritarakyat862 (pilih channel yang benar di YouTube Studio — akun punya 2 channel: "Yunobi BerCERITA RAKYAT +62" dan "Kisah POV"; pakai yang PERTAMA) + judul + deskripsi + hashtag + thumbnail
7. Upload = approval user (tertunda = "menunggu persetujuan")
8. Laporkan: judul + durasi + status upload + catat topik ke riwayat
