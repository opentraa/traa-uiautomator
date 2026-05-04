from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import ActionResult, Point


@dataclass(frozen=True)
class Snapshot:
    path: str
    width: int
    height: int
    source_id: str


class Backend(Protocol):
    def snapshot(self) -> Snapshot: ...

    def click(self, point: Point) -> ActionResult: ...

    def type_text(self, text: str) -> ActionResult: ...

    def press_hotkey(self, keys: tuple[str, ...]) -> ActionResult: ...

    def wait_for_change(self, timeout_ms: int) -> ActionResult: ...
