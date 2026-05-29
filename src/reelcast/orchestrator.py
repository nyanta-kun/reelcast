"""パイプライン駆動。動画を自動工程で進め、人間ゲート/終端/未実装で停止する。"""
from __future__ import annotations

from dataclasses import dataclass

from .pipeline.base import Stage, StageContext, StageResult
from .pipeline.stages import ALL_STAGES
from .state.models import Video, VideoStatus


@dataclass
class StepReport:
    stage: str
    result: StageResult


class Orchestrator:
    def __init__(self, ctx: StageContext, stages: list[Stage] | None = None):
        self.ctx = ctx
        # requires 状態 → 工程 の対応表
        self.by_requires: dict[VideoStatus, Stage] = {
            s.requires: s for s in (stages or ALL_STAGES)
        }

    def next_stage(self, video: Video) -> Stage | None:
        return self.by_requires.get(video.status)

    def step(self, video: Video) -> StepReport | None:
        """現在の状態に対応する工程を1つ実行する。対応工程がなければ None。"""
        stage = self.next_stage(video)
        if stage is None:
            return None  # 終端 or 人間ゲート（AWAITING_REVIEW など）

        # 冪等性: 既に成果物があれば実行せず次状態へ
        if stage.is_satisfied(video, self.ctx):
            self.ctx.store.set_status(video.id, stage.produces)  # type: ignore[arg-type]
            return StepReport(stage.name, StageResult(True, "already satisfied; skipped"))

        try:
            result = stage.run(video, self.ctx)
        except NotImplementedError as e:
            # Phase 0: 未実装工程は失敗扱いにせず保留。状態は据え置き（実装後に再開可能）。
            msg = f"未実装(Phase 1): {e}"
            self.ctx.store.log_stage_run(video.id, stage.name, False, msg)  # type: ignore[arg-type]
            return StepReport(stage.name, StageResult(False, msg))

        self.ctx.store.log_stage_run(video.id, stage.name, result.ok, result.message)  # type: ignore[arg-type]
        if result.ok:
            self.ctx.store.set_status(video.id, stage.produces)  # type: ignore[arg-type]
        else:
            self.ctx.store.set_status(video.id, VideoStatus.FAILED)  # type: ignore[arg-type]
        return StepReport(stage.name, result)

    def run(self, video_id: int) -> list[StepReport]:
        """自動で進められるところまで進める。"""
        reports: list[StepReport] = []
        while True:
            video = self.ctx.store.get_video(video_id)
            if video is None:
                break
            report = self.step(video)
            if report is None:
                break  # 対応工程なし（終端 or 人間ゲート）
            reports.append(report)
            if not report.result.ok:
                break  # 失敗/未実装で停止
        return reports
