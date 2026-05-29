"""⑥サムネ生成: 世界観に沿ったサムネイルを生成。"""
from __future__ import annotations

from ..base import Stage, StageContext, StageResult
from ...state.models import Video, VideoStatus


class ThumbnailStage(Stage):
    """固定キャラ・背景を使い、SEO/クリック率を意識したサムネを生成。"""

    name = "thumbnail"
    requires = VideoStatus.COMPOSED
    produces = VideoStatus.THUMBNAILED

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        raise NotImplementedError("Phase 1: サムネ生成を実装する")
