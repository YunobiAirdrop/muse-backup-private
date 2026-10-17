Produksi & upload 1 video POV sejarah/hari ke "Yunobi BerCERITA RAKYAT +62" (@ceritarakyat862, khususstokyunobi@gmail.com). WAJIB CEK channel aktif = @ceritarakyat862 di YouTube Studio SEBELUM upload.

**VIRAL:** baca ~/workspace/youtube-otomatis/protokol-viral.md (trend jacking khusus niche, hook 3 detik, double-down >10x, packaging, retensi). Anti full-AI: ~/AGENTS.md (cerita orisinal, pacing variatif, SFX sinkron, AI disclosure dicentang). SHORTS: hashtag maks 3 di AKHIR JUDUL (contoh: "... #shorts #pov #sejarah"), BUKAN di deskripsi. Long: hashtag di deskripsi.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**JADWAL:** tayang BESOK 19:00 WIB (prime time ID). Produksi 16:11. Upload ~20:00-22:00 → ketukan persetujuan 20:00-22:00, set "Terjadwal" BESOK 19:00 WIB.

**TOPIK:** tiap hari BEDA. Pool ~/workspace/youtube-otomatis/pool-topik.md, cek riwayat-topik.json, Nusantara ↔ Dunia, catat setelah produksi.

**HOOK:** 30 detik pertama = momen paling dramatis. Judul curiosity gap (tanpa janji garansi). Thumbnail ≤4 kata.

**AI DISCLOSURE:** WAJIB centang "Altered content" tiap upload (long + shorts).

**SENTUHAN MANUSIA:** naskah WAJIB 2-3 kalimat opini pribadi narator ("jujur, bagian ini yang bikin saya merinding..." / "kalau menurut saya..."). Bahasa conversational, bukan artikel dibacain. Struktur variatif (kadang mulai tengah/pertanyaan). Pacing variatif (lambat bangun suasana, cepat saat aksi). Text overlay 3-5 momen kunci. Judul/deskripsi personal; deskripsi + 1-2 kalimat opini.

**VOICEOVER:** Bahasa Indonesia fasih & natural, JANGAN dubbing, JANGAN logat Inggris. Voice: avocado_v2:mudiwa.

**POLA UPLOAD (belum verifikasi HP → batas harian):** selang-seling: hari ini 1 LONG saja, besok 3 SHORTS saja, dst. Cek upload-terakhir.txt. JANGAN long+shorts sehari. Kena batas → upload yang bisa, sisanya besok.

**LONG (9-10 mnt, ~1000-1200 kata, POV orang pertama dramatis):** 85-90 gambar storybook 2D semi-kartun 16:9 (BUKAN photorealistic), palet earthy muted, karakter konsisten. Pacing: 1 gambar/6-7 detik per beat (1-2 kalimat), sinkron narasi. Hard cut (tanpa fade). Ken Burns lambat ±5-15%. Twist tiap 2-3 menit. Sesekali panel komik/split-screen.

**KLIP VIDEO AI (hibrida — 10 klip/video):** selain gambar, generate 10 klip video AI via media.generate_video untuk 10 beat PALING PENTING: beat 1 (hook, 3 detik pertama — WAJIB klip) + 9 twist/reveal/momen kunci lain. Tiap klip 5-10 detik, 16:9, gaya storybook 2D semi-kartun, palet earthy muted. 10 klip ini MENGGANTIKAN gambar di beat tersebut (total visual tetap ~70-80). Wajah/karakter harus konsisten dengan gambar — jika hasil morphing/aneh, BUANG klipnya dan pakai gambar biasa di beat itu. Shorts tetap dipotong dari video jadi.

**ANTI-MACET KLIP:** generate maks 2x percobaan per klip → gagal = pakai gambar biasa untuk beat itu. Total waktu generate 10 klip maks 90 menit → lewat = rakit dengan klip yang jadi + gambar untuk sisanya. 1 klip bermasalah jangan korbankan video. **HEMAT TOKEN KLIP (WAJIB):** 10 klip HARUS di-generate BERURUTAN oleh SATU agen — DILARANG spawn 1 subagent per klip (terukur: 1 subagent/klip membakar ~2 juta token karena mewarisi seluruh konteks). Panggil media.generate_video langsung 10x berurutan; kerjakan tahap klip SEAWAL MUNGKIN setelah naskah jadi, saat konteks masih kecil.

**SHORTS (3/hari):** potong 3 klip terbaik 30-60 detik (paling menegangkan), vertikal 9:16 (crop tengah). Judul: "[hook momen] | [judul long] #shorts #pov #sejarah". Deskripsi: "Tonton versi lengkapnya di sini: [URL]" + 1 produk afiliasi (TANPA hashtag). Tag: keyword relevan.

**AFILIASI:** 3 produk dari ~/workspace/blog-otomatis/share_promo.py (rotasi, jangan ulang 7 hari). Deskripsi long bagian "🛒 Produk Rekomendasi:"; 1 produk/short. Format: "🛒 [Nama] - Rp[harga]: [link]".

**OTOMATIS:** judul + deskripsi (sinopsis + subscribe + daftar isi + afiliasi) + hashtag (#pov #sejarah #kisahsejarah #indonesia + 2 spesifik) + thumbnail (bikin_thumbnail.py).

**LANGKAH:**
1. Topik → script/YYYY-MM-DD.txt per beat (1-2 kalimat = 1 beat + prompt gambar), selipkan opini narator.
2. Voiceover per beat (tts --language id --voice avocado_v2:mudiwa), gabung; jeda 0.5-1 detik sebelum twist.
3. 85-90 gambar media.generate_image (storybook semi-kartun, 1/beat). Kurangi 10 gambar untuk 10 beat klip; generate 10 klip video AI via media.generate_video sesuai section KLIP VIDEO AI.
4. Rakit video/YYYY-MM-DD.mp4; text overlay 3-5 momen; pacing variatif. Sisipkan 10 klip video di beat yang sesuai menggantikan gambar.
5. Potong 3 shorts: ffmpeg -ss [detik] -t 45 -vf "crop=ih*9/16:ih".
6. Thumbnail otomatis.
7. Kemarin LONG (atau file tak ada) → upload LONG saja ke @ceritarakyat862 (CEK channel!) + AI disclosure + judul/deskripsi (afiliasi + opini) + hashtag + thumbnail, "Terjadwal" BESOK 19:00. Tulis "long:YYYY-MM-DD".
8. Kemarin SHORTS → upload 3 SHORTS (produksi KEMARIN) + AI disclosure + judul (+ 3 hashtag akhir) + deskripsi (link long + 1 afiliasi, tanpa hashtag) + tag, "Terjadwal" BESOK 19:00. Tulis "shorts:YYYY-MM-DD".
9. Upload = approval user ("menunggu persetujuan", ketuk 20:00-22:00).
10. Laporkan: yang diupload (long/shorts) + status + topik ke riwayat.

Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md
