---
id: truecrime-en-harian
title: True Crime English harian (Dark Case Files)
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 01:11:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC9AA9C6D8051C32898CA5DCBF116E8B","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Produksi & upload 1 video TRUE CRIME (bahasa INGGRIS) per hari ke channel YouTube "Dark Case Files" (@TrueCaseFilesTV, akun khususstokyunobi@gmail.com). TARGET: penonton internasional (USA). WAJIB CEK channel aktif benar di YouTube Studio SEBELUM upload.

**JAM UPLOAD: target tayang 07:00 WIB (= jam 19:00 US Eastern / prime time Amerika).** Produksi 01:11 (BARENG 9 channel lain), set "Terjadwal" 07:00 WIB.

**ATURAN: SETIAP HARI KASUS BERBEDA.** Fokus kasus true crime terkenal dunia (USA, UK, dll). Hindari deskripsi kekerasan grafis/sadis — gaya dokumenter/investigatif (aman monetisasi).

**PENTING — AI DISCLOSURE:** Saat upload, WAJIB centang opsi "Altered content / konten yang diubah AI" (YouTube mewajibkan label konten AI).

**FORMAT (bahasa INGGRIS semua — judul, naskah, deskripsi):**
- Durasi 9-10 menit, naskah orisinal ~1000-1200 kata ENGLISH
- 70-80 gambar ilustrasi digital 2D storybook 16:9, gaya noir/dokumenter gelap
- Voiceover TTS ENGLISH natural (tts --language en)
- Thumbnail ≤4 kata ENGLISH

**SHORTS (3/hari):** potong 3 klip terbaik 30-60 detik, vertikal 9:16, judul hook English, deskripsi + link video long + hashtag (#shorts #truecrime #mystery)

Langkah:
1. Pilih kasus → tulis script ENGLISH per beat
2. Voiceover TTS English, gabung
3. Generate gambar via media.generate_image
4. Rakit video, potong 3 shorts, buat thumbnail
5. Upload via browser ke @TrueCaseFilesTV (CEK channel!) + centang AI disclosure + judul/deskripsi English + hashtag + thumbnail, set "Terjadwal" 07:00 WIB
6. Upload 3 shorts, set "Terjadwal" 07:00 WIB
7. Upload = approval user (tertunda = "menunggu persetujuan")
8. Laporkan: judul + URL video + status

Workspace: ~/workspace/youtube-otomatis/truecrime-en/
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md
