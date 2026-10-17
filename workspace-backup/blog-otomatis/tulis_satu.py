#!/usr/bin/env python3
"""Tulis 1 artikel dari antrean (tahan restart: 1 proses = 1 artikel).
Pakai: ./venv/bin/python tulis_satu.py --blog kabarviral --index 0 --out data/mini-0.json
"""
import argparse, json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

ap = argparse.ArgumentParser()
ap.add_argument("--blog", required=True)
ap.add_argument("--index", type=int, required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--batch", default=None, help="file batch snapshot (default: antrean-<blog>.json)")
ap.add_argument("--key-idx", default=None, help="pakai key tertentu saja, misal '6,7,8' (hemat waktu, skip key habis)")
ap.add_argument("--model", default=None, help="pakai 1 model saja, misal 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free'")
a = ap.parse_args()

sys.argv = ["tulis_ulang.py", "--blog", a.blog]
src = open(os.path.join(BASE, "tulis_ulang.py")).read().split("def main():")[0]
g = {"__name__": "__lib__", "__file__": "tulis_ulang.py"}
exec(compile(src, os.path.join(BASE, "tulis_ulang.py"), "exec"), g)
if a.model:
    g["MODELS"] = [a.model]

batch_path = a.batch or os.path.join(DATA, f"antrean-{a.blog}.json")
antrean = json.load(open(batch_path))
item = antrean[a.index]
if a.key_idx:
    import re
    env = open(os.path.expanduser("~/.hermes/.env")).read()
    allkeys = re.search(r"OPENROUTER_KEYS=(\S+)", env).group(1).split(",")
    idxs = [int(x) for x in a.key_idx.split(",")]
    # coba key yang ditentukan satu per satu (tanpa key yang sudah habis)
    art = None
    last_err = None
    for i in idxs:
        try:
            art = g["tulis_ulang"](item, api_key=allkeys[i])
            break
        except RuntimeError as e:
            last_err = str(e)
            if "QUOTA_HABIS" not in str(e):
                break
    if art is None:
        raise RuntimeError(last_err or "semua key gagal")
else:
    art = g["tulis_ulang"](item)
json.dump([art], open(a.out, "w"), ensure_ascii=False, indent=1)
print(f"OK: {art['judul'][:60]}")
