#!/usr/bin/env python3
"""Sisipkan 16 beat detail ke beats-2026-10-14.json TANPA mengubah teks 72 beat lama.
Output: beats JSON baru (88 beat, ID baru), peta old_id->new_id, daftar ID baru utk TTS,
dan beat anchor baru (CTA, reveal). Gambar/mp3 lama di-rename mengikuti peta."""
import json, os, shutil

BASE = "/home/hatch/workspace/youtube-otomatis/truecrime-en"
STYLE = "2D digital storybook illustration, dark noir documentary style, 16:9, cinematic, no text, no watermark"

# (sisip SETELAH old_id, text, image_prompt)
NEW = [
 (5,  "She was a collector with a fortune — and a taste that shocked polite Boston society.",
  "Wealthy 1890s woman buying paintings in a Paris art gallery, dealers bowing, opulent"),
 (9,  "Her will also demanded the museum stay open to the public forever — art for everyone.",
  "Museum grand doors opening to a crowd of visitors in 1903, daylight, welcoming"),
 (12, "Rick was a musician in a local band; Randy was a college kid working the night shift.",
  "Young man playing electric guitar in a small smoky club, 1990, stage lights"),
 (15, "The museum's rule was simple: never open the door for anyone after hours. Rick broke it.",
  "Security guard rulebook with red warning stamp on a desk, museum office at night"),
 (17, "The warrant was a lie — a trick to pull Rick away from the panic button.",
  "Red panic button mounted under a security desk, close-up, dramatic"),
 (23, "Experts later said the cuts were clumsy — the work of thieves, not connoisseurs.",
  "Art expert with magnifying glass examining a torn canvas edge, museum lab"),
 (30, "They ignored far more valuable pieces nearby — proof they came with a shopping list.",
  "Thieves with flashlights walking past a priceless large Titian painting, ignoring it"),
 (34, "The museum's director arrived at dawn — and went pale in the Dutch Room doorway.",
  "Shocked museum director standing in a gallery doorway staring at empty frames, dawn light"),
 (42, "Another theory names a Boston gangster who allegedly hid the art as mob collateral.",
  "Gangster hiding rolled-up paintings behind crates in a dark warehouse, 1990s"),
 (44, "The announcement named no names — only that the thieves belonged to a criminal organization.",
  "FBI document with names blacked out by redaction bars, official stamp"),
 (49, "The museum doubled down too — those empty frames are now the most famous frames in America.",
  "Tourists photographing empty ornate frames in a museum, famous exhibit, daylight"),
 (51, "Interpol's stolen art database lists all thirteen — flagged in every auction house on Earth.",
  "Computer screen showing Interpol stolen art database with red flagged paintings"),
 (54, "In 2021, Netflix released a whole docuseries on the heist — and still, no answers.",
  "Television screen showing a true crime docuseries title about an art heist, living room at night"),
 (56, "A Dutch Room guard today will tell you: the frames are part of the exhibit now.",
  "Museum guard talking to visitors beside empty golden frames, elegant gallery"),
 (57, "The FBI still takes tips on its website. The file number has never been closed.",
  "Computer screen showing an FBI tip submission form about stolen artwork"),
 (60, "Some say the art was destroyed in the nineties. The museum refuses to believe that.",
  "Determined museum director shaking his head in a gallery, resolute, daylight"),
]

beats = json.load(open(f"{BASE}/script/beats-2026-10-14.json"))
insert_map = {}
for after_old, text, img in NEW:
    insert_map.setdefault(after_old, []).append((text, img))

out, idmap, new_ids = [], {}, []
n = 0
for b in beats:
    old = b["id"]
    n += 1
    nb = {"id": f"beat-{n:03d}", "text": b["text"], "image": b["image"]}
    if "overlay" in b:
        nb["overlay"] = b["overlay"]
    idmap[old] = nb["id"]
    out.append(nb)
    oldnum = int(old.split("-")[1])
    for text, img in insert_map.get(oldnum, []):
        n += 1
        nid = f"beat-{n:03d}"
        out.append({"id": nid, "text": text, "image": f"{img}, {STYLE}"})
        new_ids.append(nid)

assert len(out) == 88, len(out)

# anchor baru: cari beat berisi teks kunci
def find(sub):
    return next(b["id"] for b in out if sub in b["text"])
anchors = {
    "cta": find("hit subscribe. Dark Case Files drops a new case every day"),
    "reveal": [find("most valuable stolen painting"), find("know WHO stole the art"),
               find("half a billion dollars. The largest art theft")],
}

json.dump(out, open(f"{BASE}/script/beats-2026-10-14.json", "w"), indent=1)
full = "\n\n".join(b["text"] for b in out)
open(f"{BASE}/script/2026-10-14.txt", "w").write(full)
open(f"{BASE}/script/narasi-2026-10-14.txt", "w").write(full)
json.dump({"idmap": idmap, "new_ids": new_ids, "anchors": anchors, "total": len(out),
           "words": sum(len(b["text"].split()) for b in out)},
          open(f"{BASE}/script/extend-map-2026-10-14.json", "w"), indent=1)

# rename gambar + mp3 lama mengikuti idmap
ren = 0
for old, new in idmap.items():
    for d, ext in [(f"{BASE}/gambar/2026-10-14", ".jpg"),
                   (f"{BASE}/audio/2026-10-14", ".mp3")]:
        s, t = f"{d}/{old}{ext}", f"{d}/{new}{ext}"
        if os.path.exists(s) and not os.path.exists(t):
            os.rename(s, t)
            ren += 1
print(f"beats={len(out)} words={sum(len(b['text'].split()) for b in out)} renames={ren}")
print("anchors:", json.dumps(anchors))
print("new_ids:", ",".join(new_ids))
