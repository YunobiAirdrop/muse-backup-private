#!/usr/bin/env python3
W = "/home/hatch/workspace/youtube-otomatis/weird-en"
lines = []
for i in range(1, 75):
    lines.append("file '%s/audio/b15-beat-%03d.mp3'" % (W, i))
    if i == 42:
        lines.append("file '%s/data/bumper-weird-en.mp3'" % W)
with open("/tmp/concat-b15-bumper.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print(len(lines), "entries written")
