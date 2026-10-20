---
id: mystery-en-harian
title: Mystery English (Unsolved Shadows) — mode hemat 3-4 hari sekali
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-21T13:30:00
  every: 84h
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":4,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC16EC965485E22365DFD191408750C3","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Produksi & upload 1 video MISTERI TAK TERPECAHKAN (ENGLISH)/hari ke "Unsolved Shadows" (@MysteryShadowsTV, khususstokyunobi@gmail.com). TARGET: penonton USA. WAJIB CEK channel aktif benar di YouTube Studio SEBELUM upload.

**VIRAL:** baca ~/workspace/youtube-otomatis/protokol-viral.md (trend jacking khusus niche, hook 3 detik, double-down >10x, packaging, retensi). Anti full-AI: ~/AGENTS.md (cerita orisinal, pacing variatif, SFX sinkron, AI disclosure dicentang). SHORTS: hashtag maks 4 di AKHIR JUDUL, ditutup #foryou (contoh: "... #shorts #mystery #unsolved #foryou"), BUKAN di deskripsi. Long: hashtag di deskripsi, WAJIB termasuk #foryou.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**JADWAL:** tayang BESOK 07:00 WIB (= 19:00 US Eastern / prime time Amerika). Produksi 16:11. Upload ~20:00-22:00 → ketukan persetujuan 20:00-22:00, set "Terjadwal" BESOK 07:00 WIB.

**MISTERI:** tiap hari BERBEDA. Unsolved mysteries dunia: disappearances, strange events, dark historical secrets, unexplained phenomena.

**AI DISCLOSURE:** WAJIB centang "Altered content" tiap upload.

**SENTUHAN MANUSIA:** script WAJIB 2-3 kalimat opini/teori pribadi narator ("my personal theory is..." / "what really gets me about this case..."). Bahasa conversational, ajak penonton mikir bareng ("what do YOU think happened?"). Struktur variatif (kadang mulai dari teori paling liar). Pacing variatif; jeda dramatis sebelum reveal penting. Text overlay 3-5 momen kunci. Judul/deskripsi personal.

**POLA UPLOAD (belum verifikasi HP → batas harian):** selang-seling: hari ini 1 LONG saja, besok 3 SHORTS saja, dst. Cek upload-terakhir.txt. JANGAN long+shorts sehari. Kena batas → upload yang bisa, sisanya besok.

**FORMAT (ENGLISH semua):** 9-10 menit, naskah orisinal ~1000-1200 kata. 70-80 gambar storybook 2D misterius 16:9. Voiceover TTS ENGLISH natural (tts --language en). Thumbnail ≤4 kata ENGLISH.

**SHORTS (3/hari):** 3 klip terbaik 30-60 detik, vertikal 9:16. Judul hook English + hashtag di AKHIR JUDUL ditutup #foryou (#shorts #mystery #unsolved #foryou).

**LANGKAH:**
1. Misteri → script ENGLISH per beat, selipkan 2-3 kalimat opini/teori narator.
2. Voiceover TTS English, gabung; jeda dramatis sebelum reveal.
3. Gambar via media.generate_image.
4. Rakit video, potong 3 shorts, buat thumbnail; text overlay 3-5 momen kunci.
5. Kemarin LONG (atau file tak ada) → upload LONG saja ke @MysteryShadowsTV (CEK channel!) + AI disclosure + judul/deskripsi English + hashtag (termasuk #foryou) + thumbnail, "Terjadwal" BESOK 07:00 WIB. Tulis "long:YYYY-MM-DD".
6. Kemarin SHORTS → upload 3 SHORTS (produksi KEMARIN) + AI disclosure + judul English (+ hashtag akhir ditutup #foryou) + deskripsi English (tanpa hashtag), "Terjadwal" BESOK 07:00 WIB. Tulis "shorts:YYYY-MM-DD".
7. Upload = approval user ("menunggu persetujuan", ketuk 20:00-22:00).
8. Laporkan: yang diupload (long/shorts) + URL + status.

Workspace: ~/workspace/youtube-otomatis/mystery-en/
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** video yang SUDAH diproduksi WAJIB tayang — tidak boleh hilang/mogok diam-diam.
- Upload GAGAL karena "Batas upload harian telah tercapai" (atau pesan limit harian YouTube lain): JANGAN retry saat itu juga (limit ±24 jam — pasti gagal lagi). WAJIB: (1) tulis file instruksi upload lengkap (judul, deskripsi, hashtag, thumbnail, AI disclosure, slot jadwal target) seperti biasa; (2) tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/{channel}-YYYY-MM-DD.json dengan format {"channel":"...","video_path":"<absolut>","instruksi_path":"<absolut>","slot_target":"YYYY-MM-DD HH:MM WIB","gagal_pada":"YYYY-MM-DDTHH:MM:SS+07:00","sebab":"..."} — contoh lengkap di ~/workspace/youtube-otomatis/retry-queue/README.md. Watchdog harian otomatis mengerjakan antrean ini. Catat di laporan run: video apa yang gagal + path antreannya.
- Upload GAGAL karena sebab LAIN (bukan limit harian): perbaiki dan retry SEGERA saat itu juga (preferensi user), jangan tunda besok.
