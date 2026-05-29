"""②音楽: 人間アシスト生成（Suno Pro）＋ 自動取り込み・検証。

決定（docs/TOOLS.md）: Suno Pro($10/月) は公式APIなし。第三者APIは規約リスクのため不採用。
→ 人間が Suno Web で週次バッチ生成・DL し ``data/assets/music/<video_id>/`` に投入。
   本工程はトラックの存在を検証して MUSIC_READY へ進める（生成自体はしない）。
   音楽選定の人間キュレーションは YouTube のAI音楽収益化要件にも合致する。
"""
from __future__ import annotations

from ..base import Stage, StageContext, StageResult
from ...state.models import Video, VideoStatus

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"}


class MusicStage(Stage):
    name = "music"
    requires = VideoStatus.IDEATED
    produces = VideoStatus.MUSIC_READY

    def _track_dir(self, video: Video, ctx: StageContext):
        return ctx.config.paths.music_dir / str(video.id)

    def is_satisfied(self, video: Video, ctx: StageContext) -> bool:
        d = self._track_dir(video, ctx)
        return d.is_dir() and any(p.suffix.lower() in AUDIO_EXTS for p in d.iterdir())

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        # 取り込みモデル: 人間が投入したトラックの存在を検証する。
        raise NotImplementedError(
            "Phase 1: data/assets/music/<id>/ のトラック検証（長さ・形式・本数）を実装する。"
            " 生成は人間アシスト（Suno Pro Web → DL → 投入）。"
        )
