#!/usr/bin/env python3
"""Bangun upload-2026-10-18.json: metadata + chapters dari durasi beat.
Dijalankan SETELAH ukur_durasi_b16.py."""
import json, os

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
dj = json.load(open(os.path.join(W, "data", "durasi-beat-2026-10-18.json")))

TC = 2.5
BUMPER_AFTER = 28
starts, cum = {}, TC
for i in range(1, 75):
    starts[i] = cum
    cum += float(dj[f"b16-beat-{i:03d}"])
    if i == BUMPER_AFTER:
        cum += float(dj["b16-bumper"])

def ts(sec):
    sec = int(sec)
    return f"{sec//60:02d}:{sec%60:02d}"

chapters = [
    (1, "The 7 Weirdest Foods on Earth"),
    (9, "No.7 Century Egg - The 100-Year-Old Egg (China)"),
    (16, "No.6 Balut - The Duck Egg That Fights Back (Philippines)"),
    (23, "No.5 Escamoles - Insect Caviar (Mexico)"),
    (31, "No.4 Kopi Luwak - The $600 Poop Coffee (Indonesia)"),
    (39, "No.3 Hakarl - Poison Shark You Must Rot First (Iceland)"),
    (47, "No.2 Surstromming - Banned on Airplanes (Sweden)"),
    (55, "No.1 Casu Marzu - The Live Maggot Cheese (Italy)"),
    (68, "Final Ranking Recap"),
    (71, "Which One Would YOU Try?"),
]
chapter_lines = "\n".join(f"{ts(starts[b])} {label}" for b, label in chapters)

title = "7 Foods So Weird They Should NOT Exist!"
description = f"""There's a cheese in Italy that is still ALIVE when you eat it - and it's only number 7 on this list. From $600 poop coffee to fish that's BANNED on airplanes, these are the 7 weirdest real foods on Earth, ranked!

I'm scoring every dish on the Weirdness Scale from 1 to 10. Number one got a perfect TEN - it made me question humanity itself. Which one would YOU actually try? Tell me in the comments!

CHAPTERS:
{chapter_lines}

If this broke your brain a little, subscribe to Weird World Daily - new weird facts every single day. I find this stuff so you don't have to eat it!

More weirdness:
https://www.youtube.com/@BizarreWorldDaily

#butifyourcloseyoureyesmeme #viral #fyp #mystery #foryou"""

tags = ["weird food", "weirdest foods", "bizarre food", "strange food",
        "weird facts", "food facts", "casu marzu", "balut", "surstromming",
        "hakarl", "century egg", "kopi luwak", "escamoles",
        "grossest foods", "weird food ranking", "weird world daily"]

meta = {
    "title": title,
    "description": description,
    "tags": tags,
    "categoryId": "27",
    "thumbnail": os.path.join(W, "media-generation-thumbnail-2026-10-18-a-0-2534eb75-1c9c-4de2-bc18-d410aa63ce9a.jpg"),
    "thumbnail_variant_b": os.path.join(W, "media-generation-thumbnail-2026-10-18-b-0-f9a4e9b2-4c55-4b98-9949-4fd664775136.jpg"),
    "video_path": os.path.join(W, "video", "2026-10-18-final.mp4"),
    "publishAt": "2026-10-19T00:00:00Z",
    "slot_target": "2026-10-19 07:00 WIB",
    "pinned_comment": ("Which one would YOU actually try? Be honest! I'm still recovering from #1 "
                       "(the live maggot cheese). Full chapters in the description - jump straight to "
                       "the airplane-banned fish!"),
    "shorts_bank": [os.path.join(W, "shorts", f"2026-10-18-s{i}.mp4") for i in (1, 2, 3)],
}
json.dump(meta, open(os.path.join(W, "upload-2026-10-18.json"), "w"), indent=1, ensure_ascii=False)
print("title:", len(title), "chars")
print("desc:", len(description), "chars")
print("tags:", sum(len(t) for t in tags), "chars")
print("chapters:\n" + chapter_lines)
