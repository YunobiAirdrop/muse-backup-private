---
id: lima-misteri-harian
title: Lima Misteri YouTube harian
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 12:00:00
timeout_secs: 7200
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":4,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"ACBF9FC9B0A2114372EC6DB0C4D1761C","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Produksi & upload 1 video "5 KEJADIAN ANEH/MISTERI"/hari ke "Lima Misteri" (@LimaMisteri, khususstokyunobi@gmail.com). Channel ID: UCQ0vHTsTqVeYy3zLno6pVfQ. WAJIB CEK channel aktif benar di YouTube Studio SEBELUM upload.

**VIRAL:** baca ~/workspace/youtube-otomatis/protokol-viral.md (trend jacking khusus niche, hook 3 detik, double-down >10x, packaging, retensi). Anti full-AI: ~/AGENTS.md (cerita orisinal, pacing variatif, SFX sinkron, AI disclosure dicentang). SHORTS: hashtag di AKHIR JUDUL, ditutup #foryou (contoh: "... #shorts #misteri #penampakan #foryou"), BUKAN di deskripsi. Long: hashtag di deskripsi, WAJIB termasuk #foryou.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**KONSEP:** countdown 5 kejadian aneh/misterius/penampakan dunia. Tiap peristiwa: lokasi + deskripsi + unsur misterinya ("Nomor 1. Di [lokasi]..."). Akhir: ajakan subscribe.

**JADWAL:** tayang BESOK 19:00 WIB (prime time ID). Produksi 12:00. Upload ~20:00-22:00 → ketukan persetujuan 20:00-22:00, set "Terjadwal" BESOK 19:00 WIB.

**PERISTIWA:** tiap hari 5 BERBEDA. Pool ~/workspace/lima-misteri/pool-misteri.md, cek riwayat-misteri.json (anti-ulang 60 hari). Variasi: penampakan hantu ↔ UFO/fenomena langit ↔ kejadian aneh alam ↔ misteri tempat ↔ legenda urban.

**ORISINALITAS (aturan user 2026-10-05):** SEMUA visual HARUS ilustrasi AI orisinal. JANGAN pakai footage/foto asli dari internet (risiko copyright). Peristiwa nyata diilustrasikan ulang dengan gambar AI.

**AI DISCLOSURE:** WAJIB centang "Altered content" tiap upload (long + shorts).

**VOICEOVER:** Bahasa Indonesia fasih & natural, JANGAN logat Inggris. Voice: avocado_v2:mudiwa.

**SENTUHAN MANUSIA:** naskah WAJIB komentar pribadi narator tiap peristiwa (1-2 kalimat, misal "yang nomor 3 ini... jujur saya merinding" / "kalau kalian jadi saksinya, berani nggak?"). Bahasa conversational ("bayangin kalau kamu yang lihat..."). Urutan variatif (acak / paling seram dulu). Pacing variatif (peristiwa terseram porsi lebih lama + jeda dramatis). Text overlay momen kunci tiap peristiwa. Judul/deskripsi personal.

**POLA UPLOAD (channel SUDAH verifikasi HP 2026-10-11; keputusan user 2026-10-12):** TIAP HARI upload 1 LONG + 3 SHORTS sekaligus (semua dari produksi hari ini), semua "Terjadwal" BESOK 19:00 WIB. TIDAK ada lagi pola selang-seling. Kena batas → yang gagal masuk antrean retry (aturan anti-mogok di bawah).

**LONG (9-10 mnt, ~1000-1200 kata ID):** struktur: intro hook 30 detik → 5 peristiwa (~1,5-2 mnt tiap) → outro + CTA subscribe. 70-80 gambar storybook 2D misterius 16:9 (BUKAN photorealistic). Pacing: 1 gambar/6-7 detik, sinkron narasi. Hard cut. Ken Burns lambat.

**SHORTS (3/hari):** potong 3 peristiwa paling seram 30-60 detik, vertikal 9:16. Judul: "[hook peristiwa] | Lima Misteri #shorts #misteri #penampakan #foryou". Deskripsi: link long video (tanpa hashtag).

**AFILIASI:** 1-2 produk dari ~/workspace/blog-otomatis/share_promo.py (rotasi harian) di deskripsi long + tiap shorts.

**HASHTAG long:** #misteri #penampakan #kejadiananeh #indonesia #foryou + 2 spesifik.

