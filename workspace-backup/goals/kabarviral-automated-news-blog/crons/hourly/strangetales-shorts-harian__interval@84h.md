---
id: strangetales-shorts-harian
title: Strange Tales Shorts — mode hemat 3-4 hari sekali
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-21T13:00:00
  every: 84h
timeout_secs: 10800
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","binding_epoch":4,"origin_provider":"whatsapp","original_reply_target_id":"whatsapp_channel","chat_kind":"direct","message_id":"AC16EC965485E22365DFD191408750C3","conversation_id":"whatsapp_channel","delivery_target_id":"whatsapp_channel","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Produksi & upload 3 SHORTS/hari ke "Strange Tales" (@StrangeTales-g6n, khususstokyunobi@gmail.com). KHUSUS SHORTS, target USA. WAJIB CEK channel aktif benar SEBELUM upload.

**VIRAL & ANTI-AI (baca SEBELUM produksi):** ~/workspace/youtube-otomatis/protokol-viral.md + ~/AGENTS.md (bagian anti full-AI look) — ikuti semua. Trend jacking HANYA dalam niche (dilarang ganti tema). Double-down: video kemarin >10x rata-rata → angle sama hari ini. Hashtag (maks 4) di AKHIR JUDUL shorts, ditutup #foryou, bukan deskripsi.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**KONSEP:** cerita unik/aneh penuh penasaran, gaya dokumenter pendek (ref. video "silkhenge"): hook 3 detik ("Scientists found..."), fakta mengejutkan, teks overlay English, voiceover English.

**JADWAL TAYANG:** Short1 → 21:00 WIB hari ini; Short2 → 03:00 WIB besok; Short3 → 07:00 WIB besok. Upload + approval user 20:00-23:00 WIB.

**CERITA:** 3 cerita BERBEDA/hari, cek ~/workspace/youtube-otomatis/strange-tales/pool-cerita.md + riwayat-cerita.json (jangan ulang). Catat yang dipakai (cerita, tanggal, video_url).

**VIRAL:** selaraskan dengan trend-radar hari ini bila cocok; tiap naskah 3 varian hook (A/B/C), pakai curiosity-gap terkuat; judul = hook + pertanyaan terbuka + hashtag di akhir ditutup #foryou (cth: "Scientists Found X — But WHY?! #shorts #weirdfacts #strangetales #foryou"); deskripsi 1-2 kalimat tanpa hashtag. FYP tak bisa dijamin — jujur di laporan.

**FORMAT/short (English):** 25-40 dtk, 1080x1920 30fps, footage STOK ASLI bebas lisensi (Pexels; JANGAN reupload milik orang = copyright), naskah ±80-90 kata spoken form (angka dieja), voiceover tts --voice avocado_v2:miles --language en, caption putih bold + outline hitam + box semi-transparan (maks 2 baris). Rakit tiru ~/workspace/video-weirdworld/rakit_stock.py.

**ANTI-MACET:** download Pexels maks 2x/klip → gagal = pakai cadangan atau SKIP short itu. Total download+rakit maks 45 menit → lewat = upload yang jadi saja. 1 short bermasalah jangan korbankan lainnya.

**Langkah:** 1) 3 cerita → 3 naskah + hook A/B/C. 2) TTS miles. 3) Download 3-4 klip Pexels/short (HD landscape ≥10 dtk, relevan). 4) Rakit 9:16 + caption, verifikasi 1 frame/video. 5) Upload ke @StrangeTales-g6n (CEK channel!) — judul + hashtag akhir ditutup #foryou, deskripsi tanpa hashtag, "not for kids", Scheduled di 3 jam tayang. 6) Catat riwayat. 7) Upload = approval user (20:00-23:00). 8) Lapor: 3 judul + URL + status.

Workspace: ~/workspace/youtube-otomatis/strange-tales/ | Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** video yang SUDAH diproduksi WAJIB tayang — tidak boleh hilang/mogok diam-diam.
- Upload GAGAL karena "Batas upload harian telah tercapai" (atau pesan limit harian YouTube lain): JANGAN retry saat itu juga (limit ±24 jam — pasti gagal lagi). WAJIB: (1) tulis file instruksi upload lengkap (judul, deskripsi, hashtag, thumbnail, AI disclosure, slot jadwal target) seperti biasa; (2) tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/{channel}-YYYY-MM-DD.json dengan format {"channel":"...","video_path":"<absolut>","instruksi_path":"<absolut>","slot_target":"YYYY-MM-DD HH:MM WIB","gagal_pada":"YYYY-MM-DDTHH:MM:SS+07:00","sebab":"..."} — contoh lengkap di ~/workspace/youtube-otomatis/retry-queue/README.md. Watchdog harian otomatis mengerjakan antrean ini. Catat di laporan run: video apa yang gagal + path antreannya.
- Upload GAGAL karena sebab LAIN (bukan limit harian): perbaiki dan retry SEGERA saat itu juga (preferensi user), jangan tunda besok.
