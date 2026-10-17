#!/usr/bin/env python3
"""Runner thread_gen dengan model NON-reasoning dulu (hindari 'thinking process' leak).
Patch sementara sesuai pelajaran AGENTS.md; tidak mengubah thread_gen.py asli.
"""
import sys, os
BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
sys.path.insert(0, BASE)

src = open(os.path.join(BASE, "thread_gen.py")).read()

# 1. Model non-reasoning dulu
src = src.replace(
    'ROUTER_URL, MODELS, get_api_keys = _g["ROUTER_URL"], _g["MODELS"], _g["get_api_keys"]',
    'ROUTER_URL, MODELS, get_api_keys = _g["ROUTER_URL"], _g["MODELS"], _g["get_api_keys"]\n'
    'MODELS = ["google/gemma-4-26b-a4b-it:free", "qwen/qwen3.8-27b:free", '
    '"inclusionai/ling-3.0-flash-sante:free", "google/gemma-4-31b-it:free"]'
)
# 2. System prompt: larang monolog internal + validasi tolak leak
src = src.replace(
    'json={"model": model, "messages": [{"role": "user", "content": msg}],',
    'json={"model": model, "messages": ['
    '{"role": "system", "content": "Jawab LANGSUNG tanpa proses berpikir, tanpa monolog internal, '
    'tanpa teks pembuka/penutup. Hanya keluarkan output yang diminta."}, '
    '{"role": "user", "content": msg}],'
)
src = src.replace(
    'teks = obj["choices"][0]["message"]["content"].replace("```json", "").replace("```", "").strip()',
    'teks = obj["choices"][0]["message"]["content"].replace("```json", "").replace("```", "").strip()\n'
    '                _low = teks.lower()\n'
    '                if "thinking process" in _low or "here\'s a thinking" in _low or "here is a thinking" in _low:\n'
    '                    raise ValueError("reasoning leak ditolak")'
)

_f = os.path.join(BASE, "thread_gen_nr.py")
exec(compile(src, _f, "exec"), {"__name__": "__main__", "__file__": _f})
