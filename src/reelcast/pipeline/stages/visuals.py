"""③④映像素材: 固定キャラ（資産）を確認し、テーマ別の背景ビジュアルを生成。"""
from __future__ import annotations

from ..base import Stage, StageContext, StageResult
from ...state.models import Video, VideoStatus


class VisualsStage(Stage):
    """固定キャラ資産（``data/assets/character/``）の存在を確認し、
    テーマに合う背景を無料/低コストの画像生成で用意する（商用可ツール）。

    キャラは毎回生成しない（一貫性が崩れるため）。背景のみ差し替える。
    """

    name = "visuals"
    requires = VideoStatus.MUSIC_READY
    produces = VideoStatus.VISUALS_READY

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        raise NotImplementedError("Phase 1: 固定キャラ確認＋背景生成を実装する")
