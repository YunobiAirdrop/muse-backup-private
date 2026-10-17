#!/bin/bash
# Pipeline harian loker: agregasi -> tulis -> siapkan posting web UI.
# Browser task (spawn oleh agen cron) yang eksekusi posting sebenarnya.
set -e
cd "$(dirname "$0")"
PY="${PY:-python3}"

echo "=== [1/3] Agregasi loker ==="
$PY -u agregasi_loker.py

echo "=== [2/3] Tulis artikel ==="
$PY -u tulis_loker.py

echo "=== [3/3] Siapkan posting web UI ==="
$PY -u posting_web.py

echo "Pipeline loker selesai."
