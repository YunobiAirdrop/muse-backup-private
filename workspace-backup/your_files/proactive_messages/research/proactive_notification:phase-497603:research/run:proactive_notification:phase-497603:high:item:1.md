<!-- proactive-explanation:run:proactive_notification:phase-497603:high:item:1 -->
# Perbaiki definisi shopee-video-harian — nama file manifest & layout video salah (run 19:11 pasti gagal tanpa ini)

## Lookup

`⁨muse.db⁩` references:

| Table | Keys |
| --- | --- |
| `agent.context_items` | `agent_id=bd8245a5-e5e4-4b57-b52b-3fb847c8f9cb`; `agent_id=d90d2e6c-a763-4b45-a038-908e2ef80332` |
| `agent.message_mailbox` | `submission_id=1068a38e-28df-3ce3-c16a-cffc3e15c6ac` |
| `goals.updates` | `update_id=goal_update_8a3ca5043666` |
| `runtime.messages` | `message_id=assistant-msg-5e9c1ee7-c0f8-daa8-83f2-eb8260c29738` |
Prepared: ⁨2026-10-07T11:25:39Z⁩.

## Why this matters

Kenapa ini penting malam ini: run shopee-video-harian jam 19:11 WIB nanti (2026-10-07T12:11Z) PASTI gagal menyiapkan paket video — bukan karena videonya belum ada, tapi karena definisi cron-nya mencari file yang salah. Saya cek langsung: (1) cron mencari manifest-YYYY-MM-DD.json (tanda hubung), padahal file aslinya manifest_2026-10-07.json (underscore); (2) cron mencari video di promo_out/YYYY-MM-DD/<slug>/final-wa.mp4, padahal videonya flat: promo_out/video_final_<slug>_wa.mp4; (3) 5 video hari ini ADA dan valid (4,2–5,9 MB per file: pouch-travel, vitamin-kucing, vitamin-cerna, sabun-piring, impact-wrench); (4) manifest berisi 5 produk lengkap dengan nama, harga, link afiliasi, tags, dan caption. Tanpa perbaikan, run 19:11 akan lapor "paket video hari ini belum tersedia" (false negative) dan Yunobi tidak dapat paket siap-upload untuk upload manual ke Shopee Video. Yang sudah saya coba: cron.update dari konteks riset ini DITOLAK runtime — jadwal yang deliver ke chat WhatsApp hanya bisa diubah dari chat WhatsApp itu. Jadi ini butuh dieksekusi dari side chat WhatsApp (7382e6cd-7263-4ede-983e-939bf507ecbf). Body pengganti (pertahankan manual-route yang sudah disetujui user, perbaiki hanya langkah 1–2): "Siapkan paket 5 video afiliasi harian untuk upload MANUAL via aplikasi Shopee (akun stokakunwebyunobi@gmail.com). KONTEKS PENTING: upload via browser/Seller Center TERBUKTI jalan buntu 2x. JANGAN coba upload via browser. Jalur resmi: user upload sendiri dari aplikasi Shopee (tab Video → tombol +). Tugas cron ini HANYA menyiapkan paket siap-upload. Langkah: 1. Baca manifest hari ini di ~/workspace/blog-otomatis/promo_out/: coba dulu manifest_YYYY-MM-DD.json (UNDERSCORE, mis. manifest_2026-10-07.json); kalau tidak ada, coba manifest-YYYY-MM-DD.json (hyphen). Kalau keduanya tidak ada → laporkan 'paket video hari ini belum tersedia (promo-afiliasi-harian belum selesai)' dan SELESAI (bukan error; jangan coba lagi). 2. Untuk tiap produk di manifest[\"produk\"]: file video = ~/workspace/blog-otomatis/promo_out/video_final_<slug>_wa.mp4, dengan <slug> = nama file_gambar tanpa ekstensi (mis. 'pouch-travel.jpg' → video_final_pouch-travel_wa.mp4). Ambil nama, harga, caption, link afiliasi, tags dari entri manifest yang sama. Kalau file video tidak ada untuk suatu produk, catat belum tersedia dan lanjut. 3. Kirim ke chat sebagai paket siap-upload: tiap video sebagai lampiran + per produk (nama, harga, caption siap-copy ≤150 karakter + link afiliasi + hashtag) + instruksi: aplikasi Shopee → tab Video → + → upload satu per satu jeda 30-45 menit. 4. JANGAN buka browser, JANGAN Seller Center, JANGAN minta approval upload. 5. Laporkan daftar produk + status paket." Setelah update, verifikasi dengan cron.view. Fallback kalau perbaikan tidak keburu sebelum 19:11: kirim manual 5 video + caption/link/hashtag dari manifest ke chat WhatsApp (data sudah terverifikasi ada).

Selected for high priority at ⁨2026-10-07T11:27:12.474067+00:00⁩. Record created ⁨2026-10-07T11:27:12.749401356+00:00⁩; delivery is not yet confirmed.


**Delivery outcome (⁨2026-10-07T11:27:56.226644+00:00⁩):** Sent. Queue state: `⁨delivered⁩`.
Reason: `⁨delivered⁩`.
`⁨agent.message_mailbox.submission_id=1068a38e-28df-3ce3-c16a-cffc3e15c6ac⁩` resolves the delivery transcript.
<!-- proactive-outcome:proactive_notifier:run:proactive_notification:phase-497603:high -->
