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
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}


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


def extract_frame(video: Path, out: Path, *, t: float = 1.0) -> Path:
    """動画から1フレームを静止画として書き出す（サムネのベース等に使う）。"""
    ffmpeg = _require("ffmpeg")
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [ffmpeg, "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise FFmpegError(f"フレーム抽出に失敗:\n{proc.stderr[-2000:]}")
    return out


def find_font() -> str | None:
    """drawtext 用のフォントを探す（日本語対応を優先）。見つからなければ None。"""
    candidates = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def make_thumbnail(image: Path, out: Path, *, width: int = 1280, height: int = 720) -> Path:
    """世界画像から 1280x720 のサムネ（テキストなし・cover クロップ）を生成。

    テキスト焼き込みは media/thumbnail.py（Pillow）で行う。
    （Homebrew の ffmpeg は drawtext を含まないことがあるため ffmpeg では文字を描かない）
    """
    ffmpeg = _require("ffmpeg")
    out.parent.mkdir(parents=True, exist_ok=True)
    vf = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
    cmd = [ffmpeg, "-y", "-i", str(image), "-vf", vf, "-frames:v", "1", str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise FFmpegError(f"サムネ生成に失敗:\n{proc.stderr[-2000:]}")
    return out


def make_short(
    src: Path,
    out: Path,
    *,
    start: float = 0.0,
    duration: float = 30.0,
    width: int = 1080,
    height: int = 1920,
    crf: int = 20,
    preset: str = "veryfast",
) -> Path:
    """長尺(16:9)から縦型(9:16)ショートを切り出す。"""
    ffmpeg = _require("ffmpeg")
    out.parent.mkdir(parents=True, exist_ok=True)
    vf = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},format=yuv420p"
    cmd = [
        ffmpeg, "-y",
        "-ss", f"{start:.3f}", "-i", str(src), "-t", f"{duration:.3f}",
        "-vf", vf,
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise FFmpegError(f"ショート切り出しに失敗:\n{proc.stderr[-2000:]}")
    return out


def seamless_loop(src: Path, out: Path, *, crossfade: float = 1.0, crf: int = 20, preset: str = "veryfast") -> Path:
    """i2v クリップ等を、末尾と先頭をクロスフェードして継ぎ目のないループに変換。

    出力長 = 入力長 - crossfade。アンビエント（雨・煙・呼吸）の動きはこの手法でよく馴染む。
    入力が短すぎる場合はそのままコピー（無音化）して返す。
    """
    ffmpeg = _require("ffmpeg")
    out.parent.mkdir(parents=True, exist_ok=True)
    d = probe_duration(src)
    c = min(crossfade, d / 3.0) if d > 0 else crossfade
    if d <= 0 or d <= 2 * c:
        cmd = [ffmpeg, "-y", "-i", str(src), "-an",
               "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p", str(out)]
    else:
        loop_len = d - c
        fc = (
            f"[0:v]trim=0:{c:.3f},setpts=PTS-STARTPTS,format=yuva420p,fade=t=in:st=0:d={c:.3f}:alpha=1[head];"
            f"[0:v]trim={loop_len:.3f}:{d:.3f},setpts=PTS-STARTPTS,format=yuva420p,fade=t=out:st=0:d={c:.3f}:alpha=1[tail];"
            f"[tail][head]overlay=format=auto[seam];"
            f"[0:v]trim={c:.3f}:{loop_len:.3f},setpts=PTS-STARTPTS[mid];"
            f"[seam][mid]concat=n=2:v=1[v]"
        )
        cmd = [ffmpeg, "-y", "-i", str(src), "-filter_complex", fc, "-map", "[v]", "-an",
               "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p", str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise FFmpegError(f"シームレスループ化に失敗:\n{proc.stderr[-2000:]}")
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
