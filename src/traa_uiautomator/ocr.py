from __future__ import annotations

from typing import Protocol


class OcrEngine(Protocol):
    def find_text(self, image_path: str, query: str) -> list[dict[str, object]]: ...


class NullOcrEngine:
    def find_text(self, image_path: str, query: str) -> list[dict[str, object]]:
        return []
