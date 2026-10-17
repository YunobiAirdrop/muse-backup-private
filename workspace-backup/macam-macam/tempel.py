#!/usr/bin/env python3
"""Kartun-tempel compositing untuk channel Macam Macam (@MacamMacamID).

Mengubah foto mentah per item jadi stiker kartun: cutout (rembg u2netp) →
threshold alpha 128 (buang ghosting semi-transparan) → crop ke bbox objek →
thumbnail max 820x1000 (agar zoom Ken Burns 8% tidak motong tepi) →
outline putih gaya stiker → tempel ke background kartun 1080x1920.
Lalu update tema/<slug>.json: item[i]["foto_lokal"] = hasil tempel.

Pakai:
    python3 tempel.py <slug-tema> [--background path-ke-bg] [--cek-saja]

Baca : tema/<slug>.json  (item[i]["foto_lokal"] menunjuk foto mentah)
Tulis: work/<slug>-part<N>/cutout/itemNN.png, work/<slug>-part<N>/tempel/itemNN.jpg
       + update tema/<slug>.json

Resep ini mereplikasi persis langkah manual yang dipakai untuk video perdana
truk-part1 (disetujui user 2026-10-10): rembg venv + threshold 128 + outline putih,
stiker center-x, titik tengah vertikal ~37% frame (area bawah kosong untuk teks
nama di y=h-380, area atas kosong untuk CTA di y=120).
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageFilter

BASE = Path.home() / "workspace" / "macam-macam"
TEMA_DIR = BASE / "tema"
VENV_PY = BASE / "venv" / "bin" / "python"
BG_DEFAULT = (BASE / "branding" /
              "media-generation-macam-macam-bg-truk-0-a48e9594-ab3a-4d15-b9cd-958b41a1b6d0.webp")

CUTOUT_SCRIPT = r"""
import sys
from rembg import remove, new_session
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
out = remove(im, session=new_session("u2netp"))
out.save(dst)
"""

# stiker: batas maksimum (sebelum outline), agar zoom Ken Burns 8% aman
STIKER_MAX_W, STIKER_MAX_H = 790, 940
OUTLINE_PX = 15
# posisi stiker: center-x, titik tengah vertikal 37% dari tinggi frame
STIKER_CY_FRAC = 0.37
FRAME_W, FRAME_H = 1080, 1920


def cutout(src: Path, dst: Path) -> None:
    r = subprocess.run([str(VENV_PY), "-c", CUTOUT_SCRIPT, str(src), str(dst)],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not dst.exists():
        raise RuntimeError(f"rembg gagal untuk {src.name}: {r.stderr[-300:]}")


def threshold_alpha(img: Image.Image) -> Image.Image:
    """Alpha >128 jadi 255, sisanya 0 (buang ghosting semi-transparan)."""
    a = img.getchannel("A")
    a = a.point(lambda v: 255 if v > 128 else 0)
    img.putalpha(a)
    return img


def buat_stiker(cut: Image.Image) -> Image.Image:
    """Crop bbox → thumbnail → outline putih gaya stiker. Kembalikan RGBA."""
    cut = threshold_alpha(cut)
    bbox = cut.getchannel("A").getbbox()
    if not bbox:
        raise RuntimeError("cutout kosong — foto terlalu gelap/tidak ada objek jelas")
    cut = cut.crop(bbox)
    cut.thumbnail((STIKER_MAX_W, STIKER_MAX_H), Image.LANCZOS)
    # outline: mask di-dilate OUTLINE_PX, siluet putih di belakang cutout
    mask = cut.getchannel("A")
    dil = mask.filter(ImageFilter.MaxFilter(2 * OUTLINE_PX + 1))
    w, h = cut.size
    SW, SH = w + 2 * OUTLINE_PX, h + 2 * OUTLINE_PX
    dil_full = Image.new("L", (SW, SH), 0)
    dil_full.paste(dil, (OUTLINE_PX, OUTLINE_PX))
    stiker = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    putih = Image.new("RGBA", (SW, SH), (255, 255, 255, 255))
    stiker.paste(putih, (0, 0), dil_full)
    stiker.paste(cut, (OUTLINE_PX, OUTLINE_PX), cut)
    return stiker


def tempel_satu(src_foto: Path, background: Path, dst: Path) -> None:
    kerja = dst.parent.parent
    cut_path = kerja / "cutout" / (dst.stem + ".png")
    cut_path.parent.mkdir(parents=True, exist_ok=True)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not cut_path.exists():
        cutout(src_foto, cut_path)
    cut = Image.open(cut_path).convert("RGBA")
    stiker = buat_stiker(cut)
    bg = Image.open(background).convert("RGB").resize((FRAME_W, FRAME_H), Image.LANCZOS)
    x = (FRAME_W - stiker.width) // 2
    y = int(FRAME_H * STIKER_CY_FRAC - stiker.height / 2)
    y = max(140, min(y, FRAME_H - 420 - stiker.height))  # jaga area CTA atas & teks bawah
    bg.paste(stiker, (x, y), stiker)
    bg.save(dst, quality=92)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("pakai: python3 tempel.py <slug-tema> [--background path] [--cek-saja]")
        sys.exit(1)
    slug = args[0]
    cek_saja = "--cek-saja" in sys.argv
    bg_arg = None
    for i, a in enumerate(sys.argv):
        if a == "--background" and i + 1 < len(sys.argv):
            bg_arg = Path(sys.argv[i + 1])

    tema_path = TEMA_DIR / f"{slug}.json"
    tema = json.loads(tema_path.read_text())
    part = tema.get("part", 1)
    background = Path(tema.get("background", "")) if tema.get("background") else None
    background = bg_arg or background or BG_DEFAULT
    if not background.exists():
        raise RuntimeError(f"background tidak ada: {background}")

    kerja = BASE / "work" / f"{slug}-part{part}"
    items = tema["items"]
    for i, it in enumerate(items):
        src = Path(it["foto_lokal"])
        if "tempel" in str(src):
            print(f"  skip item{i:02d} (sudah tempel)")
            continue
        if not src.exists():
            raise RuntimeError(f"foto mentah tidak ada: {src}")
        dst = kerja / "tempel" / f"item{i:02d}.jpg"
        if cek_saja:
            print(f"  cek item{i:02d}: {src.name} -> {dst.name}")
            continue
        tempel_satu(src, background, dst)
        it["foto_lokal"] = str(dst)
        print(f"  OK item{i:02d} {it['nama']}")

    if not cek_saja:
        tema_path.write_text(json.dumps(tema, indent=1, ensure_ascii=False))
        print(f"\nSELESAI: {len(items)} stiker di {kerja/'tempel'}/ — tema json terupdate")


if __name__ == "__main__":
    main()
