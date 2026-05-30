"""⑥サムネ生成: 世界画像から 1280x720 サムネを生成（タイトル焼き込みは Pillow で best-effort）。"""
from __future__ import annotations

from pathlib import Path

from ..base import Stage, StageContext, StageResult
from ...media.render import IMAGE_EXTS, FFmpegError, extract_frame, find_font, make_thumbnail
from ...state.models import Video, VideoStatus


class ThumbnailStage(Stage):
    name = "thumbnail"
    requires = VideoStatus.COMPOSED
    produces = VideoStatus.THUMBNAILED

    def _out_path(self, video: Video, ctx: StageContext) -> Path:
        return ctx.config.paths.renders_dir / str(video.id) / "thumbnail.png"

    def _world_image(self, video: Video, ctx: StageContext) -> Path | None:
        d = ctx.config.paths.backgrounds_dir / str(video.id)
        if not d.is_dir():
            return None
        imgs = sorted(p for p in d.iterdir() if p.suffix.lower() in IMAGE_EXTS)
        return imgs[0] if imgs else None

    def _base_image(self, video: Video, ctx: StageContext) -> Path | None:
        """サムネの元画像。合成済み長尺があればそのフレーム（猫が写る）、無ければ背景画像。"""
        long = ctx.config.paths.renders_dir / str(video.id) / "long.mp4"
        if long.exists():
            base = ctx.config.paths.renders_dir / str(video.id) / "_thumb_base.png"
            try:
                return extract_frame(long, base, t=1.0)
            except FFmpegError:
                pass
        return self._world_image(video, ctx)

    def is_satisfied(self, video: Video, ctx: StageContext) -> bool:
        return self._out_path(video, ctx).exists()

    def run(self, video: Video, ctx: StageContext) -> StageResult:
        image = self._base_image(video, ctx)
        if image is None:
            return StageResult(False, "元画像が見つかりません（assets/backgrounds/<id>/ か long.mp4）")
        out = self._out_path(video, ctx)
        font = find_font()

        # Pillow があればタイトル入りで生成。無ければ ffmpeg で画像のみ。
        if font:
            try:
                from ...media.thumbnail import make_thumbnail_text

                make_thumbnail_text(image, out, title=video.title, font=font)
                return StageResult(True, f"サムネ生成（タイトル入り）: {out}")
            except ImportError:
                pass  # Pillow 未導入 → 画像のみにフォールバック

        try:
            make_thumbnail(image, out)
        except FFmpegError as e:
            return StageResult(False, str(e))
        note = "フォント未検出" if not font else "Pillow未導入"
        return StageResult(True, f"サムネ生成（{note}のためテキストなし）: {out}")
