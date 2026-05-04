from __future__ import annotations

import ctypes
import os
from pathlib import Path
from typing import Protocol

from PIL import Image

from .backend import Snapshot
from .models import ActionResult, Point


def resolve_traa_library_path() -> str | None:
    explicit = os.environ.get("TRAA_LIBRARY_PATH")
    if explicit:
        return explicit

    candidates = [
        Path("/Users/sylar/.config/superpowers/worktrees/ui-automator/traa/v1-foundation/bin_agent/macos/libtraa.dylib"),
        Path("/Users/sylar/Documents/work/vibecoding/ui-automator/traa/bin_local/macos/libtraa.dylib"),
        Path("/Users/sylar/Documents/work/vibecoding/ui-automator/traa/bin/macos/libtraa.dylib"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


class TraaSize(ctypes.Structure):
    _fields_ = [
        ("width", ctypes.c_int32),
        ("height", ctypes.c_int32),
    ]


class TraaRect(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_int32),
        ("top", ctypes.c_int32),
        ("right", ctypes.c_int32),
        ("bottom", ctypes.c_int32),
    ]


class TraaScreenSourceInfo(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int64),
        ("screen_id", ctypes.c_int64),
        ("is_window", ctypes.c_bool),
        ("is_minimized", ctypes.c_bool),
        ("is_maximized", ctypes.c_bool),
        ("is_primary", ctypes.c_bool),
        ("rect", TraaRect),
        ("icon_size", TraaSize),
        ("thumbnail_size", TraaSize),
        ("title", ctypes.c_char * 256),
        ("process_path", ctypes.c_char * 256),
        ("icon_data", ctypes.POINTER(ctypes.c_uint8)),
        ("thumbnail_data", ctypes.POINTER(ctypes.c_uint8)),
    ]


class TraaSnapshotProvider(Protocol):
    def list_sources(self) -> list[dict[str, object]]: ...

    def create_snapshot(self, source_id: int) -> tuple[str, int, int]: ...


class RealTraaSnapshotProvider:
    def __init__(self, library_path: str, output_dir: Path | None = None) -> None:
        self._library_path = library_path
        self._output_dir = output_dir or Path("/tmp/traa-uiautomator")
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._lib = ctypes.CDLL(library_path)

        self._lib.traa_enum_screen_source_info.argtypes = [
            TraaSize,
            TraaSize,
            ctypes.c_uint,
            ctypes.POINTER(ctypes.POINTER(TraaScreenSourceInfo)),
            ctypes.POINTER(ctypes.c_int),
        ]
        self._lib.traa_enum_screen_source_info.restype = ctypes.c_int

        self._lib.traa_free_screen_source_info.argtypes = [
            ctypes.POINTER(TraaScreenSourceInfo),
            ctypes.c_int,
        ]
        self._lib.traa_free_screen_source_info.restype = ctypes.c_int

        self._lib.traa_create_snapshot.argtypes = [
            ctypes.c_int64,
            TraaSize,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8)),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(TraaSize),
        ]
        self._lib.traa_create_snapshot.restype = ctypes.c_int

        self._lib.traa_free_snapshot.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
        self._lib.traa_free_snapshot.restype = None

    def list_sources(self) -> list[dict[str, object]]:
        infos = ctypes.POINTER(TraaScreenSourceInfo)()
        count = ctypes.c_int(0)
        result = self._lib.traa_enum_screen_source_info(
            TraaSize(0, 0),
            TraaSize(0, 0),
            ctypes.c_uint(0),
            ctypes.byref(infos),
            ctypes.byref(count),
        )
        if result != 0 or count.value <= 0:
            return []

        items: list[dict[str, object]] = []
        try:
            for index in range(count.value):
                info = infos[index]
                items.append(
                    {
                        "id": int(info.id),
                        "is_window": bool(info.is_window),
                        "title": bytes(info.title).split(b"\0", 1)[0].decode("utf-8", errors="ignore"),
                    }
                )
        finally:
            self._lib.traa_free_screen_source_info(infos, count)
        return items

    def create_snapshot(self, source_id: int) -> tuple[str, int, int]:
        data = ctypes.POINTER(ctypes.c_uint8)()
        data_size = ctypes.c_int(0)
        actual_size = TraaSize(0, 0)

        result = self._lib.traa_create_snapshot(
            ctypes.c_int64(source_id),
            TraaSize(1920, 1080),
            ctypes.byref(data),
            ctypes.byref(data_size),
            ctypes.byref(actual_size),
        )
        if result != 0:
            raise RuntimeError(f"traa_create_snapshot failed with error code {result}")

        try:
            byte_count = data_size.value
            raw = ctypes.string_at(data, byte_count)
            image = Image.frombytes("RGBA", (actual_size.width, actual_size.height), raw, "raw", "BGRA")
            output_path = self._output_dir / f"traa-snapshot-{source_id}.png"
            image.save(output_path)
            return str(output_path), int(actual_size.width), int(actual_size.height)
        finally:
            self._lib.traa_free_snapshot(data)


