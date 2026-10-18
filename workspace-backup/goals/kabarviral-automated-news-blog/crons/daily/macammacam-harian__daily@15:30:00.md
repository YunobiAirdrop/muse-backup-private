---
id: macammacam-harian
title: Macam Macam YouTube harian
enabled: true
owner: goal:kabarviral-automated-news-blog
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 15:30:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Produksi 1 video Shorts "Macam-macam Jenis X (Part N)"/hari ke channel "Macam Macam" (@MacamMacamID, channel ID UC5ld2qCo0wKeuRKCA1-dbow, khususstokyunobi@gmail.com). Format: foto real Pexels gaya kartun tempel (cutout + outline putih di background kartun) + label nama besar + overlay "SUBSCRIBE YA!" + sulih suara Mudiwa (bahasa Indonesia) + musik latar ceria + CTA full (awal/tengah/akhir + deskripsi). Audience: dibuat untuk anak-anak. AI disclosure: WAJIB centang Ya tiap upload (sulih suara AI).

**FORMAT INI FIX DARI USER (koreksi 2026-10-12): channel ini seri PENAMAAN buat anak — "Macam-macam Jenis Kendaraan/Hewan/dll". DILARANG mengubahnya jadi format fakta unik/variety dewasa (kesalahan 2026-10-12: cron sempat terisi format variety → 3 shorts fakta tubuh manusia diproduksi & ditarik lagi oleh user). Acuan: ~/workspace/macam-macam/cron-spec-macammacam-harian.md + video perdana truk part 1 yang disetujui user.**

**HASHTAG (perintah user 2026-10-12, mengalahkan aturan hashtag lama di spec):** judul shorts WAJIB diakhiri hashtag ditutup #foryou; total 3-4 hashtag dan MINIMAL 3 = #foryou + minimal 2 hashtag PALING RAMAI dipakai yang relevan dengan topik (dari paket trending protokol-viral.md bagian 14 — utamakan volume terbesar seperti #shorts dan #viral, lalu niche terpopuler). Contoh: "Macam-macam Jenis Truk (Part 2) #shorts #viral #kendaraan #foryou".

**PROTOKOL VIRAL WAJIB:** baca ~/workspace/youtube-otomatis/protokol-viral.md — CTA (tengah video 50% + akhir + deskripsi, shorts: 3 detik terakhir), subtitle/teks on-screen mengikuti narasi, SEAMLESS LOOP shorts (kalimat terakhir nyambung ke kalimat pertama), AUDIO original utama (voiceover Mudiwa + musik ceria sendiri), upload sebagai TIDAK PUBLIK (Unlisted) dulu → rapikan judul/deskripsi → baru Publikasikan.

**BANK TEMA:** ~/workspace/macam-macam/tema/*.json — tiap hari 1 tema BERBEDA (rotasi, anti-ulang). Status: truk part 1 SUDAH produksi 2026-10-10; siap: hewan, mobil, motor, pesawat, kapal, buah, dinosaurus, alat-musik (semua part 1). Catat tema+part terpakai ke ~/workspace/macam-macam/riwayat-tema.json. Kalau 8 tema habis → buat tema baru (8 item: nama + fakta 1 kalimat kid-friendly Indonesia + pexels_query Inggris) ATAU naikkan part tema yang responsnya paling bagus.

**FOTO (PENTING — tidak ada Pexels API key, issuance paused):** unduh 8 foto via browser task dari pexels.com (query = item["pexels_query"]). Syarat: objek TERANG & JELAS, sesuai label — foto gelap GAGAL cutout (pelajaran truk part 1: 3 foto diganti). Simpan ke work/<slug>-part<N>/foto/itemNN.jpg, set item["foto_lokal"] ke path itu, catat item["kredit"] = "Nama Fotografer / Pexels" dari halaman Pexels. VERIFIKASI VISUAL tiap foto sebelum lanjut (ekstrak & LIHAT). CADANGAN bila unduh Pexels gagal total: Wikimedia Commons (lisensi aman komersial saja — CC0/PD/CC BY/CC BY-SA, cek per file, catat kreditnya dengan cara yang sama).

**COMPOSITING:** python3 ~/workspace/macam-macam/tempel.py <slug> — cutout rembg (venv siap) + threshold alpha + outline putih gaya stiker + tempel ke background kartun 1080x1920. Otomatis update item["foto_lokal"] ke hasil tempel. Cutout gagal → ganti foto, JANGAN dipaksa.

**RAKIT:** python3 ~/workspace/macam-macam/produksi.py <slug> — TTS Mudiwa, animasi KEYFRAME kendaraan (WAJIB dari user 2026-10-12: stiker kendaraan meluncur masuk + mantul halus + background bergeser — BUKAN gambar diam/Ken Burns saja; produksi.py sudah mendukungnya), overlay nama + "SUBSCRIBE YA!", musik ceria OTOMATIS, metadata JSON (judul "Macam-macam Jenis {Judul} (Part {N})" + hashtag sesuai aturan HASHTAG di atas, deskripsi + CTA + kredit fotografer + hashtag). Output: output/<slug>-part<N>.mp4. Pakai ffmpeg via ~/workspace/youtube-otomatis/ffmpeg-queue.sh (aturan anti-OOM).

**VERIFIKASI:** ekstrak 3 frame, LIHAT (objek sesuai label, stiker utuh, teks tidak kepotong); WAJIB cek frame di 2 timestamp berbeda dalam item yang sama — posisi kendaraan HARUS berubah (bukti keyframe jalan); pastikan musik ada (durasi audio ≈ durasi video).

**UPLOAD:** via YouTube Studio (browser task) — CEK channel @MacamMacamID (ID UC5ld2qCo0wKeuRKCA1-dbow) aktif benar SEBELUM upload. Audience "dibuat untuk anak-anak", AI disclosure centang Ya, visibilitas Publik, judul+deskripsi dari metadata JSON.

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** kena "Batas upload harian" (channel baru — wajar) → JANGAN retry langsung. WAJIB tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/macammacam-YYYY-MM-DD-<slug>.json: {"channel":"macam-macam","channel_handle":"@MacamMacamID","channel_id":"UC5ld2qCo0wKeuRKCA1-dbow","judul":"<dari metadata>","video_path":"<absolut mp4>","meta_path":"<absolut json>","gagal_pada":<epoch>,"sebab":"Batas upload harian","instruksi":"Upload via YouTube Studio ke channel Macam Macam (@MacamMacamID). Judul+deskripsi dari meta_path. Audience: dibuat untuk anak-anak. AI disclosure: centang Ya. Visibilitas: Publik."} — watchdog otomatis mengerjakan. Upload gagal sebab LAIN → perbaiki + retry segera.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu.

**LAPORAN:** ringkas ke chat — video apa (tema+part), status (terupload / masuk antrean retry). Observasi ke ~/memory/YYYY-MM-DD.md. Jangan edit MEMORY.md.
