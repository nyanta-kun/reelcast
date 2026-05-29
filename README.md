# reelcast

AI機能性音楽（作業用/睡眠/lo-fi/環境音）の映像付き長尺を、企画→生成→合成→投稿→運用まで一気通貫で回すパイプライン。完全フェイスレス・YouTube広告収益が土台。

方針の詳細は [`docs/PLAN.md`](docs/PLAN.md)、作業時の規約は [`CLAUDE.md`](CLAUDE.md) を参照。

## アーキテクチャ概要

各動画は状態機械を遷移する。各工程（Stage）は疎結合な独立モジュールで、**冪等・再実行可能**に作る。**公開は必ず人間承認ゲート**を通る。

```
NEW ─ideation→ IDEATED ─music→ MUSIC_READY ─visuals→ VISUALS_READY
   ─compose→ COMPOSED ─thumbnail→ THUMBNAILED ─metadata→ AWAITING_REVIEW
   ──[人間承認]──> APPROVED ─publish→ PUBLISHED ─shorts→ DONE
```

- 状態管理: SQLite（`data/reelcast.db`）
- 素材: ローカルファイル（`data/assets/...`）
- 言語: Python（標準ライブラリのみで骨格が動く）

## セットアップ

```bash
# 1) 仮想環境（任意だが推奨）
python3 -m venv .venv && source .venv/bin/activate

# 2) 開発インストール
pip install -e ".[dev]"

# 3) 初期化（config.toml 作成・ディレクトリ作成・DB初期化）
reelcast init
# もしくは: python -m reelcast.cli init
```

> ⚠️ 合成工程（Phase 1）には ffmpeg が必要: `brew install ffmpeg`

## 使い方（骨格段階）

```bash
reelcast add --title "雨の夜カフェ vol.1" --theme "rainy night cafe"  # 動画を登録
reelcast list                  # 一覧
reelcast status 1              # 状態と工程履歴
reelcast advance 1             # 自動工程を進める（人間ゲート/未実装で停止）
reelcast approve 1             # 人間承認: AWAITING_REVIEW → APPROVED
```

現段階では各工程は stub（`NotImplementedError`）。`advance` は未実装の工程で安全に停止する。工程の中身は Phase 1 で実装する。
