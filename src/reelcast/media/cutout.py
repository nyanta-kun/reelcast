"""背景除去（切り抜き）。Nano Banana 等の「市松模様＝偽の透過（実体は不透明）」を
本物の透過スプライトに変換する。要 rembg（`pip install rembg onnxruntime`）。
"""
from __future__ import annotations

from pathlib import Path


def remove_background(src: Path, out: Path, *, crop: bool = True) -> Path:
    """src の被写体を切り抜き、透過 PNG として out に保存。crop=True で余白を詰める。

    初回実行時に rembg のモデル（u2net.onnx, ~176MB）が ~/.u2net に自動DLされる。
    """
    from PIL import Image
    from rembg import remove

    img = remove(Image.open(src).convert("RGBA"))
    if crop:
        bbox = img.split()[-1].getbbox()
        if bbox:
            img = img.crop(bbox)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out
