# Airdrop Farming — Status Report

**Date:** 2026-10-19
**Wallet:** `0xf0f25C36AC70E9d787a108eFB351626192C8107b`

## Run 2026-10-19 (cron airdrop-farming-harian, 08:00 WIB)

### farm.py
- Berjalan bersih (exit 0), log: `logs/farm-2026-10-19.log`.
- Hasil: **QUEUED** = sahara, multipli, mitosis, portal-bitcoin, dogeos,
  asentum, nowa-finance, allox, tastyco. **BLOCKED** = gte (captcha),
  neptune (captcha + mainnet balance), variational (captcha + mainnet
  balance), zenchain (social: X post), dextr (captcha + mainnet balance),
  abstract (captcha + mainnet balance), polyhedra (captcha), saturn (captcha).

### Saldo gas per jaringan (RPC langsung dari VM, read-only, ~08:15 WIB)
- Ethereum Sepolia: **0,1035 ETH** (naik dari 0,0535 — faucet Google Cloud
  09:00 kemarin mengisi) — di atas ambang STOP 0,01 ETH.
- Arbitrum Sepolia: **0** · Base Sepolia: **0**.
- BSC testnet: **0,0100005 BNB** (cukup untuk beberapa tx murah).
- DogeOS Chikyū: **42,0219 test DOGE** (sesudah 3 tx hari ini).
- Sahara testnet (chain 313313): **tidak terbaca** — RPC resmi timeout,
  routeme.sh rate-limited, thirdweb timeout (dari VM).
- MegaETH mainnet: **1 ETH — TIDAK DISENTUH** (aset mainnet, aturan hemat).
- Zenchain testnet: tidak terjangkau.

### Transaksi hari ini: 3 (DogeOS)
- Private key kini tersedia di worker ini via `~/workspace/wallet-bot/.privkey`
  (otorisasi user 2026-10-19 "kamu simpan aja biar ga minta terus"; TIDAK
  pernah ditulis ke log/chat). Signing via eth_account langsung ke RPC.
- 3x self-transfer 0 DOGE di DogeOS Chikyū (gas ~0,000001 DOGE total),
  semua confirmed (status 0x1):
  - 0x4dc4d31978ec9cd0f1cafce6140849e84acd6a23b8fd7b024b21292bd8b8b0e7
  - 0xe8eb997ef5a8bf8b904bf840dd9ed85da727f946fea873878e228ca638749f2d
  - 0x52843860b45849bbc02772b06b7a1515a71752360795852e8dc1a480d6b43a94
- Faucet DogeOS farming wallet: cooldown 24 jam dari klaim 2026-10-18 —
  coba lagi setelah ~15:30 WIB hari ini.

### Tidak dikerjakan (alasan)
- **Sepolia 0,1035 ETH disimpan** — tidak ada interaksi dApp yang eligible
  hari ini (Multipli butuh signup StarkNet + recaptcha; Mitosis testnet mati;
  Neptune butuh Backpack wallet). Self-transfer tanpa guna = boros, skip.
- **Sahara**: legends.saharaai.com tidak terjangkau + RPC mati dari VM;
  token SAHARA sudah live di mainnet (airdrop 8,15% sudah distribusi) —
  nilai farming testnet menurun. Butuh sesi browser wallet-connected.
- **Multipli**: faucet butuh recaptcha + signup StarkNet (laporan
  wallet-bot/MULTIPLI_FAUCET_REPORT.md) — user klaim dari HP tercepat.
- **Mitosis**: testnet mati (DNS tidak resolve). **Portal Bitcoin**: butuh
  install ekstensi Portal wallet (user). **Asentum**: menunggu user import
  farming wallet via takeover browser.
- **nowa-finance / allox / tastyco**: situs live (HTTP 200) tapi butuh
  onboarding (connect wallet + social connects + devnet funds). Social
  connects butuh izin user per aturan "login bilang dulu" — belum dikerjakan.
- 8 proyek faucet-blocked: tidak berubah (captcha / mainnet-balance / X post).

### Dibutuhkan dari user
1. Klaim faucet Multipli dari HP (testnet.multipli.fi, ~2-3 menit) — atau
   kirim JWT dari localStorage browser HP bila sudah signup.
