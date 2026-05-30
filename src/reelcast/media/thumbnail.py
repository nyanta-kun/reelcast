"""Pillow によるサムネのテキスト描画・合成（drawtext 非依存）。"""
from __future__ import annotations

from pathlib import Path


def _cover_resize(img, width: int, height: int):
    from PIL import Image

    sw, sh = img.size
    scale = max(width / sw, height / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - width) // 2, (nh - height) // 2
    return img.crop((left, top, left + width, top + height))


def make_thumbnail_text(
    image: Path,
    out: Path,
    *,
    title: str,
    font: str,
    width: int = 1280,
    height: int = 720,
) -> Path:
    """世界画像を 1280x720 にして、下部に半透明バー＋タイトルを描画する。

    Pillow が必要（`pip install pillow`）。フォントは日本語対応のものを渡すこと。
    """
    from PIL import Image, ImageDraw, ImageFont

    img = _cover_resize(Image.open(image).convert("RGB"), width, height)
    draw = ImageDraw.Draw(img, "RGBA")

    margin = 64
    size = 76
    while size > 28:
        fnt = ImageFont.truetype(font, size)
        if draw.textlength(title, font=fnt) <= width - 2 * margin:
            break
        size -= 4
    fnt = ImageFont.truetype(font, size)

    bbox = draw.textbbox((0, 0), title, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 22
    bar_h = th + 2 * pad
    draw.rectangle([0, height - bar_h, width, height], fill=(0, 0, 0, 120))
    tx = (width - tw) // 2 - bbox[0]
    ty = height - bar_h + pad - bbox[1]
    draw.text((tx + 2, ty + 2), title, font=fnt, fill=(0, 0, 0, 180))  # shadow
    draw.text((tx, ty), title, font=fnt, fill=(255, 255, 255, 255))

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out
