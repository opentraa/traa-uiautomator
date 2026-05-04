from __future__ import annotations

from pathlib import Path

from PIL import Image

from .backend import Snapshot
from .models import ActionResult, Point


class StaticImageBackend:
    def __init__(self, image_path: Path) -> None:
        self._image_path = image_path
        self.clicks: list[tuple[int, int]] = []

    def snapshot(self) -> Snapshot:
        with Image.open(self._image_path) as image:
            width, height = image.size
        return Snapshot(
            path=str(self._image_path),
            width=width,
            height=height,
            source_id="static-image",
        )

    def click(self, point: Point) -> ActionResult:
        self.clicks.append((point.x, point.y))
        return ActionResult(ok=True, error_code=None, message=f"clicked at ({point.x}, {point.y})")

    def click_at(self, x: int, y: int) -> dict[str, object]:
        result = self.click(Point(x=x, y=y)).to_dict()
        return result

    def type_text(self, text: str) -> ActionResult:
        return ActionResult(ok=True, error_code=None, message=f"typed '{text}'")

    def press_hotkey(self, keys: tuple[str, ...]) -> ActionResult:
        return ActionResult(ok=True, error_code=None, message=f"pressed {'+'.join(keys)}")

    def wait_for_change(self, timeout_ms: int) -> ActionResult:
        return ActionResult(ok=True, error_code=None, message=f"waited {timeout_ms}ms")
