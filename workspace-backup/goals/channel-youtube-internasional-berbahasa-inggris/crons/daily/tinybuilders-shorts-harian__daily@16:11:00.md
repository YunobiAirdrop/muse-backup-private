---
id: tinybuilders-shorts-harian
title: Tiny Builders Shorts harian (3 shorts/hari)
enabled: false
owner: goal:channel-youtube-internasional-berbahasa-inggris
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 16:11:00
timeout_secs: 14400
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
# Tiny Builders — 3 Shorts miniatur/hari (@tinybuilders-d5z)

**SEBELUM PRODUKSI, baca:** ~/workspace/youtube-otomatis/protokol-viral.md (WAJIB) + ~/AGENTS.md (bagian anti full-AI look).

**VIRAL RINGKAS:** trend jacking HANYA dalam niche; hook 3 detik; double-down (>10x rata-rata → angle sama); hashtag (maks 4) di AKHIR JUDUL shorts, ditutup #foryou.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file tak perlu; jangan ulangi verifikasi lolos; gabungkan langkah; jangan tulis laporan perantara.

**PRODUKSI (3 ide BERBEDA/hari):**
1. Baca ~/workspace/miniatur-ai/pool-ide.md + riwayat-ide.json — pilih 3 ide BELUM dipakai 60 hari; prioritaskan yang cocok trend-radar hari ini.
2. Tiap short = 1 klip 30–60 dtk, vertikal 9:16, via media.generate_video.
3. GAYA WAJIB: "Outdoor miniature farm diorama, warm daylight, photorealistic macro, shallow depth of field. Real human hand building/working with tiny materials." Tangan manusia ASLI kelihatan bekerja.
4. TANPA narasi. SFX rekaman ASLI ~/workspace/miniatur-ai/sfx-real/ — tiap sumber suara yang kelihatan HARUS terdengar.
5. Detik 0–3 = momen paling memuaskan/penasaran; akhir nge-loop natural.
6. Film grain halus (ffmpeg noise), pacing tidak monoton.
7. Catat 3 ide ke riwayat-ide.json.

**ANTI-MACET:** media.generate_video maks 2x/short → gagal = SKIP short itu, lanjut berikutnya. **HEMAT TOKEN KLIP (WAJIB):** 3 shorts HARUS di-generate BERURUTAN oleh SATU agen — DILARANG spawn 1 subagent per short (terukur: ~2 jt token/short karena tiap subagent mewarisi seluruh konteks). Panggil media.generate_video langsung 3x berurutan.

**UPLOAD (@tinybuilders-d5z — CEK channel!):** judul hook English + maks 4 hashtag di AKHIR JUDUL ditutup #foryou (cth: "He Built a WORKING Water Pump... in MINIATURE! #shorts #miniature #diy #foryou"); deskripsi 1-2 kalimat + "Full build on Tiny Builders" (tanpa hashtag); tag: miniature, diy miniature, tiny build, shorts + keyword; bukan untuk anak-anak; AI disclosure YA. Tayang: besok 03:00 / 07:00 / 21:00 WIB. Approval user 20:00–23:00. Kena batas upload → upload yang bisa, sisanya besok. JANGAN verifikasi HP.

**LAPORAN:** 3 judul + URL + status terjadwal. Bahasa Indonesia, singkat. Jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** video yang SUDAH diproduksi WAJIB tayang — tidak boleh hilang/mogok diam-diam.
- Upload GAGAL karena "Batas upload harian telah tercapai" (atau pesan limit harian YouTube lain): JANGAN retry saat itu juga (limit ±24 jam — pasti gagal lagi). WAJIB: (1) tulis file instruksi upload lengkap (judul, deskripsi, hashtag, thumbnail, AI disclosure, slot jadwal target) seperti biasa; (2) tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/{channel}-YYYY-MM-DD.json dengan format {"channel":"...","video_path":"<absolut>","instruksi_path":"<absolut>","slot_target":"YYYY-MM-DD HH:MM WIB","gagal_pada":"YYYY-MM-DDTHH:MM:SS+07:00","sebab":"..."} — contoh lengkap di ~/workspace/youtube-otomatis/retry-queue/README.md. Watchdog harian otomatis mengerjakan antrean ini. Catat di laporan run: video apa yang gagal + path antreannya.
- Upload GAGAL karena sebab LAIN (bukan limit harian): perbaiki dan retry SEGERA saat itu juga (preferensi user), jangan tunda besok.
