"""SQLite による状態ストア。"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import Video, VideoStatus

SCHEMA = """
CREATE TABLE IF NOT EXISTS videos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    theme       TEXT NOT NULL DEFAULT '',
    status      TEXT NOT NULL DEFAULT 'new',
    notes       TEXT NOT NULL DEFAULT '',
    metadata    TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stage_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id    INTEGER NOT NULL,
    stage       TEXT NOT NULL,
    ok          INTEGER NOT NULL,
    message     TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL,
    FOREIGN KEY (video_id) REFERENCES videos(id)
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    """動画と工程実行履歴を保持する軽量ストア。"""

    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # --- videos ---
    def create_video(self, title: str, theme: str = "", notes: str = "") -> Video:
        now = _now()
        cur = self.conn.execute(
            "INSERT INTO videos (title, theme, status, notes, metadata, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, theme, VideoStatus.NEW.value, notes, "{}", now, now),
        )
        self.conn.commit()
        return self.get_video(cur.lastrowid)  # type: ignore[arg-type]

    def get_video(self, vid: int) -> Video | None:
        row = self.conn.execute("SELECT * FROM videos WHERE id = ?", (vid,)).fetchone()
        return self._row_to_video(row) if row else None

    def list_videos(self, status: VideoStatus | None = None) -> list[Video]:
        if status is not None:
            rows = self.conn.execute(
                "SELECT * FROM videos WHERE status = ? ORDER BY id", (status.value,)
            ).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM videos ORDER BY id").fetchall()
        return [self._row_to_video(r) for r in rows]

    def set_status(self, vid: int, status: VideoStatus) -> None:
        self.conn.execute(
            "UPDATE videos SET status = ?, updated_at = ? WHERE id = ?",
            (status.value, _now(), vid),
        )
        self.conn.commit()

    def update_metadata(self, vid: int, metadata: dict) -> None:
        self.conn.execute(
            "UPDATE videos SET metadata = ?, updated_at = ? WHERE id = ?",
            (json.dumps(metadata, ensure_ascii=False), _now(), vid),
        )
        self.conn.commit()

    # --- stage history ---
    def log_stage_run(self, video_id: int, stage: str, ok: bool, message: str = "") -> None:
        self.conn.execute(
            "INSERT INTO stage_runs (video_id, stage, ok, message, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (video_id, stage, 1 if ok else 0, message, _now()),
        )
        self.conn.commit()

    def stage_history(self, video_id: int) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM stage_runs WHERE video_id = ? ORDER BY id", (video_id,)
        ).fetchall()

    @staticmethod
    def _row_to_video(row: sqlite3.Row) -> Video:
        return Video(
            id=row["id"],
            title=row["title"],
            theme=row["theme"],
            status=VideoStatus(row["status"]),
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            metadata=json.loads(row["metadata"] or "{}"),
        )
