---
id: truecrime-en-harian
title: True Crime English harian (Dark Case Files)
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 12:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Produksi & upload 1 video TRUE CRIME (ENGLISH)/hari ke "Dark Case Files" (@TrueCaseFilesTV, khususstokyunobi@gmail.com). TARGET: penonton USA. WAJIB CEK channel aktif benar di YouTube Studio SEBELUM upload.

**VIRAL:** baca ~/workspace/youtube-otomatis/protokol-viral.md (trend jacking khusus niche, hook 3 detik, double-down >10x, packaging, retensi). Anti full-AI: ~/AGENTS.md (cerita orisinal, pacing variatif, SFX sinkron, AI disclosure dicentang). SHORTS: hashtag maks 4 di AKHIR JUDUL, ditutup #foryou (contoh: "... #shorts #truecrime #mystery #foryou"), BUKAN di deskripsi. Long: hashtag di deskripsi, WAJIB termasuk #foryou.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**JADWAL:** tayang BESOK 07:00 WIB (= 19:00 US Eastern / prime time Amerika). Produksi 16:11. Upload ~20:00-22:00 → ketukan persetujuan 20:00-22:00, set "Terjadwal" BESOK 07:00 WIB.

**KASUS:** tiap hari BERBEDA. True crime terkenal dunia (USA, UK, dll). Hindari deskripsi kekerasan grafis/sadis — gaya dokumenter/investigatif (aman monetisasi).

**AI DISCLOSURE:** WAJIB centang "Altered content" tiap upload.

**SENTUHAN MANUSIA:** script WAJIB 2-3 kalimat opini pribadi narator ("honestly, this part still gives me chills..." / "in my opinion..."). Bahasa conversational, bukan artikel Wikipedia dibacain. Struktur variatif (kadang mulai dari momen paling mengejutkan/pertanyaan). Pacing variatif (investigasi lambat, reveal cepat). Text overlay 3-5 momen kunci. Judul/deskripsi personal; deskripsi + 1-2 kalimat opini.

**POLA UPLOAD (belum verifikasi HP → batas harian):** selang-seling: hari ini 1 LONG saja, besok 3 SHORTS saja, dst. Cek upload-terakhir.txt. JANGAN long+shorts sehari. Kena batas → upload yang bisa, sisanya besok.

**FORMAT (ENGLISH semua):** 9-10 menit, naskah orisinal ~1000-1200 kata. 70-80 gambar storybook 2D 16:9 gaya noir/dokumenter gelap. Voiceover TTS ENGLISH natural (tts --language en). Thumbnail ≤4 kata ENGLISH.

**SHORTS (3/hari):** 3 klip terbaik 30-60 detik, vertikal 9:16. Judul hook English + hashtag di AKHIR JUDUL ditutup #foryou (#shorts #truecrime #mystery #foryou). Deskripsi + link video long (tanpa hashtag).

**JALUR UPLOAD (perbaikan 2026-10-12):** upload WAJIB via API memakai yt-growth (slug truecrime-en, token OAuth per channel sudah aktif) — BUKAN browser Studio. Upload browser channel ini mati di modal verifikasi Google ("Verifikasi diri Anda") yang tidak bisa di-skip. Browser hanya dipakai SETELAH video terupload via API, untuk centang AI disclosure di Studio. JANGAN memicu login Google baru tanpa kabari user dulu (aturan user 2026-10-11). Sebelum upload via API, cek daftar upload channel dulu — bila judul yang sama sudah ada, JANGAN upload dobel.

**LANGKAH:**
1. Kasus → script ENGLISH per beat, selipkan 2-3 kalimat opini narator.
2. Voiceover TTS English, gabung; jeda dramatis sebelum reveal.
3. Gambar via media.generate_image.
4. Rakit video, potong 3 shorts, buat thumbnail; text overlay 3-5 momen kunci.
5. Kemarin LONG (atau file tak ada) → upload LONG saja ke @TrueCaseFilesTV via API (lihat JALUR UPLOAD) + judul/deskripsi English + hashtag (termasuk #foryou) + thumbnail (bila API menolak, catat saja), private TERJADWAL BESOK 07:00 WIB (publishAt). Tulis "long:YYYY-MM-DD". AI disclosure dicentang menyusul via Studio.
6. Kemarin SHORTS → upload 3 SHORTS (produksi KEMARIN) via API + judul English (+ hashtag akhir ditutup #foryou) + deskripsi English (tanpa hashtag), private TERJADWAL BESOK 07:00 WIB. Tulis "shorts:YYYY-MM-DD". AI disclosure dicentang menyusul via Studio.
7. Upload via API tidak butuh ketukan persetujuan browser; laporkan hasil + videoId.
8. Laporkan: yang diupload (long/shorts) + URL + status.

Workspace: ~/workspace/youtube-otomatis/truecrime-en/
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** video yang SUDAH diproduksi WAJIB tayang — tidak boleh hilang/mogok diam-diam.
- Upload GAGAL karena "Batas upload harian telah tercapai" (atau pesan limit harian YouTube lain): JANGAN retry saat itu juga (limit ±24 jam — pasti gagal lagi). WAJIB: (1) tulis file instruksi upload lengkap (judul, deskripsi, hashtag, thumbnail, AI disclosure, slot jadwal target) seperti biasa; (2) tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/{channel}-YYYY-MM-DD.json dengan format {"channel":"...","video_path":"<absolut>","instruksi_path":"<absolut>","slot_target":"YYYY-MM-DD HH:MM WIB","gagal_pada":"YYYY-MM-DDTHH:MM:SS+07:00","sebab":"..."} — contoh lengkap di ~/workspace/youtube-otomatis/retry-queue/README.md. Watchdog harian otomatis mengerjakan antrean ini. Catat di laporan run: video apa yang gagal + path antreannya.
- Upload GAGAL karena sebab LAIN (bukan limit harian): perbaiki dan retry SEGERA saat itu juga (preferensi user), jangan tunda besok.
