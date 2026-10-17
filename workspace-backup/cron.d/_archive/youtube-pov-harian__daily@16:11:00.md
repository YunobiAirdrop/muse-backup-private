---
id: youtube-pov-harian
title: Video POV YouTube harian
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 16:11:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC660C34E5D9889E4C65D2272BEE7805","conversation_id":"whatsapp_channel","provider":"whatsapp","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Produksi & upload 1 video POV sejarah per hari ke channel YouTube "Yunobi BerCERITA RAKYAT +62" (@ceritarakyat862, akun khususstokyunobi@gmail.com). PASTIKAN channel aktif di YouTube Studio adalah @ceritarakyat862 SEBELUM upload (jangan sampai salah channel lagi).

**JAM UPLOAD: target tayang 19:00-20:00 WIB (prime time).** Produksi 16:11, set "Terjadwal" 19:00 WIB jika selesai awal.

**ATURAN TOPIK: SETIAP HARI BEDA.** Pool ~/workspace/youtube-otomatis/pool-topik.md, cek riwayat-topik.json, bergantian Nusantara ↔ Dunia, catat setelah produksi.

**HOOK FYP:** 30 detik pertama = momen paling dramatis. Judul pakai curiosity gap + hook kuat potensi FYP (tanpa janji garansi 100%). Thumbnail ≤4 kata.

**PENTING — AI DISCLOSURE:** Saat upload (long + shorts), WAJIB centang opsi "Altered content / konten yang diubah AI" (YouTube mewajibkan label konten AI).

**STANDAR VOICEOVER (aturan user 2026-10-04):** Bahasa Indonesia fasih & natural, JANGAN terdengar seperti dubbing, JANGAN berlogat Inggris.

**FORMAT LONG VIDEO (gaya referensi Suki @Sukii65 — update 2026-10-03):**
- Durasi 9-10 menit, naskah orisinal ~1000-1200 kata, POV orang pertama dramatis
- 85-90 gambar ilustrasi digital 2D semi-kartun gaya storybook/komik 16:9 (BUKAN photorealistic), palet earthy muted, karakter konsisten
- PACING: gambar berganti tiap 6-7 detik — 1 gambar untuk 1-2 kalimat narasi (satu "beat" cerita), SANGAT sinkron dengan yang diceritakan
- Transisi: hard cut langsung (tanpa fade). Ken Burns lambat & halus per gambar (zoom/pan ±5-15%)
- Voiceover TTS Indonesia natural. Retention: twist tiap 2-3 menit.
- Layout sesekali: panel komik / split-screen untuk montase

**SHORTS DARI LONG VIDEO (3 Shorts/hari) — optimasi FYP:**
- Setelah long video jadi, potong 3 klip terbaik (30-60 detik tiap klip, momen paling menegangkan/dramatis)
- Format vertikal 9:16 (crop tengah dari 16:9)
- Judul: hook kuat + rasa penasaran, format "[hook momen] | [judul long video]"
- Deskripsi Shorts WAJIB: "Tonton versi lengkapnya di sini: [URL video long]" + 1 produk afiliasi + hashtag FYP (#shorts #pov #sejarah + 2-3 spesifik niche)
- Tag: isi tag YouTube dengan keyword relevan (pov, sejarah indonesia, kisah sejarah, + keyword topik)

**AFILIASI DI LONG + SHORTS:**
- Ambil 3 produk dari ~/workspace/blog-otomatis/share_promo.py (rotasi harian, jangan ulang dalam 7 hari)
- Tempel di deskripsi LONG video bagian "🛒 Produk Rekomendasi:" (nama + link afiliasi)
- Tempel 1 produk paling relevan di deskripsi tiap SHORTS
- Format: "🛒 [Nama Produk] - Rp[harga]: [link]"

**OTOMATIS:** judul + deskripsi (sinopsis + subscribe + daftar isi + afiliasi) + hashtag (#pov #sejarah #kisahsejarah #indonesia + 2 spesifik) + thumbnail (bikin_thumbnail.py)

Langkah:
1. Pilih topik → script/YYYY-MM-DD.txt (~1000-1200 kata). TULIS NASKAH PER BEAT: tiap 1-2 kalimat = 1 beat visual, tandai setiap beat dengan prompt gambar spesifiknya
2. Voiceover per beat (tts --language id --voice avocado_v2:mudiwa), gabung
3. 85-90 gambar via media.generate_image — gaya: ilustrasi digital 2D semi-kartun storybook, SATU gambar per beat naskah
4. Rakit long: tiap gambar tampil 6-7 detik mengikuti durasi voiceover beat-nya → video/YYYY-MM-DD.mp4 (rakit_video.py perlu disesuaikan: durasi per gambar = durasi voiceover beat, bukan total/banyak gambar)
5. Potong 3 shorts: ffmpeg -ss [detik] -t 45 -vf "crop=ih*9/16:ih" → shorts/YYYY-MM-DD-sN.mp4
6. Thumbnail otomatis
7. Upload long via browser ke @ceritarakyat862 (CEK channel aktif dulu!) + centang AI disclosure + judul + deskripsi (termasuk afiliasi) + hashtag + thumbnail, terjadwal 19:00
8. Upload 3 shorts via browser + centang AI disclosure + judul hook + deskripsi (link long video + 1 afiliasi) + hashtag FYP + tag keyword
9. Upload = approval user (tertunda = "menunggu persetujuan")
10. Laporkan: judul long + 3 judul shorts + status upload + topik ke riwayat
