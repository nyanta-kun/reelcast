"""ffmpeg ベースの映像合成：静止画 ＋ 音源 → 微細ループ長尺。

方針（docs/CONCEPT.md）:
- フルアニメは作らない。sin(t) による滑らかな水平ドリフト（パン）で「微細な動き」を付ける。
  zoompan のような整数丸めジッタを避けるため、連続値 t を使う。
- 固定キャラ＋背景は1枚の合成済み画像として受け取り、ここでは動かさず全体をドリフトさせる。
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


class FFmpegError(RuntimeError):
    pass


def _require(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        raise FFmpegError(f"{tool} が見つかりません。`brew install ffmpeg` を実行してください。")
    return path


def probe_duration(path: Path) -> float:
    """メディアの長さ（秒）を返す。"""
    ffprobe = _require("ffprobe")
    proc = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise FFmpegError(f"ffprobe 失敗: {proc.stderr.strip()}")
    data = json.loads(proc.stdout or "{}")
    return float(data.get("format", {}).get("duration", 0.0) or 0.0)


def concat_audio(tracks: list[Path], out: Path) -> Path:
    """複数トラックを1本に連結（再エンコード）。"""
    if not tracks:
        raise FFmpegError("連結するトラックがありません。")
    if len(tracks) == 1:
        return tracks[0]
    ffmpeg = _require("ffmpeg")
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [ffmpeg, "-y"]
    for t in tracks:
        cmd += ["-i", str(t)]
    streams = "".join(f"[{i}:a]" for i in range(len(tracks)))
    cmd += [
        "-filter_complex", f"{streams}concat=n={len(tracks)}:v=0:a=1[a]",
        "-map", "[a]", "-c:a", "aac", "-b:a", "192k", str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise FFmpegError(f"音源連結に失敗:\n{proc.stderr[-2000:]}")
    return out


def render_ambient_loop(
    image: Path,
    audio: Path,
    out: Path,
    *,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    drift_px: int = 80,
    period_s: float = 16.0,
    crf: int = 20,
    preset: str = "veryfast",
    duration: float | None = None,
) -> Path:
    """静止画に滑らかな微細ドリフトを付け、音源と合成して mp4 を書き出す。

    duration 未指定なら音源長に合わせる。動きは sin(t) による水平パン（ジッタなし）。
    """
    ffmpeg = _require("ffmpeg")
    if duration is None:
        duration = probe_duration(audio)
    if duration <= 0:
        raise FFmpegError("音源の長さを取得できませんでした。")

    out.parent.mkdir(parents=True, exist_ok=True)

    # 目標より一回り大きくスケールして全面を覆い、クロップ窓を time でドリフトさせる
    over_w = width + 2 * drift_px
    over_h = height + 2 * drift_px
    vf = (
        f"scale={over_w}:{over_h}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height}:"
        f"x='(in_w-{width})/2 + sin(t/{period_s})*{drift_px}':"
        f"y='(in_h-{height})/2',"
        f"format=yuv420p"
    )
    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-framerate", str(fps), "-i", str(image),
        "-i", str(audio),
        "-vf", vf,
        "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-pix_fmt", "yuv420p", "-r", str(fps),
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise FFmpegError(f"ffmpeg 合成に失敗:\n{proc.stderr[-2000:]}")
    return out
