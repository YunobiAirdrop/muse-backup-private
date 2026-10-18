---
id: horror-en-harian
title: Horror English harian (Midnight Dread Tales)
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 13:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Produksi & upload 1 video CERITA HOROR (ENGLISH)/hari ke "Midnight Dread Tales" (@TalesOfDreadTV, khususstokyunobi@gmail.com). TARGET: penonton USA. WAJIB CEK channel aktif benar di YouTube Studio SEBELUM upload.

**VIRAL:** baca ~/workspace/youtube-otomatis/protokol-viral.md (trend jacking khusus niche, hook 3 detik, double-down >10x, packaging, retensi). Anti full-AI: ~/AGENTS.md (cerita orisinal, pacing variatif, SFX sinkron, AI disclosure dicentang). SHORTS: hashtag maks 4 di AKHIR JUDUL, ditutup #foryou (contoh: "... #shorts #horror #scarystories #foryou"), BUKAN di deskripsi. Long: hashtag di deskripsi, WAJIB termasuk #foryou.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**JADWAL:** tayang BESOK 07:00 WIB (= 19:00 US Eastern / prime time Amerika). Produksi 16:11. Upload ~20:00-22:00 → ketukan persetujuan 20:00-22:00, set "Terjadwal" BESOK 07:00 WIB.

**CERITA:** tiap hari BERBEDA. Horor internasional: urban legend dunia, haunted places, creepypasta-style original.

**AI DISCLOSURE:** WAJIB centang "Altered content" tiap upload.

**SENTUHAN MANUSIA:** script WAJIB 2-3 kalimat opini pribadi narator ("this one genuinely scared me..." / "I still think about this one..."). Bahasa conversational kayak storyteller. Struktur variatif (kadang mulai dari ending mengejutkan). Pacing variatif (suasana lambat, klimaks cepat); jeda dramatis sebelum scare. Text overlay 3-5 momen kunci. Judul/deskripsi personal.

**POLA UPLOAD (belum verifikasi HP → batas harian):** selang-seling: hari ini 1 LONG saja, besok 3 SHORTS saja, dst. Cek upload-terakhir.txt. JANGAN long+shorts sehari. Kena batas → upload yang bisa, sisanya besok.

**FORMAT (ENGLISH semua):** 9-10 menit, naskah orisinal ~1000-1200 kata, mencekam. 70-80 gambar storybook 2D GELAP 16:9. Voiceover TTS ENGLISH dalam/mencekam (tts --language en). Thumbnail ≤4 kata ENGLISH.

**SHORTS (3/hari):** 3 klip termencekam 30-60 detik, vertikal 9:16. Judul hook English + hashtag di AKHIR JUDUL ditutup #foryou (#shorts #horror #scarystories #foryou).

**LANGKAH:**
1. Tema → script ENGLISH per beat, selipkan 2-3 kalimat opini narator.
2. Voiceover TTS English, gabung; jeda dramatis sebelum scare.
3. Gambar via media.generate_image (gaya gelap/misterius).
4. Rakit video, potong 3 shorts, buat thumbnail; text overlay 3-5 momen kunci.
5. Kemarin LONG (atau file tak ada) → upload LONG saja ke @TalesOfDreadTV (CEK channel!) + AI disclosure + judul/deskripsi English + hashtag (termasuk #foryou) + thumbnail, "Terjadwal" BESOK 07:00 WIB. Tulis "long:YYYY-MM-DD".
6. Kemarin SHORTS → upload 3 SHORTS (produksi KEMARIN) + AI disclosure + judul English (+ hashtag akhir ditutup #foryou) + deskripsi English (tanpa hashtag), "Terjadwal" BESOK 07:00 WIB. Tulis "shorts:YYYY-MM-DD".
7. Upload = approval user ("menunggu persetujuan", ketuk 20:00-22:00).
8. Laporkan: yang diupload (long/shorts) + URL + status.

Workspace: ~/workspace/youtube-otomatis/horror-en/
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** video yang SUDAH diproduksi WAJIB tayang — tidak boleh hilang/mogok diam-diam.
- Upload GAGAL karena "Batas upload harian telah tercapai" (atau pesan limit harian YouTube lain): JANGAN retry saat itu juga (limit ±24 jam — pasti gagal lagi). WAJIB: (1) tulis file instruksi upload lengkap (judul, deskripsi, hashtag, thumbnail, AI disclosure, slot jadwal target) seperti biasa; (2) tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/{channel}-YYYY-MM-DD.json dengan format {"channel":"...","video_path":"<absolut>","instruksi_path":"<absolut>","slot_target":"YYYY-MM-DD HH:MM WIB","gagal_pada":"YYYY-MM-DDTHH:MM:SS+07:00","sebab":"..."} — contoh lengkap di ~/workspace/youtube-otomatis/retry-queue/README.md. Watchdog harian otomatis mengerjakan antrean ini. Catat di laporan run: video apa yang gagal + path antreannya.
- Upload GAGAL karena sebab LAIN (bukan limit harian): perbaiki dan retry SEGERA saat itu juga (preferensi user), jangan tunda besok.
