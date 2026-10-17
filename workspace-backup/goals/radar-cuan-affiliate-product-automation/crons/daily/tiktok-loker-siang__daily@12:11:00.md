---
id: tiktok-loker-siang
title: Konten loker TikTok siang (kejar followers)
enabled: true
owner: goal:radar-cuan-affiliate-product-automation
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 12:11:00
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Buat dan posting 1 video loker TikTok siang ini untuk akun @ngeweb.yuk (mode kejar 600 followers), mengikuti ~/workspace/tiktok-shop-affiliate/loker-tiktok.md.

Langkah:
1. Baca loker-tiktok.md dan loker-history.json (buat {"posted": []} jika belum ada).
2. Dari ~/workspace/loker-otomatis/data/artikel-loker.json pilih 1 artikel dengan slug yang BELUM pernah dipakai (prioritas: terbaru & posisi populer).
3. Tulis naskah 25-40 detik: hook gaji/posisi/perusahaan di 3 detik pertama (tanpa perkenalan), syarat singkat maks 3 poin, cara melamar, disclaimer anti-scam wajib, CTA "Link loker lengkapnya ada di bio! Komen domisili kamu, besok saya cariin loker daerah situ! Tag temanmu yang lagi cari kerja!".
4. Generate 1 gambar AI (suasana kerja relevan, tanpa teks).
5. Voiceover via tts skill (Bahasa Indonesia natural).
6. Rakit via ~/workspace/youtube-otomatis/ffmpeg-queue.sh: gambar + zoompan + teks overlay BESAR ber-keyword (contoh "LOKER TANGERANG 2026", posisi, perusahaan) + "LINK DI BIO" di 3 detik terakhir + voiceover + film grain halus → output/loker-{slug}-{YYYYMMDD}.mp4. Format vertical 9:16.
7. Tulis caption sesuai panduan (baris 1 hook+keyword, baris 2 CTA komen, maks 5 hashtag) → file .txt.
8. Posting via `taisly posts:create --video <file> --platforms 6ac71c80572b2159e0a2f190 --description "<caption>"`. Verifikasi via `taisly posts:status --id <historyId>`.
9. Update loker-history.json.

Laporan akhir ke user (Bahasa Indonesia, singkat): judul loker + status posting (ok/gagal). Akhiri SELALU dengan: "Followers sekarang berapa? Kabari saya kalau sudah 600 biar langsung mulai mode review produk. Oh iya — balas komentar yang masuk ya, itu bahan bakar FYP."

Batasan: JANGAN menyebut/mempromosikan produk afiliasi (mode kejar followers murni). JANGAN mengarang gaji/deadline/link. JANGAN retry posts:create buta setelah timeout — cek History dulu. 1 slug = 1 video.
