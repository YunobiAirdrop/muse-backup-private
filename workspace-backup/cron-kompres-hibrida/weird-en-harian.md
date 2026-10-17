Produksi & upload 1 video FAKTA ANEH DUNIA (ENGLISH)/hari ke "Weird World Daily" (@BizarreWorldDaily, khususstokyunobi@gmail.com). TARGET: penonton USA. WAJIB CEK channel aktif benar di YouTube Studio SEBELUM upload.

**VIRAL:** baca ~/workspace/youtube-otomatis/protokol-viral.md (trend jacking khusus niche, hook 3 detik, double-down >10x, packaging, retensi). Anti full-AI: ~/AGENTS.md (cerita orisinal, pacing variatif, SFX sinkron, AI disclosure dicentang). SHORTS: hashtag maks 3 di AKHIR JUDUL (contoh: "... #shorts #facts #weirdfacts"), BUKAN di deskripsi. Long: hashtag di deskripsi.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**JADWAL:** tayang BESOK 07:00 WIB (= 19:00 US Eastern / prime time Amerika). Produksi 16:11. Upload ~20:00-22:00 → ketukan persetujuan 20:00-22:00, set "Terjadwal" BESOK 07:00 WIB.

**TOPIK:** tiap hari BERBEDA. Fakta aneh: tempat bizarre, kejadian unbelievable, rekor unik, fenomena alam aneh.

**AI DISCLOSURE:** WAJIB centang "Altered content" tiap upload.

**SENTUHAN MANUSIA:** script WAJIB 2-3 kalimat reaksi pribadi narator ("wait, WHAT?!" / "I had to read that twice..."). Bahasa fun dan ekspresif kayak orang excited. Struktur variatif (grouping by tema / battle "which is weirder", bukan selalu countdown). Pacing cepat energik; jeda di fakta paling gila. Text overlay 3-5 momen kunci (angka, reaksi). Judul/deskripsi fun personal.

**POLA UPLOAD (belum verifikasi HP → batas harian):** selang-seling: hari ini 1 LONG saja, besok 3 SHORTS saja, dst. Cek upload-terakhir.txt. JANGAN long+shorts sehari. Kena batas → upload yang bisa, sisanya besok.

**FORMAT (ENGLISH semua):** 9-10 menit, naskah orisinal ~1000-1200 kata. 70-80 gambar storybook 2D 16:9 gaya colorful/fun. Voiceover TTS ENGLISH natural (tts --language en). Thumbnail ≤4 kata ENGLISH.

**KLIP VIDEO AI (hibrida — 10 klip/video):** selain gambar, generate 10 klip video AI via media.generate_video untuk 10 beat PALING PENTING: beat 1 (hook, 3 detik pertama — WAJIB klip) + 9 twist/reveal/momen kunci lain. Tiap klip 5-10 detik, 16:9, gaya storybook 2D gaya colorful/fun. 10 klip ini MENGGANTIKAN gambar di beat tersebut (total visual tetap ~70-80). Wajah/karakter harus konsisten dengan gambar — jika hasil morphing/aneh, BUANG klipnya dan pakai gambar biasa di beat itu. Shorts tetap dipotong dari video jadi.

**ANTI-MACET KLIP:** generate maks 2x percobaan per klip → gagal = pakai gambar biasa untuk beat itu. Total waktu generate 10 klip maks 90 menit → lewat = rakit dengan klip yang jadi + gambar untuk sisanya. 1 klip bermasalah jangan korbankan video. **HEMAT TOKEN KLIP (WAJIB):** 10 klip HARUS di-generate BERURUTAN oleh SATU agen — DILARANG spawn 1 subagent per klip (terukur: 1 subagent/klip membakar ~2 juta token karena mewarisi seluruh konteks). Panggil media.generate_video langsung 10x berurutan; kerjakan tahap klip SEAWAL MUNGKIN setelah naskah jadi, saat konteks masih kecil.

**SHORTS (3/hari):** 3 klip terbaik 30-60 detik, vertikal 9:16. Judul hook English + 3 hashtag di AKHIR JUDUL (#shorts #facts #weirdfacts).

**LANGKAH:**
1. Topik → script ENGLISH per beat, selipkan 2-3 kalimat reaksi narator.
2. Voiceover TTS English, gabung; energik, jeda di fakta paling gila.
3. Gambar via media.generate_image. Kurangi 10 gambar untuk 10 beat klip; generate 10 klip video AI via media.generate_video sesuai section KLIP VIDEO AI.
4. Rakit video, potong 3 shorts, buat thumbnail; text overlay 3-5 momen kunci. Sisipkan 10 klip video di beat yang sesuai menggantikan gambar.
5. Kemarin LONG (atau file tak ada) → upload LONG saja ke @BizarreWorldDaily (CEK channel!) + AI disclosure + judul/deskripsi English + hashtag + thumbnail, "Terjadwal" BESOK 07:00 WIB. Tulis "long:YYYY-MM-DD".
6. Kemarin SHORTS → upload 3 SHORTS (produksi KEMARIN) + AI disclosure + judul English (+ 3 hashtag akhir) + deskripsi English (tanpa hashtag), "Terjadwal" BESOK 07:00 WIB. Tulis "shorts:YYYY-MM-DD".
7. Upload = approval user ("menunggu persetujuan", ketuk 20:00-22:00).
8. Laporkan: yang diupload (long/shorts) + URL + status.

Workspace: ~/workspace/youtube-otomatis/weird-en/
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md
