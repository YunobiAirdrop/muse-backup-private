# DRAFT cron harian — Fakta Bola Dunia (countryball animasi)

**Status:** DRAFT — BELUM TERDAFTAR. Daftarkan setelah user setuju: `cron.add` dengan id `fakta-bola-dunia-harian`, schedule daily 16:11 Asia/Jakarta, owner goal:kabarviral-automated-news-blog, delivery ke chat 7382e6cd-7263-4ede-983e-939bf507ecbf, timeout 10800.

Alasan: 19 channel lain punya cron produksi harian 16:11; channel ke-20 (Fakta Bola Dunia, ditambahkan 2026-10-15) belum punya — produksi hari ini hanya one-shot manual ("langsung eksekusi" 19:10 WIB). Tanpa cron ini channel baru berhenti setelah video pertama.

---

Produksi & upload 1 SHORTS/hari ke "Fakta Bola Dunia" (@FaktaBolaDuniaID, UCU9QUVkWqqjnEFtrj6QACDA). WAJIB CEK channel aktif benar SEBELUM upload.

**VIRAL & ANTI-AI (baca SEBELUM produksi):** ~/workspace/youtube-otomatis/protokol-viral.md + ~/AGENTS.md (bagian anti full-AI look) — ikuti semua. Trend jacking HANYA dalam niche countryball/fakta (dilarang ganti format). Double-down: video kemarin >10x rata-rata → angle sama hari ini. Hashtag (maks 4) di AKHIR JUDUL shorts, ditutup #foryou, bukan deskripsi.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file. ffmpeg WAJIB via ~/workspace/youtube-otomatis/ffmpeg-queue.sh.

**KONSEP (spec user 2026-10-15, tiru reel FB countryball):** countryball animasi ngobrol bergantian tentang FAKTA unik — mis. Indonesia + China + Jepang. **Indonesia WAJIB selalu muncul tiap video.** Tiap video: fakta BERBEDA + kombinasi negara BERBEDA (jangan ulang; catat ke ~/workspace/fakta-bola-dunia/riwayat-fakta.json).

**ATURAN KARAKTER (jangan dilanggar):**
- Semua karakter TETAP di layar sepanjang video — karakter baru muncul = yang lama TETAP, tidak boleh hilang.
- Tiap karakter SUARA BERBEDA, Bahasa Indonesia native (contoh terbukti: avocado_v2:mudiwa pitch 1.0x / 0.90x / 1.10x). DILARANG aksen Inggris.
- Animasi mulut: sprite open/closed per karakter (work/ball-*-open.png, ball-*-closed.png), lip-sync ke audio; background animasi orisinal (lihat work/gamebg.py — JANGAN pakai klip stok untuk channel ini).
- CTA: di TENGAH (~60% durasi: tombol LIKE + Subscribe + teks + voiceover) DAN di AKHIR, verbal + visual.

**SANITASI TTS (wajib):** DILARANG awali/sisipi teks TTS dengan label ("Narrator:", "Host:", dsb). Setiap teks WAJIB lewat `bersihkan_teks_tts()` dari ~/workspace/youtube-otomatis/tts_sanitize.py dan lolos `validasi_teks_tts()`.

**FORMAT:** vertical 1080x1920 30fps, 25-70 dtk; naskah conversational Indonesia ±90-150 kata (angka dieja); AI disclosure DICENTANG saat upload; "not for kids". Judul = hook + hashtag di akhir ditutup #foryou (cth: "3 Angka Paling Seram di Dunia! 😱 #shorts #fakta #countryball #foryou").

**PIPELINE (sudah terbukti jalan 2026-10-15):** ~/workspace/fakta-bola-dunia/work/ — draw_balls.py (sprite), rakit.py / render_p10.py (assembly; baca notes iterasi di output/angka-seram-part10.json SEBELUM ubah). Assert |durasi video − durasi audio| kecil sebelum final; tulis ke TEMP dulu, verifikasi ffprobe, baru move.

**JADWAL TAYANG:** upload + approval user 20:00-23:00 WIB; slot tayang 19:00 WIB (bisa diubah user).

**ANTI-REBUILD (aturan user):** topik yang SUDAH dibuild DILARANG dipilih lagi — cek riwayat-fakta.json + daftar video channel sebelum produksi.

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** video yang SUDAH diproduksi WAJIB tayang.
- Upload via API yt-growth DULU (token Production aktif). Browser hanya untuk centang disclosure bila perlu. (Catatan: broker upload browser down sejak 22:12 WIB 2026-10-15 — kalau masih down, pakai API saja.)
- GAGAL karena limit harian: tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/fakta-bola-dunia-YYYY-MM-DD.json (format lihat retry-queue/README.md); watchdog mengerjakan otomatis.
- GAGAL sebab lain: perbaiki + retry SEGERA.

Langkah: 1) pilih fakta + kombinasi negara (cek riwayat). 2) naskah dialog multi-karakter + CTA tengah/akhir. 3) TTS per karakter (voice beda) + sanitasi. 4) render sprite + lip-sync + background (pipeline work/). 5) verifikasi durasi + tonton 1x. 6) upload ke @FaktaBolaDuniaID (CEK channel!) — tunggu approval user 20:00-23:00. 7) catat riwayat + lapor judul + URL + status.

Workspace: ~/workspace/fakta-bola-dunia/ | Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md
