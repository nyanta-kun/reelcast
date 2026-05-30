"""ドメインモデルと状態定義。"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class VideoStatus(str, Enum):
    """動画がパイプライン上で取りうる状態。"""

    NEW = "new"                          # 登録直後（テーマ未確定）
    IDEATED = "ideated"                  # ①テーマ確定
    MUSIC_READY = "music_ready"          # ②音楽（取り込み・検証）済み
    VISUALS_READY = "visuals_ready"      # ③④キャラ＋背景（世界画像）生成済み
    COMPOSED = "composed"                # ⑤合成・長尺化済み
    THUMBNAILED = "thumbnailed"          # ⑥サムネ生成済み
    SHORTS_READY = "shorts_ready"        # ⑦ショート切り出し済み（レビュー前に用意）
    AWAITING_REVIEW = "awaiting_review"  # ⑧メタ生成済み → 人間承認ゲート待ち
    APPROVED = "approved"                # 人間が承認
    PUBLISHED = "published"              # ⑨公開（予約公開）済み
    DONE = "done"                        # 完了（IG等の手動投稿まで含む）
    FAILED = "failed"                    # 工程が失敗（要対応）
    ON_HOLD = "on_hold"                  # 保留（未実装工程含む）


# 主経路の進行順（表示・検証用）
PIPELINE_ORDER: list[VideoStatus] = [
    VideoStatus.NEW,
    VideoStatus.IDEATED,
    VideoStatus.MUSIC_READY,
    VideoStatus.VISUALS_READY,
    VideoStatus.COMPOSED,
    VideoStatus.THUMBNAILED,
    VideoStatus.SHORTS_READY,
    VideoStatus.AWAITING_REVIEW,
    VideoStatus.APPROVED,
    VideoStatus.PUBLISHED,
    VideoStatus.DONE,
]


@dataclass
class Video:
    id: int | None
    title: str
    theme: str = ""
    status: VideoStatus = VideoStatus.NEW
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""
    metadata: dict = field(default_factory=dict)
