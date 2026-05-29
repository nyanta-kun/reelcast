"""⑨アップロード: 人間承認(APPROVED)後、YouTube に限定公開アップ→予約公開。"""
from __future__ import annotations

from ..base import Stage, StageContext, StageResult
from ...state.models import Video, VideoStatus


class PublishStage(Stage):
    """APPROVED の動画を YouTube Data API でアップロードし、publishAt で予約公開する。

    人間承認ゲート（AWAITING_REVIEW → APPROVED）を通過した動画のみが対象。
    """

    name = "publish"
    requires = VideoStatus.APPROVED
    produces = VideoStatus.PUBLISHED

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        raise NotImplementedError("Phase 1: YouTube API アップロード＋予約公開を実装する")
