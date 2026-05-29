"""⑩ショート切り出し: 長尺から縦型ショートを切り出す（YouTube Shorts / IG Reels）。"""
from __future__ import annotations

from ..base import Stage, StageContext, StageResult
from ...state.models import Video, VideoStatus


class ShortsStage(Stage):
    """公開済み長尺から縦型ショートを生成。Instagram は当面 手動/半自動で投稿。"""

    name = "shorts"
    requires = VideoStatus.PUBLISHED
    produces = VideoStatus.DONE

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        raise NotImplementedError("Phase 1: ショート切り出しを実装する")
