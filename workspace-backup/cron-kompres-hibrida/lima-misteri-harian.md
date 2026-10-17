Produksi & upload 1 video "5 KEJADIAN ANEH/MISTERI"/hari ke "Lima Misteri" (@LimaMisteri, khususstokyunobi@gmail.com). Channel ID: UCQ0vHTsTqVeYy3zLno6pVfQ. WAJIB CEK channel aktif benar di YouTube Studio SEBELUM upload.

**VIRAL:** baca ~/workspace/youtube-otomatis/protokol-viral.md (trend jacking khusus niche, hook 3 detik, double-down >10x, packaging, retensi). Anti full-AI: ~/AGENTS.md (cerita orisinal, pacing variatif, SFX sinkron, AI disclosure dicentang). SHORTS: hashtag maks 3 di AKHIR JUDUL (contoh: "... #shorts #misteri #penampakan"), BUKAN di deskripsi. Long: hashtag di deskripsi.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**KONSEP:** countdown 5 kejadian aneh/misterius/penampakan dunia. Tiap peristiwa: lokasi + deskripsi + unsur misterinya ("Nomor 1. Di [lokasi]..."). Akhir: ajakan subscribe.

**JADWAL:** tayang BESOK 19:00 WIB (prime time ID). Produksi 16:11. Upload ~20:00-22:00 → ketukan persetujuan 20:00-22:00, set "Terjadwal" BESOK 19:00 WIB.

**PERISTIWA:** tiap hari 5 BERBEDA. Pool ~/workspace/lima-misteri/pool-misteri.md, cek riwayat-misteri.json (anti-ulang 60 hari). Variasi: penampakan hantu ↔ UFO/fenomena langit ↔ kejadian aneh alam ↔ misteri tempat ↔ legenda urban.

**ORISINALITAS (aturan user 2026-10-05):** SEMUA visual HARUS ilustrasi AI orisinal. JANGAN pakai footage/foto asli dari internet (risiko copyright). Peristiwa nyata diilustrasikan ulang dengan gambar AI.

**AI DISCLOSURE:** WAJIB centang "Altered content" tiap upload (long + shorts).

**VOICEOVER:** Bahasa Indonesia fasih & natural, JANGAN logat Inggris. Voice: avocado_v2:mudiwa.

**SENTUHAN MANUSIA:** naskah WAJIB komentar pribadi narator tiap peristiwa (1-2 kalimat, misal "yang nomor 3 ini... jujur saya merinding" / "kalau kalian jadi saksinya, berani nggak?"). Bahasa conversational ("bayangin kalau kamu yang lihat..."). Urutan variatif (acak / paling seram dulu). Pacing variatif (peristiwa terseram porsi lebih lama + jeda dramatis). Text overlay momen kunci tiap peristiwa. Judul/deskripsi personal.

**POLA UPLOAD (belum verifikasi HP → batas harian):** selang-seling: hari ini 1 LONG saja, besok 3 SHORTS saja, dst. Cek upload-terakhir.txt. JANGAN long+shorts sehari. Kena batas → upload yang bisa, sisanya besok.

**LONG (9-10 mnt, ~1000-1200 kata ID):** struktur: intro hook 30 detik → 5 peristiwa (~1,5-2 mnt tiap) → outro + CTA subscribe. 70-80 gambar storybook 2D misterius 16:9 (BUKAN photorealistic). Pacing: 1 gambar/6-7 detik, sinkron narasi. Hard cut. Ken Burns lambat.

**KLIP VIDEO AI (hibrida — 10 klip/video):** selain gambar, generate 10 klip video AI via media.generate_video untuk 10 beat PALING PENTING: beat 1 (hook, 3 detik pertama — WAJIB klip) + 9 twist/reveal/momen kunci lain. Tiap klip 5-10 detik, 16:9, gaya storybook 2D misterius. 10 klip ini MENGGANTIKAN gambar di beat tersebut (total visual tetap ~70-80). Wajah/karakter harus konsisten dengan gambar — jika hasil morphing/aneh, BUANG klipnya dan pakai gambar biasa di beat itu. Shorts tetap dipotong dari video jadi.

**ANTI-MACET KLIP:** generate maks 2x percobaan per klip → gagal = pakai gambar biasa untuk beat itu. Total waktu generate 10 klip maks 90 menit → lewat = rakit dengan klip yang jadi + gambar untuk sisanya. 1 klip bermasalah jangan korbankan video. **HEMAT TOKEN KLIP (WAJIB):** 10 klip HARUS di-generate BERURUTAN oleh SATU agen — DILARANG spawn 1 subagent per klip (terukur: 1 subagent/klip membakar ~2 juta token karena mewarisi seluruh konteks). Panggil media.generate_video langsung 10x berurutan; kerjakan tahap klip SEAWAL MUNGKIN setelah naskah jadi, saat konteks masih kecil.

**SHORTS (3/hari):** potong 3 peristiwa paling seram 30-60 detik, vertikal 9:16. Judul: "[hook peristiwa] | Lima Misteri #shorts #misteri #penampakan". Deskripsi: link long video (tanpa hashtag).

**AFILIASI:** 1-2 produk dari ~/workspace/blog-otomatis/share_promo.py (rotasi harian) di deskripsi long + tiap shorts.

**HASHTAG long:** #misteri #penampakan #kejadiananeh #indonesia + 2 spesifik.

**LANGKAH:**
1. 5 peristiwa dari pool → cek riwayat → script/YYYY-MM-DD.txt per beat (1-2 kalimat = 1 beat + prompt gambar), selipkan komentar narator tiap peristiwa.
2. Voiceover per beat (tts --language id --voice avocado_v2:mudiwa), gabung; jeda dramatis di peristiwa terseram.
3. 70-80 gambar media.generate_image (storybook misterius, 1/beat). Kurangi 10 gambar untuk 10 beat klip; generate 10 klip video AI via media.generate_video sesuai section KLIP VIDEO AI.
4. Rakit pakai rakit_light.py (BUKAN rakit_video.py — hindari OOM); text overlay momen kunci. Sisipkan 10 klip video di beat yang sesuai menggantikan gambar.
5. Potong 3 shorts (ffmpeg crop vertikal).
6. Thumbnail: bikin_thumbnail.py (≤4 kata).
7. Kemarin LONG (atau file tak ada) → upload LONG saja ke @LimaMisteri (CEK channel!) + AI disclosure + judul/deskripsi (afiliasi) + hashtag + thumbnail, "Terjadwal" BESOK 19:00. Tulis "long:YYYY-MM-DD".
8. Kemarin SHORTS → upload 3 SHORTS (produksi KEMARIN) + AI disclosure + judul (+ 3 hashtag akhir) + deskripsi (tanpa hashtag), "Terjadwal" BESOK 19:00. Tulis "shorts:YYYY-MM-DD".
9. Upload = approval user ("menunggu persetujuan").
10. Catat 5 peristiwa ke riwayat-misteri.json. Laporkan: yang diupload (long/shorts) + URL + status.

Workspace: ~/workspace/lima-misteri/
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md
