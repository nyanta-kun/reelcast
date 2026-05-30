"""⑤合成・長尺化: キャラ＋背景＋音楽を ffmpeg でループ合成し長尺動画を生成。"""
from __future__ import annotations

from ..base import Stage, StageContext, StageResult
from ...state.models import Video, VideoStatus


class ComposeStage(Stage):
    """世界画像（猫＋背景）と音楽を合成し、45-60分の長尺としてレンダリング
    （``data/assets/renders/``）。実装はコード自動化（ffmpeg / MoviePy）。

    動きは**微細ループ**で付与する（フルアニメは作らない）：
    ゆっくりズーム/パララックス、雨・湯気・光のゆらぎオーバーレイ等。
    ⚠️ ffmpeg 本体が必要: ``brew install ffmpeg``（導入済み 8.1.1）
    """

    name = "compose"
    requires = VideoStatus.VISUALS_READY
    produces = VideoStatus.COMPOSED

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        raise NotImplementedError("Phase 1: ffmpeg によるループ合成・長尺化を実装する")
