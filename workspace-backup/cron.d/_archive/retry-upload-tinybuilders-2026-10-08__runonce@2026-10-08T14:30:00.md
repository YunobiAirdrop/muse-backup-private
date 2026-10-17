---
id: retry-upload-tinybuilders-2026-10-08
title: Retry upload Tiny Builders (4 video, pasca batas 24 jam)
enabled: true
owner: goal:channel-youtube-internasional-berbahasa-inggris
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-10-08T14:30:00
timeout_secs: 14400
delivery:
  - chat_id: 7382e6cd-7263-4ede-983e-939bf507ecbf
metadata:
  originating_chat_context_json: '{"chat_id":"7382e6cd-7263-4ede-983e-939bf507ecbf","origin_provider":"main","chat_kind":"direct","provider":"main","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
# RETRY UPLOAD Tiny Builders (channel baru kena batas 24 jam YouTube tgl 2026-10-07)

KONTEKS: Channel "Tiny Builders" (@tinybuilders-d5z) dibuat 2026-10-07. Upload perdana 4 video GAGAL karena YouTube membatasi channel baru (0 upload/24 jam pertama tanpa verifikasi HP). User MENOLAK verifikasi HP secara permanen ("skip aja, saya ga ada nomor lagi") — JANGAN tawarkan verifikasi lagi. Solusi: coba upload lagi setelah 24 jam berlalu.

FILE (di ~/workspace/miniatur-ai/):
- tiny-builders-ep1-long.mp4 (396MB, 14:10 — MASTER, jangan upload langsung, kegedean buat file-grant browser)
- tiny-builders-ep1-long-sm.mp4 (142MB — masih kegedean, DITOLAK klasifikasi browser 2026-10-07)
- tiny-builders-ep1-long-xs.mp4 (versi CRF30, dibuat 2026-10-07 — CEK ukurannya dulu)
- tiny-builders-ep1-short1.mp4 (34MB), short2 (38MB), short3 (30MB) — LOLOS klasifikasi browser

LANGKAH:
1. Cek ukuran tiny-builders-ep1-long-xs.mp4. Jika >80MB, encode ulang yang lebih kecil: ~/workspace/youtube-otomatis/ffmpeg-queue.sh -y -i tiny-builders-ep1-long.mp4 -c:v libx264 -crf 32 -preset medium -vf scale=960:540 -c:a aac -b:a 96k -movflags +faststart tiny-builders-ep1-long-xs2.mp4 — pakai file terkecil yang lolos untuk upload (kualitas 540p masih layak untuk YouTube, nanti di-re-encode YouTube juga).
2. Spawn browser task upload ke channel "Tiny Builders" (@tinybuilders-d5z) — CEK channel aktif dulu, JANGAN salah channel:
   - LONG (file long terkecil): Judul "We Built a WORKING Mini Diesel Water Pump! (Miniature Farm Build)". Deskripsi:
Two tiny farmers. One dry field. And a miniature diesel engine that actually works.

Watch the full build: a brick water tank, a hand-assembled mini diesel engine, and an irrigation system — all in miniature, all by hand.

Subscribe to Tiny Builders for a new tiny build every week!

Sound effects (CC BY 4.0, Freesound.org): Glen_Dorner, DanielMarais, datasoundsample, yfjesse, FreqMan, Kolezan

#miniature #diy #tinybuilders #miniaturebuild #satisfying
     Tag: miniature, diy miniature, tiny build, miniature build, satisfying video, irrigation. Audience: NOT for kids. AI disclosure: YA. Visibilitas: PUBLIC langsung.
   - SHORT 1: Judul "PULL the Starter... The Mini Diesel ROARS to Life! #shorts #miniature #diy". Deskripsi (tanpa hashtag): "The moment the mini diesel engine roars to life! Watch the full 14-minute build on Tiny Builders." Tag: miniature, diy miniature, shorts, engine start. NOT for kids, AI disclosure YA. SCHEDULED 2026-10-08 21:00 WIB.
   - SHORT 2: Judul "Water GUSHING From a Miniature Pump! #shorts #miniature #satisfying". Deskripsi: "Water gushing from a pump smaller than your hand! Full build on Tiny Builders." Tag: miniature, diy miniature, shorts, satisfying. SCHEDULED 2026-10-09 03:00 WIB.
   - SHORT 3: Judul "Laying BRICKS... One Tiny Brick at a Time #shorts #miniature #diy". Deskripsi: "A real human hand building a miniature brick tank, brick by brick. Full build on Tiny Builders." Tag: miniature, diy miniature, shorts, bricklaying. SCHEDULED 2026-10-09 07:00 WIB.
3. Upload SATU PER SATU. Jika MASIH kena batas harian: JANGAN verifikasi HP, laporkan, dan buat cron runonce lagi untuk lusa.
4. Upload = approval user (20:00–23:00 WIB).

LAPORAN: 4 judul + URL + status visibilitas. Bahasa Indonesia, singkat.
Catatan: jangan edit MEMORY.md; observasi ke ~/memory/YYYY-MM-DD.md
