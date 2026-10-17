# Cron spec: macammacam-harian (SIAP DIBUAT dari chat WhatsApp)

Serah terima channel Macam Macam (@MacamMacamID) ke asisten mulai 2026-10-11.
Video perdana (truk part 1) SUDAH disetujui user ("nah udah oke", 2026-10-10 ~11:20 WIB)
dan paket upload manual ada di tangan user. Pipeline produksi lengkap, tinggal
cron harian ini yang belum ada — tanpa ini, 11 Okt produksi macet diam-diam.

## Cara membuat (dari chat WhatsApp — aturan: cron ber-delivery WhatsApp hanya
## bisa dibuat/diubah dari chat itu)

`cron.add` dengan parameter:
- id: `macammacam-harian`
- title: `Macam Macam YouTube harian`
- mode: `task`
- enabled: `true`
- schedule: kind=`daily`, time=`16:11:00`, timezone=`Asia/Jakarta`
  (selaras 17 cron channel lain)
- owner: `goal:kabarviral-automated-news-blog`
  (konsisten dengan semua cron channel YouTube lain)

**PROTOKOL VIRAL WAJIB (aturan user 2026-10-10, berlaku 2026-10-11 — baca sebelum produksi):**
`~/workspace/youtube-otomatis/protokol-viral.md` — terapkan semua aturan wajib:
CTA (tengah video 50% + akhir + deskripsi, shorts: 3 detik terakhir),
subtitle/teks on-screen mengikuti narasi, SEAMLESS LOOP shorts (kalimat
terakhir nyambung ke kalimat pertama), AUDIO original utama (voiceover
Mudiwa + musik ceria sendiri — audio tren hanya opsional), cek Tab Inspirasi
YouTube Studio sebelum pilih tema, upload sebagai TIDAK PUBLIK (Unlisted)
dulu → rapikan judul/deskripsi → baru Terjadwal, judul shorts diakhiri MAKS
3 hashtag komposisi 1 umum + 1 platform/Indonesia + 1 niche (lihat bagian 12).

- delivery: `[{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf"}]`
  (chat WhatsApp — tempat ketukan persetujuan & laporan)
- predicted_connector_permissions: `[]`
- body: teks di bawah (copy-paste persis)

Sebelum `cron.add`, panggil `cron.list` dulu untuk memastikan belum ada
(nama/id bentrok), sesuai aturan.

## BODY (copy-paste ke cron.add)

Produksi 1 video Shorts "Macam-macam Jenis X (Part N)"/hari ke channel "Macam Macam" (@MacamMacamID, channel ID UC5ld2qCo0wKeuRKCA1-dbow, khususstokyunobi@gmail.com). Format: foto real Pexels gaya kartun tempel (cutout + outline putih di background kartun) + label nama besar + overlay "SUBSCRIBE YA!" + sulih suara Mudiwa (bahasa Indonesia) + musik latar ceria + CTA full (awal/tengah/akhir + deskripsi). Audience: dibuat untuk anak-anak. AI disclosure: WAJIB centang Ya tiap upload (sulih suara AI).

