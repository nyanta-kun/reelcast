"""①テーマ選定: 需要/SEOデータをもとにAIがテーマ候補を提案 → 人間が選定。"""
from __future__ import annotations

from ..base import Stage, StageContext, StageResult
from ...state.models import Video, VideoStatus


class IdeationStage(Stage):
    """需要/SEOシグナル（YouTube Data API / Googleトレンド）＋LLMでテーマ候補を生成し、
    人間が選んだテーマを ``video.theme`` に確定する。選定は人間（AI提案→人間選定の方針）。
    """

    name = "ideation"
    requires = VideoStatus.NEW
    produces = VideoStatus.IDEATED

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        raise NotImplementedError("Phase 1: テーマ候補のAI提案と人間選定を実装する")
