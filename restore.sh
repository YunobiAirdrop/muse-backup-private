#!/bin/bash
# Restore secrets dari repo private ini ke VM baru.
# Cara pakai: ./restore.sh
# Script akan minta password dekripsi (yang dikasih waktu setup awal).

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUNDLE="$SCRIPT_DIR/secrets/secrets-bundle.tar.gz.gpg"

if [ ! -f "$BUNDLE" ]; then
  echo "ERROR: $BUNDLE tidak ditemukan."
  exit 1
fi

echo "=== Restore secrets Yunobi ==="
echo ""
read -rsp "Masukkan password dekripsi: " DECPW
echo ""

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

printf '%s' "$DECPW" | gpg --batch --yes --pinentry-mode loopback \
  --passphrase-fd 0 -d -o "$TMPDIR/bundle.tar.gz" "$BUNDLE" 2>/dev/null \
  || { echo "ERROR: password salah atau file rusak."; exit 1; }

unset DECPW

mkdir -p ~/.hermes
tar xzf "$TMPDIR/bundle.tar.gz" -C / 2>/dev/null \
  || tar xzf "$TMPDIR/bundle.tar.gz" -C "$TMPDIR/extract" --strip-components=0

# Pastikan permission ketat untuk file secret
chmod 600 ~/.hermes/.env ~/.hermes/.dashboard-pw \
  ~/.hermes/blogger-tokens.json ~/.hermes/google-oauth-blogger.env \
  ~/.hermes/youtube-stream-keys.env ~/.hermes/yt-dashboard-deploy.json \
  ~/.hermes/yt-firebase-hosting.json ~/.hermes/yt-firebase.json \
  ~/.hermes/yt-ga4.json ~/.hermes/github-dashboard-token 2>/dev/null || true
chmod 700 ~/.hermes/yt-growth/tokens 2>/dev/null || true

echo ""
echo "=== Selesai ==="
echo "File secret sudah dikembalikan ke ~/.hermes/"
echo "Cek: ls -la ~/.hermes/"
echo ""
echo "Langkah lanjut manual (kalau perlu):"
echo "  1. gh auth login  (pakai token GitHub kamu)"
echo "  2. Verifikasi: python3 ~/workspace/youtube-otomatis/yt-growth/venv/bin/python -c 'import google.auth; print(\"ok\")'"
