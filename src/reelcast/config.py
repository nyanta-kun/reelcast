"""設定の読み込み。標準ライブラリのみ（tomllib）で動く。"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# src/reelcast/config.py -> リポジトリルート
ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "config.toml"
EXAMPLE_CONFIG_PATH = ROOT / "config" / "config.example.toml"


@dataclass
class Paths:
    data_dir: Path

    @property
    def db_path(self) -> Path:
        return self.data_dir / "reelcast.db"

    @property
    def assets_dir(self) -> Path:
        return self.data_dir / "assets"

    @property
    def character_dir(self) -> Path:
        return self.assets_dir / "character"

    @property
    def backgrounds_dir(self) -> Path:
        return self.assets_dir / "backgrounds"

    @property
    def music_dir(self) -> Path:
        return self.assets_dir / "music"

    @property
    def renders_dir(self) -> Path:
        return self.assets_dir / "renders"

    def ensure(self) -> None:
        """必要なディレクトリを作成（冪等）。"""
        for p in (
            self.data_dir,
            self.assets_dir,
            self.character_dir,
            self.backgrounds_dir,
            self.music_dir,
            self.renders_dir,
        ):
            p.mkdir(parents=True, exist_ok=True)


@dataclass
class Config:
    paths: Paths
    human_review: bool = True
    raw: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        cfg_path = path or (CONFIG_PATH if CONFIG_PATH.exists() else EXAMPLE_CONFIG_PATH)
        with open(cfg_path, "rb") as f:
            raw = tomllib.load(f)

        data_dir = Path(raw.get("paths", {}).get("data_dir", "data"))
        if not data_dir.is_absolute():
            data_dir = ROOT / data_dir

        return cls(
            paths=Paths(data_dir=data_dir),
            human_review=bool(raw.get("pipeline", {}).get("human_review", True)),
            raw=raw,
        )
