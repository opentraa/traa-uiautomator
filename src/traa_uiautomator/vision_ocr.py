from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Callable

from .models import Rect


class VisionOcrEngine:
    def __init__(self, runner: Callable[[str, str], str] | None = None) -> None:
        self._runner = runner or self._default_runner

    def find_text(self, image_path: str, query: str) -> list[dict[str, object]]:
        output = self._runner(image_path, query)
        matches: list[dict[str, object]] = []
        for line in output.splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            rect = item["rect"]
            matches.append(
                {
                    "text": item["text"],
                    "confidence": item["confidence"],
                    "rect": Rect(
                        x=rect["x"],
                        y=rect["y"],
                        width=rect["width"],
                        height=rect["height"],
                    ),
                }
            )
        return matches

    @staticmethod
    def build_command(image_path: str, query: str) -> list[str]:
        script_path = Path(__file__).resolve().parents[2] / "scripts" / "vision_ocr.swift"
        return [
            "swift",
            str(script_path),
            image_path,
            query,
        ]

    @staticmethod
    def _default_runner(image_path: str, query: str) -> str:
        command = VisionOcrEngine.build_command(image_path, query)
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
        return completed.stdout
