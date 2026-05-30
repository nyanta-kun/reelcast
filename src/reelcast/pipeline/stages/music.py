"""②音楽: 人間アシスト生成（Suno Pro）＋ 自動取り込み・検証。

決定（docs/TOOLS.md）: Suno Pro($10/月) は公式APIなし。第三者APIは規約リスクのため不採用。
→ 人間が Suno Web で週次バッチ生成・DL し ``data/assets/music/<video_id>/`` に投入。
   本工程はトラックの存在・有効性を検証して MUSIC_READY へ進める（生成自体はしない）。
"""
from __future__ import annotations

from ..base import Stage, StageContext, StageResult
from ...media.render import FFmpegError, probe_duration
from ...state.models import Video, VideoStatus

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"}


class MusicStage(Stage):
    name = "music"
    requires = VideoStatus.IDEATED
    produces = VideoStatus.MUSIC_READY

    def _track_dir(self, video: Video, ctx: StageContext):
        return ctx.config.paths.music_dir / str(video.id)

    def _tracks(self, video: Video, ctx: StageContext):
        d = self._track_dir(video, ctx)
        if not d.is_dir():
            return []
        return sorted(p for p in d.iterdir() if p.suffix.lower() in AUDIO_EXTS)

    def is_satisfied(self, video: Video, ctx: StageContext) -> bool:
        return bool(self._tracks(video, ctx))

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        tracks = self._tracks(video, ctx)
        if not tracks:
            return StageResult(
                False,
                f"音源未投入: {self._track_dir(video, ctx)} に Suno で生成したトラックを入れてください",
            )
        total = 0.0
        for t in tracks:
            try:
                dur = probe_duration(t)
            except FFmpegError as e:
                return StageResult(False, str(e))
            if dur <= 0:
                return StageResult(False, f"無効または破損した音源: {t.name}")
            total += dur
        return StageResult(True, f"{len(tracks)} トラック / 合計 {total/60:.1f} 分 を確認")
