#!/bin/bash
# Download batch-1 videos
cd ~/workspace/youtube-otomatis/hidden_files/audit-2026-10-20/batch1
declare -A VIDS
VIDS=(
  [empires-en]="3fa6GubAvA4 0hbkORJAraU xN8si7OLEIc XBDTTZi5M_Y"
  [history-en]="iKD-nacbENU 8AGtu8ZpZxY ZnRBZex_avc E-Jo0o3EMNI udWq3_5VzPk"
  [horor]="N76GKq36LPQ t9Y8URnq_vY V1XVDiCeBtc -k5qqlU3JR8 vVdcMjV6MDs"
  [horror-en]="apAsm6MGlzU dNijEy2ksf8 h3rtMV35ZeQ mjlUM9FCW5E HHFNynfnmek"
)
for slug in "${!VIDS[@]}"; do
  for vid in ${VIDS[$slug]}; do
    f="${slug}__${vid}.mp4"
    if [ -f "$f" ]; then echo "SKIP ada: $f"; continue; fi
    echo "=== Download $slug/$vid ==="
    ok=0
    for attempt in 1 2; do
      if ~/.local/bin/yt-dlp -q --no-warnings --extractor-args "youtube:player_client=android" \
        --no-playlist -f "b[height<=480]/b" --merge-output-format mp4 \
        -o "$f" "https://www.youtube.com/watch?v=${vid}" 2>/tmp/dlerr.txt; then
        ok=1; break
      fi
      err=$(cat /tmp/dlerr.txt | head -3)
      echo "attempt $attempt gagal: $err"
    done
    if [ $ok -eq 0 ]; then
      echo "TIDAK_TERDOWNLOAD: $slug $vid" >> failed.txt
    else
      echo "OK: $f ($(du -h $f | cut -f1))"
    fi
  done
done
echo "SELESAI DOWNLOAD"
