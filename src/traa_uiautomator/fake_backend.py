from __future__ import annotations

from .backend import Snapshot
from .models import ActionResult, Point


class FakeBackend:
    def __init__(self) -> None:
        self.events: list[str] = []

    def snapshot(self) -> Snapshot:
        self.events.append("snapshot")
        return Snapshot(path="fake.png", width=1280, height=720, source_id="fake-source")

    def click(self, point: Point) -> ActionResult:
        self.events.append(f"click:{point.x},{point.y}")
        return ActionResult(ok=True, error_code=None, message=f"clicked at ({point.x}, {point.y})")

    def type_text(self, text: str) -> ActionResult:
        self.events.append(f"type:{text}")
        return ActionResult(ok=True, error_code=None, message=f"typed '{text}'")

    def press_hotkey(self, keys: tuple[str, ...]) -> ActionResult:
        combo = "+".join(keys)
        self.events.append(f"hotkey:{combo}")
        return ActionResult(ok=True, error_code=None, message=f"pressed {combo}")

    def wait_for_change(self, timeout_ms: int) -> ActionResult:
        self.events.append(f"wait_for_change:{timeout_ms}")
        return ActionResult(
            ok=True,
            error_code=None,
            message=f"change detected within {timeout_ms}ms",
        )
