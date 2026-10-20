import os, sys, glob
from PIL import Image
vid = sys.argv[1]
frames = sorted(glob.glob(f"fr_{vid}/f*.jpg"))
for i in range(0, len(frames), 12):
    batch = frames[i:i+12]
    imgs = [Image.open(f) for f in batch]
    w,h = imgs[0].size
    sheet = Image.new("RGB",(w*4,h*3),(0,0,0))
    for j,im in enumerate(imgs):
        sheet.paste(im,((j%4)*w,(j//4)*h))
    sheet.save(f"sheet_{vid}_{i//12:02d}.jpg", quality=70)
    print(f"sheet_{vid}_{i//12:02d}.jpg ({len(batch)} frames)")