**JALUR UPLOAD (perbaikan 2026-10-12 malam, perintah user "kalo mau login bilang dulu"):** upload WAJIB via API memakai yt-growth (slug lima-misteri, token OAuth per channel sudah aktif) — BUKAN browser Studio. Upload browser channel ini memicu verifikasi 2 langkah Google ke HP user tanpa pemberitahuan (kejadian 12 Okt malam). Browser hanya dipakai SETELAH video terupload via API, untuk centang AI disclosure di Studio memakai sesi yang sudah login. JANGAN PERNAH memicu login/verifikasi Google baru dari cron ini — bila sesi mati total, STOP dan laporkan ke agen induk. Sebelum upload via API, cek daftar upload channel dulu — bila judul yang sama sudah ada, JANGAN upload dobel.

**ANTI-TIMEOUT / RESUME (perbaikan 2026-10-19):** Pipeline ini panjang (70-80 gambar AI + render). WAJIB ikuti protokol checkpoint:
1. PRE-FLIGHT: sebelum produksi, cek upload-terakhir.txt — bila sudah berisi tanggal HARI INI, verifikasi via API bahwa 4 video (1 long + 3 shorts) benar ada di channel. Bila ya → SKIP produksi, laporkan "sudah tayang", selesai.
2. RESUME: cek file parsial hari ini (script/YYYY-MM-DD.txt, audio/YYYY-MM-DD.mp3, gambar/YYYY-MM-DD/beat-*.webp). Yang SUDAH ADA jangan dibuat ulang — lanjutkan dari yang kurang.
3. Setelah tiap tahap besar selesai (script, audio, gambar, rakit, upload), tulis checkpoint ke ~/workspace/lima-misteri/checkpoint-YYYY-MM-DD.txt.
4. Upload SEGERA setelah video jadi — jangan tunda sampai semua shorts selesai.

**LANGKAH:**
1. PRE-FLIGHT check (lihat ANTI-TIMEOUT di atas).
2. 5 peristiwa dari pool → cek riwayat → script/YYYY-MM-DD.txt per beat (1-2 kalimat = 1 beat + prompt gambar), selipkan komentar narator tiap peristiwa.
3. Voiceover per beat (tts --language id --voice avocado_v2:mudiwa), gabung; jeda dramatis di peristiwa terseram.
4. 70-80 gambar media.generate_image (storybook misterius, 1/beat).
5. Rakit pakai rakit_light.py (BUKAN rakit_video.py — hindari OOM); text overlay momen kunci.
6. Potong 3 shorts (ffmpeg crop vertikal).
7. Thumbnail: bikin_thumbnail.py (≤4 kata).
8. Upload SEMUA produksi hari ini via API (lihat JALUR UPLOAD): 1 LONG + 3 SHORTS ke @LimaMisteri + judul/deskripsi (afiliasi) + hashtag (long termasuk #foryou; shorts judul ditutup #foryou) + thumbnail, semua private TERJADWAL BESOK 19:00 WIB (publishAt). Tulis "long+shorts:YYYY-MM-DD" ke upload-terakhir.txt. AI disclosure dicentang menyusul via Studio.
9. Upload via API tidak butuh ketukan persetujuan browser; laporkan hasil + videoId.
10. Catat 5 peristiwa ke riwayat-misteri.json. Laporkan: yang diupload (long + shorts) + URL + status.

Workspace: ~/workspace/lima-misteri/
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** video yang SUDAH diproduksi WAJIB tayang — tidak boleh hilang/mogok diam-diam.
- Upload GAGAL karena "Batas upload harian telah tercapai" (atau pesan limit harian YouTube lain): JANGAN retry saat itu juga (limit ±24 jam — pasti gagal lagi). WAJIB: (1) tulis file instruksi upload lengkap (judul, deskripsi, hashtag, thumbnail, AI disclosure, slot jadwal target) seperti biasa; (2) tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/{channel}-YYYY-MM-DD.json dengan format {"channel":"...","video_path":"<absolut>","instruksi_path":"<absolut>","slot_target":"YYYY-MM-DD HH:MM WIB","gagal_pada":"YYYY-MM-DDTHH:MM:SS+07:00","sebab":"..."} — contoh lengkap di ~/workspace/youtube-otomatis/retry-queue/README.md. Watchdog harian otomatis mengerjakan antrean ini. Catat di laporan run: video apa yang gagal + path antreannya.
- Upload GAGAL karena sebab LAIN (bukan limit harian): perbaiki dan retry SEGERA saat itu juga (preferensi user), jangan tunda besok.
