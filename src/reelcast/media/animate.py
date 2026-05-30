"""2.5D レイヤーアニメ：短いシームレスループを生成し、全長へループ＋音源結合。

設計（docs/CONCEPT.md / ユーザー方針）:
- 猫レイヤー（透過スプライト）：寝息＝縦方向のサイン伸縮、頭振り＝微小な上下移動。
- 背景レイヤー（猫なし）：パララックスのドリフト。
- すべての動きを「ループ長で整数周期」にしてシームレスループにする。
- 短尺ループ（例12秒）を Pillow でフレーム生成 → ffmpeg で全長へ無劣化ループ＋音源結合。
- テンポ連動（librosa）は次の増分で周期を BPM に合わせる。

要 Pillow（`pip install pillow`）。
"""
from __future__ import annotations

import math
import subprocess
from pathlib import Path

from .render import FFmpegError, _require, probe_duration


def _cover(img, width: int, height: int):
    """アスペクト維持で width x height を覆うようリサイズ＋センタークロップ。"""
    from PIL import Image

    sw, sh = img.size
    scale = max(width / sw, height / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - width) // 2, (nh - height) // 2
    return img.crop((left, top, left + width, top + height))


def render_loop_clip(
    bg_path: Path,
    cat_path: Path,
    out: Path,
    *,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    loop_seconds: float = 12.0,
    cat_scale: float = 0.5,      # 猫の高さ＝キャンバス高の割合
    cat_cx: float = 0.5,         # 猫の水平中心（割合）
    cat_cy: float = 0.66,        # 猫の接地点（割合・下端）
    breathing_amp: float = 0.022,  # 寝息の縦伸縮量（±2.2%）
    breathing_cycles: int = 3,     # ループ内の呼吸回数（整数＝シームレス）
    bob_px: int = 10,              # 頭振りの上下幅(px)
    bob_cycles: int = 1,
    parallax_px: int = 40,         # 背景ドリフト幅(px)
    crf: int = 20,
    preset: str = "veryfast",
) -> Path:
    """猫（透過）＋背景からシームレスな短尺ループ動画（無音）を生成。"""
    from PIL import Image

    ffmpeg = _require("ffmpeg")
    out.parent.mkdir(parents=True, exist_ok=True)

    # 背景：パララックス余白を足して覆う
    bg = _cover(Image.open(bg_path).convert("RGB"), width + 2 * parallax_px, height + 2 * parallax_px)

    # 猫スプライト：高さを cat_scale に合わせる
    cat = Image.open(cat_path).convert("RGBA")
    ch = max(1, int(height * cat_scale))
    cw = max(1, int(cat.width * ch / cat.height))
    cat = cat.resize((cw, ch), Image.LANCZOS)

    anchor_x = int(width * cat_cx)
    anchor_bottom = int(height * cat_cy)

    n = max(1, int(round(loop_seconds * fps)))
    proc = subprocess.Popen(
        [ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{width}x{height}", "-r", str(fps), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
         "-pix_fmt", "yuv420p", str(out)],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    try:
        for i in range(n):
            t = i / fps
            # 背景パララックス（ループ内1周期＝シームレス）
            dx = int(round(parallax_px * math.sin(2 * math.pi * t / loop_seconds)))
            dy = int(round(parallax_px * 0.3 * math.sin(2 * math.pi * t / loop_seconds)))
            x0, y0 = parallax_px + dx, parallax_px + dy
            frame = bg.crop((x0, y0, x0 + width, y0 + height)).copy()

            # 寝息（縦伸縮・下端固定）＋頭振り（上下）
            s = 1.0 + breathing_amp * math.sin(2 * math.pi * breathing_cycles * t / loop_seconds)
            new_h = max(1, int(round(ch * s)))
            cat_s = cat.resize((cw, new_h), Image.LANCZOS)
            bob = int(round(bob_px * math.sin(2 * math.pi * bob_cycles * t / loop_seconds)))
            px = anchor_x - cw // 2
            py = anchor_bottom - new_h + bob
            frame.paste(cat_s, (px, py), cat_s)

            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
        ret = proc.wait()
        if ret != 0:
            err = proc.stderr.read().decode("utf-8", "ignore")[-2000:]
            raise FFmpegError(f"ループ生成に失敗:\n{err}")
    finally:
        if proc.poll() is None:
            proc.kill()
    return out


def loop_to_full(
    loop_mp4: Path,
    audio: Path,
    out: Path,
    *,
    duration: float | None = None,
) -> Path:
    """短尺ループを音源長まで無劣化ループ（copy）＋音源結合。"""
    ffmpeg = _require("ffmpeg")
    if duration is None:
        duration = probe_duration(audio)
    if duration <= 0:
        raise FFmpegError("音源の長さを取得できませんでした。")
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y",
        "-stream_loop", "-1", "-i", str(loop_mp4),
        "-i", str(audio),
        "-t", f"{duration:.3f}",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", "-shortest",
        str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise FFmpegError(f"全長ループ結合に失敗:\n{proc.stderr[-2000:]}")
    return out
