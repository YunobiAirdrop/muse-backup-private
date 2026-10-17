#!/bin/bash
# Unduh 19 video materi Nutriflakes dari Google Drive publik
# Cara: ambil uuid dari halaman warning virus, lalu unduh via drive.usercontent.google.com
OUT=~/workspace/clipper-bot/materi/nutriflakes
mkdir -p "$OUT"
IDS="12xsovOxDNVo7gT35Pz3J2E32I-Sk2Va5 13_el7awhd0dartnZti_bJf_kMUqEkf5H 17C9c9zt9Valw5fm3fwpgsUn7TPpkWkLX 1DKeWt9exfR_vbquOiHkWvLxvDBITDllS 1EV_NK_1lSOI2o6Xfsw2aqNWxsnuaY0dc 1eBr8MHXR-EZ8tp5DBXvIzVMrq3RDl6Nt 1jD9EjK2RBv50-7fRh7KuNV0BPyzOOqus 1uq_6k3ktGNkdt3a0v1iae2VvmKSvwFWh 12_CO0insMtADpaQScLCDqtvSxW732kpN 147kRo3hmB4JLgg3Avi9AtVa_bEm6gtav 1ATfrkdsSUADCgimdhW-Ecfs1YAvZGCb2 1C3lgIcYCNHbFMNYJepbmoRFCl3SRmOx8 1Dw9NSwvBNJZbkBIn8C-3uVLOBhaGzvPz 1FQjIXuoz_D5HETSY-D7ZTUc8DfAuvaAE 1NHCJ5eDuTpQxpJA7AIy9F90qkVbPAAsN 1Su-qTep-PxhQbHkM6I0nULJiutPIjyFf 1XpchyveL6J-Mn0eDlPDRsWfxkALDSPzx 1cpes7kUgt-qba2IDI_S9wX55ovePk95I 1qlUa5ngBLitwxuVCk0BYTeN4UN1xxA_F"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
n=0
for id in $IDS; do
  n=$((n+1))
  warn=$(curl -sL --max-time 30 "https://drive.google.com/uc?export=download&id=$id" -A "$UA")
  uuid=$(echo "$warn" | grep -o 'name="uuid" value="[^"]*"' | head -1 | cut -d'"' -f4)
  fname=$(echo "$warn" | grep -o "/open?id=$id\">[^<]*<" | head -1 | sed "s|/open?id=$id\">||;s|<$||")
  [ -z "$fname" ] && fname="file_$id.mp4"
  # sanitasi nama file
  fname=$(echo "$fname" | tr '/' '_' | tr -d '\r')
  dest="$OUT/$fname"
  if [ -f "$dest" ] && [ $(stat -c%s "$dest") -gt 5000000 ]; then
    echo "[$n/19] SKIP sudah ada: $fname"
    continue
  fi
  echo "[$n/19] Unduh: $fname"
  if [ -z "$uuid" ]; then
    curl -sL --max-time 900 "https://drive.google.com/uc?export=download&id=$id" -A "$UA" -o "$dest"
  else
    curl -sL --max-time 900 "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t&uuid=$uuid" -A "$UA" -o "$dest"
  fi
  sz=$(stat -c%s "$dest" 2>/dev/null || echo 0)
  ftype=$(file -b "$dest" 2>/dev/null | cut -c1-40)
  echo "[$n/19] -> $sz bytes | $ftype"
  sleep 2
done
echo "=== SELESAI ==="
ls -lh "$OUT" | head -25
du -sh "$OUT"
