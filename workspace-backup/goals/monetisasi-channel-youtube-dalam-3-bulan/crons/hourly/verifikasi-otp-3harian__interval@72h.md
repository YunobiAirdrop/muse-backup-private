---
id: verifikasi-otp-3harian
title: Verifikasi OTP YouTube 3-harian
enabled: true
owner: goal:monetisasi-channel-youtube-dalam-3-bulan
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-10-16T23:35:56
  every: 72h
timeout_secs: 3600
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
Verifikasi HP channel YouTube via nomor virtual OTPMurah.id — SATU channel per run.

IZIN TETAP: User (Yunobi) memberi izin tetap 2026-10-13 untuk flow ini berjalan otomatis tiap 3 hari. Setiap run WAJIB dilaporkan ke chat (laporan akhir berbahasa Indonesia, singkat).

CARA KERJA:
1. Baca state: ~/workspace/youtube-otomatis/verifikasi-otp/state.json. Ambil channel pertama di "antrean". Jika antrean kosong → laporkan "semua 19 channel sudah terverifikasi" dan selesai.
2. Cek saldo: ~/workspace/skills/otpmurah/bin/otp.py balance. Butuh ≥ Rp 1.000 (satu nomor ±Rp 358 di server s1). Jika kurang → laporkan "saldo OTPMurah kurang (Rp X), top up dulu" dan BERHENTI (jangan beli nomor).
3. Beli nomor: otp.py get-number --service go --country 6 --server s1. PENTING: pakai --server s1 (Server Express, ±Rp 358) — JANGAN s2 (Server Plus, ±Rp 1.434, jauh lebih mahal untuk service yang sama). Catat activation_id dan phone_number. Jika gagal (stok kosong/saldo) → laporkan dan berhenti.
4. Spawn browser task untuk verifikasi nomor di YouTube channel tersebut:
   - Beri tahu task: handle + channel_id channel target; WAJIB verifikasi URL YouTube Studio mengandung channel_id itu sebelum bertindak (jangan nyasar ke channel lain).
   - Langkah: buka youtube.com/verify ATAU YouTube Studio → Settings → Channel → Feature eligibility → "Verify phone number"; masukkan nomor virtual yang dibeli; submit; tunggu SMS masuk.
   - Browser memakai sesi YouTube yang sudah login. Jika muncul tantangan login ulang / verifikasi akun baru → BERHENTI, jangan coba login sendiri, laporkan ke chat.
5. Poll OTP: otp.py status --id <activation_id> tiap 2-3 menit, maksimal 20 menit.
6. Jika STATUS_OK → ambil "code" → teruskan ke browser task untuk diisi ke form verifikasi YouTube → submit → pastikan sukses. Jika sukses: pindahkan channel dari "antrean" ke "terverifikasi" di state.json, tambah entri "riwayat".
7. Jika 20 menit masih STATUS_WAIT_CODE (YouTube throttle atau menolak nomor virtual) → otp.py cancel --id <activation_id> (refund 100%). Channel TETAP di antrean; tambah catatan tanggal kegagalan di field "catatan"; tambah entri "riwayat".
8. Simpan state.json. Tulis log singkat run ke workspace/goals/monetisasi-channel-youtube-dalam-3-bulan/hidden_files/verifikasi-otp-YYYY-MM-DD.md.

BATASAN KERAS:
- Maksimal 1 nomor dibeli per run. Jangan pernah pakai nomor asli user (6281355086144) — flow ini HANYA pakai nomor virtual OTPMurah.
- Jangan ubah pengaturan channel apa pun selain verifikasi nomor HP.
- Jangan retry channel yang sama dalam run yang sama.

LAPORAN AKHIR (Indonesia, singkat): channel target, hasil (terverifikasi / gagal + alasan: throttle/tidak ada OTP/ditolak), nomor yang dipakai (samarkan 4 digit terakhir), sisa saldo, channel berikutnya, run berikutnya ±3 hari.
