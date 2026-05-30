"""③④映像素材: 固定キャラ（猫）を参照しつつ、テーマ別の世界（背景）を生成。"""
from __future__ import annotations

from ..base import Stage, StageContext, StageResult
from ...state.models import Video, VideoStatus


class VisualsStage(Stage):
    """Gemini Nano Banana 2 に猫の正典（assets/brand/cat_ref_v1.png）を参照画像として与え、
    テーマ（世界）に合う1枚絵を生成して ``data/assets/backgrounds/<id>/`` に保存する。

    - 猫は固定（毎回生成しない＝一貫性が崩れるため）。参照画像でキャラ固定する。
    - 本番フレームは可視透かし回避のため Gemini API を使う（無料アプリは透かし付き）。
    - 動き（モーション）は本工程では作らない。compose 工程で微細ループを付与する。
    """

    name = "visuals"
    requires = VideoStatus.MUSIC_READY
    produces = VideoStatus.VISUALS_READY

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        raise NotImplementedError(
            "Phase 1: Gemini API で猫参照固定の世界画像を生成・保存する"
        )
