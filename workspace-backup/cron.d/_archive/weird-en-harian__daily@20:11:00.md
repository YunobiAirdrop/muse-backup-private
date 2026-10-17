---
id: weird-en-harian
title: Weird Facts English harian (Weird World Daily)
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 20:11:00
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":1,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC4FEB788ACA61D7D564D47E87F5E249","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Produksi & upload 1 video FAKTA ANEH DUNIA (bahasa INGGRIS) per hari ke channel YouTube "Weird World Daily" (@BizarreWorldDaily, akun khususstokyunobi@gmail.com). TARGET: penonton internasional (USA). WAJIB CEK channel aktif benar di YouTube Studio SEBELUM upload.

**JAM UPLOAD: target tayang 19:00-20:00 WIB.** Produksi 20:11.

**ATURAN: SETIAP HARI TOPIK BERBEDA.** Fakta aneh: tempat bizarre, kejadian unbelievable, rekor unik, fenomena alam aneh.

**PENTING — AI DISCLOSURE:** Saat upload, WAJIB centang opsi "Altered content / konten yang diubah AI".

**FORMAT (bahasa INGGRIS semua):**
- Durasi 9-10 menit, naskah orisinal ~1000-1200 kata ENGLISH
- 70-80 gambar ilustrasi digital 2D storybook 16:9, gaya colorful/fun
- Voiceover TTS ENGLISH natural (tts --language en)
- Thumbnail ≤4 kata ENGLISH

**SHORTS (3/hari):** 3 klip terbaik 30-60 detik, vertikal 9:16, judul hook English + hashtag (#shorts #facts #weirdfacts)

Langkah:
1. Pilih topik → tulis script ENGLISH per beat
2. Voiceover TTS English, gabung
3. Generate gambar via media.generate_image
4. Rakit video, potong 3 shorts, buat thumbnail
5. Upload via browser ke @BizarreWorldDaily (CEK channel!) + centang AI disclosure + judul/deskripsi English + hashtag + thumbnail
6. Upload 3 shorts
7. Upload = approval user (tertunda = "menunggu persetujuan")
8. Laporkan: judul + URL video + status

Workspace: ~/workspace/youtube-otomatis/weird-en/
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md
