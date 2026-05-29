"""reelcast コマンドラインインターフェース。"""
from __future__ import annotations

import argparse
import shutil
import sys

from .config import CONFIG_PATH, EXAMPLE_CONFIG_PATH, Config
from .orchestrator import Orchestrator
from .pipeline.base import StageContext
from .state.db import Store
from .state.models import VideoStatus


def _store(cfg: Config) -> Store:
    cfg.paths.ensure()
    return Store(cfg.paths.db_path)


def cmd_init(args: argparse.Namespace) -> int:
    if not CONFIG_PATH.exists():
        shutil.copyfile(EXAMPLE_CONFIG_PATH, CONFIG_PATH)
        print(f"作成: {CONFIG_PATH}")
    else:
        print(f"既存: {CONFIG_PATH}")
    cfg = Config.load()
    cfg.paths.ensure()
    store = _store(cfg)
    store.close()
    print(f"データ領域: {cfg.paths.data_dir}")
    print(f"DB初期化: {cfg.paths.db_path}")
    print("初期化完了。")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    cfg = Config.load()
    store = _store(cfg)
    video = store.create_video(title=args.title, theme=args.theme or "", notes=args.notes or "")
    store.close()
    print(f"#{video.id} 登録: {video.title}  [status={video.status.value}]")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    cfg = Config.load()
    store = _store(cfg)
    status = VideoStatus(args.status) if args.status else None
    videos = store.list_videos(status)
    store.close()
    if not videos:
        print("（動画なし）")
        return 0
    for v in videos:
        theme = f" / {v.theme}" if v.theme else ""
        print(f"#{v.id:>3}  [{v.status.value:<16}] {v.title}{theme}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    cfg = Config.load()
    store = _store(cfg)
    video = store.get_video(args.id)
    if video is None:
        store.close()
        print(f"動画 #{args.id} が見つかりません", file=sys.stderr)
        return 1
    print(f"#{video.id}  {video.title}")
    print(f"  theme : {video.theme or '(未確定)'}")
    print(f"  status: {video.status.value}")
    print(f"  更新  : {video.updated_at}")
    history = store.stage_history(video.id)
    if history:
        print("  履歴:")
        for h in history:
            mark = "OK " if h["ok"] else "NG "
            print(f"    {h['created_at']}  {mark} {h['stage']}  {h['message']}")
    store.close()
    return 0


def cmd_advance(args: argparse.Namespace) -> int:
    cfg = Config.load()
    store = _store(cfg)
    video = store.get_video(args.id)
    if video is None:
        store.close()
        print(f"動画 #{args.id} が見つかりません", file=sys.stderr)
        return 1
    orch = Orchestrator(StageContext(config=cfg, store=store))
    reports = orch.run(video.id)
    if not reports:
        v = store.get_video(video.id)
        if v and v.status == VideoStatus.AWAITING_REVIEW:
            print("人間承認ゲートで停止。`reelcast approve` で承認してください。")
        else:
            print(f"進められる工程がありません（status={v.status.value if v else '?'}）。")
    for r in reports:
        mark = "OK " if r.result.ok else "NG "
        print(f"{mark} {r.stage}: {r.result.message}")
    final = store.get_video(video.id)
    store.close()
    if final:
        print(f"→ 現在: {final.status.value}")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    cfg = Config.load()
    store = _store(cfg)
    video = store.get_video(args.id)
    if video is None:
        store.close()
        print(f"動画 #{args.id} が見つかりません", file=sys.stderr)
        return 1
    if video.status != VideoStatus.AWAITING_REVIEW:
        store.close()
        print(
            f"承認できる状態ではありません（現在: {video.status.value}, "
            f"必要: {VideoStatus.AWAITING_REVIEW.value}）",
            file=sys.stderr,
        )
        return 1
    store.set_status(video.id, VideoStatus.APPROVED)
    store.log_stage_run(video.id, "review", True, "人間が承認")
    store.close()
    print(f"#{video.id} 承認 → {VideoStatus.APPROVED.value}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="reelcast", description="AI機能性音楽パイプライン")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="設定・ディレクトリ・DBを初期化").set_defaults(func=cmd_init)

    a = sub.add_parser("add", help="動画を登録")
    a.add_argument("--title", required=True)
    a.add_argument("--theme", default="")
    a.add_argument("--notes", default="")
    a.set_defaults(func=cmd_add)

    li = sub.add_parser("list", help="動画一覧")
    li.add_argument("--status", choices=[s.value for s in VideoStatus], default=None)
    li.set_defaults(func=cmd_list)

    st = sub.add_parser("status", help="動画の状態と工程履歴")
    st.add_argument("id", type=int)
    st.set_defaults(func=cmd_status)

    adv = sub.add_parser("advance", help="自動工程を進める（人間ゲート/未実装で停止）")
    adv.add_argument("id", type=int)
    adv.set_defaults(func=cmd_advance)

    ap = sub.add_parser("approve", help="人間承認: AWAITING_REVIEW → APPROVED")
    ap.add_argument("id", type=int)
    ap.set_defaults(func=cmd_approve)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
