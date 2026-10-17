import json, subprocess, os
BASE="/home/hatch/workspace/youtube-otomatis/truecrime-en"
beats=json.load(open(f"{BASE}/script/beats-2026-10-14.json"))
outdir=f"{BASE}/audio/2026-10-14"; os.makedirs(outdir,exist_ok=True)
for b in beats:
    out=f"{outdir}/{b['id']}.mp3"
    if os.path.exists(out) and os.path.getsize(out)>5000: continue
    for att in range(2):
        r=subprocess.run(["/opt/hatch/bin/tts","speak","--voice","avocado_v2:miles","--language","en","--output",out,"--text-stdin"],input=b["text"].encode(),capture_output=True)
        if os.path.exists(out) and os.path.getsize(out)>5000: break
        print("retry",b["id"],r.stderr.decode()[-200:],flush=True)
    print(b["id"], os.path.getsize(out) if os.path.exists(out) else 0, flush=True)
print("TTS DONE")
