#!/usr/bin/env python3
"""Regenerasi chapters-alexandria.json dengan timestamp yang BENAR
(timestamp mulai beat-n dipasangkan dengan judul beat-n)."""
import json

BASE = "/home/hatch/workspace/youtube-otomatis/empires-en"
db = json.load(open(f"{BASE}/durasi-beat-alexandria.json"))
titles = {
    1: "The Night We Lost Everything",
    2: "Alexandria Today",
    3: "One Scroll to Save",
    4: "Alexander's Dream",
    5: "The Wild Idea",
    6: "The First Copyright Pirates",
    7: "Inside the Brain of the World",
    8: "The First Search Engine",
    9: "Measuring the Earth",
    10: "Medicine Is Born Here",
    11: "Paid to Wonder",
    12: "The Fire",
    13: "48 BC: Caesar's Torch",
    14: "Midnight at the Harbor",
    15: "The Slow Death",
    16: "What We Lost",
    17: "A Scroll Could Rewrite History",
    18: "Cleopatra's Last Light",
    19: "The Sunken Library",
    20: "The Digs Go On",
    21: "Sentences from the Fire",
    22: "The Library Rises Again",
    23: "Memory Is a Choice",
    24: "Next: Pompeii",
}
ch = ["0:00 " + titles[1]]
cum = db["beat-000"]
for n in range(1, 24):
    cum += db[f"beat-{n:03d}"]
    m, s = divmod(int(cum), 60)
    ch.append(f"{m}:{s:02d} " + titles[n + 1])
json.dump(ch, open(f"{BASE}/chapters-alexandria.json", "w"), indent=1)
print("\n".join(ch))
print("total:", len(ch))