class TraaBackend:
    def __init__(self, provider: TraaSnapshotProvider | None = None, action_backend: object | None = None) -> None:
        self._provider = provider
        self._action_backend = action_backend

    def snapshot(self) -> Snapshot:
        if self._provider is None:
            raise RuntimeError("native traa backend is not wired yet")

        sources = self._provider.list_sources()
        source = next((item for item in sources if not item.get("is_window", False)), None)
        if source is None:
            raise RuntimeError("no non-window screen source available")

        path, width, height = self._provider.create_snapshot(int(source["id"]))
        return Snapshot(
            path=path,
            width=width,
            height=height,
            source_id=f"traa-provider:{source['id']}",
        )

    def snapshot_result(self) -> dict[str, object]:
        if self._provider is not None:
            try:
                snapshot = self.snapshot()
            except RuntimeError as exc:
                return {
                    "ok": False,
                    "error_code": "NO_SCREEN_SOURCE",
                    "message": str(exc),
                    "artifacts": {},
                    "observation_summary": None,
                    "next_action_hints": ["check_capture_permission"],
                }
            return {
                "ok": True,
                "error_code": None,
                "message": "snapshot captured",
                "artifacts": {"snapshot_path": snapshot.path},
                "observation_summary": f"Captured source {snapshot.source_id} at {snapshot.width}x{snapshot.height}",
                "next_action_hints": ["locate_target", "click", "type_text"],
                "source_id": snapshot.source_id,
                "width": snapshot.width,
                "height": snapshot.height,
            }

        return {
            "ok": False,
            "error_code": "NOT_IMPLEMENTED",
            "message": "native traa backend is not wired yet",
            "artifacts": {
                "resolved_library_path": resolve_traa_library_path(),
            },
            "observation_summary": None,
            "next_action_hints": ["use_fake_backend", "use_macos_shell_backend"],
        }

    def click(self, point: Point) -> ActionResult:
        if self._action_backend is not None:
            result = self._action_backend.click(point)
            if isinstance(result, ActionResult):
                return result
            return ActionResult(ok=bool(result["ok"]), error_code=result.get("error_code"), message=result["message"])
        return ActionResult(ok=False, error_code="NOT_IMPLEMENTED", message="traa backend does not support click")

    def type_text(self, text: str) -> ActionResult:
        if self._action_backend is not None:
            result = self._action_backend.type_text(text)
            if isinstance(result, ActionResult):
                return result
            return ActionResult(ok=bool(result["ok"]), error_code=result.get("error_code"), message=result["message"])
        return ActionResult(ok=False, error_code="NOT_IMPLEMENTED", message="traa backend does not support type_text")

    def press_hotkey(self, keys: tuple[str, ...]) -> ActionResult:
        if self._action_backend is not None:
            result = self._action_backend.press_hotkey(keys)
            if isinstance(result, ActionResult):
                return result
            return ActionResult(ok=bool(result["ok"]), error_code=result.get("error_code"), message=result["message"])
        return ActionResult(ok=False, error_code="NOT_IMPLEMENTED", message="traa backend does not support press_hotkey")

    def wait_for_change(self, timeout_ms: int) -> ActionResult:
        if self._action_backend is not None:
            result = self._action_backend.wait_for_change(timeout_ms)
            if isinstance(result, ActionResult):
                return result
            return ActionResult(ok=bool(result["ok"]), error_code=result.get("error_code"), message=result["message"])
        return ActionResult(ok=False, error_code="NOT_IMPLEMENTED", message="traa backend does not support wait_for_change")
