"""⑤合成・長尺化: 世界画像（猫＋背景）＋音楽を ffmpeg で微細ループ合成。

レイヤー素材があれば 2.5D アニメ合成（猫=寝息/頭振り、背景=パララックス）：
  assets/backgrounds/<id>/cat.png … 透過の猫スプライト
  assets/backgrounds/<id>/<other>.{png,jpg,…} … 猫なしの背景
両方そろえば layered、無ければ単一画像のドリフト（fallback）。
⚠️ ffmpeg 本体が必要: brew install ffmpeg（導入済み 8.1.1）
"""
from __future__ import annotations

from pathlib import Path

from ..base import Stage, StageContext, StageResult
from ...media.animate import loop_to_full, render_loop_clip
from ...media.render import IMAGE_EXTS, FFmpegError, concat_audio, render_ambient_loop
from ...state.models import Video, VideoStatus

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"}
CAT_LAYER = "cat.png"


class ComposeStage(Stage):
    name = "compose"
    requires = VideoStatus.VISUALS_READY
    produces = VideoStatus.COMPOSED

    def _bg_dir(self, video: Video, ctx: StageContext) -> Path:
        return ctx.config.paths.backgrounds_dir / str(video.id)

    def _out_path(self, video: Video, ctx: StageContext) -> Path:
        return ctx.config.paths.renders_dir / str(video.id) / "long.mp4"

    def _cat_layer(self, video: Video, ctx: StageContext) -> Path | None:
        p = self._bg_dir(video, ctx) / CAT_LAYER
        return p if p.exists() else None

    def _bg_image(self, video: Video, ctx: StageContext) -> Path | None:
        d = self._bg_dir(video, ctx)
        if not d.is_dir():
            return None
        imgs = sorted(
            p for p in d.iterdir()
            if p.suffix.lower() in IMAGE_EXTS and p.name != CAT_LAYER
        )
        return imgs[0] if imgs else None

    def _tracks(self, video: Video, ctx: StageContext) -> list[Path]:
        d = ctx.config.paths.music_dir / str(video.id)
        if not d.is_dir():
            return []
        return sorted(p for p in d.iterdir() if p.suffix.lower() in AUDIO_EXTS)

    def is_satisfied(self, video: Video, ctx: StageContext) -> bool:
        return self._out_path(video, ctx).exists()

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        bg = self._bg_image(video, ctx)
        if bg is None:
            return StageResult(False, "背景画像が見つかりません（assets/backgrounds/<id>/）")
        tracks = self._tracks(video, ctx)
        if not tracks:
            return StageResult(False, "音源が見つかりません（assets/music/<id>/）")

        out = self._out_path(video, ctx)
        cat = self._cat_layer(video, ctx)
        try:
            audio = tracks[0] if len(tracks) == 1 else concat_audio(tracks, out.parent / "_audio.m4a")
            if cat is not None:
                # 2.5D レイヤーアニメ：短尺ループ → 全長へ無劣化ループ＋音源
                loop = out.parent / "_loop.mp4"
                render_loop_clip(bg, cat, loop)
                loop_to_full(loop, audio, out)
                mode = "レイヤーアニメ（寝息＋頭振り＋パララックス）"
            else:
                render_ambient_loop(bg, audio, out)
                mode = "単一画像ドリフト（fallback：cat.png 未配置）"
        except FFmpegError as e:
            return StageResult(False, str(e))
        return StageResult(True, f"レンダリング完了[{mode}]: {out}")
