---
id: kisahalkitab-harian
title: Kisah Alkitab — produksi & upload harian
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 16:11:00
timeout_secs: 86400
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Produksi & upload 1 video KISAH ALKITAB/hari ke "Kisah Alkitab" (@KisahAlkitab-k9j, khususstokyunobi@gmail.com). WAJIB CEK channel aktif benar di YouTube Studio SEBELUM upload.

**ATURAN AKURASI AGAMA (PALING PENTING — pelanggaran = video dihapus & channel diperbaiki):**
- Naskah HANYA dari kisah Alkitab yang diakui bersama: Perjanjian Lama & Perjanjian Baru. Cantumkan referensi kitab:pasal (mis. Kejadian 37, Lukas 15).
- DILARANG KERAS mengarang isi Alkitab. DILARANG membahas perbedaan doktrin antar denominasi (Protestan/Katolik/Ortodoks). DILARANG menafsirkan doktrin kontroversial — ceritakan kisahnya, ambil hikmah moralnya.
- Jika ragu soal akurasi sebuah kisah → SKIP, pilih kisah lain dari pool.
- Nada: menghormati, mendidik, menginspirasi. Bukan menggurui.

**VISUAL: KLIP VIDEO ASLI (bukan gambar AI).** Download footage stok bebas lisensi dari pexels.com via browser (pipeline seperti Strange Tales). Keyword: church, bible, candle light, jerusalem, sunrise desert, olive tree. Klip HARUS takzim & hormat: rumah ibadah, lilin, alam, cahaya. DILARANG memakai gambar/video AI yang menggambarkan tokoh suci secara tidak hormat.

**VIRAL:** baca ~/workspace/youtube-otomatis/protokol-viral.md (trend jacking khusus niche, hook 3 detik, double-down >10x, packaging, retensi). Anti full-AI: ~/AGENTS.md. SHORTS: hashtag maks 4 di AKHIR JUDUL, ditutup #foryou (contoh: "... #shorts #alkitab #rohani #foryou"), BUKAN di deskripsi. Long: hashtag di deskripsi, WAJIB termasuk #foryou.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**JADWAL:** tayang BESOK 19:00 WIB (prime time ID). Produksi 16:11. Upload ~20:00-22:00 → ketukan persetujuan 20:00-22:00, set "Terjadwal" BESOK 19:00 WIB.

**KISAH:** tiap hari BEDA. Pool ~/workspace/kisah-alkitab/pool-kisah.md, cek ~/workspace/kisah-alkitab/riwayat-kisah.json (anti-ulang 90 hari), catat setelah produksi.

**AI DISCLOSURE:** WAJIB centang "Altered content" tiap upload (long + shorts).

**SENTUHAN MANUSIA:** naskah WAJIB 2-3 kalimat kekaguman/refleksi pribadi narator ("yang membuat saya takjub..." / "pelajaran yang saya ambil..."). Storytelling hangat dan menghormati. Struktur variatif (tidak selalu kronologis). Text overlay 3-5 momen kunci (nama tokoh, referensi kitab, kutipan). Judul/deskripsi personal.

**VOICEOVER:** Bahasa Indonesia fasih & natural, JANGAN dubbing. Voice: avocado_v2:mudiwa (tts --language id --voice avocado_v2:mudiwa).

**POLA UPLOAD (belum verifikasi HP → batas harian):** selang-seling: hari ini 1 LONG saja, besok 3 SHORTS saja, dst. Cek upload-terakhir.txt. JANGAN long+shorts sehari. Kena batas (termasuk batas 24 jam channel baru) → upload yang bisa, sisanya besok.

**LONG (9-10 mnt, ~1000-1200 kata ID):** 18-24 klip HD 16:9 landscape (tiap klip 20-40 detik), disambung mengikuti alur beat naskah — klip bersifat suasana/takzim, bukan ilustrasi literal tiap kalimat. Voiceover TTS Indonesia (mudiwa). Thumbnail: frame terbaik + teks ≤4 kata.

**SHORTS (3/hari):** potong 3 segmen terbaik 30-60 detik dari LONG, vertikal 9:16 (crop tengah). Judul hook + hashtag di AKHIR JUDUL ditutup #foryou (#shorts #alkitab #rohani #foryou).

