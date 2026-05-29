"""工程モジュール群。実装順に並ぶ。

Phase 1 で各 ``run()`` を実装する。現段階は stub（NotImplementedError）。
"""
from __future__ import annotations

from .compose import ComposeStage
from .ideation import IdeationStage
from .metadata import MetadataStage
from .music import MusicStage
from .publish import PublishStage
from .shorts import ShortsStage
from .thumbnail import ThumbnailStage
from .visuals import VisualsStage

# パイプラインの自動工程（人間承認ゲート AWAITING_REVIEW には自動工程を置かない）
ALL_STAGES = [
    IdeationStage(),
    MusicStage(),
    VisualsStage(),
    ComposeStage(),
    ThumbnailStage(),
    MetadataStage(),
    PublishStage(),
    ShortsStage(),
]

__all__ = [
    "ALL_STAGES",
    "IdeationStage",
    "MusicStage",
    "VisualsStage",
    "ComposeStage",
    "ThumbnailStage",
    "MetadataStage",
    "PublishStage",
    "ShortsStage",
]
