#!/bin/bash
# Pipeline harian info harga: ambil -> infografis -> posting (IG + Threads)
set -u
cd "$(dirname "$0")"
LOG="data/jalan-$(date +%F).log"
{
  echo "=== $(date '+%F %T') mulai ==="
  python3 ambil_harga.py || { echo "AMBIL HARGA GAGAL"; exit 1; }
  python3 buat_infografis.py || { echo "INFOGRAFIS GAGAL"; exit 1; }
  python3 posting_harga.py
  echo "=== $(date '+%F %T') selesai (exit $?) ==="
} 2>&1 | tee "$LOG"
