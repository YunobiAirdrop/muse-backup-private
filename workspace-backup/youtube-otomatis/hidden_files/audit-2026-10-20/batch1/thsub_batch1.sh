#!/bin/bash
cd ~/workspace/youtube-otomatis/hidden_files/audit-2026-10-20/batch1
VIDS="3fa6GubAvA4 0hbkORJAraU xN8si7OLEIc XBDTTZi5M_Y
iKD-nacbENU 8AGtu8ZpZxY ZnRBZex_avc E-Jo0o3EMNI udWq3_5VzPk
N76GKq36LPQ t9Y8URnq_vY V1XVDiCeBtc -k5qqlU3JR8 vVdcMjV6MDs
apAsm6MGlzU dNijEy2ksf8 h3rtMV35ZeQ mjlUM9FCW5E HHFNynfnmek"
SLUGS="empires-en empires-en empires-en empires-en
history-en history-en history-en history-en history-en
horor horor horor horor horor
horror-en horror-en horror-en horror-en horror-en"
arr_v=($VIDS); arr_s=($SLUGS)
i=0
while [ $i -lt ${#arr_v[@]} ]; do
  vid=${arr_v[$i]}; slug=${arr_s[$i]}
  th="th_${vid}.jpg"
  if [ ! -f "$th" ]; then
    curl -sL --max-time 30 "https://i.ytimg.com/vi/${vid}/hqdefault.jpg" -o "$th" && echo "TH OK $vid" || echo "TH FAIL $vid"
  fi
  # subs
  if ! ls "${slug}__${vid}".*.vtt >/dev/null 2>&1; then
    ~/.local/bin/yt-dlp -q --no-warnings --extractor-args "youtube:player_client=android" \
      --no-playlist --write-auto-subs --write-subs --sub-langs "en,id" --sub-format vtt --skip-download \
      -o "${slug}__${vid}.%(ext)s" "https://www.youtube.com/watch?v=${vid}" 2>>subserr.log && echo "SUB OK $vid" || echo "SUB FAIL $vid"
  fi
  i=$((i+1))
done
echo "SELESAI TH+SUB"