2. X post sekali untuk unlock faucet Zenchain (blocker lama).
3. Faucet manual (captcha): Arbitrum Sepolia ETH, Base Sepolia ETH.
4. Izin + langkah untuk onboarding nowa/allox/tastyco (connect X/Telegram/
   Discord) dan install ekstensi Portal wallet / import Asentum wallet.

---

**Date:** 2026-10-18
**Wallet:** `0xf0f25C36AC70E9d787a108eFB351626192C8107b`

## Run 2026-10-18 (trigger manual user "claim testnet sekarang", ~08:38–08:50 WIB)

### farm.py
- Berjalan bersih (exit 0), log ditambah ke `logs/farm-2026-10-18.log`.
- Hasil: **QUEUED** = sahara, multipli, mitosis, portal-bitcoin.
  **BLOCKED** = gte (captcha), neptune (captcha + mainnet balance),
  variational (captcha + mainnet balance), zenchain (X post),
  dextr (captcha + mainnet balance), abstract (captcha + mainnet balance),
  polyhedra (captcha), saturn (captcha).

### Saldo gas per jaringan (RPC langsung dari VM, read-only, ~08:45 WIB)
- Ethereum Sepolia: **0,0535 ETH** (terverifikasi via RPC publik,
  cocok dengan explorer 08:26 WIB) — di atas ambang STOP 0,01 ETH.
- Arbitrum Sepolia: **0** · BNB Chain testnet: **0 BNB**.
- MegaETH (carrot.megaeth.com, chainId 0x18c7/6343 — jaringan live):
  **1,0 ETH** (cocok catatan 17 Okt; ini aset mainnet, bukan gas testnet).
- Zenchain testnet: **tidak terbaca** — endpoint unreachable dari VM.

### Hasil: 0 transaksi (blocker tidak berubah)
- **Private key wallet farming tetap tidak tersedia di worker ini.**
  `hatch-vault --help`/`list` hang tanpa output (dicoba 2x, di-kill setelah
  45 dtk); Secure Vault hanya alur capture page sisi user. Tanpa private key,
  semua interaksi on-chain (swap/stake/deposit/claim Sahara/multipli/mitosis,
  termasuk 4 proyek QUEUED) tidak bisa di-sign; browser task tanpa key hanya
  akan stall menunggu persetujuan.
- Sepolia 0,0535 ETH cukup untuk ~puluhan tx begitu key tersedia
  (prioritas: Mitosis deposit, Multipli stake Sepolia, Neptune claim/deposit).
- MegaETH 1 ETH di jaringan live — DILARANG dipakai boros (aturan hemat);
  disimpan, tidak disentuh sampai instruksi user.

### Dibutuhkan dari user (tetap)
1. Private key wallet farming via Secure Vault di chat utama (sekali pakai,
   untuk sesi signing) — ini satu-satunya blocker transaksi.
2. Faucet manual (captcha): Arbitrum Sepolia ETH, Base Sepolia ETH →
   kirim ke wallet farming. Sepolia ETH mungkin terisi via cron faucet
   Google Cloud 09:00 — cek setelah run itu.
3. X post sekali untuk unlock faucet Zenchain.

---

## Run 2026-10-18 (cron airdrop-farming-harian, 08:05–08:55 WIB)

### farm.py
- Berjalan bersih (exit 0), log: `logs/farm-2026-10-18.log`.
- Perbaikan skrip: crash `AttributeError` pada entri mitosis (field `faucet`
  berupa string, bukan dict) + `KeyError 'frequency'` — sudah diperbaiki
  (normalisasi faucet string→{}; logging pakai default). Entri mitosis di
  `projects.json` dilengkapi (dapp_url, frequency, steps).
- Hasil: **QUEUED** = sahara, multipli, mitosis. **BLOCKED** = gte (captcha),
  neptune (captcha + mainnet balance), variational (captcha + mainnet balance),
  zenchain (social: X post).

### Saldo gas per jaringan (cek explorer via browser, read-only, 08:26–08:46 WIB)
- Ethereum Sepolia: **0,0535 ETH** (2 transaksi, 2 token transfer, update terakhir blok 11937804)
- Arbitrum Sepolia: **0 ETH**
- BNB Chain testnet: **0 BNB** (tidak ada riwayat transaksi; konfirmasi juga via RPC: 0)
- MegaETH testnet: **tidak terbaca** — explorer testnet resmi sudah dipensiunkan (404/redirect ke dokumentasi mainnet; chain ID mainnet 4326)
- Zenchain testnet: **tidak terbaca** — zentrace.io tidak dapat dijangkau (TLS/QUIC error). Koreksi data: native token = **ZTC** (chain ID 8408), bukan ZCX.
- RPC langsung dari VM: 403/timeout di semua endpoint publik (IP VM diblokir WAF) kecuali BSC testnet (0).

