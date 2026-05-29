"""状態機械とオーケストレータの最小テスト（外部依存なし）。"""
from __future__ import annotations

from pathlib import Path

from reelcast.config import Config, Paths
from reelcast.orchestrator import Orchestrator
from reelcast.pipeline.base import Stage, StageContext, StageResult
from reelcast.state.db import Store
from reelcast.state.models import Video, VideoStatus


def _ctx(tmp_path: Path) -> StageContext:
    cfg = Config(paths=Paths(data_dir=tmp_path))
    cfg.paths.ensure()
    return StageContext(config=cfg, store=Store(cfg.paths.db_path))


def test_create_and_status_roundtrip(tmp_path):
    ctx = _ctx(tmp_path)
    v = ctx.store.create_video(title="雨の夜カフェ vol.1", theme="rainy night cafe")
    assert v.id is not None
    assert v.status == VideoStatus.NEW

    ctx.store.set_status(v.id, VideoStatus.IDEATED)
    assert ctx.store.get_video(v.id).status == VideoStatus.IDEATED
    ctx.store.close()


def test_orchestrator_stops_on_unimplemented_stage(tmp_path):
    """stub工程は未実装。状態は据え置きで停止する（再開可能）。"""
    ctx = _ctx(tmp_path)
    v = ctx.store.create_video(title="t", theme="x")
    orch = Orchestrator(ctx)
    reports = orch.run(v.id)
    assert len(reports) == 1
    assert reports[0].stage == "ideation"
    assert reports[0].result.ok is False
    assert ctx.store.get_video(v.id).status == VideoStatus.NEW  # 据え置き
    ctx.store.close()


def test_orchestrator_runs_with_fake_stages(tmp_path):
    """実装済み工程なら状態が前進し、人間ゲート(AWAITING_REVIEW)で停止する。"""

    class FakeIdeation(Stage):
        name = "ideation"
        requires = VideoStatus.NEW
        produces = VideoStatus.AWAITING_REVIEW

        def run(self, video: Video, ctx: StageContext) -> StageResult:
            return StageResult(True, "done")

    ctx = _ctx(tmp_path)
    v = ctx.store.create_video(title="t")
    orch = Orchestrator(ctx, stages=[FakeIdeation()])
    reports = orch.run(v.id)
    assert reports[0].result.ok is True
    # AWAITING_REVIEW には自動工程がないので停止
    assert ctx.store.get_video(v.id).status == VideoStatus.AWAITING_REVIEW
    ctx.store.close()
