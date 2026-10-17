---
id: fakta-bola-dunia-harian
title: Fakta Bola Dunia harian (countryball shorts)
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 16:11:00
timeout_secs: 10800
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":4,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC4EF770449EC7080ADC978A99C5DCDF","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
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
- Upload via API yt-growth DULU (token Production aktif). Browser hanya untuk centang disclosure bila perlu.
- GAGAL karena limit harian: tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/fakta-bola-dunia-YYYY-MM-DD.json (format lihat retry-queue/README.md); watchdog mengerjakan otomatis.
- GAGAL sebab lain: perbaiki + retry SEGERA.

Langkah: 1) pilih fakta + kombinasi negara (cek riwayat). 2) naskah dialog multi-karakter + CTA tengah/akhir. 3) TTS per karakter (voice beda) + sanitasi. 4) render sprite + lip-sync + background (pipeline work/). 5) verifikasi durasi + tonton 1x. 6) upload ke @FaktaBolaDuniaID (CEK channel!) — tunggu approval user 20:00-23:00. 7) catat riwayat + lapor judul + URL + status.

Workspace: ~/workspace/fakta-bola-dunia/ | Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md