**BANK TEMA:** ~/workspace/macam-macam/tema/*.json — tiap hari 1 tema BERBEDA (rotasi, anti-ulang). Status: truk part 1 SUDAH produksi 2026-10-10; siap: hewan, mobil, motor, pesawat, kapal, buah, dinosaurus, alat-musik (semua part 1). Catat tema+part terpakai ke ~/workspace/macam-macam/riwayat-tema.json. Kalau 8 tema habis → buat tema baru (8 item: nama + fakta 1 kalimat kid-friendly Indonesia + pexels_query Inggris) ATAU naikkan part tema yang responsnya paling bagus.

**FOTO (PENTING — tidak ada Pexels API key, issuance paused):** unduh 8 foto via browser task dari pexels.com (query = item["pexels_query"]). Syarat: objek TERANG & JELAS, sesuai label — foto gelap GAGAL cutout (pelajaran truk part 1: 3 foto diganti). Simpan ke work/<slug>-part<N>/foto/itemNN.jpg, set item["foto_lokal"] ke path itu, catat item["kredit"] = "Nama Fotografer / Pexels" dari halaman Pexels. VERIFIKASI VISUAL tiap foto sebelum lanjut (ekstrak & LIHAT).

**COMPOSITING:** python3 ~/workspace/macam-macam/tempel.py <slug> — cutout rembg (venv siap) + threshold alpha + outline putih gaya stiker + tempel ke background kartun 1080x1920. Otomatis update item["foto_lokal"] ke hasil tempel. Cutout gagal → ganti foto via browser, JANGAN dipaksa.

**RAKIT:** python3 ~/workspace/macam-macam/produksi.py <slug> — TTS Mudiwa, Ken Burns, overlay nama + "SUBSCRIBE YA!", musik ceria OTOMATIS, metadata JSON (judul "Macam-macam Jenis {Judul} (Part {N})" diakhiri MAKS 3 hashtag: "#shorts" + 1 Indonesia/anak + 1 niche per paket hashtag protokol-viral bagian 12, contoh: "Macam-macam Jenis Truk (Part 1) #shorts #anak #edukasi", deskripsi + CTA + kredit fotografer + hashtag). Output: output/<slug>-part<N>.mp4. Pakai ffmpeg via ~/workspace/youtube-otomatis/ffmpeg-queue.sh (aturan anti-OOM).

**VERIFIKASI:** ekstrak 3 frame, LIHAT (objek sesuai label, stiker utuh, teks tidak kepotong); pastikan musik ada (durasi audio ≈ durasi video).

**UPLOAD:** via YouTube Studio (browser task) — CEK channel @MacamMacamID aktif benar SEBELUM upload. Audience "dibuat untuk anak-anak", AI disclosure centang Ya, visibilitas Publik, judul+deskripsi dari metadata JSON.

**ANTI-MOGOK UPLOAD (aturan tetap user 2026-10-07):** kena "Batas upload harian" (channel baru — wajar) → JANGAN retry langsung. WAJIB tulis antrean JSON ke ~/workspace/youtube-otomatis/retry-queue/macammacam-YYYY-MM-DD-<slug>.json: {"channel":"macam-macam","channel_handle":"@MacamMacamID","channel_id":"UC5ld2qCo0wKeuRKCA1-dbow","judul":"<dari metadata>","video_path":"<absolut mp4>","meta_path":"<absolut json>","gagal_pada":<epoch>,"sebab":"Batas upload harian","instruksi":"Upload via YouTube Studio ke channel Macam Macam (@MacamMacamID). Judul+deskripsi dari meta_path. Audience: dibuat untuk anak-anak. AI disclosure: centang Ya. Visibilitas: Publik."} — watchdog otomatis mengerjakan. Upload gagal sebab LAIN → perbaiki + retry segera.

**HEMAT TOKEN:** tool call sesedikit mungkin; jangan baca file yang tak perlu.

**LAPORAN:** ringkas ke chat — video apa (tema+part), status (terupload / masuk antrean retry). Observasi ke ~/memory/YYYY-MM-DD.md. Jangan edit MEMORY.md.

## Status persiapan (2026-10-10, diverifikasi)
- tempel.py: DITULIS + DITES — output 1080x1920 gaya stiker identik dengan
  referensi manual yang disetujui user (cek visual /tmp/test-tempel.jpg vs
  work/truk-part1/tempel/item00.jpg).
- produksi.py: SUDAH mencakup musik ceria otomatis (per permintaan user
  "musiknya mana", disetujui "nah udah oke").
- Bank tema: 8 tema siap (hewan, mobil, motor, pesawat, kapal, buah,
  dinosaurus, alat-musik) — semua JSON tervalidasi (8 item/tema).
- Retry-queue: format antrean channel ini sudah dipakai
  (macammacam-2026-10-10-truk-part1.json) dan dikenali watchdog.
- Yang BELUM: cron ini sendiri (dibuat dari chat WhatsApp oleh main agent).
