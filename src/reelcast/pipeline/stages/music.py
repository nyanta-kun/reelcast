"""②音楽生成: 商用権を確保した有料AI音楽ツールで複数トラックを生成し、45-60分に構成。"""
from __future__ import annotations

from ..base import Stage, StageContext, StageResult
from ...state.models import Video, VideoStatus


class MusicStage(Stage):
    """テーマに沿った楽曲を生成し ``data/assets/music/`` に保存。

    ⚠️ 使用ツールは商用利用権を明文で確保したプランであること（収益化の前提）。
    """

    name = "music"
    requires = VideoStatus.IDEATED
    produces = VideoStatus.MUSIC_READY

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        raise NotImplementedError("Phase 1: AI音楽生成（商用権あり）と長尺構成を実装する")
