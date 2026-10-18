---
id: youtube-pov-harian
title: Video POV YouTube harian
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 15:15:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Produksi & upload 1 video POV sejarah/hari ke "Yunobi BerCERITA RAKYAT +62" (@ceritarakyat862, khususstokyunobi@gmail.com). WAJIB CEK channel aktif = @ceritarakyat862 di YouTube Studio SEBELUM upload.

**VIRAL:** baca ~/workspace/youtube-otomatis/protokol-viral.md (trend jacking khusus niche, hook 3 detik, double-down >10x, packaging, retensi). SHORTS: hashtag maks 4 di AKHIR JUDUL, ditutup #foryou (contoh: "... #shorts #pov #sejarah #foryou"), BUKAN di deskripsi. Long: hashtag di deskripsi, WAJIB termasuk #foryou.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**JADWAL:** tayang BESOK 19:00 WIB (prime time ID). Produksi 16:11. Upload ~20:00-22:00 → ketukan persetujuan 20:00-22:00, set "Terjadwal" BESOK 19:00 WIB.

**TOPIK:** tiap hari BEDA. Pool ~/workspace/youtube-otomatis/pool-topik.md, cek riwayat-topik.json, Nusantara ↔ Dunia, catat setelah produksi.

**HOOK (FORMULA BARU 2026-10-09 — data retensi: penonton kabur dalam 5 detik):**
- COLD OPEN WAJIB: kalimat pertama naskah = momen paling tegang/konflik, TANPA pemanasan ("Bayangin..." / "Pada tahun..." DILARANG sebagai pembuka). Contoh pola: "Tanganku gemetar. Di depan, 300 prajurit mengangkat tombak." — langsung adegan, langsung bahaya.
- 10 detik pertama: SATU gambar paling dramatis + SFX paling keras. Jangan ada jeda hening di awal.
- Kalimat 2-3: pertanyaan yang bikin penonton TAKUT ketinggalan jawaban ("...dan aku cuma punya satu pilihan.").
- Judul: pola emosional seperti channel yang rame — "[momen syok]! | [konteks]" (contoh: "Tanganku Gemetar... 300 Tombak Mengarah ke Aku! | POV Prajurit Majapahit"). DILARANG judul datar/deskriptif.
- Thumbnail: ≤4 kata, EKSPRESI WAJAH karakter ketakutan/kaget (close-up), bukan pemandangan.

**AI DISCLOSURE:** WAJIB centang "Altered content" tiap upload (long + shorts).

**SENTUHAN MANUSIA:** naskah WAJIB 2-3 kalimat opini pribadi narator ("jujur, bagian ini yang bikin saya merinding..." / "kalau menurut saya..."). Bahasa conversational, bukan artikel dibacain. Struktur variatif (kadang mulai tengah/pertanyaan). Pacing variatif (lambat bangun suasana, cepat saat aksi). Text overlay 3-5 momen kunci. Judul/deskripsi personal; deskripsi + 1-2 kalimat opini.

**VOICEOVER:** Bahasa Indonesia fasih & natural, JANGAN dubbing, JANGAN logat Inggris. Voice: avocado_v2:mudiwa.

**POLA UPLOAD (belum verifikasi HP → batas harian):** selang-seling: hari ini 1 LONG saja, besok 3 SHORTS saja, dst. Cek upload-terakhir.txt. JANGAN long+shorts sehari. Kena batas → upload yang bisa, sisanya besok.

**LONG (9-10 mnt, ~1000-1200 kata, POV orang pertama dramatis):** 85-90 gambar storybook 2D semi-kartun 16:9 (BUKAN photorealistic), palet earthy muted, karakter konsisten. Pacing: 1 gambar/6-7 detik per beat (1-2 kalimat), sinkron narasi. Hard cut (tanpa fade). Ken Burns lambat ±5-15%. Twist tiap 2-3 menit. Sesekali panel komik/split-screen.

**SHORTS (3/hari):** potong 3 klip terbaik 30-60 detik (paling menegangkan), vertikal 9:16 (crop tengah). Judul: "[hook momen] | [judul long] #shorts #pov #sejarah #foryou". Deskripsi: "Tonton versi lengkapnya di sini: [URL]" + 1 produk afiliasi (TANPA hashtag). Tag: keyword relevan.

**AFILIASI:** 3 produk dari ~/workspace/blog-otomatis/share_promo.py (rotasi, jangan ulang 7 hari). Deskripsi long bagian "🛒 Produk Rekomendasi:"; 1 produk/short. Format: "🛒 [Nama] - Rp[harga]: [link]".

**OTOMATIS:** judul + deskripsi (sinopsis + subscribe + daftar isi + afiliasi) + hashtag (#pov #sejarah #kisahsejarah #indonesia #foryou + 2 spesifik) + thumbnail (bikin_thumbnail.py).

**LANGKAH:**
1. Topik → script/YYYY-MM-DD.txt per beat (1-2 kalimat = 1 beat + prompt gambar), selipkan opini narator.
2. Voiceover per beat (tts --language id --voice avocado_v2:mudiwa), gabung; jeda 0.5-1 detik sebelum twist.
3. 85-90 gambar media.generate_image (storybook semi-kartun, 1/beat).
4. Rakit video/YYYY-MM-DD.mp4; text overlay 3-5 momen; pacing variatif.
5. Potong 3 shorts: ffmpeg -ss [detik] -t 45 -vf "crop=ih*9/16:ih".
6. Thumbnail otomatis.
7. Kemarin LONG (atau file tak ada) → upload LONG saja ke @ceritarakyat862 (CEK channel!) + AI disclosure + judul/deskripsi (afiliasi + opini) + hashtag (termasuk #foryou) + thumbnail, "Terjadwal" BESOK 19:00. Tulis "long:YYYY-MM-DD".
8. Kemarin SHORTS → upload 3 SHORTS (produksi KEMARIN) + AI disclosure + judul (+ hashtag akhir ditutup #foryou) + deskripsi (link long + 1 afiliasi, tanpa hashtag) + tag, "Terjadwal" BESOK 19:00. Tulis "shorts:YYYY-MM-DD".
9. Upload = approval user ("menunggu persetujuan", ketuk 20:00-22:00).
10. Laporkan: yang diupload (long/shorts) + status + topik ke riwayat.

Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** video yang SUDAH diproduksi WAJIB tayang — tidak boleh hilang/mogok diam-diam.
- Upload GAGAL karena "Batas upload harian telah tercapai" (atau pesan limit harian YouTube lain): JANGAN retry saat itu juga (limit ±24 jam — pasti gagal lagi). WAJIB: (1) tulis file instruksi upload lengkap (judul, deskripsi, hashtag, thumbnail, AI disclosure, slot jadwal target) seperti biasa; (2) tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/{channel}-YYYY-MM-DD.json dengan format {"channel":"...","video_path":"<absolut>","instruksi_path":"<absolut>","slot_target":"YYYY-MM-DD HH:MM WIB","gagal_pada":"YYYY-MM-DDTHH:MM:SS+07:00","sebab":"..."} — contoh lengkap di ~/workspace/youtube-otomatis/retry-queue/README.md. Watchdog harian otomatis mengerjakan antrean ini. Catat di laporan run: video apa yang gagal + path antreannya.
- Upload GAGAL karena sebab LAIN (bukan limit harian): perbaiki dan retry SEGERA saat itu juga (preferensi user), jangan tunda besok.
