#!/bin/bash
# Build script untuk Airdrop Farm APK
# Jalankan: ./build.sh
set -e

APK_DIR="$(cd "$(dirname "$0")" && pwd)"
export ANDROID_HOME=~/Android/Sdk
export JAVA_HOME=$APK_DIR/tools/jdk
export PATH=$JAVA_HOME/bin:$PATH

cd "$APK_DIR"
mkdir -p build/gen build/obj build/dex

echo "=== 1. Sync farming_status.json ==="
cp ~/workspace/wallet-bot/farming_status.json app/src/main/assets/www/farming_status.json

echo "=== 2. aapt2 compile (res) ==="
$ANDROID_HOME/build-tools/34.0.0/aapt2 compile --dir app/src/main/res -o build/compiled_res.zip

echo "=== 3. aapt2 link ==="
$ANDROID_HOME/build-tools/34.0.0/aapt2 link -o build/app-unaligned.apk \
  --manifest app/src/main/AndroidManifest.xml \
  -I $ANDROID_HOME/platforms/android-34/android.jar \
  -A app/src/main/assets \
  -R build/compiled_res.zip \
  --java build/gen

echo "=== 4. javac ==="
javac -source 17 -target 17 -cp $ANDROID_HOME/platforms/android-34/android.jar -d build/obj \
  $(find app/src/main/java -name "*.java") $(find build/gen -name "*.java")

echo "=== 5. d8 (dex) ==="
$ANDROID_HOME/build-tools/34.0.0/d8 --lib $ANDROID_HOME/platforms/android-34/android.jar \
  --output build/dex $(find build/obj -name "*.class")

echo "=== 6. Package + sign + align ==="
cp build/app-unaligned.apk build/app.apk
(cd build && $JAVA_HOME/bin/jar uf app.apk -C dex classes.dex)
$ANDROID_HOME/build-tools/34.0.0/zipalign -f 4 build/app.apk build/app-aligned.apk
$ANDROID_HOME/build-tools/34.0.0/apksigner sign \
  --ks build/debug.keystore --ks-pass pass:android \
  --out build/airdrop-farm-debug.apk build/app-aligned.apk

cp build/airdrop-farm-debug.apk ./airdrop-farm-debug.apk
echo ""
echo "✅ APK: $APK_DIR/airdrop-farm-debug.apk"
ls -lh ./airdrop-farm-debug.apk