### Hasil: tidak ada transaksi yang dibuat
- **Koreksi atas draf awal:** saldo Sepolia = 0,0535 ETH (sesuai catatan 0,05 ETH
  per 2026-10-17) — aturan STOP (< 0,01 ETH) TIDAK terpicu untuk Sepolia.
  Saldo 0 hanya di Arbitrum Sepolia dan BSC testnet.
- Namun **private key tetap tidak tersedia di worker ini**. Tidak ada konektor
  Secure Vault yang dapat dipakai dari run detached (`hatch-vault` CLI tidak
  memberi output/dok; Secure Vault = alur capture page sisi user). Semua
  interaksi on-chain (swap/stake/deposit/claim, termasuk daily task Sahara AI
  yang butuh wallet signature) tetap blocked.
- Urutan kerja user tetap berlaku: farming airdrop dikerjakan SETELAH hasil
  faucet terkonsolidasi (cron 10:00 MegaETH + 11:00 mining). Run 08:00 =
  cek + persiapan.

### Dibutuhkan dari user
1. Faucet manual (captcha): MegaETH testnet ETH, Sepolia ETH, Arbitrum Sepolia
   ETH → kirim ke wallet farming. (Google Cloud faucet cron 09:00 mungkin
   mengisi Sepolia; cek hasil cron itu.)
2. X post sekali untuk unlock faucet Zenchain.
3. Private key via Secure Vault (jalur chat utama) agar transaksi dApp bisa jalan.
4. ~~Catatan: catatan 2026-10-17 menyebut 0,05 Sepolia ETH — explorer hari ini
   menunjukkan 0 ETH tanpa riwayat transaksi; perlu verifikasi ulang.~~
   KOREKSI (laporan final browser task): Sepolia = 0,0535 ETH (2 tx) — cocok
   dengan catatan 0,05 ETH per 17 Okt; diskrepansi teratasi.

---

**Date:** 2026-10-17
**Wallet:** `0xf0f25C36AC70E9d787a108eFB351626192C8107b`

## Reconnaissance Summary (read-only, no transactions made)

### BLOCKED — Captcha (cannot automate)

| Project | Faucet | Blocker |
|---------|--------|---------|
| GTE (MegaETH) | testnet.megaeth.com | Captcha on faucet |
| Neptune | alchemy.com/faucets/ethereum-sepolia | Captcha + needs 0.001 mainnet ETH |
| Variational | alchemy.com/faucets/arbitrum-sepolia | Captcha + needs 0.001 Arb mainnet ETH |

**Root cause:** Alchemy faucets (the gas-token source for Sepolia, Arbitrum
Sepolia, Base Sepolia) require interactive captcha + a mainnet balance.
These cannot be automated. This blocks the *gas* for Neptune, Variational,
and partially Multipli/Plaza.

### BLOCKED — Social action required

| Project | Blocker |
|---------|---------|
| Zenchain | Faucet requires posting on X first |

### POTENTIALLY AUTOMATABLE (needs live browser + wallet signing)

| Project | Notes |
|---------|-------|
| Plaza Finance | Own faucet at testnet.plaza.finance ("Get Test Tokens", no captcha per guide, needs 0.001 ETH in wallet). Page is JS-heavy — needs live browser to verify. |
| Sahara AI | Daily tasks on website + Galxe quests. No captcha mentioned. Needs live browser. |
| Multipli.fi | Own token faucet ("Claim 100 USDC free") appears captcha-free, but needs ETH for gas (from Alchemy = captcha). Chicken-and-egg. |

### What was verified today
- `farm.py --check-only` runs clean; queues plaza/sahara/multipli, blocks the rest.
- MegaETH testnet page loads; faucet link present but form is JS-rendered.
- Zenchain faucet page loads; form is JS-rendered (X-post step per guide).
- Multipli testnet page loads; shows "Claim 100 USDC for free" button, links to Alchemy for ETH.

