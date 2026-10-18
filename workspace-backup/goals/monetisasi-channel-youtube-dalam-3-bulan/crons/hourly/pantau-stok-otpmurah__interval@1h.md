---
id: pantau-stok-otpmurah
title: Pantau stok OTPMurah (1 jam)
enabled: false
owner: goal:monetisasi-channel-youtube-dalam-3-bulan
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-18T02:09:25
  every: 1h
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Pantau stok nomor virtual Google di OTPMurah.id — cek tiap 1 jam, order OTOMATIS saat stok beneran tersedia.

KONTEKS: Stok Google di Server Express tampil 101.471 tapi backend menolak order ("Layanan sedang dalam pengisian") — angka tampilan tidak bisa dipercaya. API OTPMurah juga menolak semua pembelian. Jadi cek HARUS via website.

IZIN TETAP: User (Yunobi) memberi izin tetap untuk flow verifikasi OTP otomatis (2026-10-13) + meminta penjadwalan pantauan stok ini (2026-10-17). Setiap run yang BERHASIL order WAJIB dilaporkan ke chat (Indonesia, singkat). Run yang stok masih kosong: JANGAN ganggu user, cukup tulis log.

CARA KERJA:
1. Baca state: ~/workspace/youtube-otomatis/verifikasi-otp/state.json. Jika antrean kosong → laporkan "semua channel sudah terverifikasi" dan selesai.
2. Spawn browser task: login https://otpmurah.id via "Lanjutkan dengan Google" (akun stokwebyakis@gmail.com, sesi biasanya sudah tersimpan — JANGAN minta kredensial baru; kalau sesi expired dan butuh login ulang yang butuh ketukan user, STOP dan laporkan). Di halaman Beli OTP: negara Indonesia, Server Express, layanan "Google,youtube,Gmail". Klik Beli → konfirmasi "Beli Sekarang" SEKALI SAJA.
3. Jika muncul toast "Layanan sedang dalam pengisian" → stok masih kosong. Tulis 1 baris log ke workspace/goals/monetisasi-channel-youtube-dalam-3-bulan/hidden_files/pantau-stok-otpmurah.log (format: YYYY-MM-DD HH:MM - stok kosong). JANGAN laporkan ke user. Selesai.
4. Jika order BERHASIL (muncul nomor + ID aktivasi di Order Aktif) → LANJUTKAN flow verifikasi persis seperti cron verifikasi-otp-3harian langkah 4-8: verifikasi nomor di YouTube channel pertama antrean via browser task, poll OTP max 20 menit, sukses → pindahkan ke "terverifikasi", gagal → cancel (refund 100%). Update state.json, tulis log run.
5. Jika saldo < Rp 1.000 → laporkan ke user "saldo OTPMurah kurang, top up dulu" dan berhenti.

BATASAN KERAS:
- Maksimal 1x klik Beli per run (jangan spam order).
- Jangan pernah pakai nomor asli user (6281355086144).
- Jangan ubah pengaturan channel apa pun selain verifikasi nomor HP.
- Jangan retry channel yang sama dalam run yang sama.

LAPORAN (hanya saat ada hasil): channel target, hasil (terverifikasi/gagal + alasan), nomor dipakai (samarkan 4 digit terakhir), sisa saldo.
