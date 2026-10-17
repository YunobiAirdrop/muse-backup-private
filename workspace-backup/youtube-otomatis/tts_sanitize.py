#!/usr/bin/env python3
"""Sanitasi teks SEBELUM dikirim ke TTS — WAJIB dipakai semua channel.

Kasus 2026-10-13: penonton (@benbiddle1373) komplain voiceover ikut mengucapkan
kata "Narrator" karena skrip TTS history-en diawali label "Narrator: ".
Label sutradara/pembicara adalah DIREKTIF NASKAH, bukan untuk diucapkan.

Aturan: JANGAN PERNAH mengumpan label, stage direction, atau markup ke TTS.
Pakai bersihkan_teks_tts() di setiap worker TTS, lalu validasi_teks_tts()
sebelum render final.
"""
import re

_LABEL_AWAL = re.compile(
    r'^\s*[\[\(]?\s*(narrator|narator|host|narrasi|voiceover|voice over)\s*[\]\)]?\s*[:\-–—]\s*',
    flags=re.I,
)
_BRACKET_AWAL = re.compile(r'^\s*\[[^\]\n]{1,60}\]\s*')
_SCENE_AWAL = re.compile(r'^\s*(scene|chapter|part|bagian|segmen)\s+\d+[a-z]?\s*[:\-–—]\s*', flags=re.I)


def bersihkan_teks_tts(text: str) -> str:
    """Buang label/stage-direction dari awal teks. Idempoten."""
    t = (text or "").strip()
    prev = None
    while prev != t:
        prev = t
        t = _LABEL_AWAL.sub('', t)
        t = _BRACKET_AWAL.sub('', t)
        t = _SCENE_AWAL.sub('', t)
        t = t.strip()
    # normalisasi spasi ganda sisa penghapusan
    t = re.sub(r'[ \t]{2,}', ' ', t)
    return t.strip()


def validasi_teks_tts(text: str) -> list:
    """Kembalikan daftar masalah jika teks masih mengandung label terlarang."""
    masalah = []
    t = (text or "").strip()
    if _LABEL_AWAL.match(t):
        masalah.append("label pembicara (Narrator:/Host:) di awal teks ikut terbaca TTS")
    if re.search(r'(?<!\w)(narrator|narator)\s*:', t, flags=re.I):
        masalah.append("kata 'Narrator:' muncul di dalam teks")
    return masalah


if __name__ == "__main__":
    uji = [
        "Narrator: In 1815, Mount Tambora erupted.",
        "[Narrator] In 1815, Mount Tambora erupted.",
        "NARRATOR - In 1815, Mount Tambora erupted.",
        "[pause] In 1815, Mount Tambora erupted.",
        "Scene 3: In 1815, Mount Tambora erupted.",
        "In 1815, Mount Tambora erupted.",  # bersih -> tetap
    ]
    for u in uji:
        b = bersihkan_teks_tts(u)
        print(f"IN : {u}\nOUT: {b}\nOK : {not validasi_teks_tts(b)}\n")
