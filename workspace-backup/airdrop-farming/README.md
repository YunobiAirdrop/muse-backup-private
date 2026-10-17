# Airdrop Farming — Testnet

Sistem farming airdrop testnet otomatis untuk wallet khusus farming.

## Wallet

**Address:** `0xf0f25C36AC70E9d787a108eFB351626192C8107b`

> Seed phrase dipegang user. TIDAK disimpan di repo/file mana pun.
> Private key akan disuplai via Secure Vault saat dibutuhkan untuk transaksi.

## Proyek (7)

| # | Proyek | Jaringan | Status Token | Frekuensi |
|---|--------|----------|--------------|-----------|
| 1 | GTE | MegaETH testnet | Confirmed | Mingguan |
| 2 | Neptune Protocol | Sepolia → Eclipse | Belum | Tiap 3 hari |
| 3 | Variational | Arbitrum Sepolia | Belum | Tiap 3 hari |
| 4 | Plaza Finance | Base Sepolia | Belum | Harian |
| 5 | Zenchain | Zenchain testnet | Belum | Rutin |
| 6 | Sahara AI | — | Confirmed | Harian |
| 7 | Multipli.fi | BSC testnet + Sepolia | Belum | Rutin |

Detail tiap proyek (URL, langkah, faucet): lihat `projects.json`.

## Cara kerja

- Cron `airdrop-farming-harian` jalan tiap hari 08:00 WIB.
- `farm.py` adalah orkestrator: baca `projects.json`, log aktivitas ke `logs/`,
  dan memicu interaksi dApp via browser task (didelegasikan ke parent agent,
  karena subagent tidak bisa mengoperasikan browser).
- Faucet yang butuh captcha / aksi sosial (posting X) dicatat sebagai
  blocked dan dilaporkan — tidak dicoba otomatis.

## File

- `projects.json` — definisi 7 proyek
- `farm.py` — skrip orkestrasi (logging + status)
- `logs/` — log harian per run
- `STATUS.md` — laporan status: apa yang jalan, apa yang blocked
