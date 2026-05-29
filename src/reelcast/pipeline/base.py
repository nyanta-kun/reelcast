"""工程（Stage）の基底クラスと共通型。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..config import Config
from ..state.db import Store
from ..state.models import Video, VideoStatus


@dataclass
class StageContext:
    """各工程に渡す実行コンテキスト。"""

    config: Config
    store: Store


@dataclass
class StageResult:
    ok: bool
    message: str = ""


class Stage(ABC):
    """工程の基底クラス。

    設計原則（docs/PLAN.md F より）:
    - 冪等・再実行可能: 途中失敗しても安全に再実行できること。
      既に成果物がある場合は ``is_satisfied()`` で検知してスキップする。
    - 単方向の状態遷移: ``requires`` 状態の動画を受け取り、成功時に ``produces`` へ進める。
    - ``human_gate=True`` の工程は自動実行の対象だが、人間の承認が必要なことを示す。
    """

    name: str = "stage"
    requires: VideoStatus = VideoStatus.NEW
    produces: VideoStatus = VideoStatus.NEW
    human_gate: bool = False

    def is_satisfied(self, video: Video, ctx: StageContext) -> bool:
        """成果物が既にあるか（冪等性チェック）。既定は False＝常に実行。"""
        return False

    @abstractmethod
    def run(self, video: Video, ctx: StageContext) -> StageResult:
        """工程を実行する。実装は Phase 1。"""
        raise NotImplementedError
