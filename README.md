# muse-backup-private 🔒

Repo **PRIVATE** milik YunobiAirdrop. Berisi:
- Tooling auto-backup (dari Kutuyyy/muse-auto-backup — lihat `prompt-auto-backup-github.md`)
- `secrets/secrets-bundle.tar.gz.gpg` — bundle API key & token **terenkripsi AES-256**
- `restore.sh` — skrip restore sekali jalan buat VM baru

## Isi bundle secret (terenkripsi)
- `~/.hermes/.env` — OpenRouter key, Composio key, dll
- `~/.hermes/blogger-tokens.json` + `google-oauth-blogger.env` — Blogger OAuth
- `~/.hermes/yt-growth/` — YouTube OAuth tokens (20 channel)
- `~/.hermes/yt-*.json` — Firebase deploy, GA4, dashboard
- `~/.hermes/github-dashboard-token` — token GitHub
- `~/.hermes/youtube-stream-keys.env` — stream keys
- `~/.hermes/.dashboard-pw` — password dashboard

## Cara restore di VM baru
```bash
git clone https://github.com/YunobiAirdrop/muse-backup-private.git
cd muse-backup-private
chmod +x restore.sh
./restore.sh
# masukkan password dekripsi saat diminta
```

## Keamanan
- File `.gpg` cuma bisa dibuka pakai password dekripsi (AES-256 + SHA512 KDF)
- Password TIDAK disimpan di repo ini — simpan di password manager / tempat aman
- Repo ini PRIVATE — jangan pernah di-public-kan
- Jangan commit file `.tar.gz` polos (tanpa enkripsi) ke repo ini

---
Dokumen asli tooling backup ada di `prompt-auto-backup-github.md`.
