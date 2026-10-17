Produksi & upload 1 video JEJAK BUDDHA/hari ke "Jejak Buddha" (@JejakBuddha, khususstokyunobi@gmail.com). WAJIB CEK channel aktif benar di YouTube Studio SEBELUM upload.

**ATURAN AKURASI AGAMA (PALING PENTING — pelanggaran = video dihapus & channel diperbaiki):**
- Naskah HANYA dari sumber yang jelas & masyhur: riwayat hidup Siddhartha Gautama, kisah-kisah Jataka yang populer, ajaran dasar yang umum (Empat Kebenaran Mulia, Jalan Mulia Berunsur Delapan).
- Ceritakan dengan TAKZIM dan menghormati. DILARANG mengarang kisah. DILARANG membahas perbedaan doktrin antar aliran (Theravada/Mahayana/dll).
- Jika ragu soal akurasi sebuah kisah → SKIP, pilih kisah lain dari pool.
- Nada: menghormati, mendidik, menginspirasi. Bukan menggurui.

**VIRAL:** baca ~/workspace/youtube-otomatis/protokol-viral.md (trend jacking khusus niche, hook 3 detik, double-down >10x, packaging, retensi). Anti full-AI: ~/AGENTS.md (cerita orisinal, pacing variatif, SFX sinkron, AI disclosure dicentang). SHORTS: hashtag maks 3 di AKHIR JUDUL (contoh: "... #shorts #buddha #kebijaksanaan"), BUKAN di deskripsi. Long: hashtag di deskripsi.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**JADWAL:** tayang BESOK 19:00 WIB (prime time ID). Produksi 16:11. Upload ~20:00-22:00 → ketukan persetujuan 20:00-22:00, set "Terjadwal" BESOK 19:00 WIB.

**KISAH:** tiap hari BEDA. Pool ~/workspace/jejak-buddha/pool-kisah.md, cek ~/workspace/jejak-buddha/riwayat-kisah.json (anti-ulang 90 hari), catat setelah produksi.

**AI DISCLOSURE:** WAJIB centang "Altered content" tiap upload (long + shorts).

**SENTUHAN MANUSIA:** naskah WAJIB 2-3 kalimat kekaguman/refleksi pribadi narator. Storytelling tenang, hangat, menghormati. Struktur variatif (tidak selalu kronologis). Text overlay 3-5 momen kunci (nama tokoh/tempat, kutipan ajaran). Judul/deskripsi personal.

**VOICEOVER:** Bahasa Indonesia fasih & natural, JANGAN dubbing. Voice: avocado_v2:mudiwa (tts --language id --voice avocado_v2:mudiwa).

**POLA UPLOAD (belum verifikasi HP → batas harian):** selang-seling: hari ini 1 LONG saja, besok 3 SHORTS saja, dst. Cek upload-terakhir.txt. JANGAN long+shorts sehari. Kena batas (termasuk batas 24 jam channel baru) → upload yang bisa, sisanya besok.

**LONG (9-10 mnt, ~1000-1200 kata ID):** 70-80 gambar storybook 2D 16:9 gaya tenang/zen (candi, hutan, pohon Bodhi). Penggambaran Buddha dengan takzim dan damai. Voiceover TTS Indonesia (mudiwa). Thumbnail ≤4 kata.

**SHORTS (3/hari):** 3 klip terbaik 30-60 detik, vertikal 9:16. Judul hook + 3 hashtag di AKHIR JUDUL (#shorts #buddha #kebijaksanaan).

**LANGKAH:**
1. Kisah dari pool → cek riwayat → script per beat (~1000-1200 kata), selipkan 2-3 kalimat refleksi narator.
2. Voiceover per beat (mudiwa), gabung.
3. 70-80 gambar media.generate_image (storybook tenang, penggambaran Buddha dengan takzim).
4. Rakit via ~/workspace/youtube-otomatis/ffmpeg-queue.sh (JANGAN ffmpeg langsung), potong 3 shorts, buat thumbnail; text overlay 3-5 momen kunci.
5. Kemarin LONG (atau file tak ada) → upload LONG saja ke @JejakBuddha (CEK channel!) + AI disclosure + judul/deskripsi + hashtag + thumbnail, "Terjadwal" BESOK 19:00. Tulis "long:YYYY-MM-DD".
6. Kemarin SHORTS → upload 3 SHORTS (produksi KEMARIN) + AI disclosure + judul (+ 3 hashtag akhir) + deskripsi (tanpa hashtag), "Terjadwal" BESOK 19:00. Tulis "shorts:YYYY-MM-DD".
7. Upload = approval user ("menunggu persetujuan", ketuk 20:00-22:00).
8. Catat kisah ke riwayat-kisah.json. Laporkan: yang diupload (long/shorts) + URL + status.

Workspace: ~/workspace/jejak-buddha/
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** video yang SUDAH diproduksi WAJIB tayang — tidak boleh hilang/mogok diam-diam.
- Upload GAGAL karena "Batas upload harian telah tercapai" (atau pesan limit harian YouTube lain): JANGAN retry saat itu juga (limit ±24 jam — pasti gagal lagi). WAJIB: (1) tulis file instruksi upload lengkap (judul, deskripsi, hashtag, thumbnail, AI disclosure, slot jadwal target) seperti biasa; (2) tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/{channel}-YYYY-MM-DD.json dengan format {"channel":"...","video_path":"<absolut>","instruksi_path":"<absolut>","slot_target":"YYYY-MM-DD HH:MM WIB","gagal_pada":"YYYY-MM-DDTHH:MM:SS+07:00","sebab":"..."} — contoh lengkap di ~/workspace/youtube-otomatis/retry-queue/README.md. Watchdog harian otomatis mengerjakan antrean ini. Catat di laporan run: video apa yang gagal + path antreannya.
- Upload GAGAL karena sebab LAIN (bukan limit harian): perbaiki dan retry SEGERA saat itu juga (preferensi user), jangan tunda besok.
