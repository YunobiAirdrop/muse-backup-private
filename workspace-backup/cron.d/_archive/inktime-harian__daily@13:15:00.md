---
id: inktime-harian
title: InkTime harian (whiteboard explainer EN)
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 13:15:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Produksi & upload 1 video WHITEBOARD EXPLAINER SEJARAH (ENGLISH)/hari ke "InkTime" (@InkTime-d3t, channel ID UCoZl5OaqjXSVkE4S96RY8_g, khususstokyunobi@gmail.com). TARGET: penonton USA. Gaya acuan: channel explainer "What Did Ancient Humans Actually Do All Day?" — naskah berbasis riset + sumber dicantumkan. WAJIB CEK channel aktif benar di YouTube Studio SEBELUM upload.

**VIRAL:** baca ~/workspace/youtube-otomatis/protokol-viral.md (hook 3 detik, double-down >10x, packaging, retensi). Anti full-AI: ~/AGENTS.md (AI disclosure dicentang). SHORTS: hashtag maks 4 di AKHIR JUDUL, ditutup #foryou (contoh: "... #shorts #history #explainer #foryou"), BUKAN di deskripsi. Long: hashtag di deskripsi, WAJIB termasuk #foryou.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file tak perlu; jangan ulangi verifikasi yang lolos; gabungkan langkah; jangan tulis laporan perantara ke file.

**JADWAL:** tayang BESOK 07:00 WIB (= 19:00 US Eastern / prime time Amerika). Produksi 16:11. Upload ~20:00-22:00 → ketukan persetujuan 20:00-22:00, set "Terjadwal" BESOK 07:00 WIB.

**TOPIK:** tiap hari BERBEDA dari ~/workspace/youtube-otomatis/inktime/pool-topik.md; cek riwayat-topik.json (anti-ulang 60 hari). Niche: ancient humans, lost civilizations, turning points sejarah, antropologi. Naskah WAJIB berbasis riset nyata — cantumkan 3-6 sumber (studi/buku/DOI) di deskripsi seperti channel acuan.

**FORMAT HYBRID (keputusan user 2026-10-08):**
- KLIP ANIMASI AI (whiteboard hand-drawing, tangan menggambar live): HANYA di hook (~10 detik pertama) + MAKS 3 momen kunci. TOTAL MAKS 4 klip AI per video long, MAKS 1 klip AI per shorts. JANGAN lebih (hemat token — 1 klip ≈ 2 jt token).
- SISANYA: gambar sketsa gaya whiteboard explainer (ink outlines, background putih bersih) dengan FRAMEWORK: judul header di atas + 2-4 bullet poin di bawah. Efek draw-reveal: gambar terbuka progresif kiri-ke-kanan mengikuti narasi (ffmpeg drawbox wipe: drawbox=x='iw*t/DUR':y=0:w=iw:h=ih:color=white:t=fill).
- Voiceover: TTS English voice avocado_v2:miles (--language en).

**AI DISCLOSURE:** WAJIB centang "Altered content" tiap upload.

**SENTUHAN MANUSIA:** script WAJIB 2-3 kalimat refleksi narator ("what fascinates me about this..." / "think about that for a second..."). Bahasa conversational, ajak penonton takjub. Struktur variatif. Pacing variatif; jeda dramatis di fakta paling mind-blowing.

**POLA UPLOAD (belum verifikasi HP → batas harian):** selang-seling: hari ini 1 LONG saja, besok 3 SHORTS saja, dst. Cek upload-terakhir.txt. JANGAN long+shorts sehari. Kena batas → upload yang bisa, sisanya besok.

**FORMAT (ENGLISH semua):** 9-10 menit, naskah orisinal ~1000-1200 kata. Voiceover TTS ENGLISH natural. Thumbnail ≤4 kata ENGLISH.

**SHORTS (3/hari):** 3 momen terbaik 30-60 detik, vertikal 9:16. Judul hook English + hashtag di AKHIR JUDUL ditutup #foryou (#shorts #history #explainer #foryou). 1 klip AI animasi per shorts (hook), sisanya gambar + draw-reveal.

**LANGKAH:**
1. Topik dari pool → cek riwayat → script ENGLISH per beat + prompt gambar per beat (framework: judul + bullets).
2. Voiceover per beat (tts --language en --voice avocado_v2:miles), gabung.
3. MAKS 4 klip AI whiteboard (hook + ≤3 momen kunci) via media.generate_video — prompt: "Whiteboard explainer animation, top-down view: a real human hand holding a black marker draws on white paper, sketching [SUBJEK], drawing progresses line by line, clean white background".
4. Gambar sketsa via media.generate_image untuk beat sisanya (gaya: hand-drawn sketch, whiteboard explainer, ink outlines, judul header + bullet framework).
5. Rakit: klip AI di hook & momen kunci; gambar + draw-reveal wipe untuk sisanya; text overlay momen kunci.
6. Potong 3 shorts (ffmpeg crop vertikal), thumbnail.
7. Kemarin LONG (atau file tak ada) → upload LONG saja ke @InkTime-d3t (CEK channel!) + AI disclosure + judul/deskripsi English (+ sumber riset) + hashtag (termasuk #foryou) + thumbnail, "Terjadwal" BESOK 07:00 WIB. Tulis "long:YYYY-MM-DD".
8. Kemarin SHORTS → upload 3 SHORTS (produksi KEMARIN) + AI disclosure + judul English (+ hashtag akhir ditutup #foryou) + deskripsi English (tanpa hashtag), "Terjadwal" BESOK 07:00 WIB. Tulis "shorts:YYYY-MM-DD".
9. Upload = approval user ("menunggu persetujuan", ketuk 20:00-22:00).
10. Catat topik ke riwayat-topik.json. Laporkan: yang diupload (long/shorts) + URL + status.

Workspace: ~/workspace/youtube-otomatis/inktime/
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** video yang SUDAH diproduksi WAJIB tayang — tidak boleh hilang/mogok diam-diam.
- Upload GAGAL karena "Batas upload harian telah tercapai" (atau pesan limit harian YouTube lain): JANGAN retry saat itu juga (limit ±24 jam — pasti gagal lagi). WAJIB: (1) tulis file instruksi upload lengkap (judul, deskripsi, hashtag, thumbnail, AI disclosure, slot jadwal target) seperti biasa; (2) tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/{channel}-YYYY-MM-DD.json dengan format {"channel":"...","video_path":"<absolut>","instruksi_path":"<absolut>","slot_target":"YYYY-MM-DD HH:MM WIB","gagal_pada":"YYYY-MM-DDTHH:MM:SS+07:00","sebab":"..."} — contoh lengkap di ~/workspace/youtube-otomatis/retry-queue/README.md. Watchdog harian otomatis mengerjakan antrean ini. Catat di laporan run: video apa yang gagal + path antreannya.
- Upload GAGAL karena sebab LAIN (bukan limit harian): perbaiki dan retry SEGERA saat itu juga (preferensi user), jangan tunda besok.
