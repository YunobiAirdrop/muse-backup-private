#!/bin/bash
# Render semua segmen Lima Misteri 2026-10-14 batch kecil (<=10) lalu rakit final.
cd /home/hatch/workspace/lima-misteri
for r in "0 10" "10 20" "20 30" "30 40" "40 50" "50 60" "60 70" "70 74"; do
  echo "=== batch $r ==="
  python3 rakit_multi_2026-10-14.py $r || exit 1
done
echo "=== rakit final ==="
python3 rakit_final_2026-10-14.py || exit 1
echo "SELESAI SEMUA"
