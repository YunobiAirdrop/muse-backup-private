#!/usr/bin/env python3
"""Grid thumbnail per channel (5 thumb + judul) untuk review visual cepat."""
import json, os
from PIL import Image, ImageDraw
D = os.path.expanduser("~/workspace/youtube-otomatis/hidden_files/audit-2026-10-19")
inv = json.load(open(os.path.expanduser(
    "~/workspace/youtube-otomatis/hidden_files/audit-inventory-2026-10-19.json")))
for slug, ch in inv["channels"].items():
    cells = []
    for v in ch["videos"]:
        p = f"{D}/thumbs/{slug}__{v['videoId']}.jpg"
        if os.path.exists(p):
            im = Image.open(p).convert("RGB").resize((320,180))
            cells.append((im, v["title"][:70], v["videoId"]))
    if not cells: continue
    grid = Image.new("RGB", (320*len(cells), 180+40), (10,10,10))
    dr = ImageDraw.Draw(grid)
    for i,(im,t,vid) in enumerate(cells):
        grid.paste(im,(i*320,0)); dr.text((i*320+6,186), f"{i+1}. {t}", fill=(255,255,255))
    grid.save(f"{D}/sheets/grid-{slug}.jpg", quality=75)
    print("grid", slug)
