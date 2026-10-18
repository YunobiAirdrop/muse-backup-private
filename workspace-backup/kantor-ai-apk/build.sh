#!/bin/bash
# Build APK Kantor AI — WebView wrapper untuk kantor-ai.html
# Usage: ./build.sh
# Output: app/build/kantor-ai.apk (signed, zipaligned)
set -e

PROJ=~/workspace/kantor-ai-apk
SDK=~/android-sdk
JDK=~/jdk17
BT=$SDK/build-tools/34.0.0
PLATFORM=$SDK/platforms/android-34/android.jar
OUT=$PROJ/app/build

export JAVA_HOME=$JDK
export PATH=$JDK/bin:$PATH
# apksigner butuh java di PATH (sudah di atas)

echo "=== 1. Cek assets/kantor-ai.html ==="
if [ ! -f "$PROJ/app/src/main/assets/kantor-ai.html" ]; then
    echo "ERROR: kantor-ai.html belum ada di assets/."
    echo "Export dulu via artifact.export -> copy ke app/src/main/assets/kantor-ai.html"
    exit 1
fi

echo "=== 2. Compile resources (aapt2) ==="
rm -rf $OUT && mkdir -p $OUT/compiled_res $OUT/gen
$BT/aapt2 compile --dir $PROJ/app/src/main/res -o $OUT/compiled_res/

echo "=== 3. Link (buat base APK) ==="
$BT/aapt2 link -o $OUT/base.apk \
    -I $PLATFORM \
    --manifest $PROJ/app/src/main/AndroidManifest.xml \
    --java $OUT/gen \
    $OUT/compiled_res/*.flat \
    --min-sdk-version 24 --target-sdk-version 34 \
    --version-code 1 --version-name "1.0"

echo "=== 4. Compile Java ==="
mkdir -p $OUT/classes
find $OUT/gen $PROJ/app/src/main/java -name "*.java" > $OUT/sources.txt
javac -source 8 -target 8 -bootclasspath $PLATFORM \
    -d $OUT/classes @$OUT/sources.txt

echo "=== 5. DEX (d8) ==="
mkdir -p $OUT/dex
$BT/d8 --lib $PLATFORM --min-api 24 \
    --output $OUT/dex $(find $OUT/classes -name "*.class")

echo "=== 6. Tambah classes.dex + assets ke APK ==="
cp $OUT/base.apk $OUT/unsigned.apk
cd $OUT/dex && zip -q ../unsigned.apk classes.dex && cd - > /dev/null
cd $PROJ/app/src/main && zip -q -r $OUT/unsigned.apk assets && cd - > /dev/null

echo "=== 7. Zipalign ==="
$BT/zipalign -f 4 $OUT/unsigned.apk $OUT/aligned.apk

echo "=== 8. Sign (debug key) ==="
KEYSTORE=$PROJ/debug.keystore
if [ ! -f "$KEYSTORE" ]; then
    keytool -genkeypair -keystore $KEYSTORE -alias kantorai \
        -keyalg RSA -keysize 2048 -validity 10950 \
        -storepass android -keypass android \
        -dname "CN=Yunobi, OU=KantorAI, O=Yunobi, C=ID" 2>/dev/null
fi
printf 'android\nandroid\n' | $BT/apksigner sign --ks $KEYSTORE \
    --out $OUT/kantor-ai.apk $OUT/aligned.apk

echo ""
echo "=== SELESAI ==="
ls -lh $OUT/kantor-ai.apk
$BT/apksigner verify --print-certs $OUT/kantor-ai.apk 2>/dev/null | head -3
