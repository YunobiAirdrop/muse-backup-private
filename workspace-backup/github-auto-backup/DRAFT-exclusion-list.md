# DRAFT — Daftar file yang WAJIB dikecualikan dari auto-backup GitHub
<!-- Status: DRAFT riset, disiapkan 2026-10-17 14:23 WIB. Bukan keputusan final. -->
<!-- Dipakai saat setup auto-backup per jam ke private repo (proyek Kutuyyy/muse-auto-backup). -->
<!-- Keputusan terbuka "API key masuk repo atau tidak" TIDAK diputus di sini — -->
<!-- daftar ini hanya memastikan file di bawah TIDAK ter-push plaintext apa pun keputusannya. -->

Verifikasi keberadaan file: 2026-10-17 ~14:20 WIB (Asia/Jakarta), langsung di VM.

## 1. Path absolut — JANGAN PERNAH push plaintext

| Path | Isi | Ukuran/izin (terverifikasi) |
|---|---|---|
| `~/.hermes/.env` | OpenRouter API key, COMPOSIO_CONSUMER_KEY, NINEROUTER_API_KEY | 600, ada |
| `~/.hermes/.dashboard-pw` | Password dashboard 9Router | 600, ada |
| `~/.hermes/google-oauth-blogger.env` | OAuth Client ID + Secret Google (Blogger) | 600, ada |
| `~/.hermes/blogger-tokens.json` | Token OAuth Blogger (auto-refresh) | 600, ada |
| `~/.hermes/github-dashboard-token` | Token GitHub (dashboard) | 600, 40 byte, ada |
| `~/.hermes/yt-growth/client_secret.json` | OAuth client secret yt-growth (20 channel) | 600, ada |
| `~/.hermes/yt-growth/client_secret.json.bak-desktop` | Backup client secret | ada |
| `~/.hermes/yt-growth/pkce.json` | PKCE state OAuth | 600, ada |
| `~/.hermes/yt-growth/tokens/*.json` | 20 token OAuth Production per channel | 20 file, ada |
| `~/.config/ngrok/ngrok.yml` | Token ngrok | 600, ada |
| `~/workspace/yt-dashboard/.secret` | Secret dashboard (32 byte, nama file polos!) | 600, ada |

Catatan: sebagian besar path di atas ada DI LUAR `~/workspace`, jadi backup per jam
yang hanya menyapu workspace TIDAK akan menangkapnya — itu kabar baik untuk keamanan,
tapi artinya permintaan "API key masuk repo" butuh penanganan eksplisit terpisah
(lihat keputusan terbuka di bawah), BUKAN sekadar mengandalkan sapuan workspace.

## 2. Pola nama file — kecualikan via glob (seluruh repo)

```
**/.env
**/.env.*
**/*token*.json
**/*secret*
**/*credential*
**/*.pem
**/id_rsa*
**/*api*key*
**/client_secret*.json
**/pkce.json
**/tokens/*.json
```

## 3. Temuan penting untuk audit

- `~/workspace/yt-dashboard/.secret` adalah CONTOH NYATA temuan audit #3:
  file berisi secret dengan nama polos — exclusion berbasis nama file saja
  (".env, token, API key") BERISIKO lolos kalau pola tidak mencakup `*secret*`.
  Pola di bagian 2 sudah mencakupnya.
- Inventaris kredensial lama (`backup-repo/docs/07-kredensial.md`, 2026-10-08)
  sudah kedaluwarsa sebagian: token yt-growth sekarang 20 (bukan 17), dan ada
  file baru (`.secret`, `github-dashboard-token`, `pkce.json`).
- Repo backup lama: `YunobiAirdrop/yunobi_project_backup` — push terakhir
  2026-10-08 16:32 UTC, 133 MB, isi docs + scripts (tanpa secret/media).
  Jangan jalan paralel dengan sistem auto-backup baru (temuan audit #4).

## 4. Keputusan yang masih terbuka (bukan wewenang draft ini)

User meminta "apikey openrouter dll masukin ke repo juga tapi di privat"
(2026-10-17). Alternatif yang sudah diajukan ke user: key tetap di Secure Vault
+ `RESTORE.md` berisi daftar key & cara isi ulang, ATAU enkripsi `.age` dengan
password. Tunggu jawaban user sebelum implementasi.
