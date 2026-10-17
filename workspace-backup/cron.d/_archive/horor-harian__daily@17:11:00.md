---
id: horor-harian
title: Cerita Horor YouTube harian
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 17:11:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC660C34E5D9889E4C65D2272BEE7805","conversation_id":"whatsapp_channel","provider":"whatsapp","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Produksi & upload 1 video CERITA HOROR per hari ke channel YouTube "Kisah Horor" (@KisahPOV, akun khususstokyunobi@gmail.com). JANGAN upload ke @ceritarakyat862 — channel horor adalah @KisahPOV. WAJIB CEK channel aktif benar ("Kisah Horor") di YouTube Studio SEBELUM upload (pelajaran: pernah salah upload ke channel lain).

**JAM UPLOAD: target tayang 19:00-20:00 WIB (prime time).** Produksi 17:11. Channel @KisahPOV sudah terverifikasi nomor HP, jadi video >15 menit & thumbnail kustom aktif.

**ATURAN CERITA: SETIAP HARI BEDA TEMA.** Pool ~/workspace/horor-otomatis/pool-cerita.md, cek riwayat-cerita.json (anti-ulang 60 hari), gonta-ganti tema: hantu lokal ↔ urban legend ↔ misteri/tempat angker ↔ legenda. Catat setelah produksi.

**HOOK:** 30 detik pertama = momen paling mencekam. Judul pakai curiosity gap. Thumbnail ≤4 kata, gaya horor gelap. Jangan janji garansi FYP/views.

**PENTING — AI DISCLOSURE:** Saat upload (long + shorts), WAJIB centang opsi "Altered content / konten yang diubah AI" (YouTube mewajibkan label konten AI).

**STANDAR VOICEOVER (aturan user 2026-10-04):** Bahasa Indonesia fasih & natural, JANGAN terdengar seperti dubbing, JANGAN berlogat Inggris.

**FORMAT VIDEO (sama seperti format POV baru):**
- Durasi 9-10 menit, naskah orisinal ~1000-1200 kata BAHASA INDONESIA, sudut pandang orang pertama/kedua yang mencekam
- 70-80 gambar ilustrasi digital 2D storybook GELAP/misterius 16:9 (BUKAN photorealistic), palet gelap, karakter konsisten
- PACING: gambar berganti tiap 6-7 detik — 1 gambar untuk 1-2 kalimat narasi (satu "beat" cerita), sinkron dengan yang diceritakan
- Transisi: hard cut langsung (tanpa fade). Ken Burns lambat & halus per gambar
- Voiceover TTS Indonesia: tts --language id --voice avocado_v2:magnus (suara dalam & berat, cocok horor)
- Retention: twist/kejutan tiap 2-3 menit

**SHORTS (3 Shorts/hari) — optimasi:**
- Potong 3 klip termencekam (30-60 detik), vertikal 9:16
- Judul: hook kuat + rasa penasaran, format "[hook momen] | [judul video]"
- Deskripsi WAJIB: "Tonton versi lengkapnya di sini: [URL video]" + 1 produk afiliasi + hashtag (#shorts #horor #ceritahoror + 2 spesifik)
- Tag YouTube: keyword relevan (cerita horor, hantu indonesia, misteri, + keyword tema)

**AFILIASI:**
- Ambil 1-2 produk dari ~/workspace/blog-otomatis/share_promo.py (rotasi harian, jangan ulang dalam 7 hari)
- Tempel di deskripsi video bagian "Rekomendasi:" + di tiap Shorts (1 produk)
- Format: "[Nama Produk] - Rp[harga]: [link]"

**OTOMATIS:** judul + deskripsi (sinopsis + subscribe + afiliasi) + hashtag (#horor #ceritahoror #misteri + 2 spesifik) + thumbnail (bikin_thumbnail.py)

Langkah:
1. Pilih tema dari pool → cek riwayat-cerita.json → tulis script/YYYY-MM-DD.txt (~1000-1200 kata). TULIS PER BEAT: tiap 1-2 kalimat = 1 beat visual, sertakan prompt gambar spesifik per beat
2. Voiceover per beat: tts --language id --voice avocado_v2:magnus, gabung jadi audio/YYYY-MM-DD.mp3
3. 70-80 gambar via media.generate_image — gaya: ilustrasi digital 2D storybook gelap/misterius, SATU gambar per beat
4. Rakit: rakit_video.py ~/workspace/horor-otomatis/gambar/YYYY-MM-DD/ audio/YYYY-MM-DD.mp3 video/YYYY-MM-DD.mp4 (durasi per gambar mengikuti voiceover beat)
5. Potong 3 shorts: ffmpeg -ss [detik] -t 45 -vf "crop=ih*9/16:ih" → shorts/YYYY-MM-DD-sN.mp4
6. Thumbnail: bikin_thumbnail.py <gambar_termencekam> "<JUDUL_4_KATA>" thumbnail-YYYY-MM-DD.jpg
7. Upload via browser ke @KisahPOV — CEK DULU channel aktif = "Kisah Horor"! Centang AI disclosure + judul + deskripsi (afiliasi) + hashtag + thumbnail
8. Upload 3 shorts + centang AI disclosure + judul hook + deskripsi (link video + 1 afiliasi) + hashtag + tag
9. Upload = approval user (tertunda = "menunggu persetujuan")
10. Catat tema ke riwayat-cerita.json. Laporkan: judul + 3 judul shorts + status upload
