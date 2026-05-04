from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
import subprocess
import time
from typing import Callable

from PIL import Image

from .backend import Snapshot
from .models import ActionResult, Point


class MacOsShellBackend:
    def __init__(
        self,
        screenshot_dir: Path,
        runner: Callable[[list[str]], None] | None = None,
        screencapture_runner: Callable[[list[str]], None] | None = None,
    ) -> None:
        self._screenshot_dir = screenshot_dir
        self._runner = runner or self._default_runner
        self._screencapture_runner = screencapture_runner or self._default_runner

    def snapshot(self) -> Snapshot:
        self._screenshot_dir.mkdir(parents=True, exist_ok=True)
        path = self._screenshot_dir / (
            f"snapshot-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.png"
        )
        self._screencapture_runner(["screencapture", "-x", str(path)])
        with Image.open(path) as image:
            width, height = image.size
        return Snapshot(path=str(path), width=width, height=height, source_id="main-display")

    def click(self, point: Point) -> ActionResult:
        script = f'tell application "System Events" to click at {{{point.x}, {point.y}}}'
        try:
            self._runner(["osascript", "-e", script])
        except subprocess.CalledProcessError as exc:
            return self._translate_runner_error(exc)
        return ActionResult(ok=True, error_code=None, message=f"clicked at ({point.x}, {point.y})")

    def type_text(self, text: str) -> ActionResult:
        script = f'tell application "System Events" to keystroke "{text}"'
        try:
            self._runner(["osascript", "-e", script])
        except subprocess.CalledProcessError as exc:
            return self._translate_runner_error(exc)
        return ActionResult(ok=True, error_code=None, message=f"typed '{text}'")

    def press_hotkey(self, keys: tuple[str, ...]) -> ActionResult:
        modifiers = [key for key in keys[:-1]]
        key = keys[-1]
        statements = [f"key down {modifier}" for modifier in modifiers]
        statements.append(f'keystroke "{key}"')
        statements.extend(f"key up {modifier}" for modifier in reversed(modifiers))
        script = 'tell application "System Events" to ' + "\n".join(statements)
        try:
            self._runner(["osascript", "-e", script])
        except subprocess.CalledProcessError as exc:
            return self._translate_runner_error(exc)
        return ActionResult(ok=True, error_code=None, message=f"pressed {'+'.join(keys)}")

    def wait_for_change(self, timeout_ms: int, poll_interval_ms: int = 100) -> ActionResult:
        baseline = self.snapshot()
        deadline = time.monotonic() + (timeout_ms / 1000)
        while time.monotonic() <= deadline:
            current = self.snapshot()
            if current.width != baseline.width or current.height != baseline.height:
                return ActionResult(ok=True, error_code=None, message="change detected")
            time.sleep(poll_interval_ms / 1000)
        return ActionResult(ok=False, error_code="TIMEOUT", message="no visible change detected")

    @staticmethod
    def _default_runner(command: list[str]) -> None:
        subprocess.run(command, check=True)

    @staticmethod
    def _translate_runner_error(exc: subprocess.CalledProcessError) -> ActionResult:
        stderr = ""
        if exc.stderr:
            stderr = exc.stderr.decode("utf-8", errors="ignore") if isinstance(exc.stderr, bytes) else exc.stderr
        if "assistive access" in stderr.lower() or "-25211" in stderr:
            return ActionResult(
                ok=False,
                error_code="ASSISTIVE_ACCESS_DENIED",
                message="assistive access denied",
            )
        return ActionResult(
            ok=False,
            error_code="COMMAND_FAILED",
            message=stderr.strip() or f"command failed with exit code {exc.returncode}",
        )
