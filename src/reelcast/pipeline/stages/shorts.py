"""⑦ショート切り出し: 長尺(16:9)から縦型(9:16)ショートを生成（レビュー前に用意）。

Instagram Reels / YouTube Shorts 用。投稿は別（YouTubeはAPI、IGは当面手動/半自動）。
ここでは長尺(long.mp4)からクリップを切り出してファイルを用意するのみ。
"""
from __future__ import annotations

from pathlib import Path

from ..base import Stage, StageContext, StageResult
from ...media.render import FFmpegError, make_short, probe_duration
from ...state.models import Video, VideoStatus

SHORT_DURATION = 30.0


class ShortsStage(Stage):
    name = "shorts"
    requires = VideoStatus.THUMBNAILED
    produces = VideoStatus.SHORTS_READY

    def _long_path(self, video: Video, ctx: StageContext) -> Path:
        return ctx.config.paths.renders_dir / str(video.id) / "long.mp4"

    def _out_path(self, video: Video, ctx: StageContext) -> Path:
        return ctx.config.paths.renders_dir / str(video.id) / "short.mp4"

    def is_satisfied(self, video: Video, ctx: StageContext) -> bool:
        return self._out_path(video, ctx).exists()

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        src = self._long_path(video, ctx)
        if not src.exists():
            return StageResult(False, "長尺が見つかりません（compose 工程を先に）")
        out = self._out_path(video, ctx)
        try:
            # 長尺の中盤からSHORT_DURATION秒を切り出す（先頭の助走を避ける）
            total = probe_duration(src)
            start = max(0.0, (total - SHORT_DURATION) / 2) if total > SHORT_DURATION else 0.0
            dur = min(SHORT_DURATION, total) if total > 0 else SHORT_DURATION
            make_short(src, out, start=start, duration=dur)
        except FFmpegError as e:
            return StageResult(False, str(e))
        return StageResult(True, f"ショート生成: {out}")