## What's needed from the user

1. **Manual faucet claims** (one-time, ~10 min): claim Sepolia ETH, Arbitrum
   Sepolia ETH, Base Sepolia ETH, and MegaETH testnet ETH from their
   respective faucets (all need captcha). Send to
   `0xf0f25C36AC70E9d787a108eFB351626192C8107b`.
   Without gas tokens, no on-chain farming is possible.
2. **Zenchain X post**: required once to unlock the ZCX faucet.
3. **Private key via Secure Vault**: when ready for the parent agent to run
   live-browser transactions.

## Automation plan (once gas is funded)

- Cron `airdrop-farming-harian` runs `farm.py` daily 08:00 WIB (logging only).
- Parent agent picks up the queued summary and runs browser tasks for:
  Plaza (faucet + earn/leverage), Sahara (daily tasks), Multipli (claim + stake),
  GTE/Neptune/Variational (dApp interactions only — faucets stay manual).
- Re-run `farm.py` after each run; update this file with results.

## Peluang Baru 2026-10-18 (airdrop-hunter-x)

Sumber: X threads @MaransCrypto via typefully mirror (diterbitkan 2026-10-17 s.d.
2026-10-18). Kandidat yang LOLOS filter dan ditambahkan ke `projects.json`
(status "queued"):

1. **Saturn BTC** (Bitcoin Testnet4) — saturnbtc.io
   - DEX/AMM Bitcoin pertama di testnet; legit (diliput CryptoBriefing &
     Cointelegraph 11/2024, kolab Arch Network).
   - Faucet gratis: faucet.testnet4.dev (captcha, 0.005 tBTC).
   - Langkah: mint runes → swap → add liquidity pool BTC/token.
   - BUTUH TINDAKAN USER: install wallet Unisat (set Testnet4 + Taproot),
     bukan EVM — di luar otomatisasi farming saat ini.

Sudah ada di sistem (tidak ditambahkan ulang): Polyhedra EXPchain, Dextr,
Portal Bitcoin, Abstract — semuanya sudah terdaftar di `projects.json`.
Tidak lolos filter hari ini: Fiamma chain (effort berat, butuh wallet Signet +
bridge 2 jam; dipantau).

## Peluang Baru 2026-10-19 (airdrop-hunter-x)

Sumber: social.search (IG/FB/Threads) + browser.search news (10/10–19/10). Tidak
ada yang lolos filter hari ini — tidak ada penambahan ke `projects.json`.

Sudah ada di sistem (tidak ditambahkan ulang): Neptune, Variational, GTE,
Zenchain, Dextr, Multipli, Saturn (semua via thread @MaransCrypto/typefully).
Ditolak sebelumnya, tetap ditolak: GIWA & Titan (riset 2026-10-18 — ketuaan /
non-EVM wallet); Extended/Starknet perp DEX (butuh modal asli, bukan gratis).
Ditolak hari ini: **deFarm** (testnet.de.farm, @deFarm_ETH) — thread Tanaka_L2
mengklaim "testnet launched October 12th" tapi FAQ resmi Coda.io berumur
907 hari (program Early Adopter/mainnet beta 2024, 7 epoch selesai); BUKAN
peluang baru, kemungkinan sudah tutup.

## 2026-10-18 — Proyek baru ditambahkan (4)
- Dextr (Base testnet, points REP, target 500k)
- Portal Bitcoin (swap BTC-EVM harian, sparks points, butuh Portal extension)
- Abstract (Pudgy Penguins L2, XP system, bridge Sepolia->Abstract)
- Polyhedra/Expchain (zkBridge infra, faucet tZKJ 3 networks)
Total proyek aktif: 11 (GTE/MegaETH tetap di list tapi testnet tidak eligible lagi)

## Run manual 2026-10-18 09:35 WIB (user: "kamu saja yang lakuin semua")
- 5 tx Sepolia terkirim (self-transfer 0 ETH, gas ~0.019 gwei, murah).
  TX: c19b9820..., 21b6458a..., f687dd9a..., 711f18a5..., bc4ad579...
- Saldo Sepolia: 0.0535 -> 0.05349999 ETH (gas hampir nol).
- ArbSepolia/BSC: 0 (skip, tidak ada gas).
- MegaETH testnet: 1 ETH tapi testnet mati (tidak dipakai).
