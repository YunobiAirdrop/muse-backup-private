# Kantor AI — APK Build

WebView wrapper untuk aplikasi Kantor AI (package `com.yunobi.kantorai`).

## Cara build APK final

1. Export HTML dari artifact:
   ```
   artifact.export(slug="kantor-ai")
   # hasil: ~/workspace/your_files/kantor-ai/kantor-ai.html
   ```
2. Copy ke assets:
   ```
   cp ~/workspace/your_files/kantor-ai/kantor-ai.html \
      ~/workspace/kantor-ai-apk/app/src/main/assets/kantor-ai.html
   ```
3. Build:
   ```
   cd ~/workspace/kantor-ai-apk && ./build.sh
   ```
4. Hasil: `app/build/kantor-ai.apk` (signed, siap install)

## Tooling (sudah terinstall)

| Komponen | Path | Versi |
|---|---|---|
| JDK | ~/jdk17 | 17.0.20.1 (Temurin) |
| Android SDK | ~/android-sdk | cmdline-tools 11076708 |
| platform-tools | ~/android-sdk/platform-tools | 37.0.1 |
| platforms;android-34 | ~/android-sdk/platforms/android-34 | API 34 |
| build-tools;34.0.0 | ~/android-sdk/build-tools/34.0.0 | 34.0.0 |
| Gradle | ~/gradle | 8.10.2 |

## Catatan teknis

- Build pakai `build.sh` (aapt2 + d8 + apksigner langsung) — TANPA Gradle,
  karena Java di VM ini tidak bisa lewat proxy egress untuk download
  dependency Maven (sdkmanager juga gagal dengan alasan yang sama;
  package SDK diinstall manual via curl).
- Signing pakai debug keystore (`debug.keystore`, password `android`) —
  cukup untuk install langsung via `adb install` / file manager.
  Untuk rilis Play Store perlu keystore production terpisah.
- Min SDK 24 (Android 7.0), target SDK 34.
- WebView load `file:///android_asset/kantor-ai.html`, JavaScript + DOM storage aktif.