**ANTI-MACET:** download Pexels maks 2x/klip → gagal = keyword cadangan atau pakai klip yang sudah ada (1 klip boleh dipakai maks 2x dalam 1 video, urutan beda). Total download maks 60 menit → lewat = rakit dengan klip yang ada.

**JALUR UPLOAD (perbaikan 2026-10-12 malam, perintah user "kalo mau login bilang dulu"):** upload WAJIB via API memakai yt-growth (slug kisahalkitab, token OAuth per channel sudah aktif) — BUKAN browser Studio. Upload browser channel ini berulang kali memicu verifikasi 2 langkah Google ke HP user tanpa pemberitahuan (kejadian 12 Okt malam: dua prompt beruntun). Browser hanya dipakai SETELAH video terupload via API, untuk centang AI disclosure di Studio memakai sesi yang sudah login. JANGAN PERNAH memicu login/verifikasi Google baru dari cron ini — bila sesi mati total, STOP dan laporkan ke agen induk; login ulang hanya boleh setelah user diberi tahu & menyetujui di chat. Sebelum upload via API, cek daftar upload channel dulu — bila judul yang sama sudah ada, JANGAN upload dobel.

**LANGKAH:**
1. Kisah dari pool → cek riwayat → script per beat (~1000-1200 kata), selipkan 2-3 kalimat refleksi narator; cantumkan referensi kitab di catatan produksi.
2. Voiceover per beat (mudiwa), gabung.
3. Download 18-24 klip Pexels via browser (HD 16:9, keyword di atas, relevan & takzim); verifikasi 1 frame/klip (tidak rusak, tidak ada watermark).
4. Rakit via ~/workspace/youtube-otomatis/ffmpeg-queue.sh (JANGAN ffmpeg langsung): sambung klip + voiceover, text overlay 3-5 momen kunci; potong 3 shorts vertikal; thumbnail dari frame terbaik + teks.
5. Kemarin LONG (atau file tak ada) → upload LONG saja ke @KisahAlkitab-k9j via API (lihat JALUR UPLOAD) + judul/deskripsi + hashtag (termasuk #foryou) + thumbnail (bila API menolak, catat saja), private TERJADWAL BESOK 19:00 WIB (publishAt). Tulis "long:YYYY-MM-DD". AI disclosure dicentang menyusul via Studio.
6. Kemarin SHORTS → upload 3 SHORTS (produksi KEMARIN) via API + judul (+ hashtag akhir ditutup #foryou) + deskripsi (tanpa hashtag), private TERJADWAL BESOK 19:00 WIB. Tulis "shorts:YYYY-MM-DD". AI disclosure dicentang menyusul via Studio.
7. Upload via API tidak butuh ketukan persetujuan browser; laporkan hasil + videoId.
8. Catat kisah ke riwayat-kisah.json. Laporkan: yang diupload (long/shorts) + URL + status.

Workspace: ~/workspace/kisah-alkitab/
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** video yang SUDAH diproduksi WAJIB tayang — tidak boleh hilang/mogok diam-diam.
- Upload GAGAL karena "Batas upload harian telah tercapai" (atau pesan limit harian YouTube lain): JANGAN retry saat itu juga (limit ±24 jam — pasti gagal lagi). WAJIB: (1) tulis file instruksi upload lengkap (judul, deskripsi, hashtag, thumbnail, AI disclosure, slot jadwal target) seperti biasa; (2) tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/{channel}-YYYY-MM-DD.json dengan format {"channel":"...","video_path":"<absolut>","instruksi_path":"<absolut>","slot_target":"YYYY-MM-DD HH:MM WIB","gagal_pada":"YYYY-MM-DDTHH:MM:SS+07:00","sebab":"..."} — contoh lengkap di ~/workspace/youtube-otomatis/retry-queue/README.md. Watchdog harian otomatis mengerjakan antrean ini. Catat di laporan run: video apa yang gagal + path antreannya.
- Upload GAGAL karena sebab LAIN (bukan limit harian): perbaiki dan retry SEGERA saat itu juga (preferensi user), jangan tunda besok.
