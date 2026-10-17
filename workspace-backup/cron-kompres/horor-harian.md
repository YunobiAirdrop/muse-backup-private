Produksi & upload 1 video CERITA HOROR/hari ke "Kisah Horor" (@KisahPOV, khususstokyunobi@gmail.com). JANGAN upload ke @ceritarakyat862. WAJIB CEK channel aktif = "Kisah Horor" di YouTube Studio SEBELUM upload (pernah salah channel).

**VIRAL:** baca ~/workspace/youtube-otomatis/protokol-viral.md (trend jacking khusus niche, hook 3 detik, double-down >10x, packaging, retensi). Anti full-AI: ~/AGENTS.md (cerita orisinal, pacing variatif, SFX sinkron, AI disclosure dicentang). SHORTS: hashtag maks 3 di AKHIR JUDUL (contoh: "... #shorts #horor #ceritahoror"), BUKAN di deskripsi. Long: hashtag di deskripsi.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**JADWAL:** tayang BESOK 19:00 WIB (prime time ID). Produksi 16:11. Upload ~20:00-22:00 → ketukan persetujuan 20:00-22:00, set "Terjadwal" BESOK 19:00 WIB. Channel ini SUDAH verifikasi HP → video >15 menit & thumbnail kustom aktif.

**CERITA:** tiap hari BEDA TEMA. Pool ~/workspace/horor-otomatis/pool-cerita.md, cek riwayat-cerita.json (anti-ulang 60 hari), gonta-ganti: hantu lokal ↔ urban legend ↔ misteri/tempat angker ↔ legenda. Catat setelah produksi.

**HOOK:** 30 detik pertama = momen paling mencekam. Judul curiosity gap (tanpa janji garansi FYP/views). Thumbnail ≤4 kata, gaya horor gelap.

**AI DISCLOSURE:** WAJIB centang "Altered content" tiap upload (long + shorts).

**SENTUHAN MANUSIA:** naskah WAJIB 2-3 kalimat opini pribadi narator ("jujur, bagian ini yang bikin saya merinding..." / "kalau menurut saya..."). Bahasa conversational kayak cerita horor ke teman. Struktur variatif (kadang mulai dari akhir/pertanyaan). Pacing variatif (lambat bangun suasana, cepat saat jumpscare). Text overlay 3-5 momen kunci. Judul/deskripsi personal.

**VOICEOVER:** Bahasa Indonesia fasih & natural, JANGAN dubbing, JANGAN logat Inggris. Voice: avocado_v2:mudiwa.

**POLA UPLOAD (belum verifikasi HP → batas harian):** selang-seling: hari ini 1 LONG saja, besok 3 SHORTS saja, dst. Cek upload-terakhir.txt. JANGAN long+shorts sehari. Kena batas → upload yang bisa, sisanya besok.

**LONG (9-10 mnt, ~1000-1200 kata, POV orang pertama/kedua mencekam):** 70-80 gambar storybook 2D GELAP/misterius 16:9 (BUKAN photorealistic), palet gelap, karakter konsisten. Pacing: 1 gambar/6-7 detik per beat (1-2 kalimat), sinkron narasi. Hard cut (tanpa fade). Ken Burns lambat & halus. Twist/kejutan tiap 2-3 menit.

**SHORTS (3/hari):** potong 3 klip termencekam 30-60 detik, vertikal 9:16. Judul: "[hook momen] | [judul video] #shorts #horor #ceritahoror". Deskripsi: "Tonton versi lengkapnya di sini: [URL]" + 1 produk afiliasi (TANPA hashtag). Tag: keyword relevan.

**AFILIASI:** 1-2 produk dari ~/workspace/blog-otomatis/share_promo.py (rotasi, jangan ulang 7 hari). Deskripsi bagian "Rekomendasi:" + 1 produk/short. Format: "[Nama Produk] - Rp[harga]: [link]".

**OTOMATIS:** judul + deskripsi (sinopsis + subscribe + afiliasi) + hashtag (#horor #ceritahoror #misteri + 2 spesifik) + thumbnail (bikin_thumbnail.py).

**LANGKAH:**
1. Tema dari pool → cek riwayat → script/YYYY-MM-DD.txt per beat (1-2 kalimat = 1 beat + prompt gambar), selipkan opini narator.
2. Voiceover per beat (tts --language id --voice avocado_v2:mudiwa) → audio/YYYY-MM-DD.mp3; jeda dramatis sebelum twist.
3. 70-80 gambar media.generate_image (storybook gelap, 1/beat).
4. Rakit: rakit_video.py ~/workspace/horor-otomatis/gambar/YYYY-MM-DD/ audio/YYYY-MM-DD.mp3 video/YYYY-MM-DD.mp4; text overlay 3-5 momen.
5. Potong 3 shorts: ffmpeg -ss [detik] -t 45 -vf "crop=ih*9/16:ih" → shorts/YYYY-MM-DD-sN.mp4.
6. Thumbnail: bikin_thumbnail.py <gambar_termencekam> "<JUDUL_4_KATA>" thumbnail-YYYY-MM-DD.jpg.
7. Kemarin LONG (atau file tak ada) → upload LONG saja ke @KisahPOV (CEK channel!) + AI disclosure + judul/deskripsi (afiliasi) + hashtag + thumbnail, "Terjadwal" BESOK 19:00. Tulis "long:YYYY-MM-DD".
8. Kemarin SHORTS → upload 3 SHORTS (produksi KEMARIN) + AI disclosure + judul hook (+ 3 hashtag akhir) + deskripsi (link video + 1 afiliasi, tanpa hashtag) + tag, "Terjadwal" BESOK 19:00. Tulis "shorts:YYYY-MM-DD".
9. Upload = approval user ("menunggu persetujuan", ketuk 20:00-22:00).
10. Catat tema ke riwayat-cerita.json. Laporkan: yang diupload (long/shorts) + status.

Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** video yang SUDAH diproduksi WAJIB tayang — tidak boleh hilang/mogok diam-diam.
- Upload GAGAL karena "Batas upload harian telah tercapai" (atau pesan limit harian YouTube lain): JANGAN retry saat itu juga (limit ±24 jam — pasti gagal lagi). WAJIB: (1) tulis file instruksi upload lengkap (judul, deskripsi, hashtag, thumbnail, AI disclosure, slot jadwal target) seperti biasa; (2) tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/{channel}-YYYY-MM-DD.json dengan format {"channel":"...","video_path":"<absolut>","instruksi_path":"<absolut>","slot_target":"YYYY-MM-DD HH:MM WIB","gagal_pada":"YYYY-MM-DDTHH:MM:SS+07:00","sebab":"..."} — contoh lengkap di ~/workspace/youtube-otomatis/retry-queue/README.md. Watchdog harian otomatis mengerjakan antrean ini. Catat di laporan run: video apa yang gagal + path antreannya.
- Upload GAGAL karena sebab LAIN (bukan limit harian): perbaiki dan retry SEGERA saat itu juga (preferensi user), jangan tunda besok.
