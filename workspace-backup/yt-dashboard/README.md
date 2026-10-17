# YT Dashboard — aplikasi dashboard 19 channel YouTube (PWA)

Meniru aplikasi Bang Dadone (FB): 1 layar berisi semua channel, lihat statistik +
video, review video private/terjadwal lalu publish langsung dari HP.

## Status (2026-10-15)

- Backend: **jalan** sebagai systemd service `yt-dashboard-backend.service`
  (http://127.0.0.1:8765, restart otomatis).
- Frontend: PWA mobile-first (`static/index.html` + `manifest.json` + ikon),
  siap "Add to Home Screen" di Chrome Android.
- Password: dibuat user saat pertama buka (min. 4 karakter), disimpan sebagai
  hash di `.pw_hash` (600). Login session 30 hari.

## AKSES DARI HP — BELUM BISA (blokir infrastruktur)

Dicoba 2026-10-15, semua gagal karena proxy egress VM:
- **cloudflared quick tunnel**: cloudflared tidak memakai proxy env,
  koneksi langsung diblokir ("tls: first record does not look like a TLS handshake").
- **localtunnel**: hang (tidak memakai proxy).
- **pinggy via SSH+proxy**: CONNECT ok tapi banner SSH timeout (host kemungkinan tidak di-whitelist).
- **Tailscale**: client-nya hanya client-only (tidak bisa hosting service untuk diakses HP).

**Opsi yang realistis:** ngrok (agen-nya proxy-aware). Butuh user bikin akun
ngrok gratis → kasih authtoken → pasang sebagai pengganti tunnel.sh.
Atau: user buka dashboard dari browser yang se-VM (tidak praktis dari HP).

Service tunnel (`yt-dashboard-tunnel.service`) DINONAKTIFKAN sampai ada solusi
tunnel yang terbukti jalan. File unit tetap ada di `systemd/`.

## BLOKIR KEDUA — token OAuth YouTube MATI SEMUA (2026-10-15)

`invalid_grant: Token has been expired or revoked` di SEMUA 17 channel.
Kemungkinan penyebab: consent screen Google Cloud masih "Testing"
(refresh token testing kedaluwarsa 7 hari; dibuat ~8 Okt → mati 15 Okt).
Dampak: dashboard tidak bisa ambil data (tampil "error" per channel),
dan SELURUH pipeline yt-growth (upload API, scan, dsb) ikut mati.

Perbaikan (di luar jangkauan subagent — butuh user):
`cd ~/workspace/youtube-otomatis/yt-growth && python auth.py auth-url <slug>`
lalu `python auth.py exchange <slug> <kode>` — untuk 17 channel, satu per satu
di HP user. Jangka panjang: publish OAuth app ke Production di Google Cloud Console.

## File

- `app.py` — backend Flask (import auth.py dari yt-growth, tidak mengubahnya)
- `static/` — index.html, manifest.json, icon-192/512.png
- `tunnel.sh` — wrapper cloudflared (nonaktif; siap dipakai kalau proxy mendukung)
- `systemd/` — unit backend + tunnel (master; terinstall di /etc/systemd/system/)
- `proxycommand.py` — ProxyCommand ssh via proxy (eksperimen pinggy)
- `publish.log` — log setiap publish dari dashboard
- `AKSES.txt` — ditulis otomatis oleh tunnel.sh saat tunnel hidup (belum ada URL)

## API

- POST /api/login {password} — login / set password pertama kali
- GET /api/channels — 19 channel (cache 15 mnt)
- GET /api/videos?slug=X — 10 video terbaru (cache 10 mnt)
- GET /api/pending — video private/unlisted semua channel (cache 10 mnt)
- POST /api/publish {slug, videoId} — jadikan public + log
- GET /api/publish_log — 50 publish terakhir
