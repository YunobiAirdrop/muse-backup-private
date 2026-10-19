# Airdrop Farm APK

Aplikasi Android (WebView) untuk pantau airdrop farming + tombol faucet manual.

## Fitur
- **Tab Dashboard**: status semua proyek, saldo, TX hari ini, perlu tindakan (dari `farming_status.json`)
- **Tab Faucet**: 3 faucet manual dengan tombol "Buka Faucet" + "Tandai Diklaim"
  - Elysium HYPE (https://elysium.kinetiq.xyz/testnet-faucet)
  - DogeOS DOGE (https://faucet.testnet.dogeos.com/)
  - Sepolia ETH Google Cloud (https://cloud.google.com/application/web3/faucet/ethereum/sepolia)
- Countdown 24 jam per faucet, tersimpan di localStorage HP
- Bahasa Indonesia, mobile-friendly

## File APK
- `airdrop-farm-debug.apk` — debug build, bisa langsung di-install di HP
  (aktifkan "Install dari sumber tidak dikenal" saat install)

## Cara build ulang
```bash
cd ~/workspace/wallet-bot/apk
./build.sh
```

Build memakai Android SDK (`~/Android/Sdk`, build-tools 34.0.0, platform android-34),
JDK 17 + Gradle tidak diperlukan (build manual via aapt2/d8/apksigner).
Tools (JDK portable + Gradle) ada di `tools/` — tidak ikut di-backup ke git.

## Struktur
```
apk/
├── app/
│   ├── build.gradle            # (referensi, build aktual via build.sh)
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── assets/www/
│       │   ├── index.html          # UI utama (dashboard + faucet)
│       │   └── farming_status.json # snapshot status (disalin saat build)
│       └── java/com/yunobi/airdropfarm/MainActivity.java
├── build.sh                    # script build manual
├── build/                      # artefak build (gen, obj, dex, apk)
├── tools/                      # JDK portable + Gradle (tidak di git)
└── airdrop-farm-debug.apk      # hasil akhir
```

## Catatan
- `farming_status.json` di-bundle saat build — jalankan `./build.sh` ulang
  untuk refresh data status sebelum install ke HP.
- Data klaim faucet tersimpan di localStorage WebView HP (tidak hilang saat update APK).
