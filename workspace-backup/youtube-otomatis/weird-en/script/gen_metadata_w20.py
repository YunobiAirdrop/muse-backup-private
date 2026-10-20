#!/usr/bin/env python3
"""Bangun upload-2026-10-20.json: metadata + chapters dari chapter-starts-w20.json.
Dijalankan SETELAH prep_audio_w20.py. thumbnail_path diisi setelah thumbnail jadi."""
import json, os

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
ch = json.load(open(os.path.join(W, "data", "chapter-starts-w20.json")))

def ts(sec):
    sec = int(sec)
    return f"{sec//60:02d}:{sec%60:02d}"

chapter_lines = "\n".join(
    f"{ts(v['start'])} {v['title']}" for k, v in sorted(ch.items(), key=lambda x: int(x[0])))

title = "7 World Records SO WEIRD They Should Be Illegal"

description = f"""A woman grew her fingernails for THIRTY years - then lost them all in one car crash. That is just ONE of 7 insane world records I am scoring 1 to 10 on the Weirdness Scale today. Who takes the crown?

I am Bo, and I did NOT believe half of this list at first - but every record is verified by Guinness World Records. From 85 spoons on one body to the loudest burp in human history (109.9 decibels!), these are the weirdest official records on the planet. My champion got a PERFECT 10 - thirty years of pure commitment.

Which one was YOUR champion? FIGHT in the comments (keep it friendly)!

CHAPTERS:
{chapter_lines}

If this broke your brain a little, subscribe to Weird World Daily - new weird facts every single day. I find this stuff so you do not have to.

More weirdness:
https://www.youtube.com/@BizarreWorldDaily
Watch next: https://youtu.be/U4UwccK9vdI

#butifyourcloseyoureyesmeme #viral #fyp #mystery #foryou"""

tags = ["world records", "weirdest world records", "guinness world records",
        "bizarre records", "strange world records", "funny world records",
        "weird facts", "unbelievable records", "longest fingernails",
        "loudest burp", "big mac record", "spoon balancing",
        "weird world daily", "records ranked", "top 7 weird records",
        "crazy records", "amazing records", "taco eating record"]

meta = {
    "title": title,
    "description": description,
    "tags": tags,
    "categoryId": "27",
    "thumbnail_path": os.path.join(W, "thumbnail-2026-10-20.jpg"),
    "video_path": os.path.join(W, "video", "2026-10-20-final.mp4"),
    "publishAt": "2026-10-21T00:00:00Z",
    "slot_target": "2026-10-21 07:00 WIB",
    "channel_id": "UCJ6KqdYvVJ-PaxhGLfTFVhA",
    "slug": "weird-en",
    "channel": "Weird World Daily",
    "pinned_comment": ("Which one was YOUR champion? I am still Team Nails - 30 years of commitment "
                       "is unbeatable. Full chapters in the description so you can rewatch your favorite!"),
    "shorts_bank": [os.path.join(W, "shorts", f"2026-10-20-s{i}.mp4") for i in (1, 2, 3)],
    "upload_steps": ("Upload as UNLISTED first via API, polish metadata, THEN set to Scheduled "
                     "(2026-10-21 07:00 WIB). AI disclosure MUST be checked in Studio session. "
                     "Comments: set EXPLICITLY to 'Allow all comments'."),
}
json.dump(meta, open(os.path.join(W, "upload-2026-10-20.json"), "w"), indent=1, ensure_ascii=False)
json.dump({}, open(os.path.join(W, "upload-2026-10-20-result.json"), "w"), indent=1)
print("title:", len(title), "chars")
print("desc:", len(description), "chars")
print("tags:", sum(len(t) for t in tags), "chars")
print("chapters:\n" + chapter_lines)
