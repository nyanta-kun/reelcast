"""⑦メタデータ/SEO: タイトル・説明・章・タグを生成し、人間承認ゲートへ。"""
from __future__ import annotations

from ..base import Stage, StageContext, StageResult
from ...state.models import Video, VideoStatus


class MetadataStage(Stage):
    """需要/SEO起点でタイトル・説明・チャプター・タグを生成し ``video.metadata`` に保存。
    完了すると AWAITING_REVIEW（人間承認ゲート）へ遷移する。

    ⚠️ AI生成コンテンツの開示など規約順守項目もここで付与する。
    """

    name = "metadata"
    requires = VideoStatus.SHORTS_READY
    produces = VideoStatus.AWAITING_REVIEW

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        raise NotImplementedError("Phase 1: タイトル/説明/章/タグ生成と規約開示付与を実装する")
