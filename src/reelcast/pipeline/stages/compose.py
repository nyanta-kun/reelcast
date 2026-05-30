"""⑤合成・長尺化: 世界画像（猫＋背景）＋音楽を ffmpeg で微細ループ合成。"""
from __future__ import annotations

from pathlib import Path

from ..base import Stage, StageContext, StageResult
from ...media.render import IMAGE_EXTS, FFmpegError, concat_audio, render_ambient_loop
from ...state.models import Video, VideoStatus

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"}


class ComposeStage(Stage):
    """世界画像（猫＋背景）と音楽を合成し、長尺としてレンダリング
    （``data/assets/renders/<id>/long.mp4``）。

    動きは**微細ループ**で付与する（フルアニメは作らない）：
    sin(t) による滑らかな水平ドリフト。
    ⚠️ ffmpeg 本体が必要: ``brew install ffmpeg``（導入済み 8.1.1）
    """

    name = "compose"
    requires = VideoStatus.VISUALS_READY
    produces = VideoStatus.COMPOSED

    def _out_path(self, video: Video, ctx: StageContext) -> Path:
        return ctx.config.paths.renders_dir / str(video.id) / "long.mp4"

    def _world_image(self, video: Video, ctx: StageContext) -> Path | None:
        d = ctx.config.paths.backgrounds_dir / str(video.id)
        if not d.is_dir():
            return None
        imgs = sorted(p for p in d.iterdir() if p.suffix.lower() in IMAGE_EXTS)
        return imgs[0] if imgs else None

    def _tracks(self, video: Video, ctx: StageContext) -> list[Path]:
        d = ctx.config.paths.music_dir / str(video.id)
        if not d.is_dir():
            return []
        return sorted(p for p in d.iterdir() if p.suffix.lower() in AUDIO_EXTS)

    def is_satisfied(self, video: Video, ctx: StageContext) -> bool:
        return self._out_path(video, ctx).exists()

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        image = self._world_image(video, ctx)
        if image is None:
            return StageResult(False, "背景画像が見つかりません（assets/backgrounds/<id>/ に1枚必要）")
        tracks = self._tracks(video, ctx)
        if not tracks:
            return StageResult(False, "音源が見つかりません（assets/music/<id>/ にトラックが必要）")

        out = self._out_path(video, ctx)
        try:
            audio = tracks[0] if len(tracks) == 1 else concat_audio(tracks, out.parent / "_audio.m4a")
            render_ambient_loop(image, audio, out)
        except FFmpegError as e:
            return StageResult(False, str(e))
        return StageResult(True, f"レンダリング完了: {out}")
